#!/usr/bin/env python3
"""
Simple vision test through API
"""
import requests

# Test 1: Ask about vision capabilities
print("Test 1: Vision capabilities")
response = requests.post(
    "http://localhost:8000/api/v1/lex",
    json={"message": "Can you analyze images? What vision models do you have?"}
)
print(f"Response: {response.json()['response'][:200]}...\n")

# Test 2: Simple image test
print("Test 2: Simple image analysis")
with open("test_cyberpunk.jpg", "rb") as f:
    files = {'files': ('test.jpg', f, 'image/jpeg')}
    data = {'message': 'What do you see in this image?', 'voice_mode': 'false'}
    
    response = requests.post(
        "http://localhost:8000/api/v1/lex/multimodal",
        files=files,
        data=data
    )
    
    result = response.json()
    print(f"Full response: {result['response']}")
    print(f"\nOrchestration info:")
    if 'orchestration' in result:
        for k, v in result['orchestration'].items():
            print(f"  {k}: {v}")
    print(f"\nModel: {result.get('orchestration', {}).get('model', 'Unknown')}")
    print(f"Confidence: {result.get('confidence', 0) * 100:.0f}%")