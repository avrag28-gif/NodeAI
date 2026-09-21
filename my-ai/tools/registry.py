import logging
from typing import Optional

logger = logging.getLogger(__name__)


class ToolRegistry:
    def __init__(self, permissions: dict = None):
        self.tools = {}
        self.permissions = permissions or {}

    def register(self, tool):
        self.tools[tool.name] = tool
        logger.debug(f"Registered tool: {tool.name}")

    def get_tool(self, name: str):
        return self.tools.get(name)

    def list_tools(self) -> list[str]:
        return list(self.tools.keys())

    def get_schemas(self) -> list[dict]:
        return [tool.to_schema() for tool in self.tools.values()]

    def get_tools_for_prompt(self) -> str:
        lines = []
        for name, tool in self.tools.items():
            params = ", ".join(tool.parameters.keys())
            lines.append(f"- {name}({params}): {tool.description}")
        return "\n".join(lines)
