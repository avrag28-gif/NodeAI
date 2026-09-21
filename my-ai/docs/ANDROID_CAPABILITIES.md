# MyAI - Adding Android Capabilities

## How It Works

Android device runs MyAI Android app that:
1. Connects to PC server via WebSocket
2. Registers available device capabilities
3. Receives tool execution requests
4. Executes on device
5. Returns results

## Adding New Android Tool

### Step 1: Define capability in Android app

In `tools/AndroidTool.kt`:

```kotlin
class MyCustomTool : DeviceTool {
    override val name = "my_custom"
    override val description = "My custom Android tool"
    
    override suspend fun execute(action: String, params: Map<String, String>): ToolResult {
        return when (action) {
            "do_something" -> {
                // Android implementation
                ToolResult(true, "Result here")
            }
            else -> ToolResult(false, "Unknown action")
        }
    }
}
```

### Step 2: Register in Android app

```kotlin
toolRegistry.register(MyCustomTool())
```

### Step 3: Call from PC agent

The agent can now call:

```json
{"action": "android_tool", "args": {"tool": "my_custom", "action": "do_something"}}
```

## Available Android APIs

- Camera: photo capture
- Microphone: audio recording
- Flashlight: toggle torch
- Files: read/write storage
- Notifications: show alerts
- Battery: status info
- Clipboard: copy/paste
- Network: WiFi info
- Apps: launch applications
