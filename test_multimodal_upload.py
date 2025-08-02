#!/usr/bin/env python3
"""
Test multimodal upload functionality
"""
import requests
import os
from pathlib import Path

# Get the test image path
test_image = "test_cyberpunk.jpg"

print(f"Testing multimodal upload with: {test_image}")

# Check if file exists
if not os.path.exists(test_image):
    print(f"File not found: {test_image}")
    exit(1)

# Prepare the request
url = "http://localhost:8000/api/v1/lex/multimodal"

try:
    with open(test_image, 'rb') as f:
        files = {'files': ('cyberpunk.jpg', f, 'image/jpeg')}
        data = {'message': 'What do you see?', 'voice_mode': 'false'}
        
        print("Sending request...")
        response = requests.post(url, files=files, data=data)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\nSuccess!")
            print(f"Response: {result.get('response', 'No response')[:500]}...")
            print(f"Model used: {result.get('orchestration', {}).get('model', 'Unknown')}")
            print(f"Confidence: {result.get('confidence', 0) * 100:.0f}%")
        else:
            print(f"Error: {response.text}")
            
except Exception as e:
    print(f"Exception: {e}")