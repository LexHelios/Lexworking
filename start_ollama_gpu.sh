#!/bin/bash
# Start Ollama with GPU support

echo "🔥 Starting Ollama with GPU support on H100..."

# Set GPU environment
export CUDA_VISIBLE_DEVICES=0
export OLLAMA_HOST=0.0.0.0:11434
export OLLAMA_MODELS=/home/user/.ollama/models
export OLLAMA_DEBUG=INFO

# Force GPU usage
export OLLAMA_NUM_GPU=999  # Use all layers on GPU
export OLLAMA_GPU_OVERHEAD=0
export OLLAMA_FLASH_ATTENTION=true
export OLLAMA_CONTEXT_LENGTH=32768

# Try different CUDA paths
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH

echo "Environment set. Starting Ollama serve..."

# Start Ollama
ollama serve