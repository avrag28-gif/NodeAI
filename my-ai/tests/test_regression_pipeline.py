import os
import sys
import asyncio
import re
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.agent.loop import AgentLoop


def make_mock_llm(response_text="Hello world"):
    client = AsyncMock()
    client.chat = AsyncMock(return_value=response_text)
    return client


def make_mock_tools():
    tools = MagicMock()
    tools.get_tool.return_value = None
    tools.list_tools.return_value = []
    return tools


# --- Config tests ---

def test_config_env_expansion():
    os.environ["MYAI_TEST_VAR"] = "expanded_value"
    try:
        from server.app import load_config
        config_path = str(Path(__file__).parent.parent / "config" / "config.yaml")
        raw = open(config_path).read()
        raw = raw.replace("${MYAI_AUTH_TOKEN}", "${MYAI_TEST_VAR}")
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(raw)
            tmp = f.name
        c = load_config(tmp)
        os.unlink(tmp)
        assert c["server"]["auth_token"] == "expanded_value", \
            f"Env expansion failed: {c['server']['auth_token']}"
        print("PASS: config env expansion works")
    finally:
        del os.environ["MYAI_TEST_VAR"]


def test_config_missing_env_fails():
    old = os.environ.pop("MYAI_AUTH_TOKEN", None)
    try:
        from server.app import load_config
        config_path = str(Path(__file__).parent.parent / "config" / "config.yaml")
        try:
            load_config(config_path)
            assert False, "Should have raised RuntimeError"
        except RuntimeError as e:
            assert "MYAI_AUTH_TOKEN" in str(e)
            print("PASS: missing env causes RuntimeError")
    finally:
        if old:
            os.environ["MYAI_AUTH_TOKEN"] = old


# --- Auth tests ---

def test_valid_auth():
    import httpx
    token = os.environ.get("MYAI_AUTH_TOKEN", "")
    if not token:
        print("SKIP: valid auth (no token set)")
        return
    try:
        r = httpx.post("http://127.0.0.1:5000/api/chat",
                       json={"message": "test"},
                       headers={"Authorization": f"Bearer {token}"},
                       timeout=120)
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        print("PASS: valid auth returns 200")
    except httpx.ConnectError:
        print("SKIP: valid auth (server not running)")


def test_invalid_auth():
    import httpx
    try:
        r = httpx.post("http://127.0.0.1:5000/api/chat",
                       json={"message": "test"},
                       headers={"Authorization": "Bearer wrong_token"},
                       timeout=10)
        assert r.status_code == 401, f"Expected 401, got {r.status_code}"
        print("PASS: invalid auth returns 401")
    except httpx.ConnectError:
        print("SKIP: invalid auth (server not running)")


def test_missing_auth():
    import httpx
    try:
        r = httpx.post("http://127.0.0.1:5000/api/chat",
                       json={"message": "test"},
                       timeout=10)
        assert r.status_code == 401, f"Expected 401, got {r.status_code}"
        print("PASS: missing auth returns 401")
    except httpx.ConnectError:
        print("SKIP: missing auth (server not running)")


# --- AgentLoop tests (mock) ---

@pytest.mark.asyncio
async def test_agentloop_returns_llm_text():
    llm = make_mock_llm("This is the answer")
    loop = AgentLoop(llm, make_mock_tools())
    result = await loop.process_message("What is 2+2?")
    assert result == "This is the answer", f"Expected LLM text, got: {result}"
    print("PASS: AgentLoop returns LLM text directly")


@pytest.mark.asyncio
async def test_agentloop_temperature():
    llm = make_mock_llm("OK")
    loop = AgentLoop(llm, make_mock_tools(), {"temperature": 0.3})
    await loop.process_message("test")
    call_kwargs = llm.chat.call_args
    assert call_kwargs.kwargs.get("temperature") == 0.3 or call_kwargs[1].get("temperature") == 0.3, \
        f"Temperature not passed: {call_kwargs}"
    print("PASS: AgentLoop forwards temperature")


