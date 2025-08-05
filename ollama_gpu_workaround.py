#!/usr/bin/env python3
"""
Ollama GPU Workaround for CUDA Error 802
Forces Ollama to use GPU despite initialization issues
"""

import os
import subprocess
import time
import requests

print("🔥 OLLAMA GPU WORKAROUND - H100 Edition")
print("=" * 50)

# Step 1: Kill any existing Ollama
print("\n1. Stopping existing Ollama processes...")
subprocess.run(["pkill", "-f", "ollama"], capture_output=True)
time.sleep(2)

# Step 2: Set aggressive GPU environment
print("\n2. Setting GPU environment variables...")
env = os.environ.copy()
env.update({
    # Force GPU usage
    "CUDA_VISIBLE_DEVICES": "0",
    "OLLAMA_NUM_GPU": "999",  # All layers on GPU
    "OLLAMA_GPU_OVERHEAD": "0",
    
    # CUDA workarounds
    "CUDA_MODULE_LOADING": "LAZY",
    "CUDA_DEVICE_ORDER": "PCI_BUS_ID",
    "PYTORCH_CUDA_ALLOC_CONF": "backend:cudaMallocAsync",
    
    # Ollama settings
    "OLLAMA_HOST": "0.0.0.0:11434",
    "OLLAMA_CONTEXT_LENGTH": "32768",
    "OLLAMA_FLASH_ATTENTION": "true",
    "OLLAMA_DEBUG": "INFO",
    
    # Library paths
    "LD_LIBRARY_PATH": "/usr/local/cuda/lib64:/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH",
    "LD_PRELOAD": "/usr/lib/x86_64-linux-gnu/libcuda.so.1"
})

print("   Environment configured for GPU usage")

# Step 3: Start Ollama with GPU environment
print("\n3. Starting Ollama with GPU settings...")
ollama_proc = subprocess.Popen(
    ["ollama", "serve"],
    env=env,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Wait for startup
print("   Waiting for Ollama to start...")
time.sleep(5)

# Step 4: Check if Ollama is running
print("\n4. Checking Ollama status...")
try:
    response = requests.get("http://localhost:11434/api/tags")
    if response.status_code == 200:
        models = response.json().get("models", [])
        print(f"   ✅ Ollama running with {len(models)} models")
        
        # List models
        if models:
            print("\n   Available models:")
            for model in models:
                size = model.get("details", {}).get("parameter_size", "unknown")
                print(f"   - {model['name']} ({size})")
    else:
        print(f"   ❌ Ollama API returned: {response.status_code}")
except Exception as e:
    print(f"   ❌ Failed to connect to Ollama: {e}")

# Step 5: Test GPU usage
print("\n5. Testing GPU inference...")
try:
    # Run a small test prompt
    payload = {
        "model": "llama3.1:8b",
        "prompt": "Hello, how are you?",
        "stream": False,
        "options": {
            "num_gpu": 999,
            "num_thread": 32
        }
    }
    
    response = requests.post(
        "http://localhost:11434/api/generate",
        json=payload,
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        eval_duration = result.get("eval_duration", 0) / 1e9  # Convert to seconds
        tokens = result.get("eval_count", 0)
        
        if eval_duration > 0:
            tokens_per_sec = tokens / eval_duration
            print(f"   ✅ Inference successful!")
            print(f"   Speed: {tokens_per_sec:.1f} tokens/sec")
            
            # GPU would be much faster than CPU
            if tokens_per_sec > 50:
                print(f"   🔥 GPU acceleration detected!")
            else:
                print(f"   ⚠️  Running on CPU (slow speed)")
    else:
        print(f"   ❌ Inference failed: {response.status_code}")
        
except Exception as e:
    print(f"   ❌ Test failed: {e}")

print("\n6. Monitoring Ollama output...")
print("   Press Ctrl+C to stop\n")

# Monitor Ollama output
try:
    while True:
        line = ollama_proc.stderr.readline()
        if line:
            print(f"   Ollama: {line.strip()}")
        
        # Check if process is still running
        if ollama_proc.poll() is not None:
            print("\n   ❌ Ollama process terminated!")
            break
            
except KeyboardInterrupt:
    print("\n\n   Stopping Ollama...")
    ollama_proc.terminate()
    ollama_proc.wait()
    print("   ✅ Ollama stopped")

print("\n🔥 GPU Workaround Complete!")