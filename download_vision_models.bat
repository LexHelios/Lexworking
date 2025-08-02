@echo off
echo ========================================
echo LEX VISION MODEL SETUP
echo ========================================
echo.
echo Downloading vision-capable models for multimodal support...
echo.

REM Download LLaVA for image understanding
echo [1/2] Downloading LLaVA 7B (Image understanding)...
"C:/Users/Vince/AppData/Local/Programs/Ollama/ollama.exe" pull llava:7b

echo.
echo [2/2] Downloading BakLLaVA (Alternative vision model)...
"C:/Users/Vince/AppData/Local/Programs/Ollama/ollama.exe" pull bakllava:latest

echo.
echo ========================================
echo VISION MODELS READY!
echo ========================================
echo.
echo Your LEX can now:
echo - View and understand images
echo - Analyze visual content
echo - Answer questions about pictures
echo - Process multimodal inputs
echo.
pause