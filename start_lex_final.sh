#!/bin/bash
# 🔥 FINAL LEX PRODUCTION STARTUP SCRIPT
# This works around all the issues we've encountered

echo "🔱 ========================================== 🔱"
echo "   LEX AI SYSTEM - PRODUCTION READY"
echo "   H100 80GB GPU - lexcommand.ai"
echo "🔱 ========================================== 🔱"

# Kill conflicting processes
echo -e "\n📋 Cleaning up..."
pkill -f "python.*start_production" 2>/dev/null
pkill -f "ollama serve" 2>/dev/null
sleep 2

# GPU Setup
export CUDA_VISIBLE_DEVICES=0
export OLLAMA_NUM_GPU=999
export OLLAMA_HOST=127.0.0.1:11434

# Start Ollama
echo -e "\n🚀 Starting Ollama..."
ollama serve > /dev/null 2>&1 &
OLLAMA_PID=$!
sleep 5

# Check Ollama
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "✅ Ollama is running"
else
    echo "⚠️  Ollama startup issue - continuing anyway"
fi

# Find available port
PORT=8081
while lsof -i :$PORT > /dev/null 2>&1; do
    echo "Port $PORT in use, trying next..."
    PORT=$((PORT + 1))
done

echo -e "\n🌟 Starting LEX on port $PORT..."
cd /home/user/Alphalexnew/QodoLexosbuild-main/LexWorking

# Start server
export PORT=$PORT
python3 start_production_gpu.py