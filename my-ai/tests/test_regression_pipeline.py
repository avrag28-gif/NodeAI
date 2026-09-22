import sys
import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

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


async def test_process_message_returns_llm_text():
    llm = make_mock_llm("This is the answer")
    loop = AgentLoop(llm, make_mock_tools())
    result = await loop.process_message("What is 2+2?")
    assert result == "This is the answer", f"Expected LLM text, got: {result}"
    print("PASS: process_message returns LLM text directly")


async def test_temperature_passed_to_llm():
    llm = make_mock_llm("OK")
    loop = AgentLoop(llm, make_mock_tools(), {"temperature": 0.3})
    await loop.process_message("test")
    call_kwargs = llm.chat.call_args
    assert call_kwargs.kwargs.get("temperature") == 0.3 or call_kwargs[1].get("temperature") == 0.3, \
        f"Temperature not passed: {call_kwargs}"
    print("PASS: temperature passed to LLM")


async def test_max_tokens_passed_to_llm():
    llm = make_mock_llm("OK")
    loop = AgentLoop(llm, make_mock_tools(), {"max_tokens": 1024})
    await loop.process_message("test")
    call_kwargs = llm.chat.call_args
    assert call_kwargs.kwargs.get("max_tokens") == 1024 or call_kwargs[1].get("max_tokens") == 1024, \
        f"max_tokens not passed: {call_kwargs}"
    print("PASS: max_tokens passed to LLM")


async def test_system_prompt_consistent():
    llm = make_mock_llm("OK")
    loop = AgentLoop(llm, make_mock_tools())
    await loop.process_message("test")
    call_args = llm.chat.call_args
    messages = call_args[0][0]
    assert messages[0]["role"] == "system", f"No system message: {messages}"
    assert "helpful assistant" in messages[0]["content"], \
        f"System prompt changed: {messages[0]['content']}"
    print("PASS: system prompt consistent")


async def test_no_refusal_detection():
    llm = make_mock_llm("I cannot do that")
    loop = AgentLoop(llm, make_mock_tools())
    result = await loop.process_message("test request")
    assert result == "I cannot do that", \
        f"Refusal detection intercepted: got {result}"
    print("PASS: no refusal detection in pipeline")


async def test_user_message_in_request():
    llm = make_mock_llm("OK")
    loop = AgentLoop(llm, make_mock_tools())
    await loop.process_message("What is Python?")
    call_args = llm.chat.call_args
    messages = call_args[0][0]
    user_msgs = [m for m in messages if m["role"] == "user"]
    assert len(user_msgs) >= 1, f"No user message: {messages}"
    assert user_msgs[0]["content"] == "What is Python?", \
        f"User message mismatch: {user_msgs[0]['content']}"
    print("PASS: user message included in request")


async def main():
    tests = [
        test_process_message_returns_llm_text,
        test_temperature_passed_to_llm,
        test_max_tokens_passed_to_llm,
        test_system_prompt_consistent,
        test_no_refusal_detection,
        test_user_message_in_request,
    ]

    passed = 0
    failed = 0
    for test in tests:
        try:
            await test()
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


if __name__ == "__main__":
    asyncio.run(main())
