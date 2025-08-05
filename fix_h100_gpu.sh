#!/bin/bash
# 🔥 H100 GPU Fix Script - Resolves CUDA Error 802

echo "🔱 H100 GPU Fix Script"
echo "======================"

# 1. Stop all GPU-using processes
echo "1. Stopping GPU processes..."
sudo pkill -f ollama
sudo pkill -f python
sudo systemctl stop nvidia-fabricmanager 2>/dev/null
sleep 2

# 2. Unload and reload NVIDIA kernel modules
echo "2. Reloading NVIDIA kernel modules..."
sudo rmmod nvidia_uvm 2>/dev/null
sudo rmmod nvidia_drm 2>/dev/null
sudo rmmod nvidia_modeset 2>/dev/null
sudo rmmod nvidia 2>/dev/null
sleep 2
sudo modprobe nvidia
sudo modprobe nvidia_uvm
sudo modprobe nvidia_drm
sudo modprobe nvidia_modeset

# 3. Enable persistence mode
echo "3. Enabling GPU persistence mode..."
sudo nvidia-smi -pm 1

# 4. Disable ECC if enabled (can cause issues)
echo "4. Checking ECC mode..."
sudo nvidia-smi -e 0

# 5. Reset GPU state
echo "5. Attempting GPU reset..."
sudo nvidia-smi -r || echo "GPU busy - will clear on next step"

# 6. Clear CUDA cache
echo "6. Clearing CUDA cache..."
rm -rf ~/.nv/ComputeCache/*

# 7. Test GPU access
echo -e "\n7. Testing GPU access..."
python3 -c "
import os
os.environ['CUDA_MODULE_LOADING'] = 'EAGER'
os.environ['CUDA_LAUNCH_BLOCKING'] = '1'

try:
    import torch
    torch.cuda.empty_cache()
    torch.cuda.synchronize()
    print(f'PyTorch version: {torch.__version__}')
    print(f'CUDA available: {torch.cuda.is_available()}')
    if torch.cuda.is_available():
        print(f'GPU: {torch.cuda.get_device_name(0)}')
        print(f'GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB')
        
        # Test computation
        x = torch.randn(1000, 1000).cuda()
        y = torch.matmul(x, x)
        print('✅ GPU computation successful!')
    else:
        print('❌ CUDA still not available')
except Exception as e:
    print(f'Error: {e}')
"

echo -e "\n8. Final GPU status:"
nvidia-smi --query-gpu=name,driver_version,memory.total,persistence_mode --format=csv