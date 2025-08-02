#!/usr/bin/env python3
"""
Debug vision processing
"""
import requests
import json

# First check what the multimodal processor returns
print("1. Testing multimodal processor directly...")
from lex_multimodal_processor import multimodal_processor
import asyncio

async def test_processor():
    result = await multimodal_processor.process_file("test_cyberpunk.jpg", "image/jpeg")
    print(f"Processor result keys: {result.keys()}")
    print(f"Content type: {result.get('content_type')}")
    print(f"Requires vision model: {result.get('requires_vision_model')}")
    if 'data' in result:
        print(f"Data keys: {result['data'].keys()}")
        if 'base64' in result['data']:
            print(f"Base64 length: {len(result['data']['base64'])}")
    return result

# Run the test
result = asyncio.run(test_processor())

# Now test the full multimodal endpoint
print("\n2. Testing full multimodal endpoint...")
with open("test_cyberpunk.jpg", "rb") as f:
    files = {'files': ('test_cyberpunk.jpg', f, 'image/jpeg')}
    data = {'message': 'What specific text do you see in this image?', 'voice_mode': 'false'}
    
    response = requests.post(
        "http://localhost:8000/api/v1/lex/multimodal",
        files=files,
        data=data
    )
    
    result = response.json()
    print(f"Response preview: {result['response'][:100]}...")
    if 'orchestration' in result:
        print(f"Model: {result['orchestration']['model']}")