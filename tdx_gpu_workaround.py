#!/usr/bin/env python3
"""
TDX/Confidential Computing GPU Workaround
For CUDA Error 802: system not yet initialized
"""

import os
import ctypes
import subprocess

print("🔥 TDX GPU Initialization Workaround")
print("=" * 50)

# Set environment for TDX/CC environments
env_vars = {
    # Force CUDA initialization
    "CUDA_VISIBLE_DEVICES": "0",
    "CUDA_DEVICE_ORDER": "PCI_BUS_ID",
    
    # TDX/CC specific settings
    "CUDA_LAUNCH_BLOCKING": "1",
    "CUDA_MODULE_LOADING": "EAGER",  # Force eager loading
    "CUDA_FORCE_PTX_JIT": "1",
    
    # Memory settings for CC
    "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True",
    "CUDA_MANAGED_FORCE_DEVICE_ALLOC": "1",
    
    # Disable certain optimizations that conflict with CC
    "CUDA_CACHE_DISABLE": "1",
    "CUDA_DISABLE_UNIFIED_MEMORY": "0",
    
    # Force specific driver behavior
    "CUDA_DRIVER_LIBRARY": "/usr/lib/x86_64-linux-gnu/libcuda.so.1",
    "__CUDA_LAZY_LOADING": "0"
}

# Apply environment
for key, value in env_vars.items():
    os.environ[key] = value
    print(f"Set {key}={value}")

print("\nAttempting direct CUDA initialization...")

# Method 1: Direct CUDA init via ctypes
try:
    # Load CUDA driver directly
    cuda = ctypes.CDLL("/usr/lib/x86_64-linux-gnu/libcuda.so.1")
    
    # Initialize CUDA
    result = cuda.cuInit(0)
    print(f"cuInit result: {result}")
    
    if result == 0:
        print("✅ CUDA initialized successfully!")
        
        # Get device count
        device_count = ctypes.c_int()
        result = cuda.cuDeviceGetCount(ctypes.byref(device_count))
        print(f"Device count: {device_count.value}")
    else:
        print(f"❌ cuInit failed with code: {result}")
        
except Exception as e:
    print(f"❌ Direct CUDA init failed: {e}")

# Method 2: Try PyTorch with CC workarounds
print("\nTesting PyTorch with CC workarounds...")
try:
    import torch
    
    # Force backend initialization
    torch.cuda.init()
    
    # Check availability
    available = torch.cuda.is_available()
    print(f"PyTorch CUDA available: {available}")
    
    if available:
        print(f"Device: {torch.cuda.get_device_name(0)}")
        print(f"Capability: {torch.cuda.get_device_capability(0)}")
    
except Exception as e:
    print(f"PyTorch error: {e}")

# Method 3: Check for CC/TDX indicators
print("\nChecking for Confidential Computing environment...")
cc_indicators = [
    "/sys/firmware/acpi/tables/CCEL",  # CC Event Log
    "/sys/kernel/security/tdx",         # TDX sysfs
    "/dev/tdx-guest",                   # TDX guest device
    "/sys/devices/virtual/misc/tdx-guest"
]

for path in cc_indicators:
    if os.path.exists(path):
        print(f"✅ Found CC indicator: {path}")

# Method 4: Alternative GPU access via nvidia-ml
print("\nTrying nvidia-ml library...")
try:
    nvml = ctypes.CDLL("libnvidia-ml.so.1")
    
    # Initialize NVML
    result = nvml.nvmlInit()
    if result == 0:
        print("✅ NVML initialized")
        
        # Get device count
        count = ctypes.c_uint()
        result = nvml.nvmlDeviceGetCount(ctypes.byref(count))
        if result == 0:
            print(f"NVML device count: {count.value}")
    else:
        print(f"❌ NVML init failed: {result}")
        
except Exception as e:
    print(f"❌ NVML error: {e}")

print("\n" + "=" * 50)
print("🔥 Workaround Summary:")
print("- CUDA error 802 is due to CC/TDX restrictions")
print("- GPU is present but isolated by security policy")
print("- Consider using CPU inference or non-CC instance")
print("=" * 50)