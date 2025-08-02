# Download ComfyUI Windows Portable by YanWenKun
Write-Host "=== ComfyUI Windows Portable Downloader ===" -ForegroundColor Cyan
Write-Host ""

# Create directory for ComfyUI
$comfyDir = "$PSScriptRoot\ComfyUI_Windows_Portable"
if (!(Test-Path $comfyDir)) {
    New-Item -ItemType Directory -Path $comfyDir | Out-Null
}

Write-Host "Downloading ComfyUI Windows Portable (YanWenKun Edition)..." -ForegroundColor Yellow
Write-Host "This includes 40+ custom nodes and xFormers!" -ForegroundColor Green
Write-Host ""

# Download the parts
$baseUrl = "https://github.com/YanWenKun/ComfyUI-Windows-Portable/releases/download/v9.4/"
$files = @(
    "ComfyUI_windows_portable_nvidia_cu124_or_cpu_py312_v9.4.7z.001",
    "ComfyUI_windows_portable_nvidia_cu124_or_cpu_py312_v9.4.7z.002"
)

foreach ($file in $files) {
    $url = $baseUrl + $file
    $output = Join-Path $comfyDir $file
    
    Write-Host "Downloading: $file" -ForegroundColor Cyan
    try {
        # Use System.Net.WebClient for more reliable downloads
        $webClient = New-Object System.Net.WebClient
        $webClient.DownloadFile($url, $output)
        Write-Host "✓ Downloaded: $file" -ForegroundColor Green
    } catch {
        Write-Host "✗ Failed to download: $file" -ForegroundColor Red
        Write-Host "Error: $_" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Download complete!" -ForegroundColor Green
Write-Host "Files saved to: $comfyDir" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Extract the .7z.001 file (it will automatically extract all parts)" -ForegroundColor White
Write-Host "2. Run 'run_nvidia_gpu.bat' from the extracted folder" -ForegroundColor White
Write-Host "3. ComfyUI will open at http://localhost:8188" -ForegroundColor White
}