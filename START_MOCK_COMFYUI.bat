@echo off
echo Starting Mock ComfyUI Server for Testing...
echo.
echo This will simulate ComfyUI API responses
echo No actual images will be generated
echo.
start "Mock ComfyUI" python mock_comfyui_server.py
echo.
echo Mock ComfyUI should be starting on http://localhost:8188
echo.
echo You can now test image generation in LEX!
echo.
pause