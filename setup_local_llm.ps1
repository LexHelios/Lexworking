# Setup Local LLM for LEX with RTX 4090

Write-Host "🔱 Setting up Local LLM Inference for LEX 🔱" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# Download Ollama for Windows
Write-Host "`n📥 Downloading Ollama..." -ForegroundColor Yellow
$ollamaUrl = "https://ollama.ai/download/OllamaSetup.exe"
$ollamaPath = "$env:TEMP\OllamaSetup.exe"

if (-not (Test-Path $ollamaPath)) {
    Invoke-WebRequest -Uri $ollamaUrl -OutFile $ollamaPath
    Write-Host "✅ Downloaded Ollama installer" -ForegroundColor Green
} else {
    Write-Host "✅ Ollama installer already downloaded" -ForegroundColor Green
}

Write-Host "`n🚀 Installing Ollama..." -ForegroundColor Yellow
Write-Host "Please follow the installer prompts" -ForegroundColor Cyan
Start-Process -FilePath $ollamaPath -Wait

Write-Host "`n✅ Ollama installed!" -ForegroundColor Green
Write-Host "`n📋 Recommended models for RTX 4090 (24GB):" -ForegroundColor Yellow
Write-Host "1. mixtral:8x7b-instruct-v0.1-q4_K_M (26GB but fits with quantization)" -ForegroundColor White
Write-Host "2. llama2:70b-chat-q4_K_M (38GB but can run with offloading)" -ForegroundColor White
Write-Host "3. deepseek-coder:33b-instruct-q4_K_M (18GB - great for coding)" -ForegroundColor White
Write-Host "4. yi:34b-chat-q4_K_M (19GB - excellent general purpose)" -ForegroundColor White
Write-Host "5. llama3:8b-instruct (4.7GB - super fast for quick tasks)" -ForegroundColor White

Write-Host "`n💡 To download models, run:" -ForegroundColor Cyan
Write-Host "ollama pull mixtral:8x7b" -ForegroundColor White
Write-Host "ollama pull deepseek-coder:33b" -ForegroundColor White
Write-Host "ollama pull llama3:8b" -ForegroundColor White