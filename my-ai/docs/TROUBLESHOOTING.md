# MyAI - Troubleshooting

## LLM Server Issues

### "Cannot connect to LLM"
1. Check if llama.cpp is running: `curl http://localhost:8080/health`
2. Start server: `python scripts\setup.py start`
3. Check model path in config

### "Model not found"
1. Download model: `python scripts\setup.py model`
2. Verify path in `config/config.yaml`

## Server Issues

### "Port already in use"
Change port in `config/config.yaml`:
```yaml
server:
  port: 5001
```

### "Module not found"
Install dependencies:
```powershell
pip install -r requirements.txt
```

## Memory/Database Issues

### "Database locked"
1. Stop all MyAI processes
2. Delete `data/memory/memory.db`
3. Restart server

## Android Connection Issues

### "Connection refused"
1. Ensure PC firewall allows port 5000
2. Check IP address in Android app settings
3. Verify both devices on same network

### "Authentication failed"
1. Check auth_token in config
2. Enter same token in Android app

## Performance Issues

### Slow responses
1. Reduce context length in config
2. Use smaller model
3. Close other applications

### High memory usage
1. Restart server periodically
2. Limit conversation history
