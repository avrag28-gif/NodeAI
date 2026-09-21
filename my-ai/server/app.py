import sys
import yaml
import logging
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.llm.client import LLMClient
from core.agent.loop import AgentLoop
from core.memory.memory import MemorySystem
from core.knowledge.knowledge import KnowledgeBase
from tools.registry import ToolRegistry
from tools.filesystem.tools import ReadFileTool, WriteFileTool, ListDirTool, DeleteFileTool, SearchFilesTool, MakeDirTool, CopyFileTool
from tools.terminal.tools import TerminalTool
from tools.python.tools import PythonTool
from tools.internet.tools import WebSearchTool, FetchWebTool
from server.auth.manager import AuthManager
from server.api.app import create_app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s"
)
logger = logging.getLogger("myai")


def load_config(config_path: str = "config/config.yaml") -> dict:
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def setup_tools(tool_registry: ToolRegistry, permissions: dict, workspace: str):
    tool_classes = [
        ReadFileTool, WriteFileTool, ListDirTool, DeleteFileTool,
        SearchFilesTool, MakeDirTool, CopyFileTool,
        TerminalTool, PythonTool,
        WebSearchTool, FetchWebTool
    ]

    for cls in tool_classes:
        tool = cls(workspace=workspace, permissions=permissions)
        tool_registry.register(tool)

    logger.info(f"Registered {len(tool_registry.list_tools())} tools: {tool_registry.list_tools()}")


async def main():
    logger.info("Starting MyAI Server...")

    config = load_config()

    llm_config = config.get("llm", {})
    llm_client = LLMClient(
        host=llm_config.get("host", "127.0.0.1"),
        port=llm_config.get("port", 8080),
        model=llm_config.get("model", "")
    )

    llm_ok = await llm_client.health_check()
    if llm_ok:
        logger.info("LLM server connected")
    else:
        logger.warning("LLM server not available - start llama.cpp")

    memory = MemorySystem()
    await memory.initialize()

    knowledge = KnowledgeBase()
    await knowledge.initialize()

    tool_registry = ToolRegistry()
    permissions = config.get("permissions", {})
    workspace = config.get("server", {}).get("workspace", "workspace")
    setup_tools(tool_registry, permissions, workspace)

    agent_config = config.get("agent", {})
    agent_loop = AgentLoop(llm_client, tool_registry, agent_config)

    server_config = config.get("server", {})
    auth = AuthManager(auth_token=server_config.get("auth_token", ""))

    app = create_app(agent_loop, auth, tool_registry, knowledge, memory, config)

    import uvicorn
    uvicorn_config = uvicorn.Config(
        app,
        host=server_config.get("host", "0.0.0.0"),
        port=server_config.get("port", 5000),
        log_level="info"
    )
    server = uvicorn.Server(uvicorn_config)

    logger.info(f"MyAI Server starting on http://{server_config.get('host', '0.0.0.0')}:{server_config.get('port', 5000)}")
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
