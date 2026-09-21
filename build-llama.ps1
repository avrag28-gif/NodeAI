Write-Host "=== Building llama.cpp ===" -ForegroundColor Cyan

if (!(Test-Path ".\llama.cpp")) {
    Write-Host "Cloning llama.cpp..." -ForegroundColor Yellow
    git clone https://github.com/ggml-org/llama.cpp
}

Write-Host "Building with CUDA..." -ForegroundColor Yellow
cd .\llama.cpp
cmake -B build -DGGML_CUDA=ON
cmake --build build --config Release

Write-Host "=== Build Complete! ===" -ForegroundColor Green
Write-Host "Binary at: .\llama.cpp\build\bin\llama-server.exe" -ForegroundColor White
