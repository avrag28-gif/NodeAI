Write-Host "=== MyAI Personal AI System ===" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$llamaPort = 8080
$appPort = 5000
$llamaExe = Join-Path $root "my-ai\llama.cpp\llama-server.exe"
$appScript = Join-Path $root "my-ai\server\app.py"
$appWorkingDir = Join-Path $root "my-ai"

# Step 1: Check auth token
Write-Host "[1/6] Checking auth token..." -ForegroundColor Yellow
$authToken = [System.Environment]::GetEnvironmentVariable("MYAI_AUTH_TOKEN", "User")

if ([string]::IsNullOrWhiteSpace($authToken)) {
    Write-Host "  MYAI_AUTH_TOKEN is not set." -ForegroundColor Red
    exit 1
}

$env:MYAI_AUTH_TOKEN = $authToken
Write-Host "  Auth token loaded (length: $($authToken.Length))" -ForegroundColor Green

# Step 2: Check llama-server binary
Write-Host "[2/6] Checking llama.cpp..." -ForegroundColor Yellow
if (-not (Test-Path $llamaExe)) {
    Write-Host "  llama-server not found at $llamaExe" -ForegroundColor Red
    exit 1
}
Write-Host "  llama-server found" -ForegroundColor Green

# Step 3: Start/check llama-server
Write-Host "[3/6] Checking llama-server..." -ForegroundColor Yellow
$llamaRunning = netstat -ano | Select-String ":$llamaPort\s.*LISTENING"

if ($llamaRunning) {
    Write-Host "  llama-server already running on port $llamaPort" -ForegroundColor Green
} else {
    Write-Host "  Starting llama-server..." -ForegroundColor Yellow

    $targetModel = Get-Item (Join-Path $root "my-ai\models\Qwen2.5-Coder-7B-Instruct-Uncensored-Q4_K_M.gguf") -ErrorAction SilentlyContinue
    if (-not $targetModel) { $targetModel = Get-ChildItem (Join-Path $root "my-ai\models\*.gguf") -ErrorAction SilentlyContinue | Where-Object { $_.Length -gt 1GB } | Select-Object -First 1 }
    $defaultModel = if ($targetModel) { $targetModel.FullName } else { "" }

    $args = "--host 0.0.0.0 --port $llamaPort --ctx-size 4096"
    if ($defaultModel) {
        $args = "--host 0.0.0.0 --port $llamaPort --ctx-size 4096 --model `"$defaultModel`""
        Write-Host "  Loading model: $($targetModel.Name)" -ForegroundColor Cyan
    }

    Start-Process `
        -FilePath $llamaExe `
        -WorkingDirectory (Split-Path $llamaExe) `
        -ArgumentList $args `
        -WindowStyle Hidden

    Start-Sleep -Seconds 10

    $llamaRunning = netstat -ano | Select-String ":$llamaPort\s.*LISTENING"

    if (-not $llamaRunning) {
        Write-Host "  Failed to start llama-server." -ForegroundColor Red
        exit 1
    }

    Write-Host "  llama-server started on port $llamaPort" -ForegroundColor Green
}

# Step 4: Check active model
Write-Host "[4/6] Checking active model..." -ForegroundColor Yellow

try {
    $modelInfo = Invoke-RestMethod `
        -Uri "http://127.0.0.1:$llamaPort/v1/models" `
        -TimeoutSec 5

    $activeModel = $modelInfo.data[0].id

    if ($activeModel) {
        $modelName = Split-Path $activeModel -Leaf
        Write-Host "  Model: $modelName" -ForegroundColor Cyan
    } else {
        Write-Host "  No model reported." -ForegroundColor Red
        exit 1
    }
}
catch {
    Write-Host "  Cannot reach llama-server: $_" -ForegroundColor Red
    exit 1
}

# Step 5: Start/check FastAPI
Write-Host "[5/6] Checking FastAPI..." -ForegroundColor Yellow
$appRunning = netstat -ano | Select-String ":$appPort\s.*LISTENING"

if ($appRunning) {
    Write-Host "  FastAPI already running on port $appPort" -ForegroundColor Green
} else {
    Write-Host "  Starting FastAPI..." -ForegroundColor Yellow

    Start-Process `
        -FilePath "python" `
        -WorkingDirectory $appWorkingDir `
        -ArgumentList "`"$appScript`"" `
        -WindowStyle Hidden

    Start-Sleep -Seconds 5

    $appRunning = netstat -ano | Select-String ":$appPort\s.*LISTENING"

    if (-not $appRunning) {
        Write-Host "  Failed to start FastAPI." -ForegroundColor Red
        exit 1
    }

    Write-Host "  FastAPI started on port $appPort" -ForegroundColor Green
}

# Step 6: Health check
Write-Host "[6/6] Health check..." -ForegroundColor Yellow

try {
    $status = Invoke-RestMethod `
        -Uri "http://127.0.0.1:$appPort/" `
        -TimeoutSec 5

    if ($status.status -ne "running") {
        throw "Unexpected server status: $($status.status)"
    }

    Write-Host "  Server: $($status.name) v$($status.version) - $($status.status)" -ForegroundColor Green
}
catch {
    Write-Host "  FastAPI health check failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== Services ===" -ForegroundColor Cyan
Write-Host "llama-server: http://localhost:$llamaPort" -ForegroundColor White
Write-Host "FastAPI:      http://localhost:$appPort" -ForegroundColor White
Write-Host ""
Write-Host "=== READY ===" -ForegroundColor Green
