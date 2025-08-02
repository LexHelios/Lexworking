#!/usr/bin/env python3
"""
Test orchestration with vision capabilities
"""
import requests
import json

# First, check available models
print("1. Checking available models...")
response = requests.get("http://localhost:8000/orchestration-stats")
stats = response.json()
print(f"Available models: {stats['available_models']}")
print(f"Total models: {stats['total_models']}")

# Test text query first
print("\n2. Testing text query...")
response = requests.post(
    "http://localhost:8000/api/v1/lex",
    json={"message": "What vision models do you have available?"}
)
print(f"Response: {response.json()['response'][:200]}...")

# Test multimodal with our test image
print("\n3. Testing multimodal with image...")
with open("test_cyberpunk.jpg", "rb") as f:
    files = {'files': ('test_cyberpunk.jpg', f, 'image/jpeg')}
    data = {'message': 'Describe this image in detail. What colors, shapes, and text do you see?', 'voice_mode': 'false'}
    
    response = requests.post(
        "http://localhost:8000/api/v1/lex/multimodal",
        files=files,
        data=data
    )
    
    result = response.json()
    print(f"Status: {response.status_code}")
    print(f"Response: {result['response'][:300]}...")
    
    if 'orchestration' in result:
        print(f"Model used: {result['orchestration']['model']}")
        print(f"Task type: {result['orchestration']['task_type']}")
    
    print(f"Confidence: {result.get('confidence', 0) * 100:.0f}%")
    print(f"Processing time: {result.get('processing_time', 0):.2f}s")

# Check if vision models are being used
print("\n4. Checking orchestration stats after multimodal...")
response = requests.get("http://localhost:8000/orchestration-stats")
stats = response.json()
print(f"Model usage: {stats['orchestration_stats']['model_usage']}")
print(f"Task distribution: {stats['orchestration_stats']['task_distribution']}")