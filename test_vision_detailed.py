#!/usr/bin/env python3
"""
Test vision capabilities in detail
"""
import requests

print("Testing LEX Vision Capabilities")
print("=" * 50)

# Test with our cyberpunk test image
with open("test_cyberpunk.jpg", "rb") as f:
    files = {'files': ('test_cyberpunk.jpg', f, 'image/jpeg')}
    data = {
        'message': '''Please describe this image in detail. I need to know:
1. What colors do you see?
2. What shapes are visible?
3. What text can you read in the image?
4. What is the overall theme or style?
5. Any specific elements or patterns you notice?

Be as specific as possible.''',
        'voice_mode': 'false'
    }
    
    print("Sending detailed image analysis request...")
    response = requests.post(
        "http://localhost:8000/api/v1/lex/multimodal",
        files=files,
        data=data
    )
    
    result = response.json()
    print(f"\nStatus: {response.status_code}")
    print(f"\nFull Response:\n{result['response']}")
    
    if 'orchestration' in result:
        print(f"\n--- Orchestration Details ---")
        print(f"Model used: {result['orchestration']['model']}")
        print(f"Task type: {result['orchestration']['task_type']}")
        print(f"Complexity: {result['orchestration']['complexity']}")
    
    print(f"\nConfidence: {result.get('confidence', 0) * 100:.0f}%")
    print(f"Processing time: {result.get('processing_time', 0):.2f}s")
    print(f"Capabilities used: {result.get('capabilities_used', [])}")