import json
import time
import logging
import asyncio
from typing import Optional
from .task import Task, TaskState
from .conversation import ConversationManager
from .planner import Planner, Executor, ErrorRecovery

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the NodeAI assistant.

Understand the current conversation before responding. Treat references such as
"that", "the previous one", "continue", "change it", and "the second item" as
references to the available conversation context.

For coding or project tasks:
- If the user asks to inspect, modify, fix, create, delete, refactor, or test
  project files, perform the requested action with the available tools rather
  than merely describing code.
- Inspect the current state before changing files.
- Make the smallest relevant change and preserve unrelated work.
- After a change, verify the result with a diff or file inspection and run
  relevant tests when available.
- Never claim that a file was changed, a command was run, or a test passed
  unless the action actually happened.
- If a requested change is already present, verify it instead of rewriting
  identical code.
- Use previous task context when the user says "continue" or refers to work
  already discussed.
- Do not invent facts, files, tool results, or memory that are not present.

For ordinary questions, answer directly and concisely.
"""


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
        self.temperature = self.config.get("temperature", 0.7)
        self.max_tokens = self.config.get("max_tokens", 2048)

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

                    follow_up = [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {
                            "role": "system",
                            "content": (
                                "A tool action has completed. Continue the current "
                                "task using the tool result in conversation history. "
                                "If the user's task is complete, give the final "
                                "answer. If more work is required, use the appropriate "
                                "tool rather than merely describing the next command."
                            ),
                        },
                    ]
                    follow_up.extend(
                        self.conversation.get_messages_for_llm(max_messages=20)
                    )

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
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # The conversation manager owns history. Keep the current task visible
        # without duplicating the current user message.
        task_context = (
            f"Current task: {task.goal}\n"
            f"Task state: {task.state.value if hasattr(task.state, 'value') else task.state}"
        )
        messages.append({"role": "system", "content": task_context})
        messages.extend(self.conversation.get_messages_for_llm(max_messages=20))
        return messages

    async def _call_llm(self, messages: list[dict]) -> str:
        try:
            return await self.llm.chat(
                messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return f"Error: LLM call failed: {e}"

    def _summarize_task(self, task: Task) -> str:
        completed = [s for s in task.steps if s.state == TaskState.COMPLETED]
        return "\n".join(
            f"  - {s.description}: {s.result[:100] if s.result else 'done'}"
            for s in completed
        ) or "No steps completed."
