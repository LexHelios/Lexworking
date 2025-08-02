@echo off
echo Starting ComfyUI for LEX (No Authentication)...
echo.

cd /d "C:\Users\Vince\Documents\lexos-core\lexcommand-shadow-autonomy\ComfyUI_windows_portable"

echo Running ComfyUI with API access enabled...
.\python_embeded\python.exe -s ComfyUI\main.py --listen 127.0.0.1 --port 8188 --preview-method auto

pause