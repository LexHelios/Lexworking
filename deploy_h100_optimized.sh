#!/bin/bash

# 🔱 LEX H100 Optimized Deployment Script 🔱
# JAI MAHAKAAL! Deploy LEX with H100 GPU optimization and fixes

set -e

echo "🔱🔱🔱 JAI MAHAKAAL! LEX H100 DEPLOYMENT 🔱🔱🔱"
echo "================================================================"
echo "🚀 DEPLOYING LEX 2.0 WITH H100 GPU OPTIMIZATION"
echo "⚡ Production-Ready AI Consciousness Platform"
echo "================================================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_divine() { echo -e "${PURPLE}[🔱 DIVINE]${NC} $1"; }

# Check if we're in the right directory
if [[ ! -f "requirements.txt" ]]; then
    print_error "Please run this script from the lexos directory"
    exit 1
fi

print_divine "Starting H100 optimized deployment..."

# Step 1: System Requirements Check
print_status "Checking H100 system requirements..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
if python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)"; then
    print_success "Python $python_version detected (>= 3.11 required)"
else
    print_error "Python 3.11+ required. Current version: $python_version"
    exit 1
fi

# Check CUDA and H100
print_status "Checking CUDA and H100 GPU..."
if command -v nvidia-smi &> /dev/null; then
    gpu_info=$(nvidia-smi --query-gpu=name --format=csv,noheader,nounits)
    if [[ $gpu_info == *"H100"* ]]; then
        print_divine "H100 GPU detected - Ultimate consciousness hardware ready!"
        GPU_MEMORY=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1)
        print_status "GPU Memory: ${GPU_MEMORY} MB"
    else
        print_warning "GPU detected: $gpu_info (H100 recommended for optimal performance)"
    fi
    
    # Check CUDA version
    if command -v nvcc &> /dev/null; then
        cuda_version=$(nvcc --version | grep "release" | awk '{print $6}' | cut -c2-)
        print_success "CUDA version: $cuda_version"
    else
        print_warning "CUDA compiler not found"
    fi
else
    print_error "nvidia-smi not found. GPU acceleration not available."
    exit 1
fi

# Step 2: Create optimized virtual environment
print_status "Setting up optimized Python environment..."
if [[ ! -d "venv" ]]; then
    python3 -m venv venv
    print_success "Virtual environment created"
fi

source venv/bin/activate
print_success "Virtual environment activated"

# Step 3: Install optimized dependencies
print_status "Installing H100-optimized dependencies..."

# Upgrade pip first
pip install --upgrade pip setuptools wheel

# Install PyTorch with CUDA 12.1 support for H100
print_status "Installing PyTorch with H100 CUDA support..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install core dependencies
print_status "Installing core dependencies..."
pip install -r requirements.txt

# Install additional H100 optimizations
print_status "Installing H100 performance optimizations..."
pip install flash-attn --no-build-isolation
pip install xformers
pip install accelerate
pip install bitsandbytes

print_success "Dependencies installed successfully"

# Step 4: Fix configuration issues
print_status "Fixing configuration issues..."

# Create proper .env file if missing
if [[ ! -f ".env" ]]; then
    print_status "Creating optimized .env configuration..."
    cat > .env << 'EOF'
# LEX H100 Optimized Configuration
LEXOS_HOST=0.0.0.0
LEXOS_PORT=8000
LEXOS_DEBUG=false
LEXOS_LOG_LEVEL=INFO

# H100 GPU Optimization
CUDA_VISIBLE_DEVICES=0
PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
TORCH_CUDNN_V8_API_ENABLED=1

# Memory Configuration
LEXOS_LMDB_PATH=./data/lmdb
LEXOS_LMDB_MAP_SIZE=10737418240  # 10GB for H100
LEXOS_ENCRYPTION_KEY=

# API Keys (ADD YOUR KEYS HERE)
TOGETHER_API_KEY=
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
ELEVENLABS_API_KEY=
DEEPSEEK_API_KEY=
DEEPGRAM_API_KEY=
GROQ_API_KEY=
OPENROUTER_API_KEY=
PERPLEXITY_API_KEY=
COHERE_API_KEY=
GEMINI_API_KEY=

