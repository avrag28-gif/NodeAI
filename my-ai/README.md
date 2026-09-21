# MyAI - Personal AI Agent Platform

## Quick Start

```powershell
# 1. Install dependencies
pip install -r requirements.txt

# 2. Download model (Qwen2.5-3B Q4_K_M)
python scripts\download_model.py

# 3. Start llama.cpp server
python scripts\start_llm.py

# 4. Start MyAI server
python -m server.app

# 5. Open browser
# http://localhost:5000
```

## Architecture

- **Agent Core**: Python-based autonomous agent loop
- **LLM Backend**: llama.cpp with Qwen2.5-3B Q4_K_M
- **API Server**: FastAPI with WebSocket support
- **Memory**: SQLite-based short/long-term memory
- **Knowledge**: SQLite + TF-IDF for RAG
- **Tools**: Modular plugin system
- **Android**: Kotlin client app

## Documentation

- [Environment Report](docs/ENVIRONMENT.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Tool System](docs/TOOLS.md)
- [Configuration](docs/CONFIGURATION.md)
