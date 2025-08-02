@echo off
echo === Downloading ComfyUI Portable ===
echo.

REM Create directory
if not exist ComfyUI_Portable mkdir ComfyUI_Portable
cd ComfyUI_Portable

echo Downloading Part 1...
curl -L -o comfyui_part1.7z.001 "https://github.com/YanWenKun/ComfyUI-Windows-Portable/releases/download/v9.4/ComfyUI_windows_portable_nvidia_cu124_or_cpu_py312_v9.4.7z.001"

echo.
echo Downloading Part 2...
curl -L -o comfyui_part2.7z.002 "https://github.com/YanWenKun/ComfyUI-Windows-Portable/releases/download/v9.4/ComfyUI_windows_portable_nvidia_cu124_or_cpu_py312_v9.4.7z.002"

echo.
echo Download complete!
echo.
echo Extract comfyui_part1.7z.001 with 7-Zip to use ComfyUI
echo.
pause