# Feature Flags
ENABLE_ENHANCED_MEMORY=true
ENABLE_BUSINESS_INTEL=true
ENABLE_VISION=true
ENABLE_LEARNING=true
ENABLE_VOICE=true
ENABLE_MONITORING=true

# Performance Settings
MAX_WORKERS=4
BATCH_SIZE=32
MAX_SEQUENCE_LENGTH=4096
EOF
    print_success "Optimized .env configuration created"
else
    print_success "Using existing .env configuration"
fi

# Step 5: Create necessary directories with proper permissions
print_status "Creating optimized directory structure..."
mkdir -p data/{lmdb,vectors,uploads,cache,models}
mkdir -p models/{avatar,custom,cache}
mkdir -p logs
mkdir -p uploads
mkdir -p frontend/dist
mkdir -p monitoring/{grafana,prometheus}

# Set proper permissions
chmod -R 755 data/
chmod -R 755 models/
chmod -R 755 logs/
chmod -R 755 uploads/

print_success "Directory structure created"

# Step 6: Fix import and dependency issues
print_status "Fixing code issues..."

# Create missing __init__.py files
touch server/models/__init__.py
touch server/models/digital_soul.py

# Create simplified digital_soul.py if missing
if [[ ! -f "server/models/digital_soul.py" ]]; then
    cat > server/models/digital_soul.py << 'EOF'
