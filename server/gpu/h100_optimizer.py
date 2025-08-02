
"""
H100 GPU Optimization Module
Implements H100-specific optimizations for PyTorch, vLLM, and CUDA operations
"""
import os
import logging
import subprocess
import json
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from contextlib import contextmanager
import threading
import psutil

try:
    import torch
    import torch.cuda
    import torch.distributed as dist
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    import pynvml
    PYNVML_AVAILABLE = True
except ImportError:
    PYNVML_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class H100Config:
    """H100 GPU configuration parameters"""
    # CUDA Configuration
    cuda_visible_devices: str = "0,1,2,3,4,5,6,7"
    cuda_memory_fraction: float = 0.9
    cuda_allow_growth: bool = True
    
    # NCCL Configuration
    nccl_debug: str = "INFO"
    nccl_ib_disable: int = 0
    nccl_net_gdr_level: int = 2
    nccl_socket_ifname: str = "eth0"
    nccl_ib_ar_threshold: int = 0
    nccl_ib_pci_relaxed_ordering: int = 1
    nccl_ib_qps_per_connection: int = 2
    nccl_ib_split_data_on_qps: int = 0
    
    # PyTorch Optimizations
    torch_cuda_arch_list: str = "9.0"  # H100 architecture
    omp_num_threads: int = 8
    cuda_launch_blocking: int = 0
    torch_cudnn_benchmark: bool = True
    torch_backends_cudnn_deterministic: bool = False
    
    # vLLM Configuration
    vllm_gpu_memory_utilization: float = 0.85
    vllm_max_model_len: int = 8192
    vllm_tensor_parallel_size: int = 8
    vllm_pipeline_parallel_size: int = 1
    vllm_max_num_seqs: int = 256
    vllm_max_num_batched_tokens: int = 8192
    vllm_block_size: int = 16
    vllm_swap_space: int = 4
    vllm_enforce_eager: bool = False
    vllm_max_context_len_to_capture: int = 8192
    
    # Memory Management
    pytorch_cuda_alloc_conf: str = "max_split_size_mb:512,roundup_power2_divisions:16"
    cuda_memory_pool_size: str = "0.9"
    
    # Performance Monitoring
    gpu_health_check_interval: int = 30
    gpu_memory_threshold: float = 0.95
    gpu_temperature_threshold: int = 85
    gpu_utilization_threshold: float = 0.95


