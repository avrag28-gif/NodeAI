import asyncio
import subprocess
import os
from ..base import BaseTool


class TerminalTool(BaseTool):
    name = "terminal"
    description = "Execute a terminal/command prompt command"
    parameters = {
        "command": {"type": "string", "description": "Command to execute"},
        "cwd": {"type": "string", "description": "Working directory"},
        "timeout": {"type": "integer", "description": "Timeout in seconds"}
    }
    permission_required = "execute"

    async def execute(self, command: str = "", cwd: str = None, timeout: int = 60, **kwargs) -> str:
        if not command:
            return "Error: command is required"

        blocked = ["format", "del /s", "rm -rf /", "shutdown", "restart"]
        cmd_lower = command.lower()
        for b in blocked:
            if b in cmd_lower:
                return f"Error: Blocked dangerous command: {command}"

        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd or os.getcwd()
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)

            output = stdout.decode("utf-8", errors="replace")
            error = stderr.decode("utf-8", errors="replace")

            result = ""
            if output:
                result += output
            if error:
                result += f"\nSTDERR:\n{error}" if result else error

            if not result.strip():
                result = f"Command executed (exit code: {proc.returncode})"

            if len(result) > 10000:
                result = result[:10000] + "\n... (truncated)"

            return result
        except asyncio.TimeoutError:
            return f"Error: Command timed out after {timeout}s"
        except Exception as e:
            return f"Error executing command: {e}"
