import asyncio
import tempfile
import os
from ..base import BaseTool


class PythonTool(BaseTool):
    name = "python"
    description = "Execute Python code"
    parameters = {
        "code": {"type": "string", "description": "Python code to execute"},
        "timeout": {"type": "integer", "description": "Timeout in seconds"}
    }
    permission_required = "execute"

    async def execute(self, code: str = "", timeout: int = 30, **kwargs) -> str:
        if not code:
            return "Error: code is required"

        dangerous = ["os.system", "subprocess", "shutil.rmtree", "__import__('os')"]
        for d in dangerous:
            if d in code:
                return f"Error: Blocked dangerous Python code pattern: {d}"

        tmp_file = tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        )
        try:
            tmp_file.write(code)
            tmp_file.close()

            proc = await asyncio.create_subprocess_exec(
                "python", tmp_file.name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
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
                result = f"Code executed (exit code: {proc.returncode})"

            if len(result) > 10000:
                result = result[:10000] + "\n... (truncated)"

            return result
        except asyncio.TimeoutError:
            return f"Error: Code timed out after {timeout}s"
        except Exception as e:
            return f"Error executing Python: {e}"
        finally:
            try:
                os.unlink(tmp_file.name)
            except:
                pass
