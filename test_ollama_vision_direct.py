#!/usr/bin/env python3
"""
Test Ollama vision API directly
"""
import requests
import base64
import json

# Load image and convert to base64
with open("test_cyberpunk.jpg", "rb") as f:
    image_base64 = base64.b64encode(f.read()).decode('utf-8')

print(f"Image base64 length: {len(image_base64)}")

# Test Ollama vision API directly
payload = {
    "model": "bakllava:latest",
    "prompt": "Describe this image in detail. What colors, shapes, and text do you see?",
    "images": [image_base64],
    "stream": False,
    "options": {
        "temperature": 0.7,
        "num_predict": 500
    }
}

print("\nSending request to Ollama...")
response = requests.post(
    "http://localhost:11434/api/generate",
    json=payload,
    timeout=60
)

print(f"Response status: {response.status_code}")
if response.status_code == 200:
    result = response.json()
    print(f"\nVision model response:")
    print(result.get('response', 'No response'))
else:
    print(f"Error: {response.text}")