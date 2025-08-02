#!/usr/bin/env python3
"""
Download vision models for multimodal support
"""
import subprocess
import sys

print("Downloading vision models for LEX multimodal support...")
print("This will enable image understanding capabilities")
print("-" * 50)

models = [
    ("llava:7b", "LLaVA 7B - Primary vision model"),
    ("bakllava:latest", "BakLLaVA - Alternative vision model"),
]

for model, description in models:
    print(f"\nDownloading: {description}")
    print(f"Model: {model}")
    
    try:
        # Run ollama pull command
        # Try with full path first, then fallback to PATH
        ollama_paths = [
            r"C:\Users\Vince\AppData\Local\Programs\Ollama\ollama.exe",
            "ollama"
        ]
        
        for ollama_cmd in ollama_paths:
            try:
                result = subprocess.run(
                    [ollama_cmd, "pull", model],
                    capture_output=True,
                    text=True
                )
                break
            except FileNotFoundError:
                if ollama_cmd == ollama_paths[-1]:
                    raise
                continue
        
        if result.returncode == 0:
            print(f"[OK] Successfully downloaded {model}")
        else:
            print(f"[FAIL] Failed to download {model}")
            print(f"Error: {result.stderr}")
            
    except FileNotFoundError:
        print("[ERROR] Ollama not found. Please ensure Ollama is installed and in PATH")
        print("Download from: https://ollama.ai")
        sys.exit(1)
        
print("\n" + "-" * 50)
print("Vision model setup complete!")
print("LEX can now process and understand images")