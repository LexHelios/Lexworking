@echo off
echo ========================================
echo Installing ComfyUI for LEX Integration
echo RTX 4090 Optimized Setup
echo ========================================
echo.

REM Check if git is installed
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Git is not installed. Please install Git first.
    echo Download from: https://git-scm.com/download/win
    pause
    exit /b 1
)

REM Create directory for ComfyUI
echo Creating ComfyUI directory...
cd /d C:\Users\Vince\Documents\lexos-core\lexcommand-shadow-autonomy\lexworking
mkdir comfyui_system 2>nul
cd comfyui_system

REM Clone ComfyUI
echo.
echo Cloning ComfyUI repository...
if not exist ComfyUI (
    git clone https://github.com/comfyanonymous/ComfyUI.git
) else (
    echo ComfyUI already exists, updating...
    cd ComfyUI
    git pull
    cd ..
)

REM Clone ComfyUI Manager
echo.
echo Installing ComfyUI Manager...
cd ComfyUI\custom_nodes
if not exist ComfyUI-Manager (
    git clone https://github.com/ltdrdata/ComfyUI-Manager.git
) else (
    echo ComfyUI Manager already exists
)
cd ..\..

REM Create model directories
echo.
echo Creating model directories...
cd ComfyUI
mkdir models\checkpoints 2>nul
mkdir models\vae 2>nul
mkdir models\loras 2>nul
mkdir models\controlnet 2>nul
mkdir models\clip 2>nul
mkdir models\diffusion_models 2>nul
mkdir models\upscale_models 2>nul

REM Create Python virtual environment
echo.
echo Setting up Python environment...
python -m venv venv
call venv\Scripts\activate

REM Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install PyTorch with CUDA support for RTX 4090
echo.
echo Installing PyTorch with CUDA 12.1 support...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

REM Install ComfyUI requirements
echo.
echo Installing ComfyUI requirements...
pip install -r requirements.txt

REM Install additional packages for better performance
echo.
echo Installing performance optimizations...
pip install xformers accelerate transformers diffusers opencv-python pillow

REM Create startup script
echo.
echo Creating startup script...
echo @echo off > ..\run_comfyui.bat
echo cd /d "%~dp0ComfyUI" >> ..\run_comfyui.bat
echo call venv\Scripts\activate >> ..\run_comfyui.bat
echo echo Starting ComfyUI... >> ..\run_comfyui.bat
echo python main.py --listen 0.0.0.0 --port 8188 --use-pytorch-cross-attention >> ..\run_comfyui.bat
echo pause >> ..\run_comfyui.bat

REM Create API test script
echo.
echo Creating API test script...
echo import requests > ..\test_comfyui_api.py
echo import json >> ..\test_comfyui_api.py
echo. >> ..\test_comfyui_api.py
echo print("Testing ComfyUI API...") >> ..\test_comfyui_api.py
echo try: >> ..\test_comfyui_api.py
echo     response = requests.get("http://localhost:8188/system_stats") >> ..\test_comfyui_api.py
echo     print(f"Status: {response.status_code}") >> ..\test_comfyui_api.py
echo     print(f"System: {response.json()}") >> ..\test_comfyui_api.py
echo except Exception as e: >> ..\test_comfyui_api.py
echo     print(f"Error: {e}") >> ..\test_comfyui_api.py
echo     print("Make sure ComfyUI is running!") >> ..\test_comfyui_api.py

echo.
echo ========================================
echo ComfyUI Installation Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Run 'run_comfyui.bat' to start ComfyUI
echo 2. Access ComfyUI at http://localhost:8188
echo 3. Download models to ComfyUI\models\checkpoints\
echo.
echo Recommended uncensored models:
echo - Pony Diffusion V6 XL
echo - Realistic Vision V5.1
echo - DreamShaper XL
echo - Juggernaut XL
echo.
pause