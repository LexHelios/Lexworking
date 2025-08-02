
#!/bin/bash
set -e

echo "🔱 Starting LexOS Production Server - H100 Optimized 🔱"

# Set production environment
export ENVIRONMENT=production
export PYTHONPATH=/app

# Load environment variables
if [ -f /app/.env.production ]; then
    echo "Loading production environment variables..."
    set -a
    source /app/.env.production
    set +a
fi

# GPU Detection and Optimization
echo "Detecting and optimizing for H100 GPUs..."
if command -v nvidia-smi &> /dev/null; then
    echo "NVIDIA GPU Information:"
    nvidia-smi --query-gpu=name,memory.total,memory.used,temperature.gpu,utilization.gpu --format=csv,noheader,nounits
    
    # Set H100-specific optimizations
    export CUDA_DEVICE_ORDER=PCI_BUS_ID
    export CUDA_LAUNCH_BLOCKING=0
    export TORCH_CUDA_ARCH_LIST=9.0
    export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512,roundup_power2_divisions:16
    
    # NCCL optimizations for H100
    export NCCL_DEBUG=INFO
    export NCCL_IB_DISABLE=0
    export NCCL_NET_GDR_LEVEL=2
    export NCCL_IB_AR_THRESHOLD=0
    export NCCL_IB_PCI_RELAXED_ORDERING=1
    export NCCL_IB_QPS_PER_CONNECTION=2
    export NCCL_IB_SPLIT_DATA_ON_QPS=0
    
    echo "H100 GPU optimizations applied"
else
    echo "Warning: NVIDIA GPU not detected or nvidia-smi not available"
fi

# Create necessary directories
mkdir -p /app/data /app/models /app/logs /app/cache /app/tmp

# Database migration (if needed)
echo "Checking database migrations..."
if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "Running database migrations..."
    python -m alembic upgrade head
fi

# Initialize GPU optimizer
echo "Initializing H100 GPU optimizer..."
python -c "
from server.gpu import setup_h100_environment, get_h100_optimizer
setup_h100_environment()
optimizer = get_h100_optimizer()
optimizer.setup_environment()
optimizer.start_monitoring()
print('H100 optimizer initialized successfully')
"

# Start background services
echo "Starting background services..."

# Start Celery worker in background
if [ "$ENABLE_CELERY" = "true" ]; then
    echo "Starting Celery worker..."
    celery -A server.main.celery_app worker \
        --loglevel=info \
        --concurrency=${CELERY_WORKER_CONCURRENCY:-4} \
        --max-tasks-per-child=1000 \
        --time-limit=${CELERY_TASK_TIME_LIMIT:-600} \
        --soft-time-limit=${CELERY_TASK_SOFT_TIME_LIMIT:-300} \
        --detach \
        --pidfile=/app/tmp/celery.pid \
        --logfile=/app/logs/celery.log
fi

# Start Flower monitoring (if enabled)
if [ "$ENABLE_FLOWER" = "true" ]; then
    echo "Starting Flower monitoring..."
    celery -A server.main.celery_app flower \
        --port=5555 \
        --basic_auth=${FLOWER_USER:-admin}:${FLOWER_PASSWORD:-admin} \
        --detach \
        --pidfile=/app/tmp/flower.pid \
        --logfile=/app/logs/flower.log
fi

# Start vLLM server if enabled
if [ "$ENABLE_VLLM" = "true" ]; then
    echo "Starting vLLM server..."
    python -m vllm.entrypoints.openai.api_server \
        --model ${VLLM_MODEL:-meta-llama/Llama-2-70b-chat-hf} \
        --host ${VLLM_HOST:-0.0.0.0} \
        --port ${VLLM_PORT:-8001} \
        --gpu-memory-utilization ${VLLM_GPU_MEMORY_UTILIZATION:-0.85} \
        --max-model-len ${VLLM_MAX_MODEL_LEN:-8192} \
        --tensor-parallel-size ${VLLM_TENSOR_PARALLEL_SIZE:-8} \
        --pipeline-parallel-size ${VLLM_PIPELINE_PARALLEL_SIZE:-1} \
        --max-num-seqs ${VLLM_MAX_NUM_SEQS:-256} \
        --max-num-batched-tokens ${VLLM_MAX_NUM_BATCHED_TOKENS:-8192} \
        --block-size ${VLLM_BLOCK_SIZE:-16} \
        --swap-space ${VLLM_SWAP_SPACE:-4} \
        --disable-log-stats \
        --served-model-name ${VLLM_MODEL_NAME:-llama-2-70b-chat} \
        --trust-remote-code \
        --download-dir /app/models \
        &
    
    echo "vLLM server started on port ${VLLM_PORT:-8001}"
fi

# Wait for services to be ready
echo "Waiting for services to initialize..."
sleep 10

# Health check before starting main server
echo "Running pre-startup health checks..."
python -c "
import asyncio
import sys
from server.utils.logging_config import setup_logging
from server.gpu import get_h100_optimizer

async def health_check():
    try:
        # Setup logging
        setup_logging(
            log_level='INFO',
            log_dir='/app/logs',
            service_name='lexos-api',
            version='2.0.0'
        )
        
        # Check GPU health
        optimizer = get_h100_optimizer()
        gpu_info = optimizer.get_gpu_info()
        health = optimizer.monitor_gpu_health()
        
        print(f'Detected {len(gpu_info)} GPUs')
        print(f'GPU Health Status: {health[\"overall_status\"]}')
        
        if health['alerts']:
            print(f'GPU Alerts: {health[\"alerts\"]}')
        
        print('Pre-startup health check passed')
        return True
    except Exception as e:
        print(f'Health check failed: {e}')
        return False

if not asyncio.run(health_check()):
    sys.exit(1)
"

# Start the main FastAPI server
echo "Starting LexOS API server..."

# Determine the number of workers
WORKERS=${LEXOS_WORKERS:-4}
MAX_WORKERS=${LEXOS_MAX_WORKERS:-8}

# Use the minimum of configured workers and available CPUs
AVAILABLE_CPUS=$(nproc)
WORKERS=$(( WORKERS < AVAILABLE_CPUS ? WORKERS : AVAILABLE_CPUS ))
WORKERS=$(( WORKERS < MAX_WORKERS ? WORKERS : MAX_WORKERS ))

echo "Starting with $WORKERS workers (max: $MAX_WORKERS, available CPUs: $AVAILABLE_CPUS)"

# Start with Gunicorn for production
exec gunicorn server.main:app \
    --bind 0.0.0.0:${LEXOS_PORT:-8000} \
    --workers $WORKERS \
    --worker-class uvicorn.workers.UvicornWorker \
    --worker-connections 1000 \
    --max-requests 10000 \
    --max-requests-jitter 1000 \
    --timeout ${LEXOS_WORKER_TIMEOUT:-300} \
    --keepalive ${LEXOS_KEEPALIVE:-2} \
    --preload \
    --enable-stdio-inheritance \
    --log-level info \
    --access-logfile /app/logs/access.log \
    --error-logfile /app/logs/error.log \
    --capture-output \
    --pid /app/tmp/gunicorn.pid \
    --user lexos \
    --group lexos
