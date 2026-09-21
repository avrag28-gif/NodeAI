# MyAI - Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    WINDOWS PC (Server)                       │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  AGENT CORE (Python)                 │   │
│  │                                                     │   │
│  │  ┌──────────────┐  ┌──────────────┐               │   │
│  │  │ Conversation │  │   Planner    │               │   │
│  │  │   Manager    │  │              │               │   │
│  │  └──────────────┘  └──────────────┘               │   │
│  │                                                     │   │
│  │  ┌──────────────┐  ┌──────────────┐               │   │
│  │  │   Executor   │  │ Tool Router  │               │   │
│  │  │              │  │              │               │   │
│  │  └──────────────┘  └──────────────┘               │   │
│  │                                                     │   │
│  │  ┌──────────────┐  ┌──────────────┐               │   │
│  │  │ Observation  │  │    Error     │               │   │
│  │  │   System     │  │   Recovery   │               │   │
│  │  └──────────────┘  └──────────────┘               │   │
│  │                                                     │   │
│  │  ┌──────────────┐  ┌──────────────┐               │   │
│  │  │    Memory    │  │  Knowledge   │               │   │
│  │  │   System     │  │    Base      │               │   │
│  │  └──────────────┘  └──────────────┘               │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  TOOL SYSTEM                         │   │
│  │                                                     │   │
│  │  ┌─────────┐ ┌──────────┐ ┌──────────┐           │   │
│  │  │ File    │ │ Terminal │ │ Python   │           │   │
│  │  │ System  │ │          │ │ Executor │           │   │
│  │  └─────────┘ └──────────┘ └──────────┘           │   │
│  │                                                     │   │
│  │  ┌─────────┐ ┌──────────┐ ┌──────────┐           │   │
│  │  │ Browser │ │   Git    │ │ Internet │           │   │
│  │  │         │ │          │ │ Search   │           │   │
│  │  └─────────┘ └──────────┘ └──────────┘           │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  LLM BACKEND                         │   │
│  │                                                     │   │
│  │  llama.cpp server (Qwen2.5-3B Q4_K_M)             │   │
│  │  http://localhost:8080                              │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  API SERVER (FastAPI)                │   │
│  │                                                     │   │
│  │  POST /api/chat                                     │   │
│  │  POST /api/task                                     │   │
│  │  GET  /api/task/{id}                                │   │
│  │  POST /api/tool/execute                             │   │
│  │  GET  /api/capabilities                             │   │
│  │  WS   /ws                                           │   │
│  │                                                     │   │
│  │  Authentication: Bearer token                       │   │
│  │  Port: 5000                                         │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │   LAN / Internet  │
                    └─────────┬─────────┘
                              │
┌─────────────────────────────┴─────────────────────────────┐
│                    ANDROID CLIENT                          │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │  Chat UI    │  │ API Client  │  │  Device     │       │
│  │  (Compose)  │  │ (Retrofit)  │  │  Tools      │       │
│  └─────────────┘  └─────────────┘  └─────────────┘       │
│                                                             │
│  Tools: Flash, Camera, Mic, Files, Battery, etc.          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Tech Stack

| Component | Technology | Reason |
|-----------|-----------|--------|
| Agent Core | Python 3.14 | Fast development, rich ecosystem |
| LLM Backend | llama.cpp | CPU inference, GGUF support |
| API Server | FastAPI | Async, WebSocket, auto-docs |
| Memory | SQLite + numpy | Lightweight, no external DB |
| Knowledge | SQLite + TF-IDF | Simple RAG without heavy deps |
| Android | Kotlin + Compose | Modern, official |
| Communication | REST + WebSocket | Real-time + reliable |

## Model Strategy

```
Qwen2.5-3B-Instruct Q4_K_M
├── Size: ~2 GB
├── Context: 32K tokens
├── Reasoning: Good for agent tasks
├── Tool calling: Supported
├── Language: Multilingual (EN/ID)
└── Runtime: llama.cpp server
```

## Autonomous Loop

```
1. RECEIVE task from user
2. UNDERSTAND intent + context
3. PLAN steps (LLM reasoning)
4. SELECT appropriate tool
5. EXECUTE tool
6. OBSERVE result
7. EVALUATE success
8. IF failed: ERROR RECOVERY → retry/modify
9. IF done: VERIFY result
10. RETURN final response
```

Limits:
- Max iterations: 20
- Timeout: 300s per step
- Max retries: 3
- Context compression: summarize every 10 messages
