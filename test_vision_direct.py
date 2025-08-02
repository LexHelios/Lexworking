#!/usr/bin/env python3
"""
Test vision models directly
"""
import subprocess
import base64

# Read the test image
with open("test_cyberpunk.jpg", "rb") as f:
    image_data = base64.b64encode(f.read()).decode()

# Test with llava model
print("Testing LLaVA vision model...")
prompt = f"What do you see in this image? Please describe in detail."

# Create request
ollama_cmd = r"C:\Users\Vince\AppData\Local\Programs\Ollama\ollama.exe"

try:
    result = subprocess.run(
        [ollama_cmd, "run", "llava:7b", prompt],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='ignore'
    )
    
    print("Response:", result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
        
except Exception as e:
    print(f"Error: {e}")