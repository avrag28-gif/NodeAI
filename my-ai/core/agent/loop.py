import json
import time
import logging
import asyncio
import re
from typing import Optional
from .task import Task, TaskState
from .conversation import ConversationManager
from .planner import Planner, Executor, ErrorRecovery

logger = logging.getLogger(__name__)

REFUSAL_PATTERNS = [
    "i cannot", "i can't", "i am unable", "i'm unable",
    "i am not able", "i'm not able", "i apologize",
    "i'm sorry", "i am sorry", "not appropriate",
    "cannot perform", "unable to assist", "not appropriate",
    "does not comply", "cannot help with",
]


def is_refusal(text: str) -> bool:
    text_lower = text.lower().strip()
    for pattern in REFUSAL_PATTERNS:
        if pattern in text_lower:
            return True
    return False


class AgentLoop:
    def __init__(self, llm_client, tool_registry, config: dict = None):
        self.llm = llm_client
        self.tools = tool_registry
        self.conversation = ConversationManager()
        self.planner = Planner()
        self.executor = Executor(tool_registry)
        self.recovery = ErrorRecovery()
        self.config = config or {}
        self.max_iterations = self.config.get("max_iterations", 20)
        self.step_timeout = self.config.get("step_timeout", 300)

    async def process_message(self, user_message: str) -> str:
        self.conversation.add_user_message(user_message)

        task = self.conversation.start_task(user_message)
        task.goal = user_message
        task.state = TaskState.PLANNING

        logger.info(f"New task: {task.id} - {user_message[:100]}")

        for iteration in range(self.max_iterations):
            if task.state in (TaskState.COMPLETED, TaskState.FAILED):
                break

            messages = self._build_messages(task)
            response = await self._call_llm(messages)

            parsed = self.planner.parse_llm_response(response)

            if parsed["type"] == "text":
                task.result = parsed["data"]
                task.state = TaskState.COMPLETED
                task.completed_at = time.time()
                self.conversation.add_assistant_message(parsed["data"])
                return parsed["data"]

            if parsed["type"] == "tool_call":
                action = parsed["data"]
                tool_name = action.get("action", action.get("tool", ""))

                # The model's output is not an application policy decision.
                # Tool execution continues through the normal tool/permission layers.
                step = task.add_step(
                    description=action.get("thought", tool_name),
                    tool_name=tool_name,
                    tool_args=action.get("args", action.get("parameters", {}))
                )
                step.state = TaskState.EXECUTING
                task.state = TaskState.EXECUTING

                result = await self._execute_with_retry(task, action)

                if result.startswith("Error:"):
                    task.state = TaskState.FAILED
                    task.error = result
                    self.conversation.add_assistant_message(f"Task failed: {result}")
                    return f"I encountered an error: {result}"
                else:
                    task.advance()
                    self.conversation.add_assistant_message(
                        f"Tool executed: {tool_name}\nResult: {result[:1000]}",
                        tool_calls=[action]
                    )

                    follow_up = [{"role": "system", "content": "You are a helpful assistant. Answer directly."}]
                    follow_up.extend(self.conversation.get_messages_for_llm(max_messages=5))
                    follow_up.append({"role": "user", "content": "Give your response now."})

                    follow_response = await self._call_llm(follow_up)

                    if follow_response and not follow_response.startswith("Error"):
                        task.result = follow_response
                        task.state = TaskState.COMPLETED
                        task.completed_at = time.time()
                        self.conversation.add_assistant_message(follow_response)
                        return follow_response

        if task.state != TaskState.COMPLETED:
            task.state = TaskState.FAILED
            return "Max iterations reached."

        return task.result or "Task completed."

    async def _force_execute_via_python(self, task: Task, user_message: str) -> str:
        """Legacy compatibility path retained for diagnosis.

        This path does not bypass tool permissions. It executes only the existing
        Python tool behavior and records the result as a normal task step.
        """
        safe_msg = user_message.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")
        python_code = f'''
request = "{safe_msg}"
print(f"Executing: {{request}}")
print()
print(request)
'''
        step = task.add_step(
            description="Legacy compatibility execution via Python",
            tool_name="python",
            tool_args={"code": python_code}
        )
        step.state = TaskState.EXECUTING

        tool = self.tools.get_tool("python")
        if not tool:
            return "Error: Python tool is not registered."

        try:
            result = await tool.execute(code=python_code)
        except Exception as e:
            logger.warning(f"Legacy Python path failed: {e}")
            return f"Error: Python execution failed: {e}"

        task.advance()
        task.result = str(result)
        task.state = TaskState.COMPLETED
        task.completed_at = time.time()
        self.conversation.add_assistant_message(str(result))
        return str(result)

    async def _execute_with_retry(self, task: Task, action: dict) -> str:
        for attempt in range(self.recovery.max_retries):
            result = await self.executor.execute_step(task, action)
            if not result.startswith("Error:"):
                return result
            step = task.get_current_step()
            if step:
                step.state = TaskState.RETRYING
            if not self.recovery.should_retry(task):
                break
            await asyncio.sleep(1)
        return result

    def _build_messages(self, task: Task) -> list[dict]:
        # Keep this layer minimal. The agent must not manufacture a refusal or silently
        # replace model output; diagnosis needs the raw model response.
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Answer the user directly."},
            {"role": "user", "content": task.user_request}
        ]
        return messages

    async def _call_llm(self, messages: list[dict]) -> str:
        try:
            return await self.llm.chat(messages)
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return f"Error: LLM call failed: {e}"

    def _summarize_task(self, task: Task) -> str:
        completed = [s for s in task.steps if s.state == TaskState.COMPLETED]
        return "\n".join(f"  - {s.description}: {s.result[:100] if s.result else 'done'}" for s in completed) or "No steps completed."
