import time
import logging
from typing import Optional
from .task import Task, TaskState

logger = logging.getLogger(__name__)


class ConversationManager:
    def __init__(self, max_history: int = 50, max_context_chars: int = 12000):
        self.max_history = max_history
        self.max_context_chars = max_context_chars
        self.history: list[dict] = []
        self.current_task: Optional[Task] = None
        self.context: dict = {
            "user_name": "",
            "preferences": {},
            "active_project": None,
            "capabilities": []
        }

    def add_user_message(self, content: str):
        self.history.append({
            "role": "user",
            "content": content,
            "timestamp": time.time()
        })
        self._trim_history()

    def add_assistant_message(self, content: str, tool_calls: list = None):
        msg = {
            "role": "assistant",
            "content": content,
            "timestamp": time.time()
        }
        if tool_calls:
            msg["tool_calls"] = tool_calls
        self.history.append(msg)
        self._trim_history()

    def add_system_message(self, content: str):
        self.history.append({
            "role": "system",
            "content": content,
            "timestamp": time.time()
        })
        self._trim_history()

    def get_messages_for_llm(
        self,
        max_messages: int = 20,
        max_chars: Optional[int] = None,
    ) -> list[dict]:
        """Return recent complete messages within a bounded context budget.

        Messages are never sliced mid-message. Newest context is retained first,
        then returned in chronological order. The caller owns the canonical
        system prompt, so persisted system messages are treated like history.
        """
        if max_messages <= 0:
            return []

        budget = max_chars or self.max_context_chars
        selected: list[dict] = []
        used_chars = 0

        for message in reversed(self.history[-max_messages:]):
            content = str(message.get("content", ""))
            message_chars = len(content)

            if selected and used_chars + message_chars > budget:
                break

            selected.append({
                "role": message["role"],
                "content": content,
            })
            used_chars += message_chars

        selected.reverse()
        return selected

    def _trim_history(self):
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]

    def start_task(self, user_request: str) -> Task:
        self.current_task = Task(user_request=user_request)
        return self.current_task

    def get_context_summary(self) -> str:
        summary_parts = []
        if self.context.get("user_name"):
            summary_parts.append(f"User: {self.context['user_name']}")
        if self.context.get("active_project"):
            summary_parts.append(f"Project: {self.context['active_project']}")
        if self.current_task and self.current_task.state != TaskState.COMPLETED:
            summary_parts.append(f"Active task: {self.current_task.goal}")
        return " | ".join(summary_parts) if summary_parts else "No active context"
