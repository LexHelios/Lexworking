# ComfyUI Quick Start Script
Write-Host "🎨 Starting ComfyUI for LEX Image Generation..." -ForegroundColor Cyan
Write-Host ""

$comfyDir = "$PSScriptRoot\ComfyUI_windows_portable"

# Check if already exists
if (Test-Path $comfyDir) {
    Write-Host "✅ ComfyUI already installed!" -ForegroundColor Green
    Write-Host "Starting ComfyUI..." -ForegroundColor Yellow
    
    # Start ComfyUI
    Set-Location $comfyDir
    if (Test-Path "run_nvidia_gpu.bat") {
        Start-Process "run_nvidia_gpu.bat"
        Write-Host "✅ ComfyUI started! Opening at http://localhost:8188" -ForegroundColor Green
    } else {
        Write-Host "❌ ComfyUI executable not found!" -ForegroundColor Red
    }
} else {
    Write-Host "ComfyUI not found. Downloading..." -ForegroundColor Yellow
    Write-Host "This is a 2GB download, please be patient!" -ForegroundColor Cyan
    Write-Host ""
    
    # Create temp directory
    $tempDir = "$PSScriptRoot\comfyui_download"
    New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
    
    # Download URL
    $url = "https://github.com/comfyanonymous/ComfyUI/releases/latest/download/ComfyUI_windows_portable_nvidia_cu124_or_cpu.7z"
    $output = "$tempDir\ComfyUI_portable.7z"
    
    Write-Host "Downloading from GitHub..." -ForegroundColor Yellow
    
    try {
        # Try Invoke-WebRequest first
        $ProgressPreference = 'SilentlyContinue'
        Invoke-WebRequest -Uri $url -OutFile $output -UseBasicParsing
        Write-Host "✅ Download complete!" -ForegroundColor Green
    } catch {
        Write-Host "Trying alternative download method..." -ForegroundColor Yellow
        # Try with System.Net.WebClient
        $webClient = New-Object System.Net.WebClient
        $webClient.DownloadFile($url, $output)
    }
    
    # Extract
    Write-Host ""
    Write-Host "Extracting ComfyUI..." -ForegroundColor Yellow
    
    if (Test-Path "C:\Program Files\7-Zip\7z.exe") {
        & "C:\Program Files\7-Zip\7z.exe" x $output -o"$PSScriptRoot" -y
        Write-Host "✅ Extraction complete!" -ForegroundColor Green
        
        # Clean up
        Remove-Item -Path $tempDir -Recurse -Force
        
        # Start ComfyUI
        Write-Host ""
        Write-Host "Starting ComfyUI..." -ForegroundColor Yellow
        Set-Location "$PSScriptRoot\ComfyUI_windows_portable"
        Start-Process "run_nvidia_gpu.bat"
        Write-Host "✅ ComfyUI started!" -ForegroundColor Green
    } else {
        Write-Host "❌ 7-Zip not found! Please install from: https://www.7-zip.org/" -ForegroundColor Red
        Write-Host "After installing 7-Zip, run this script again." -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "ComfyUI will open at:" -ForegroundColor White
Write-Host "http://localhost:8188" -ForegroundColor Green
Write-Host ""
Write-Host "Once it's running, try in LEX:" -ForegroundColor White
Write-Host '"Generate an image of a dragon"' -ForegroundColor Yellow
Write-Host '"Create a picture of a sunset"' -ForegroundColor Yellow
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to close..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")