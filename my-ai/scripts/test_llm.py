import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.llm.client import LLMClient


async def check_connection():
    client = LLMClient()
    ok = await client.health_check()
    print(f"LLM Connection: {'OK' if ok else 'FAILED'}")
    if ok:
        info = await client.get_model_info()
        print(f"Model Info: {info}")
    await client.close()


if __name__ == "__main__":
    asyncio.run(check_connection())
