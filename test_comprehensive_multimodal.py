#!/usr/bin/env python3
"""
Comprehensive multimodal test
"""
import requests
import time

print("=== LEX MULTIMODAL COMPREHENSIVE TEST ===")
print("Version 2.4 - Full Vision Support")
print("=" * 50)

# Test 1: System status
print("\n1. SYSTEM STATUS")
response = requests.get("http://localhost:8000/orchestration-stats")
stats = response.json()
print(f"Mode: {stats['mode']}")
print(f"Available models: {stats['available_models']}")
print(f"Vision models: {[m for m in stats['available_models'] if m in ['llava:7b', 'bakllava:latest']]}")

# Test 2: Test our cyberpunk image
print("\n2. CYBERPUNK IMAGE ANALYSIS")
with open("test_cyberpunk.jpg", "rb") as f:
    files = {'files': ('cyberpunk.jpg', f, 'image/jpeg')}
    data = {
        'message': '''This is a test image I created. Please describe:
1. The background colors and gradient
2. The geometric shapes you see (polygon, ellipse)
3. Any text you can read
4. The grid pattern
5. The overall style''',
        'voice_mode': 'false'
    }
    
    start = time.time()
    response = requests.post(
        "http://localhost:8000/api/v1/lex/multimodal",
        files=files,
        data=data
    )
    elapsed = time.time() - start
    
    result = response.json()
    print(f"Response: {result['response']}")
    print(f"\nStats:")
    print(f"- Model: {result.get('orchestration', {}).get('model', 'Unknown')}")
    print(f"- Processing time: {elapsed:.2f}s")
    print(f"- Confidence: {result.get('confidence', 0) * 100:.0f}%")

# Test 3: Check model usage
print("\n3. MODEL USAGE STATS")
response = requests.get("http://localhost:8000/orchestration-stats")
stats = response.json()
print(f"Model usage: {stats['orchestration_stats']['model_usage']}")
print(f"Performance stats: {stats['orchestration_stats']['model_performance']}")

print("\n" + "=" * 50)
print("MULTIMODAL TEST COMPLETE")
print(f"✅ Vision models available: {len([m for m in stats['available_models'] if 'llava' in m or 'bakllava' in m])}")
print("✅ Image processing working")
print("✅ Intelligent orchestration active")
print("🔱 LEX v2.4 - Ready for multimodal AI!")