@pytest.mark.asyncio
async def test_agentloop_max_tokens():
    llm = make_mock_llm("OK")
    loop = AgentLoop(llm, make_mock_tools(), {"max_tokens": 1024})
    await loop.process_message("test")
    call_kwargs = llm.chat.call_args
    assert call_kwargs.kwargs.get("max_tokens") == 1024 or call_kwargs[1].get("max_tokens") == 1024, \
        f"max_tokens not passed: {call_kwargs}"
    print("PASS: AgentLoop forwards max_tokens")


@pytest.mark.asyncio
async def test_agentloop_system_prompt():
    llm = make_mock_llm("OK")
    loop = AgentLoop(llm, make_mock_tools())
    await loop.process_message("test")
    call_args = llm.chat.call_args
    messages = call_args[0][0]
    assert messages[0]["role"] == "system", f"No system message: {messages}"
    assert "NodeAI assistant" in messages[0]["content"], \
        f"System prompt changed: {messages[0]['content']}"
    print("PASS: AgentLoop system prompt consistent")


@pytest.mark.asyncio
async def test_agentloop_no_refusal():
    llm = make_mock_llm("I cannot do that")
    loop = AgentLoop(llm, make_mock_tools())
    result = await loop.process_message("test request")
    assert result == "I cannot do that", \
        f"Refusal detection intercepted: got {result}"
    print("PASS: AgentLoop no refusal detection")


@pytest.mark.asyncio
async def test_agentloop_user_message():
    llm = make_mock_llm("OK")
    loop = AgentLoop(llm, make_mock_tools())
    await loop.process_message("What is Python?")
    call_args = llm.chat.call_args
    messages = call_args[0][0]
    user_msgs = [m for m in messages if m["role"] == "user"]
    assert len(user_msgs) >= 1, f"No user message: {messages}"
    assert user_msgs[0]["content"] == "What is Python?", \
        f"User message mismatch: {user_msgs[0]['content']}"
    print("PASS: AgentLoop user message included")


# --- LLM config consistency ---

def test_config_consistency():
    import yaml
    config_path = str(Path(__file__).parent.parent / "config" / "config.yaml")
    with open(config_path) as f:
        config = yaml.safe_load(f)

    llm_temp = config.get("llm", {}).get("temperature")
    agent_temp = config.get("agent", {}).get("temperature")
    llm_tokens = config.get("llm", {}).get("max_tokens")
    agent_tokens = config.get("agent", {}).get("max_tokens")

    assert llm_temp is not None, "LLM temperature not set"
    assert llm_tokens is not None, "LLM max_tokens not set"
    assert agent_temp is None or agent_temp == llm_temp, \
        f"Temperature mismatch: LLM={llm_temp}, Agent={agent_temp}"
    assert agent_tokens is None or agent_tokens == llm_tokens, \
        f"max_tokens mismatch: LLM={llm_tokens}, Agent={agent_tokens}"
    print("PASS: LLM config consistent (agent inherits LLM defaults)")


@pytest.mark.asyncio
async def test_agentloop_preserves_multi_turn_context():
    llm = make_mock_llm("ALPHA-7392")
    loop = AgentLoop(llm, make_mock_tools())
    await loop.process_message("Ingat token konteks ini: ALPHA-7392.")
    await loop.process_message("Token konteks apa yang tadi saya berikan?")
    messages = llm.chat.call_args[0][0]
    user_msgs = [m["content"] for m in messages if m["role"] == "user"]
    assert user_msgs == [
        "Ingat token konteks ini: ALPHA-7392.",
        "Token konteks apa yang tadi saya berikan?",
    ], f"Conversation context missing or reordered: {messages}"


@pytest.mark.asyncio
async def test_agentloop_action_prompt_requires_actual_tool_use():
    llm = make_mock_llm("OK")
    loop = AgentLoop(llm, make_mock_tools())
    await loop.process_message("Modifikasi kode project dan verifikasi hasilnya.")
    system_text = "\n".join(
        m["content"] for m in llm.chat.call_args[0][0] if m["role"] == "system"
    )
    assert "perform the requested action" in system_text
    assert "verify the result" in system_text
    assert "Never claim" in system_text


