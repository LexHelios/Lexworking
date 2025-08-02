@echo off
echo ============================================
echo LEX COMPLETE SETUP - UNCENSORED AI + IMAGES
echo ============================================
echo.
echo This will set up:
echo 1. ComfyUI for image generation
echo 2. Uncensored models
echo 3. Full LEX integration
echo.
pause

echo.
echo Step 1: Installing ComfyUI...
echo ==============================
call install_comfyui.bat

echo.
echo Step 2: Downloading models...
echo ==============================
cd comfyui_system\ComfyUI
call ..\..\venv\Scripts\activate
python ..\..\download_uncensored_models.py
cd ..\..

echo.
echo Step 3: Starting services...
echo ==============================
echo.
echo Starting ComfyUI in background...
start /min cmd /c "cd comfyui_system && run_comfyui.bat"

echo Waiting for ComfyUI to start...
timeout /t 10

echo.
echo Starting LEX with image generation...
cd ..
docker-compose -f docker-compose.simple.yml down
docker-compose -f docker-compose.simple.yml up -d --build

echo.
echo ============================================
echo SETUP COMPLETE!
echo ============================================
echo.
echo Services running:
echo - ComfyUI: http://localhost:8188
echo - LEX: http://localhost:8080
echo.
echo Test image generation:
echo "Generate an image of a beautiful sunset"
echo "Create a picture of a cyberpunk city"
echo "Make an image of a cute cat"
echo.
pause