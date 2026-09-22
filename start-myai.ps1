Write-Host "=== MyAI Personal AI System ===" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Stop"
$llamaPort = 8080
$appPort = 5000
$llamaExe = ".\my-ai\llama.cpp\llama-server.exe"
$configPath = ".\my-ai\config\config.yaml"

# Step 1: Check MYAI_AUTH_TOKEN
Write-Host "[1/6] Checking auth token..." -ForegroundColor Yellow
$authToken = [System.Environment]::GetEnvironmentVariable("MYAI_AUTH_TOKEN", "User")
if (-not $authToken) {
    Write-Host "  MYAI_AUTH_TOKEN is not set." -ForegroundColor Red
    Write-Host "  Run: [System.Environment]::SetEnvironmentVariable('MYAI_AUTH_TOKEN', '<your-token>', 'User')" -ForegroundColor Yellow
    exit 1
}
Write-Host "  Auth token loaded (length: $($authToken.Length))" -ForegroundColor Green

# Step 2: Check llama-server binary
Write-Host "[2/6] Checking llama.cpp..." -ForegroundColor Yellow
if (-not (Test-Path $llamaExe)) {
    Write-Host "  llama-server not found at $llamaExe" -ForegroundColor Red
    Write-Host "  Run build first." -ForegroundColor Yellow
    exit 1
}
Write-Host "  llama-server found" -ForegroundColor Green

# Step 3: Start llama-server if not running
Write-Host "[3/6] Checking llama-server port..." -ForegroundColor Yellow
$llamaRunning = netstat -ano | Select-String ":$llamaPort\s.*LISTENING"
if ($llamaRunning) {
    Write-Host "  llama-server already running on port $llamaPort" -ForegroundColor Green
} else {
    Write-Host "  Starting llama-server..." -ForegroundColor Yellow
    Start-Process -FilePath $llamaExe -ArgumentList "--host 0.0.0.0 --port $llamaPort" -WindowStyle Hidden
    Start-Sleep -Seconds 3
    $llamaRunning = netstat -ano | Select-String ":$llamaPort\s.*LISTENING"
    if (-not $llamaRunning) {
        Write-Host "  Failed to start llama-server on port $llamaPort" -ForegroundColor Red
        exit 1
    }
    Write-Host "  llama-server started on port $llamaPort" -ForegroundColor Green
}

# Step 4: Check active model
Write-Host "[4/6] Checking active model..." -ForegroundColor Yellow
try {
    $modelInfo = Invoke-RestMethod -Uri "http://127.0.0.1:$llamaPort/v1/models" -TimeoutSec 5
    $activeModel = $modelInfo.data[0].id
    if ($activeModel) {
        $modelName = Split-Path $activeModel -Leaf
        Write-Host "  Model: $modelName" -ForegroundColor Cyan
    } else {
        Write-Host "  No model loaded" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  Cannot reach llama-server: $_" -ForegroundColor Yellow
}

# Step 5: Start FastAPI if not running
Write-Host "[5/6] Checking FastAPI port..." -ForegroundColor Yellow
$appRunning = netstat -ano | Select-String ":$appPort\s.*LISTENING"
if ($appRunning) {
    Write-Host "  FastAPI already running on port $appPort" -ForegroundColor Green
} else {
    Write-Host "  Starting FastAPI..." -ForegroundColor Yellow
    Start-Process -FilePath "python" -ArgumentList "my-ai\server\app.py" -WindowStyle Hidden
    Start-Sleep -Seconds 5
    $appRunning = netstat -ano | Select-String ":$appPort\s.*LISTENING"
    if (-not $appRunning) {
        Write-Host "  Failed to start FastAPI on port $appPort" -ForegroundColor Red
        exit 1
    }
    Write-Host "  FastAPI started on port $appPort" -ForegroundColor Green
}

# Step 6: Health check
Write-Host "[6/6] Health check..." -ForegroundColor Yellow
try {
    $status = Invoke-RestMethod -Uri "http://127.0.0.1:$appPort/" -TimeoutSec 5
    Write-Host "  Server: $($status.name) v$($status.version) - $($status.status)" -ForegroundColor Green
} catch {
    Write-Host "  FastAPI health check failed: $_" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Services ===" -ForegroundColor Cyan
Write-Host "llama-server: http://localhost:$llamaPort" -ForegroundColor White
Write-Host "FastAPI:      http://localhost:$appPort" -ForegroundColor White
Write-Host "Android:      Connect via settings" -ForegroundColor White
Write-Host ""
Write-Host "=== Ready! ===" -ForegroundColor Green
