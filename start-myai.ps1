Write-Host "=== MyAI Personal AI System ===" -ForegroundColor Cyan
Write-Host ""

# Check Docker
Write-Host "[1/4] Checking Docker..." -ForegroundColor Yellow
if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Host "  Docker found!" -ForegroundColor Green
} else {
    Write-Host "  Docker not found. Install from https://docker.com" -ForegroundColor Red
    exit 1
}

# Check if Agent Zero is running
Write-Host "[2/4] Checking Agent Zero..." -ForegroundColor Yellow
$containers = docker ps -a --filter "name=agent-zero" --format "{{.Names}}"
if ($containers -contains "agent-zero") {
    Write-Host "  Agent Zero container exists" -ForegroundColor Green
    $running = docker ps --filter "name=agent-zero" --format "{{.Names}}"
    if ($running -contains "agent-zero") {
        Write-Host "  Agent Zero is running!" -ForegroundColor Green
    } else {
        Write-Host "  Starting Agent Zero..." -ForegroundColor Yellow
        docker start agent-zero
        Write-Host "  Agent Zero started!" -ForegroundColor Green
    }
} else {
    Write-Host "  Creating Agent Zero container..." -ForegroundColor Yellow
    docker run -d -p 50080:80 -v a0_usr:/a0/usr --name agent-zero agent0ai/agent-zero
    Write-Host "  Agent Zero created and started!" -ForegroundColor Green
}

# Check llama.cpp
Write-Host "[3/4] Checking llama.cpp..." -ForegroundColor Yellow
if (Test-Path ".\llama.cpp\build\bin\llama-server.exe") {
    Write-Host "  llama.cpp found!" -ForegroundColor Green
} else {
    Write-Host "  llama.cpp not built yet. Run build-llama.ps1" -ForegroundColor Yellow
}

# Check models
Write-Host "[4/4] Checking models..." -ForegroundColor Yellow
$modelCount = (Get-ChildItem -Path ".\models\*.gguf" -ErrorAction SilentlyContinue).Count
Write-Host "  Found $modelCount model(s)" -ForegroundColor Green

Write-Host ""
Write-Host "=== Services ===" -ForegroundColor Cyan
Write-Host "Agent Zero: http://localhost:50080" -ForegroundColor White
Write-Host "llama.cpp:  http://localhost:8080" -ForegroundColor White
Write-Host "Android:    Connect via settings" -ForegroundColor White
Write-Host ""
Write-Host "=== Ready! ===" -ForegroundColor Green
