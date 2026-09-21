import json
import logging
import time
import httpx
from typing import Optional

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self, host: str = "127.0.0.1", port: int = 8080, model: str = ""):
        self.base_url = f"http://{host}:{port}"
        self.model = model
        self.client = httpx.AsyncClient(timeout=120.0)
        # Diagnostic state: lets the agent distinguish model behavior from agent-layer behavior.
        self.last_trace = {
            "started_at": None,
            "messages": None,
            "response": None,
            "error": None,
            "model": model,
        }

    async def chat(self, messages: list[dict], max_tokens: int = 2048, temperature: float = 0.7) -> str:
        payload = {
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False
        }
        self.last_trace = {
            "started_at": time.time(),
            "messages": messages,
            "response": None,
            "error": None,
            "model": self.model,
        }

        try:
            response = await self.client.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            data = response.json()
            result = data["choices"][0]["message"]["content"]
            self.last_trace["response"] = result
            # Capture server-reported model metadata when available.
            self.last_trace["server_response_id"] = data.get("id")
            self.last_trace["server_model"] = data.get("model")
            return result
        except httpx.ConnectError:
            logger.error(f"Cannot connect to LLM at {self.base_url}")
            self.last_trace["error"] = "LLM server not running"
            return "Error: LLM server not running. Start llama.cpp first."
        except Exception as e:
            logger.error(f"LLM error: {e}")
            self.last_trace["error"] = str(e)
            return f"Error: {e}"

    async def complete(self, prompt: str, max_tokens: int = 2048) -> str:
        payload = {
            "prompt": prompt,
            "max_tokens": max_tokens,
            "stream": False
        }

        try:
            response = await self.client.post(
                f"{self.base_url}/v1/completions",
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["text"]
        except Exception as e:
            return f"Error: {e}"

    async def health_check(self) -> bool:
        try:
            response = await self.client.get(f"{self.base_url}/health")
            return response.status_code == 200
        except:
            return False

    async def get_model_info(self) -> dict:
        try:
            response = await self.client.get(f"{self.base_url}/v1/models")
            return response.json()
        except:
            return {"error": "Cannot reach LLM server"}

    async def close(self):
        await self.client.aclose()
