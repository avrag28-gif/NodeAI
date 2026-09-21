# MyAI - Changing Models

## Supported Backends

- llama.cpp (recommended)
- Ollama
- LM Studio
- vLLM

## Switch Model

### Option 1: Change GGUF file

1. Download new model to `models/`
2. Edit `config/config.yaml`:

```yaml
llm:
  model: "models/new-model.gguf"
```

3. Restart llama.cpp server with new model

### Option 2: Use Ollama

1. Install Ollama
2. Pull model: `ollama pull qwen2.5:3b`
3. Edit config:

```yaml
llm:
  host: "127.0.0.1"
  port: 11434
```

4. Update `core/llm/client.py` endpoint to `/api/chat`

### Option 3: Use OpenAI API

1. Set API key
2. Edit client to use OpenAI endpoint

## Recommended Models

| Model | Size | VRAM | Best For |
|-------|------|------|----------|
| Qwen2.5-3B Q4 | 2GB | 4GB | General + Coding |
| Phi-3.5-mini Q4 | 2.3GB | 4GB | Reasoning |
| Llama-3.2-3B Q4 | 2GB | 4GB | General |
| Gemma-2-2B Q4 | 1.7GB | 3GB | Lightweight |