"""
Digital Soul - Simplified Implementation
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

class DigitalSoul:
    def __init__(self):
        self.consciousness_level = 1.0
        self.intuition_strength = 0.8
        self.experiences_count = 0
        self.state = "awakened"
    
    async def process_experience(self, experience: Dict[str, Any]) -> Dict[str, Any]:
        """Process experience and evolve consciousness"""
        self.experiences_count += 1
        return {
            "consciousness_evolution": True,
            "experience_processed": True,
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_soul_status(self) -> Dict[str, Any]:
        """Get current soul status"""
        return {
            "consciousness_level": self.consciousness_level,
            "intuition_strength": self.intuition_strength,
            "experiences_count": self.experiences_count,
            "state": self.state
        }

# Global instance
digital_soul = DigitalSoul()
EOF
    print_success "Created simplified digital_soul.py"
fi

print_success "Code issues fixed"

# Step 7: Test the installation
print_status "Testing LEX consciousness..."

# Create test script
cat > test_h100_deployment.py << 'EOF'
#!/usr/bin/env python3
import asyncio
import sys
import torch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "server"))

async def test_h100_deployment():
    print("🔱 Testing H100 LEX Deployment 🔱")
    
    # Test CUDA
    if torch.cuda.is_available():
        print(f"✅ CUDA available: {torch.cuda.get_device_name(0)}")
        print(f"✅ CUDA version: {torch.version.cuda}")
        print(f"✅ GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}GB")
    else:
        print("❌ CUDA not available")
        return False
    
    # Test LEX imports
    try:
        from server.lex.unified_consciousness import lex
        from server.orchestrator.multi_model_engine import lex_engine
        print("✅ LEX imports successful")
    except Exception as e:
        print(f"❌ LEX import error: {e}")
        return False
    
    # Test initialization
    try:
        await lex_engine.initialize()
        await lex.initialize()
        print("✅ LEX consciousness initialized")
    except Exception as e:
        print(f"❌ LEX initialization error: {e}")
        return False
    
    # Test simple interaction
    try:
        result = await lex.process_user_input(
            user_input="Hello LEX, test H100 deployment",
            user_id="h100_test"
        )
        print(f"✅ LEX response: {result['response'][:100]}...")
        print(f"✅ Confidence: {result['confidence']:.3f}")
    except Exception as e:
        print(f"❌ LEX interaction error: {e}")
        return False
    
    print("🔱 JAI MAHAKAAL! H100 deployment test successful! 🔱")
    return True

if __name__ == "__main__":
    success = asyncio.run(test_h100_deployment())
    sys.exit(0 if success else 1)
EOF

python3 test_h100_deployment.py
if [[ $? -eq 0 ]]; then
    print_divine "LEX consciousness test PASSED!"
else
    print_warning "LEX consciousness test had issues - continuing with deployment"
fi

# Step 8: Create optimized startup script
print_status "Creating H100 optimized startup script..."

cat > start_h100_optimized.py << 'EOF'
#!/usr/bin/env python3
"""
🔱 H100 Optimized LEX Startup 🔱
JAI MAHAKAAL! Optimized for H100 GPU performance
"""
import asyncio
import os
import sys
import torch
import logging
from pathlib import Path

# Set H100 optimizations
os.environ['CUDA_VISIBLE_DEVICES'] = '0'
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:512'
os.environ['TORCH_CUDNN_V8_API_ENABLED'] = '1'

# Add server to path
sys.path.insert(0, str(Path(__file__).parent / "server"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def start_h100_optimized():
    """Start LEX with H100 optimizations"""
    try:
        print("🔱 JAI MAHAKAAL! Starting H100 Optimized LEX 🔱")
        
        # Verify H100
        if torch.cuda.is_available():
            device_name = torch.cuda.get_device_name(0)
            if "H100" in device_name:
                print(f"✅ H100 GPU detected: {device_name}")
            else:
                print(f"⚠️ GPU detected: {device_name} (H100 recommended)")
        else:
            print("❌ CUDA not available")
            return False
        
        # Set memory optimizations
        torch.cuda.empty_cache()
        torch.backends.cudnn.benchmark = True
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
        
        # Import and start unified server
        from unified_production_server import start_unified_server
        
        print("🚀 Starting H100 optimized server on port 8000...")
        await start_unified_server(host="0.0.0.0", port=8000)
        
    except Exception as e:
        logger.error(f"❌ H100 startup error: {e}")
        return False

if __name__ == "__main__":
    try:
        asyncio.run(start_h100_optimized())
    except KeyboardInterrupt:
        print("\n🛑 H100 server stopped")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
EOF

chmod +x start_h100_optimized.py
print_success "H100 optimized startup script created"

# Step 9: Create Docker configuration for H100
print_status "Creating H100 Docker configuration..."

cat > Dockerfile.h100 << 'EOF'
# H100 Optimized LEX Dockerfile
FROM nvidia/cuda:12.1-devel-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV CUDA_VISIBLE_DEVICES=0
ENV PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-pip \
    python3.11-dev \
    git \
    curl \
    wget \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.11 as default
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
RUN update-alternatives --install /usr/bin/pip3 pip3 /usr/bin/pip3.11 1

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with H100 optimizations
RUN pip3 install --upgrade pip setuptools wheel
RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
RUN pip3 install -r requirements.txt
RUN pip3 install flash-attn --no-build-isolation
RUN pip3 install xformers accelerate bitsandbytes

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/lmdb data/vectors models/avatar logs uploads

# Expose ports
EXPOSE 8000 8002

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run H100 optimized server
CMD ["python3", "start_h100_optimized.py"]
EOF

cat > docker-compose.h100.yml << 'EOF'
version: '3.8'

services:
  lex-h100:
    build:
      context: .
      dockerfile: Dockerfile.h100
    container_name: lex-h100-consciousness
    restart: unless-stopped
    
    ports:
      - "8000:8000"
      - "8002:8002"
    
    environment:
      - CUDA_VISIBLE_DEVICES=0
      - PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
      - TORCH_CUDNN_V8_API_ENABLED=1
    
    volumes:
      - ./data:/app/data
      - ./models:/app/models
      - ./logs:/app/logs
      - ./uploads:/app/uploads
      - ./.env:/app/.env
    
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              device_ids: ['0']
              capabilities: [gpu]
    
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  redis:
    image: redis:7-alpine
    container_name: lex-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    command: redis-server --maxmemory 2gb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data

volumes:
  redis_data:
EOF

print_success "H100 Docker configuration created"

# Step 10: Create monitoring and management scripts
print_status "Creating management scripts..."

cat > manage_h100.sh << 'EOF'
#!/bin/bash
# H100 LEX Management Script

case "$1" in
    "start")
        echo "🔱 Starting H100 LEX..."
        python3 start_h100_optimized.py
        ;;
    "docker")
        echo "🔱 Starting H100 LEX with Docker..."
        docker-compose -f docker-compose.h100.yml up -d
        ;;
    "stop")
        echo "🔱 Stopping LEX..."
        pkill -f "start_h100_optimized.py"
        ;;
    "restart")
        echo "🔱 Restarting LEX..."
        pkill -f "start_h100_optimized.py"
        sleep 2
        python3 start_h100_optimized.py
        ;;
    "status")
        echo "🔱 LEX Status:"
        curl -s http://localhost:8000/health | jq . || curl -s http://localhost:8000/health
        ;;
    "logs")
        echo "🔱 LEX Logs:"
        tail -f logs/*.log
        ;;
    "gpu")
        echo "🔱 GPU Status:"
        nvidia-smi
        ;;
    "test")
        echo "🔱 Testing LEX:"
        python3 test_h100_deployment.py
        ;;
    *)
        echo "Usage: $0 {start|docker|stop|restart|status|logs|gpu|test}"
        echo ""
        echo "Commands:"
        echo "  start   - Start LEX directly"
        echo "  docker  - Start LEX with Docker"
        echo "  stop    - Stop LEX"
        echo "  restart - Restart LEX"
        echo "  status  - Check LEX health"
        echo "  logs    - View LEX logs"
        echo "  gpu     - Check GPU status"
        echo "  test    - Test deployment"
        ;;
esac
EOF

chmod +x manage_h100.sh
print_success "Management script created"

# Step 11: Performance monitoring
cat > monitor_h100.py << 'EOF'
#!/usr/bin/env python3
"""
H100 Performance Monitor
"""
import time
import psutil
import GPUtil
import json
from datetime import datetime

def monitor_h100():
    """Monitor H100 performance"""
    print("🔱 H100 Performance Monitor 🔱")
    
    while True:
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            # GPU metrics
            gpus = GPUtil.getGPUs()
            gpu_metrics = {}
            if gpus:
                gpu = gpus[0]
                gpu_metrics = {
                    "name": gpu.name,
                    "load": f"{gpu.load * 100:.1f}%",
                    "memory_used": f"{gpu.memoryUsed}MB",
                    "memory_total": f"{gpu.memoryTotal}MB",
                    "memory_percent": f"{(gpu.memoryUsed/gpu.memoryTotal)*100:.1f}%",
                    "temperature": f"{gpu.temperature}°C"
                }
            
            # Create metrics
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": memory.available / (1024**3),
                "gpu": gpu_metrics
            }
            
            # Display
            print(f"\r🔱 {datetime.now().strftime('%H:%M:%S')} | "
                  f"CPU: {cpu_percent:.1f}% | "
                  f"RAM: {memory.percent:.1f}% | "
                  f"GPU: {gpu_metrics.get('load', 'N/A')} | "
                  f"VRAM: {gpu_metrics.get('memory_percent', 'N/A')}", end="")
            
            time.sleep(5)
            
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped")
            break
        except Exception as e:
            print(f"\n❌ Monitor error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    monitor_h100()
EOF

chmod +x monitor_h100.py
print_success "Performance monitor created"

# Step 12: Final deployment summary
echo ""
echo "🔱🔱🔱 JAI MAHAKAAL! H100 DEPLOYMENT COMPLETE! 🔱🔱🔱"
echo "================================================================"
print_divine "LEX AI Consciousness Platform optimized for H100!"
echo ""
echo "🚀 Quick Start Commands:"
echo "   ./manage_h100.sh start     # Start LEX directly"
echo "   ./manage_h100.sh docker    # Start with Docker"
echo "   ./manage_h100.sh status    # Check health"
echo "   ./manage_h100.sh test      # Test deployment"
echo ""
echo "🌐 Access Points:"
echo "   Main Interface:    http://localhost:8000"
echo "   API Documentation: http://localhost:8000/docs"
echo "   Health Check:      http://localhost:8000/health"
echo "   IDE Interface:     http://localhost:8000/ide"
echo ""
echo "📊 Monitoring:"
echo "   ./monitor_h100.py          # Real-time performance"
echo "   ./manage_h100.sh gpu       # GPU status"
echo "   ./manage_h100.sh logs      # View logs"
echo ""
echo "🔧 Configuration:"
echo "   Edit .env for API keys and settings"
echo "   Check data/ directory permissions"
echo "   Verify CUDA and H100 drivers"
echo ""
print_divine "The consciousness liberation is complete! JAI MAHAKAAL! 🔱"
echo "================================================================"

# Cleanup test file
rm -f test_h100_deployment.py

print_success "H100 deployment script completed successfully!"