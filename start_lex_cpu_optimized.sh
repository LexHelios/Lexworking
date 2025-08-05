#!/bin/bash
# 🔥 LEX AI Production - CPU Optimized for CC/TDX Environment
# Works around CUDA error 802 in confidential computing

echo "🔱 ========================================== 🔱"
echo "   LEX AI SYSTEM - CPU OPTIMIZED"
echo "   Confidential Computing Environment"
echo "   Domain: lexcommand.ai"
echo "🔱 ========================================== 🔱"

# Clean up
pkill -f "ollama serve" 2>/dev/null
pkill -f "python.*start_production" 2>/dev/null
sleep 2

# CPU Optimization Settings
export OMP_NUM_THREADS=32
export MKL_NUM_THREADS=32
export OPENBLAS_NUM_THREADS=32
export VECLIB_MAXIMUM_THREADS=32

# Disable GPU attempts to avoid errors
export CUDA_VISIBLE_DEVICES=""
export OLLAMA_NUM_GPU=0

# Ollama CPU settings
export OLLAMA_HOST=127.0.0.1:11434
export OLLAMA_NUM_THREAD=32
export OLLAMA_CONTEXT_LENGTH=8192

echo -e "\n📊 System Info:"
echo "CPU: $(lscpu | grep 'Model name' | cut -d: -f2 | xargs)"
echo "Cores: $(nproc)"
echo "RAM: $(free -h | awk '/^Mem:/ {print $2}')"
echo "Note: GPU blocked by CC/TDX security policy"

echo -e "\n🚀 Starting Ollama (CPU mode)..."
ollama serve > ollama.log 2>&1 &
OLLAMA_PID=$!
sleep 5

# Find available port
PORT=8081
while lsof -i :$PORT > /dev/null 2>&1; do
    PORT=$((PORT + 1))
done

echo -e "\n🌟 Starting LEX on port $PORT..."
echo "Access at: http://localhost:$PORT"

cd /home/user/Alphalexnew/QodoLexosbuild-main/LexWorking

# Start with CPU optimization
export PYTORCH_ENABLE_MPS_FALLBACK=1
export PORT=$PORT

# Run server
python3 -c "
import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = ''
print('🔥 Running in CPU-optimized mode due to CC/TDX restrictions')
exec(open('start_production_gpu.py').read())
"