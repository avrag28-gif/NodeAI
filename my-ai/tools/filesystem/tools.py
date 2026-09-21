import os
import glob
import shutil
from pathlib import Path
from ..base import BaseTool


class ReadFileTool(BaseTool):
    name = "read_file"
    description = "Read the contents of a file"
    parameters = {
        "path": {"type": "string", "description": "File path to read"}
    }
    permission_required = "read"

    async def execute(self, path: str = "", **kwargs) -> str:
        if not path:
            return "Error: path is required"
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            if len(content) > 50000:
                content = content[:50000] + "\n... (truncated)"
            return content
        except Exception as e:
            return f"Error reading file: {e}"


class WriteFileTool(BaseTool):
    name = "write_file"
    description = "Write content to a file (creates or overwrites)"
    parameters = {
        "path": {"type": "string", "description": "File path"},
        "content": {"type": "string", "description": "Content to write"}
    }
    permission_required = "write"

    async def execute(self, path: str = "", content: str = "", **kwargs) -> str:
        if not path:
            return "Error: path is required"
        try:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Written {len(content)} bytes to {path}"
        except Exception as e:
            return f"Error writing file: {e}"


class ListDirTool(BaseTool):
    name = "list_dir"
    description = "List files and directories in a path"
    parameters = {
        "path": {"type": "string", "description": "Directory path"}
    }
    permission_required = "read"

    async def execute(self, path: str = ".", **kwargs) -> str:
        try:
            items = []
            for item in sorted(Path(path).iterdir()):
                prefix = "[DIR] " if item.is_dir() else "[FILE]"
                size = f" ({item.stat().st_size} bytes)" if item.is_file() else ""
                items.append(f"{prefix} {item.name}{size}")
            return "\n".join(items) if items else "Empty directory"
        except Exception as e:
            return f"Error listing directory: {e}"


class DeleteFileTool(BaseTool):
    name = "delete_file"
    description = "Delete a file or empty directory"
    parameters = {
        "path": {"type": "string", "description": "Path to delete"}
    }
    permission_required = "delete"

    async def execute(self, path: str = "", **kwargs) -> str:
        if not path:
            return "Error: path is required"
        try:
            p = Path(path)
            if p.is_file():
                p.unlink()
                return f"Deleted file: {path}"
            elif p.is_dir():
                shutil.rmtree(p)
                return f"Deleted directory: {path}"
            else:
                return f"Path not found: {path}"
        except Exception as e:
            return f"Error deleting: {e}"


class SearchFilesTool(BaseTool):
    name = "search_files"
    description = "Search for files matching a pattern"
    parameters = {
        "pattern": {"type": "string", "description": "Glob pattern"},
        "path": {"type": "string", "description": "Search directory"}
    }
    permission_required = "read"

    async def execute(self, pattern: str = "*", path: str = ".", **kwargs) -> str:
        try:
            search_path = os.path.join(path, pattern)
            matches = glob.glob(search_path, recursive=True)
            if not matches:
                return f"No files found matching: {pattern}"
            return "\n".join(matches[:100])
        except Exception as e:
            return f"Error searching: {e}"


class MakeDirTool(BaseTool):
    name = "make_dir"
    description = "Create a directory"
    parameters = {
        "path": {"type": "string", "description": "Directory path to create"}
    }
    permission_required = "write"

    async def execute(self, path: str = "", **kwargs) -> str:
        if not path:
            return "Error: path is required"
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            return f"Created directory: {path}"
        except Exception as e:
            return f"Error creating directory: {e}"


class CopyFileTool(BaseTool):
    name = "copy_file"
    description = "Copy a file or directory"
    parameters = {
        "source": {"type": "string", "description": "Source path"},
        "destination": {"type": "string", "description": "Destination path"}
    }
    permission_required = "write"

    async def execute(self, source: str = "", destination: str = "", **kwargs) -> str:
        if not source or not destination:
            return "Error: source and destination required"
        try:
            src = Path(source)
            if src.is_file():
                shutil.copy2(source, destination)
            elif src.is_dir():
                shutil.copytree(source, destination)
            return f"Copied {source} to {destination}"
        except Exception as e:
            return f"Error copying: {e}"
