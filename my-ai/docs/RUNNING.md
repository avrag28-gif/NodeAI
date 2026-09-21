# MyAI - How to Run

## Prerequisites

- Python 3.10+
- llama.cpp (for LLM inference)

## Quick Start

```powershell
# 1. Install Python dependencies
cd C:\NodeAi\my-ai
pip install -r requirements.txt

# 2. Download model and llama.cpp
python scripts\setup.py

# 3. Start llama.cpp server (in separate terminal)
python scripts\setup.py start

# 4. Start MyAI server
python -m server.app
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/status` | Server status |
| POST | `/api/chat` | Send chat message |
| POST | `/api/task` | Create autonomous task |
| GET | `/api/task/{id}` | Get task status |
| GET | `/api/tools` | List available tools |
| POST | `/api/tool/execute` | Execute a tool |
| GET | `/api/memory` | Memory stats |
| POST | `/api/memory/save` | Save to memory |
| GET | `/api/memory/search` | Search memory |
| GET | `/api/knowledge` | List knowledge |
| POST | `/api/knowledge/add` | Add knowledge |
| GET | `/api/knowledge/search` | Search knowledge |
| WS | `/ws` | WebSocket for real-time chat |

## Authentication

All endpoints require Bearer token:

```powershell
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:5000/api/status
```

## WebSocket Chat

```javascript
const ws = new WebSocket("ws://localhost:5000/ws");
ws.onmessage = (e) => console.log(JSON.parse(e.data));
ws.send(JSON.stringify({type: "chat", content: "Hello!"}));
```
