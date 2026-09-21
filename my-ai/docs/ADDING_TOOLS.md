# MyAI - Adding Custom Tools

## Create a New Tool

1. Create a Python file in `tools/`:

```python
from tools.base import BaseTool

class MyCustomTool(BaseTool):
    name = "my_tool"
    description = "Description of what the tool does"
    parameters = {
        "param1": {"type": "string", "description": "First parameter"},
        "param2": {"type": "integer", "description": "Second parameter"}
    }
    permission_required = "read"

    async def execute(self, param1: str = "", param2: int = 0, **kwargs) -> str:
        # Your tool logic here
        result = f"Processed: {param1} with value {param2}"
        return result
```

2. Register in `server/app.py`:

```python
from tools.my_tool import MyCustomTool

# In setup_tools():
tool_registry.register(MyCustomTool(workspace=workspace, permissions=permissions))
```

3. Restart the server.

## Tool Requirements

- Must extend `BaseTool`
- Must have `name`, `description`, `parameters`
- Must implement `execute(**kwargs) -> str`
- Return string result (success or error message)

## Permission System

Configure in `config/config.yaml`:

```yaml
permissions:
  my_tool:
    default: "ASK"  # ALLOW, ASK, or DENY
```
