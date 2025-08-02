# Download ComfyUI Portable
Write-Host "Downloading ComfyUI Portable..." -ForegroundColor Yellow

$url = "https://github.com/comfyanonymous/ComfyUI/releases/latest/download/ComfyUI_windows_portable_nvidia_cu124_or_cpu.7z"
$output = "$PSScriptRoot\ComfyUI_portable.7z"

# Download the file
Write-Host "Downloading from: $url" -ForegroundColor Cyan
Invoke-WebRequest -Uri $url -OutFile $output -UseBasicParsing

Write-Host "Download complete!" -ForegroundColor Green
Write-Host "File saved to: $output" -ForegroundColor Cyan

# Extract if 7-Zip is available
if (Test-Path "C:\Program Files\7-Zip\7z.exe") {
    Write-Host "Extracting ComfyUI..." -ForegroundColor Yellow
    & "C:\Program Files\7-Zip\7z.exe" x $output -o"$PSScriptRoot\ComfyUI_portable" -y
    Write-Host "Extraction complete!" -ForegroundColor Green
} else {
    Write-Host "7-Zip not found. Please extract manually." -ForegroundColor Yellow
}