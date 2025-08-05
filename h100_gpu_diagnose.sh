#!/bin/bash
echo "=== NVIDIA H100 GPU Diagnostic Script ==="

echo "1. Checking NVIDIA driver version..."
nvidia-smi || { echo "nvidia-smi failed. Driver not installed or GPU not detected."; exit 1; }

echo "2. Checking CUDA toolkit version..."
nvcc --version || echo "nvcc not found. CUDA toolkit may not be installed."

echo "3. Listing CUDA installations..."
ls /usr/local | grep cuda

echo "4. Checking environment variables..."
echo "CUDA_HOME: $CUDA_HOME"
echo "PATH: $PATH"
echo "LD_LIBRARY_PATH: $LD_LIBRARY_PATH"

echo "5. Checking user permissions for /dev/nvidia* ..."
ls -l /dev/nvidia*

echo "6. Checking dmesg for NVIDIA errors..."
dmesg | grep -i nvidia | tail -20

echo "7. Testing PyTorch GPU access..."
python3 -c "import torch; print('PyTorch CUDA available:', torch.cuda.is_available()); print('Device count:', torch.cuda.device_count())"

echo "8. Testing TensorFlow GPU access..."
python3 -c "import tensorflow as tf; print('TensorFlow GPUs:', tf.config.list_physical_devices('GPU'))"

echo "9. If using Docker, checking NVIDIA Container Toolkit..."
docker --version && docker info | grep -i nvidia

echo "=== End of Diagnostics ==="