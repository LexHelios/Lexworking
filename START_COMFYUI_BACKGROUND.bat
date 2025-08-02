@echo off
echo Starting ComfyUI in background...
echo.
cd comfyui_system\ComfyUI
start "ComfyUI Server" /min python main.py --listen 0.0.0.0 --port 8188 --cpu
echo.
echo ComfyUI is starting...
echo Wait 10-20 seconds then check: http://localhost:8188
echo.
echo Once it's running, test in LEX:
echo - "Generate an image of a dragon"
echo - "Create a picture of a sunset"
echo.
pause