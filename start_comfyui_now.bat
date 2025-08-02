@echo off
echo Starting ComfyUI...

REM Check if venv exists
if exist venv (
    echo Using virtual environment...
    call venv\Scripts\activate
) else (
    echo No virtual environment found, using system Python...
)

cd comfyui_system\ComfyUI
python main.py --listen 0.0.0.0 --port 8188 || (
    echo.
    echo ===================================
    echo ComfyUI requires PyTorch!
    echo.
    echo Install it with:
    echo pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
    echo.
    echo Or download ComfyUI Portable:
    echo https://github.com/comfyanonymous/ComfyUI/releases
    echo ===================================
    pause
)