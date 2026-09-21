Write-Host "=== Downloading Models ===" -ForegroundColor Cyan

if (!(Test-Path ".\models")) {
    New-Item -ItemType Directory -Path ".\models"
}

$models = @(
    @{
        Name = "Qwen2.5-7B-Instruct"
        Url = "https://huggingface.co/TheBloke/Qwen2.5-7B-Instruct-GGUF/resolve/main/qwen2.5-7b-instruct-q4_k_m.gguf"
        File = "qwen2.5-7b-instruct-q4_k_m.gguf"
    }
)

foreach ($model in $models) {
    $output = ".\models\$($model.File)"
    if (Test-Path $output) {
        Write-Host "  $($model.Name) already exists, skipping" -ForegroundColor Green
    } else {
        Write-Host "  Downloading $($model.Name)..." -ForegroundColor Yellow
        Invoke-WebRequest -Uri $model.Url -OutFile $output
        Write-Host "  Downloaded!" -ForegroundColor Green
    }
}

Write-Host "=== Done! ===" -ForegroundColor Green
