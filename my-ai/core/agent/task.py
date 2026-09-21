import json
import time
import uuid
from enum import Enum
from typing import Any, Optional
from dataclasses import dataclass, field


class TaskState(Enum):
    PENDING = "pending"
    PLANNING = "planning"
    EXECUTING = "executing"
    OBSERVING = "observing"
    EVALUATING = "evaluating"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class TaskStep:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    description: str = ""
    tool_name: str = ""
    tool_args: dict = field(default_factory=dict)
    state: TaskState = TaskState.PENDING
    result: Optional[str] = None
    error: Optional[str] = None
    retries: int = 0
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None


@dataclass
class Task:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    user_request: str = ""
    goal: str = ""
    steps: list = field(default_factory=list)
    state: TaskState = TaskState.PENDING
    current_step_index: int = 0
    context: dict = field(default_factory=dict)
    result: Optional[str] = None
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None

    def add_step(self, description: str, tool_name: str = "", tool_args: dict = None):
        step = TaskStep(
            description=description,
            tool_name=tool_name,
            tool_args=tool_args or {}
        )
        self.steps.append(step)
        return step

    def get_current_step(self) -> Optional[TaskStep]:
        if 0 <= self.current_step_index < len(self.steps):
            return self.steps[self.current_step_index]
        return None

    def advance(self):
        if self.current_step_index < len(self.steps) - 1:
            self.current_step_index += 1
            self.steps[self.current_step_index].state = TaskState.EXECUTING
        else:
            self.state = TaskState.COMPLETED
            self.completed_at = time.time()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_request": self.user_request,
            "goal": self.goal,
            "state": self.state.value,
            "steps": [
                {
                    "id": s.id,
                    "description": s.description,
                    "tool_name": s.tool_name,
                    "state": s.state.value,
                    "result": s.result,
                    "error": s.error,
                    "retries": s.retries
                }
                for s in self.steps
            ],
            "current_step": self.current_step_index,
            "result": self.result,
            "created_at": self.created_at
        }