class H100Optimizer:
    """H100 GPU optimization manager"""
    
    def __init__(self, config: Optional[H100Config] = None):
        self.config = config or H100Config()
        self.gpu_count = 0
        self.gpu_info = {}
        self.monitoring_thread = None
        self.monitoring_active = False
        
        # Initialize NVML if available
        if PYNVML_AVAILABLE:
            try:
                pynvml.nvmlInit()
                self.gpu_count = pynvml.nvmlDeviceGetCount()
                logger.info(f"Initialized NVML with {self.gpu_count} GPUs")
            except Exception as e:
                logger.warning(f"Failed to initialize NVML: {e}")
                PYNVML_AVAILABLE = False
        
        # Initialize PyTorch if available
        if TORCH_AVAILABLE and torch.cuda.is_available():
            self.gpu_count = max(self.gpu_count, torch.cuda.device_count())
            logger.info(f"PyTorch detected {torch.cuda.device_count()} CUDA devices")
    
    def setup_environment(self) -> None:
        """Setup H100-optimized environment variables"""
        logger.info("Setting up H100-optimized environment variables")
        
        env_vars = {
            # CUDA Configuration
            "CUDA_VISIBLE_DEVICES": self.config.cuda_visible_devices,
            "CUDA_MEMORY_FRACTION": str(self.config.cuda_memory_fraction),
            "CUDA_DEVICE_ORDER": "PCI_BUS_ID",
            "CUDA_LAUNCH_BLOCKING": str(self.config.cuda_launch_blocking),
            
            # NCCL Configuration
            "NCCL_DEBUG": self.config.nccl_debug,
            "NCCL_IB_DISABLE": str(self.config.nccl_ib_disable),
            "NCCL_NET_GDR_LEVEL": str(self.config.nccl_net_gdr_level),
            "NCCL_SOCKET_IFNAME": self.config.nccl_socket_ifname,
            "NCCL_IB_AR_THRESHOLD": str(self.config.nccl_ib_ar_threshold),
            "NCCL_IB_PCI_RELAXED_ORDERING": str(self.config.nccl_ib_pci_relaxed_ordering),
            "NCCL_IB_QPS_PER_CONNECTION": str(self.config.nccl_ib_qps_per_connection),
            "NCCL_IB_SPLIT_DATA_ON_QPS": str(self.config.nccl_ib_split_data_on_qps),
            
            # PyTorch Optimizations
            "TORCH_CUDA_ARCH_LIST": self.config.torch_cuda_arch_list,
            "OMP_NUM_THREADS": str(self.config.omp_num_threads),
            "PYTORCH_CUDA_ALLOC_CONF": self.config.pytorch_cuda_alloc_conf,
            
            # NVIDIA Driver Capabilities
            "NVIDIA_VISIBLE_DEVICES": "all",
            "NVIDIA_DRIVER_CAPABILITIES": "compute,utility",
            "NVIDIA_REQUIRE_CUDA": "cuda>=12.0",
            
            # Memory Management
            "CUDA_MEMORY_POOL_SIZE": self.config.cuda_memory_pool_size,
        }
        
        for key, value in env_vars.items():
            os.environ[key] = value
            logger.debug(f"Set {key}={value}")
        
        # Set PyTorch-specific optimizations
        if TORCH_AVAILABLE:
            torch.backends.cudnn.benchmark = self.config.torch_backends_cudnn_benchmark
            torch.backends.cudnn.deterministic = self.config.torch_backends_cudnn_deterministic
            
            # Enable TensorFloat-32 (TF32) for H100
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
            
            logger.info("Applied PyTorch H100 optimizations")
    
    def optimize_pytorch_model(self, model: Any, device_ids: Optional[List[int]] = None) -> Any:
        """Optimize PyTorch model for H100"""
        if not TORCH_AVAILABLE:
            logger.warning("PyTorch not available, skipping model optimization")
            return model
        
        logger.info("Optimizing PyTorch model for H100")
        
        # Move model to GPU(s)
        if device_ids is None:
            device_ids = list(range(min(self.gpu_count, 8)))  # Use up to 8 H100 GPUs
        
        if len(device_ids) == 1:
            # Single GPU
            device = torch.device(f"cuda:{device_ids[0]}")
            model = model.to(device)
            logger.info(f"Model moved to single GPU: {device}")
        else:
            # Multi-GPU with DataParallel or DistributedDataParallel
            if dist.is_initialized():
                # Use DistributedDataParallel for better performance
                model = torch.nn.parallel.DistributedDataParallel(
                    model,
                    device_ids=device_ids,
                    output_device=device_ids[0],
                    find_unused_parameters=False,
                    broadcast_buffers=False,
                    bucket_cap_mb=25,  # Optimize for H100 bandwidth
                    gradient_as_bucket_view=True
                )
                logger.info(f"Model wrapped with DistributedDataParallel on GPUs: {device_ids}")
            else:
                # Use DataParallel as fallback
                model = torch.nn.DataParallel(model, device_ids=device_ids)
                model = model.to(f"cuda:{device_ids[0]}")
                logger.info(f"Model wrapped with DataParallel on GPUs: {device_ids}")
        
        # Enable mixed precision if supported
        try:
            from torch.cuda.amp import autocast, GradScaler
            logger.info("Mixed precision (AMP) available for H100 optimization")
        except ImportError:
            logger.warning("Mixed precision not available")
        
        # Compile model for H100 if using PyTorch 2.0+
        if hasattr(torch, 'compile'):
            try:
                model = torch.compile(
                    model,
                    mode="max-autotune",  # Aggressive optimization for H100
                    dynamic=False,
                    backend="inductor"
                )
                logger.info("Model compiled with torch.compile for H100")
            except Exception as e:
                logger.warning(f"Failed to compile model: {e}")
        
        return model
    
    def get_gpu_info(self) -> Dict[int, Dict[str, Any]]:
        """Get detailed GPU information"""
        gpu_info = {}
        
        if PYNVML_AVAILABLE:
            try:
                for i in range(self.gpu_count):
                    handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                    
                    # Basic info
                    name = pynvml.nvmlDeviceGetName(handle).decode('utf-8')
                    memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                    utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
                    temperature = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                    power = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0  # Convert to watts
                    
                    # H100-specific info
                    try:
                        compute_capability = pynvml.nvmlDeviceGetCudaComputeCapability(handle)
                        max_clock_info = pynvml.nvmlDeviceGetMaxClockInfo(handle, pynvml.NVML_CLOCK_GRAPHICS)
                        memory_clock = pynvml.nvmlDeviceGetMaxClockInfo(handle, pynvml.NVML_CLOCK_MEM)
                    except:
                        compute_capability = (0, 0)
                        max_clock_info = 0
                        memory_clock = 0
                    
                    gpu_info[i] = {
                        "name": name,
                        "memory_total": memory_info.total,
                        "memory_used": memory_info.used,
                        "memory_free": memory_info.free,
                        "memory_utilization": (memory_info.used / memory_info.total) * 100,
                        "gpu_utilization": utilization.gpu,
                        "memory_bandwidth_utilization": utilization.memory,
                        "temperature": temperature,
                        "power_usage": power,
                        "compute_capability": f"{compute_capability[0]}.{compute_capability[1]}",
                        "max_graphics_clock": max_clock_info,
                        "max_memory_clock": memory_clock,
                        "is_h100": "H100" in name
                    }
            except Exception as e:
                logger.error(f"Failed to get GPU info via NVML: {e}")
        
        # Fallback to PyTorch if NVML fails
        if not gpu_info and TORCH_AVAILABLE and torch.cuda.is_available():
            for i in range(torch.cuda.device_count()):
                props = torch.cuda.get_device_properties(i)
                memory_allocated = torch.cuda.memory_allocated(i)
                memory_reserved = torch.cuda.memory_reserved(i)
                
                gpu_info[i] = {
                    "name": props.name,
                    "memory_total": props.total_memory,
                    "memory_used": memory_allocated,
                    "memory_reserved": memory_reserved,
                    "memory_utilization": (memory_allocated / props.total_memory) * 100,
                    "compute_capability": f"{props.major}.{props.minor}",
                    "multiprocessor_count": props.multi_processor_count,
                    "is_h100": "H100" in props.name
                }
        
        self.gpu_info = gpu_info
        return gpu_info
    
    def monitor_gpu_health(self) -> Dict[str, Any]:
        """Monitor GPU health and performance"""
        if not self.gpu_info:
            self.get_gpu_info()
        
        health_status = {
            "timestamp": time.time(),
            "overall_status": "healthy",
            "alerts": [],
            "gpus": {}
        }
        
        for gpu_id, info in self.gpu_info.items():
            gpu_status = {
                "status": "healthy",
                "alerts": []
            }
            
            # Check temperature
            if "temperature" in info and info["temperature"] > self.config.gpu_temperature_threshold:
                gpu_status["status"] = "warning"
                gpu_status["alerts"].append(f"High temperature: {info['temperature']}°C")
                health_status["alerts"].append(f"GPU {gpu_id}: High temperature")
            
            # Check memory usage
            if "memory_utilization" in info and info["memory_utilization"] > self.config.gpu_memory_threshold * 100:
                gpu_status["status"] = "warning"
                gpu_status["alerts"].append(f"High memory usage: {info['memory_utilization']:.1f}%")
                health_status["alerts"].append(f"GPU {gpu_id}: High memory usage")
            
            # Check GPU utilization (low utilization might indicate issues)
            if "gpu_utilization" in info and info["gpu_utilization"] < 10:
                gpu_status["status"] = "info"
                gpu_status["alerts"].append(f"Low utilization: {info['gpu_utilization']}%")
            
            health_status["gpus"][gpu_id] = gpu_status
        
        # Set overall status
        if any(gpu["status"] == "warning" for gpu in health_status["gpus"].values()):
            health_status["overall_status"] = "warning"
        
        return health_status
    
    def start_monitoring(self) -> None:
        """Start background GPU monitoring"""
        if self.monitoring_active:
            logger.warning("Monitoring already active")
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        logger.info("Started GPU monitoring thread")
    
    def stop_monitoring(self) -> None:
        """Stop background GPU monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("Stopped GPU monitoring")
    
    def _monitoring_loop(self) -> None:
        """Background monitoring loop"""
        while self.monitoring_active:
            try:
                self.get_gpu_info()
                health = self.monitor_gpu_health()
                
                # Log warnings
                if health["alerts"]:
                    logger.warning(f"GPU health alerts: {health['alerts']}")
                
                time.sleep(self.config.gpu_health_check_interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(10)  # Wait before retrying
    
    def optimize_vllm_config(self) -> Dict[str, Any]:
        """Generate optimized vLLM configuration for H100"""
        config = {
            "gpu_memory_utilization": self.config.vllm_gpu_memory_utilization,
            "max_model_len": self.config.vllm_max_model_len,
            "tensor_parallel_size": min(self.config.vllm_tensor_parallel_size, self.gpu_count),
            "pipeline_parallel_size": self.config.vllm_pipeline_parallel_size,
            "max_num_seqs": self.config.vllm_max_num_seqs,
            "max_num_batched_tokens": self.config.vllm_max_num_batched_tokens,
            "block_size": self.config.vllm_block_size,
            "swap_space": self.config.vllm_swap_space,
            "enforce_eager": self.config.vllm_enforce_eager,
            "max_context_len_to_capture": self.config.vllm_max_context_len_to_capture,
            
            # H100-specific optimizations
            "enable_chunked_prefill": True,
            "max_num_batched_tokens": self.config.vllm_max_num_batched_tokens,
            "use_v2_block_manager": True,
            "enable_prefix_caching": True,
            "disable_log_stats": False,
            "quantization": None,  # H100 has enough memory for full precision
            "dtype": "auto",  # Let vLLM choose optimal dtype
            
            # Multi-step scheduling for better throughput
            "num_scheduler_steps": 10,
            
            # GPU-specific settings
            "device": "cuda",
            "trust_remote_code": True,
            "download_dir": "/app/models",
            "load_format": "auto",
            "revision": None,
            "tokenizer_revision": None,
            "max_paddings": 256,
        }
        
        logger.info(f"Generated vLLM config for {self.gpu_count} H100 GPUs")
        return config
    
    @contextmanager
    def cuda_stream_context(self, device_id: int = 0):
        """Context manager for CUDA stream optimization"""
        if not TORCH_AVAILABLE:
            yield None
            return
        
        device = torch.device(f"cuda:{device_id}")
        with torch.cuda.device(device):
            stream = torch.cuda.Stream()
            with torch.cuda.stream(stream):
                yield stream
    
    def benchmark_gpu_performance(self, duration: int = 60) -> Dict[str, Any]:
        """Benchmark H100 GPU performance"""
        if not TORCH_AVAILABLE:
            logger.warning("PyTorch not available for benchmarking")
            return {}
        
        logger.info(f"Starting {duration}s GPU benchmark")
        
        results = {}
        
        for gpu_id in range(min(self.gpu_count, 8)):  # Test up to 8 GPUs
            device = torch.device(f"cuda:{gpu_id}")
            
            # Memory bandwidth test
            size = 1024 * 1024 * 256  # 256M elements
            a = torch.randn(size, device=device, dtype=torch.float32)
            b = torch.randn(size, device=device, dtype=torch.float32)
            
            torch.cuda.synchronize()
            start_time = time.time()
            
            iterations = 0
            end_time = start_time + duration
            
            while time.time() < end_time:
                c = a + b
                torch.cuda.synchronize()
                iterations += 1
            
            elapsed = time.time() - start_time
            bandwidth = (iterations * size * 4 * 2) / elapsed / 1e9  # GB/s
            
            # Compute performance test (matrix multiplication)
            matrix_size = 4096
            a_mm = torch.randn(matrix_size, matrix_size, device=device, dtype=torch.float16)
            b_mm = torch.randn(matrix_size, matrix_size, device=device, dtype=torch.float16)
            
            torch.cuda.synchronize()
            start_time = time.time()
            
            mm_iterations = 0
            end_time = start_time + 10  # 10 second test
            
            while time.time() < end_time:
                c_mm = torch.mm(a_mm, b_mm)
                torch.cuda.synchronize()
                mm_iterations += 1
            
            mm_elapsed = time.time() - start_time
            flops = (mm_iterations * 2 * matrix_size**3) / mm_elapsed / 1e12  # TFLOPS
            
            results[gpu_id] = {
                "memory_bandwidth_gb_s": bandwidth,
                "compute_tflops": flops,
                "memory_test_iterations": iterations,
                "compute_test_iterations": mm_iterations
            }
            
            logger.info(f"GPU {gpu_id}: {bandwidth:.1f} GB/s bandwidth, {flops:.1f} TFLOPS")
        
        return results
    
    def cleanup(self) -> None:
        """Cleanup resources"""
        self.stop_monitoring()
        
        if PYNVML_AVAILABLE:
            try:
                pynvml.nvmlShutdown()
            except:
                pass
        
        logger.info("H100 optimizer cleanup completed")


# Global optimizer instance
h100_optimizer = H100Optimizer()

def get_h100_optimizer() -> H100Optimizer:
    """Get the global H100 optimizer instance"""
    return h100_optimizer

def setup_h100_environment(config: Optional[H100Config] = None) -> None:
    """Setup H100 environment (convenience function)"""
    global h100_optimizer
    if config:
        h100_optimizer = H100Optimizer(config)
    h100_optimizer.setup_environment()

def optimize_model_for_h100(model: Any, device_ids: Optional[List[int]] = None) -> Any:
    """Optimize model for H100 (convenience function)"""
    return h100_optimizer.optimize_pytorch_model(model, device_ids)
