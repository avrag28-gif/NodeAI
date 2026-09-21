import logging
from abc import ABC, abstractmethod
from typing import Any, Optional

logger = logging.getLogger(__name__)


class BaseTool(ABC):
    name: str = "base"
    description: str = "Base tool"
    parameters: dict = {}
    permission_required: str = "read"

    def __init__(self, workspace: str = "workspace", permissions: dict = None):
        self.workspace = workspace
        self.permissions = permissions or {}

    @abstractmethod
    async def execute(self, **kwargs) -> str:
        pass

    def check_permission(self, action: str = "read") -> bool:
        tool_perms = self.permissions.get(self.name, {})
        level = tool_perms.get(action, tool_perms.get("default", "ASK"))
        return level == "ALLOW"

    def to_schema(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }
