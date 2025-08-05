#!/bin/bash
# 🔥 LEX Production Server Startup - H100 GPU Edition
# This script handles CUDA error 802 and starts the production server

echo "🔱 ========================================== 🔱"
echo "   LEX AI PRODUCTION SERVER - H100 80GB"
echo "   Domain: lexcommand.ai"
echo "🔱 ========================================== 🔱"

# Stop any existing processes
echo -e "\n📋 Cleaning up existing processes..."
pkill -f "ollama" 2>/dev/null
pkill -f "python.*simple_lex_server" 2>/dev/null
sleep 2

# GPU Environment Setup
echo -e "\n🔥 Setting up GPU environment..."
export CUDA_VISIBLE_DEVICES=0
export CUDA_MODULE_LOADING=LAZY
export CUDA_DEVICE_ORDER=PCI_BUS_ID
export PYTORCH_CUDA_ALLOC_CONF=backend:cudaMallocAsync
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
export LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libcuda.so.1

# Ollama GPU settings
export OLLAMA_NUM_GPU=999
export OLLAMA_GPU_OVERHEAD=0
export OLLAMA_FLASH_ATTENTION=true
export OLLAMA_CONTEXT_LENGTH=32768
export OLLAMA_HOST=127.0.0.1:11434

# vLLM settings
export VLLM_SKIP_CUDA_DEVICE_COUNT_CHECK=1
export VLLM_USE_CUDA_IPC=0

echo "✅ GPU environment configured"

# Show GPU status
echo -e "\n📊 GPU Status:"
nvidia-smi --query-gpu=name,memory.total,memory.free,utilization.gpu --format=csv,noheader || echo "GPU info unavailable"

# Start Ollama in background
echo -e "\n🚀 Starting Ollama service..."
nohup ollama serve > ollama.log 2>&1 &
OLLAMA_PID=$!
echo "   Ollama PID: $OLLAMA_PID"

# Wait for Ollama
echo "   Waiting for Ollama to initialize..."
sleep 5

# Check Ollama status
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "   ✅ Ollama is running"
    
    # Show available models
    echo -e "\n📦 Available Ollama models:"
    curl -s http://localhost:11434/api/tags | python3 -c "
import json, sys
data = json.load(sys.stdin)
for model in data.get('models', []):
    size = model.get('details', {}).get('parameter_size', 'unknown')
    print(f'   - {model[\"name\"]} ({size})')
"
else
    echo "   ⚠️  Ollama failed to start - continuing anyway"
fi

# Start the production server
echo -e "\n🌟 Starting LEX Production Server..."
echo "   Port: 8080 (to avoid conflicts)"
echo "   Access: http://localhost:8080"
echo "   Domain: Configure DNS to point lexcommand.ai here"

# Change to working directory
cd /home/user/Alphalexnew/QodoLexosbuild-main/LexWorking

# Run the server (using port 8080)
python3 -c "
import os
os.environ['PORT'] = '8080'
exec(open('start_production_gpu.py').read())
"

# Cleanup on exit
echo -e "\n🔱 Shutting down..."
kill $OLLAMA_PID 2>/dev/null
echo "✅ Server stopped"