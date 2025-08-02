@echo off
echo =============================================
echo COMFYUI PORTABLE DOWNLOADER AND RUNNER
echo =============================================
echo.

REM Check if ComfyUI_windows_portable exists
if exist ComfyUI_windows_portable (
    echo ComfyUI Portable already exists!
    goto :run_comfyui
)

echo Step 1: Downloading ComfyUI Portable...
echo =======================================
echo.
echo This will download the official ComfyUI Windows Portable
echo from GitHub (about 2GB)
echo.

REM Create download directory
mkdir ComfyUI_download 2>nul
cd ComfyUI_download

echo Downloading from GitHub releases...
echo Please be patient, this is a large file...
echo.

REM Use PowerShell to download
powershell -Command "& {
    $url = 'https://github.com/comfyanonymous/ComfyUI/releases/latest/download/ComfyUI_windows_portable_nvidia_cu124_or_cpu.7z'
    $output = 'ComfyUI_portable.7z'
    Write-Host 'Starting download...'
    try {
        Invoke-WebRequest -Uri $url -OutFile $output -UseBasicParsing
        Write-Host 'Download complete!'
    } catch {
        Write-Host 'Download failed. Trying alternative method...'
        Start-BitsTransfer -Source $url -Destination $output
    }
}"

echo.
echo Step 2: Extracting ComfyUI...
echo ===============================

if exist "C:\Program Files\7-Zip\7z.exe" (
    "C:\Program Files\7-Zip\7z.exe" x ComfyUI_portable.7z -o.. -y
) else if exist "C:\Program Files (x86)\7-Zip\7z.exe" (
    "C:\Program Files (x86)\7-Zip\7z.exe" x ComfyUI_portable.7z -o.. -y
) else (
    echo.
    echo ERROR: 7-Zip not found!
    echo Please install 7-Zip from: https://www.7-zip.org/
    echo Or extract ComfyUI_portable.7z manually
    echo.
    pause
    exit /b 1
)

cd ..

:run_comfyui
echo.
echo Step 3: Starting ComfyUI...
echo ===========================
echo.

if exist ComfyUI_windows_portable\run_nvidia_gpu.bat (
    echo Starting ComfyUI with NVIDIA GPU support...
    cd ComfyUI_windows_portable
    start "ComfyUI" run_nvidia_gpu.bat
) else (
    echo ERROR: ComfyUI not found or extraction failed!
    echo Please check the extraction.
    pause
    exit /b 1
)

echo.
echo =============================================
echo ComfyUI is starting!
echo =============================================
echo.
echo It will open in your browser at:
echo http://127.0.0.1:8188
echo.
echo LEX can now use ComfyUI for image generation!
echo.
echo Test it by saying:
echo "Generate an image of a cyberpunk city"
echo "Create a picture of a beautiful sunset"
echo.
pause