@echo off
echo ========================================
echo LEX UNRESTRICTED MODEL SETUP
echo ========================================
echo.
echo Installing uncensored models for personal use...
echo.

REM Check if Ollama is installed
where ollama >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Ollama not found! Please install from https://ollama.ai
    echo.
    pause
    exit /b 1
)

echo Starting Ollama service...
start /B ollama serve

timeout /t 3 >nul

echo.
echo Downloading uncensored models optimized for RTX 4090...
echo.

echo [1/4] Downloading Mixtral 8x7B (General purpose, less censored)...
ollama pull mixtral:8x7b

echo.
echo [2/4] Downloading Dolphin Mixtral (Completely uncensored)...
ollama pull dolphin-mixtral:8x7b 2>nul || (
    echo Dolphin model not available, trying alternative...
    ollama pull mixtral:8x7b-instruct-v0.1-q4_K_M
)

echo.
echo [3/4] Downloading DeepSeek Coder 33B (Uncensored coding)...
ollama pull deepseek-coder:33b

echo.
echo [4/4] Downloading Llama 3 8B (Fast responses)...
ollama pull llama3:8b

echo.
echo ========================================
echo SETUP COMPLETE!
echo ========================================
echo.
echo Installed models:
ollama list
echo.
echo Your LEX instance now has unrestricted local models!
echo.
echo For image generation, add these to your .env:
echo - REPLICATE_API_KEY (for SDXL uncensored)
echo - STABILITY_API_KEY (for Stable Diffusion)
echo.
pause