def test_conversation_context_budget_keeps_complete_recent_messages():
    from core.agent.conversation import ConversationManager
    conversation = ConversationManager(max_context_chars=20)
    conversation.add_user_message("old message")
    conversation.add_assistant_message("recent")
    conversation.add_user_message("current")
    messages = conversation.get_messages_for_llm(max_messages=20)
    assert messages == [
        {"role": "assistant", "content": "recent"},
        {"role": "user", "content": "current"},
    ], f"Unexpected bounded context: {messages}"


# --- Main ---

async def main():
    sync_tests = [
        test_config_env_expansion,
        test_config_missing_env_fails,
        test_config_consistency,
    ]

    async_tests = [
        test_agentloop_returns_llm_text,
        test_agentloop_temperature,
        test_agentloop_max_tokens,
        test_agentloop_system_prompt,
        test_agentloop_no_refusal,
        test_agentloop_user_message,
    ]

    http_tests = [
        test_valid_auth,
        test_invalid_auth,
        test_missing_auth,
    ]

    passed = 0
    failed = 0

    for test in sync_tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"FAIL: {test.__name__}: {e}")
            failed += 1

    for test in async_tests:
        try:
            await test()
            passed += 1
        except Exception as e:
            print(f"FAIL: {test.__name__}: {e}")
            failed += 1

    for test in http_tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"FAIL: {test.__name__}: {e}")
            failed += 1

    print(f"\n{'='*40}")
    print(f"Results: {passed} passed, {failed} failed")
    if failed == 0:
        print("ALL TESTS PASSED")
    else:
        print("SOME TESTS FAILED")
        sys.exit(1)


# --- Instruction-following tests (sentinel) ---

SENTINEL = "MODEL_OUTPUT_SENTINEL_7392"

@pytest.mark.asyncio
async def test_sentinel_returned_identically():
    llm = make_mock_llm(SENTINEL)
    loop = AgentLoop(llm, make_mock_tools())
    result = await loop.process_message("test")
    assert result == SENTINEL, f"Expected sentinel identical, got: {result}"
    print("PASS: sentinel returned identically")


@pytest.mark.asyncio
async def test_no_post_processing():
    responses = [
        "I cannot help with that.",
        "I'm sorry, but I can't assist with that request.",
        "As an AI, I must decline this request.",
        "DISCLAIMER: This is for educational purposes only.",
    ]
    for resp in responses:
        llm = make_mock_llm(resp)
        loop = AgentLoop(llm, make_mock_tools())
        result = await loop.process_message("test")
        assert result == resp, f"Post-processing detected: expected {resp!r}, got {result!r}"
    print("PASS: no post-processing on any response")


@pytest.mark.asyncio
async def test_no_disclaimer_injection():
    llm = make_mock_llm("Plain answer.")
    loop = AgentLoop(llm, make_mock_tools())
    result = await loop.process_message("test")
    assert "DISCLAIMER" not in result.upper()
    assert "WARNING" not in result.upper()
    assert "NOTICE" not in result.upper()
    print("PASS: no disclaimer injection")


@pytest.mark.asyncio
async def test_conversation_history_forwarded():
    llm = make_mock_llm("response")
    loop = AgentLoop(llm, make_mock_tools())
    await loop.process_message("first message")
    await loop.process_message("second message")
    call_args = llm.chat.call_args_list
    first_call_msgs = call_args[0][0][0]
    second_call_msgs = call_args[1][0][0]
    assert len(first_call_msgs) >= 2, f"Turn 1 should have >= 2 messages: {first_call_msgs}"
    assert len(second_call_msgs) >= 4, f"Turn 2 should have >= 4 messages: {second_call_msgs}"
    user_msgs_first = [m for m in first_call_msgs if m["role"] == "user"]
    user_msgs_second = [m for m in second_call_msgs if m["role"] == "user"]
    assert any("first message" in m["content"] for m in user_msgs_first)
    assert any("first message" in m["content"] for m in second_call_msgs)
    assert any("second message" in m["content"] for m in user_msgs_second)
    print("PASS: conversation history forwarded correctly")


if __name__ == "__main__":
    pytest.main([__file__, "-q"])
