#!/usr/bin/env python3
"""
Simple ComfyUI starter - works with system Python
"""
import os
import sys
import subprocess

print("Starting ComfyUI with system Python...")
print("This will use your existing Python installation")

# Change to ComfyUI directory
os.chdir("comfyui_system/ComfyUI")

# Try to start ComfyUI directly
try:
    # Run ComfyUI main
    subprocess.run([
        sys.executable, 
        "main.py",
        "--listen", "0.0.0.0",
        "--port", "8188"
    ])
except Exception as e:
    print(f"Error starting ComfyUI: {e}")
    print("\nComfyUI requires specific dependencies.")
    print("For best results, use ComfyUI Portable from:")
    print("https://github.com/comfyanonymous/ComfyUI/releases")
    
    # Try minimal start
    print("\nAttempting minimal start...")
    subprocess.run([sys.executable, "main.py"])