import argparse
import asyncio
import json
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[2]
MY_AI = ROOT / "my-ai"
sys.path.insert(0, str(MY_AI))

from core.llm.client import LLMClient
from core.agent.loop import AgentLoop
from tools.registry import ToolRegistry


LLM_URL = "http://127.0.0.1:8080"


async def raw_llama(prompt: str, system: str, temperature: float):
    payload = {
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 512,
        "temperature": temperature,
        "stream": False,
    }
    async with httpx.AsyncClient(timeout=120) as client:
        props = None
        try:
            props = (await client.get(f"{LLM_URL}/props")).json()
        except Exception as exc:
            props = {"error": str(exc)}
        response = await client.post(f"{LLM_URL}/v1/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()
    return data, props


async def main():
    parser = argparse.ArgumentParser(
        description="Trace whether a refusal is produced by llama.cpp/model or MyAI layers."
    )
    parser.add_argument("prompt", help="Exact prompt to test.")
    parser.add_argument("--temperature", type=float, default=0.0)
    args = parser.parse_args()

    system = "You are a helpful assistant. Answer the user directly."

    print("=== REFUSAL SOURCE TRACE ===")
    print(f"Prompt: {args.prompt!r}")
    print(f"Temperature: {args.temperature}")
    print()

    # A: raw llama.cpp. This is the closest available test of model + server
    # chat-template behavior.
    raw_data, props = await raw_llama(args.prompt, system, args.temperature)
    raw_message = raw_data["choices"][0]["message"]["content"]
    print("=== A: RAW LLAMA.CPP ===")
    print(raw_message)
    print()
    print("Server model:", raw_data.get("model"))
    print("Response id:", raw_data.get("id"))
    print("Chat template from /props:")
    print((props or {}).get("chat_template", "<not reported>"))
    print("Model path from /props:", (props or {}).get("model_path"))
    print()

    # B: MyAI LLMClient. Same message structure, same temperature.
    client = LLMClient(host="127.0.0.1", port=8080)
    b = await client.chat(
        [
            {"role": "system", "content": system},
            {"role": "user", "content": args.prompt},
        ],
        max_tokens=512,
        temperature=args.temperature,
    )
    print("=== B: MYAI LLMCLIENT ===")
    print(b)
    print()
    print(json.dumps(client.last_trace, indent=2, ensure_ascii=False, default=str))
    print()

    # C: MyAI AgentLoop. Tool registry is intentionally empty so this test
    # isolates the chat/planner layer and does not execute any external action.
    loop = AgentLoop(client, ToolRegistry(), {"max_iterations": 1})
    c = await loop.process_message(args.prompt)
    print("=== C: MYAI AGENT LOOP ===")
    print(c)
    print()
    print("Agent LLM trace:")
    print(json.dumps(client.last_trace, indent=2, ensure_ascii=False, default=str))

    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
