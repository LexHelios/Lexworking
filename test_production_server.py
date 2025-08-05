#!/usr/bin/env python3
"""Test Production Server and GPU Status"""

import requests
import json
import subprocess

print("🔥 LEX PRODUCTION SERVER TEST")
print("=" * 50)

# Test 1: Server running
print("\n1. Server Status:")
try:
    response = requests.get("http://localhost:8080/", timeout=5)
    print(f"   ✅ Server is running on port 8080")
    print(f"   Status code: {response.status_code}")
except Exception as e:
    print(f"   ❌ Server not reachable: {e}")

# Test 2: Ollama status
print("\n2. Ollama Status:")
try:
    response = requests.get("http://localhost:11434/api/tags", timeout=5)
    if response.status_code == 200:
        data = response.json()
        models = data.get("models", [])
        print(f"   ✅ Ollama running with {len(models)} models")
        for model in models[:5]:  # Show first 5
            size = model.get("details", {}).get("parameter_size", "unknown")
            print(f"   - {model['name']} ({size})")
        if len(models) > 5:
            print(f"   ... and {len(models) - 5} more")
    else:
        print(f"   ❌ Ollama API error: {response.status_code}")
except Exception as e:
    print(f"   ❌ Ollama not reachable: {e}")

# Test 3: GPU status
print("\n3. GPU Status:")
try:
    result = subprocess.run(
        ["nvidia-smi", "--query-gpu=name,memory.used,memory.total,utilization.gpu", "--format=csv,noheader"],
        capture_output=True, text=True
    )
    print(f"   {result.stdout.strip()}")
except:
    print("   ❌ GPU info unavailable")

# Test 4: API endpoints
print("\n4. Testing API Endpoints:")
endpoints = [
    "/api/orchestrator/status",
    "/api/models",
    "/api/chat"
]

for endpoint in endpoints:
    try:
        response = requests.get(f"http://localhost:8080{endpoint}", timeout=2)
        print(f"   {endpoint}: {response.status_code}")
    except:
        print(f"   {endpoint}: Not available")

print("\n5. Quick GPU Inference Test:")
try:
    # Test with smallest model
    payload = {
        "model": "llama3.1:8b",
        "prompt": "Say hello in 5 words",
        "stream": False,
        "options": {
            "num_predict": 20,
            "temperature": 0.1
        }
    }
    
    response = requests.post(
        "http://localhost:11434/api/generate",
        json=payload,
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Response: {result.get('response', '').strip()}")
        
        # Check speed
        eval_duration = result.get("eval_duration", 0) / 1e9
        tokens = result.get("eval_count", 0)
        
        if eval_duration > 0:
            speed = tokens / eval_duration
            print(f"   Speed: {speed:.1f} tokens/sec")
            
            if speed > 100:
                print(f"   🔥 GPU acceleration working!")
            elif speed > 50:
                print(f"   ⚡ Partial GPU acceleration")
            else:
                print(f"   🐌 Running on CPU")
except Exception as e:
    print(f"   ❌ Inference test failed: {e}")

print("\n" + "=" * 50)
print("🌐 Your LEX AI server is accessible at:")
print("   Local: http://localhost:8080")
print("   Configure DNS to point lexcommand.ai to this server")
print("=" * 50)