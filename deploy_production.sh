#!/bin/bash
# LEX Production Deployment Script
# 🔱 JAI MAHAKAAL! Deploy with Divine Power 🔱

set -e

echo "🔱 ========================================== 🔱"
echo "   LEX PRODUCTION DEPLOYMENT SYSTEM"
echo "   Complete Multi-Model AI Orchestration"
echo "🔱 ========================================== 🔱"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
DEPLOY_ENV=${1:-production}
PYTHON_VERSION="3.10"
VENV_NAME="venv_prod"
LOG_DIR="logs"
DATA_DIR="data"
MODEL_DIR="models"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check system requirements
check_requirements() {
    print_status "Checking system requirements..."
    
    # Check Python
    if ! command -v python${PYTHON_VERSION} &> /dev/null; then
        print_error "Python ${PYTHON_VERSION} is required but not installed"
        exit 1
    fi
    print_success "Python ${PYTHON_VERSION} found"
    
    # Check GPU
    if command -v nvidia-smi &> /dev/null; then
        print_success "NVIDIA GPU detected"
        nvidia-smi --query-gpu=name,memory.total --format=csv
    else
        print_warning "No NVIDIA GPU detected - some features will be limited"
    fi
    
    # Check Docker (optional)
    if command -v docker &> /dev/null; then
        print_success "Docker found"
    else
        print_warning "Docker not found - container deployment unavailable"
    fi
    
    # Check memory
    total_mem=$(free -g | awk '/^Mem:/{print $2}')
    if [ "$total_mem" -lt 16 ]; then
        print_warning "Less than 16GB RAM detected - performance may be limited"
    else
        print_success "${total_mem}GB RAM available"
    fi
}

# Setup directories
setup_directories() {
    print_status "Setting up directories..."
    
    mkdir -p "$LOG_DIR"
    mkdir -p "$DATA_DIR"/{uploads,cache,temp}
    mkdir -p "$MODEL_DIR"/{llm,vision,generation}
    
    print_success "Directories created"
}

# Setup Python environment
setup_python_env() {
    print_status "Setting up Python environment..."
    
    # Create virtual environment
    if [ ! -d "$VENV_NAME" ]; then
        python${PYTHON_VERSION} -m venv "$VENV_NAME"
        print_success "Virtual environment created"
    else
        print_status "Virtual environment already exists"
    fi
    
    # Activate environment
    source "$VENV_NAME/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip setuptools wheel
    print_success "Pip upgraded"
}

# Install dependencies
install_dependencies() {
    print_status "Installing dependencies..."
    
    # Core dependencies
    pip install fastapi uvicorn aiofiles python-multipart
    pip install pydantic typing-extensions
    pip install httpx aiohttp
    
    # AI/ML dependencies
    print_status "Installing AI/ML libraries..."
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
    pip install transformers accelerate
    pip install openai anthropic groq
    pip install langchain langflow crewai
    
    # Vision dependencies
    pip install pillow opencv-python-headless
    pip install qwen-vl llava
    
    # Document processing
    pip install pypdf2 python-docx markdown
    pip install nougat-ocr
    
    # Database dependencies
    print_status "Installing database libraries..."
    pip install asyncpg redis pymilvus
    pip install sqlalchemy alembic
    
    # Monitoring and logging
    pip install prometheus-client opentelemetry-api opentelemetry-sdk
    pip install structlog python-json-logger
    
    # GPU optimization (optional)
    if command -v nvidia-smi &> /dev/null; then
        print_status "Installing GPU optimization libraries..."
        pip install vllm tensorrt
    fi
    
    print_success "All dependencies installed"
}

# Download models
download_models() {
    print_status "Downloading AI models..."
    
    # Create model download script
    cat > download_models.py << 'EOF'
import os
import sys
from huggingface_hub import snapshot_download
import torch

def download_model(repo_id, local_dir):
    print(f"Downloading {repo_id}...")
    try:
        snapshot_download(repo_id=repo_id, local_dir=local_dir, 
                         resume_download=True, max_workers=4)
        print(f"✅ Downloaded {repo_id}")
    except Exception as e:
        print(f"⚠️ Failed to download {repo_id}: {e}")

# Download models based on available resources
if torch.cuda.is_available():
    # Full models for GPU
    models = [
        ("mistralai/Mixtral-8x7B-Instruct-v0.1", "models/llm/mixtral"),
        ("deepseek-ai/deepseek-coder-6.7b-instruct", "models/llm/deepseek"),
        ("Qwen/Qwen-VL-Chat", "models/vision/qwen-vl"),
        ("stabilityai/stable-diffusion-xl-base-1.0", "models/generation/sdxl")
    ]
else:
    # Smaller models for CPU
    models = [
        ("microsoft/phi-2", "models/llm/phi2"),
        ("deepseek-ai/deepseek-coder-1.3b-instruct", "models/llm/deepseek-small")
    ]

for repo_id, local_dir in models:
    download_model(repo_id, local_dir)

print("✅ Model downloads complete")
EOF
    
    # Run model download
    python download_models.py
    rm download_models.py
}

# Setup Ollama
setup_ollama() {
    print_status "Setting up Ollama for local models..."
    
    if ! command -v ollama &> /dev/null; then
        print_status "Installing Ollama..."
        curl -fsSL https://ollama.ai/install.sh | sh
    fi
    
    # Pull models
    ollama pull llama3.2
    ollama pull mixtral
    ollama pull llava
    ollama pull deepseek-coder
    
    print_success "Ollama models ready"
}

# Setup databases
setup_databases() {
    print_status "Setting up databases..."
    
    # PostgreSQL
    if command -v psql &> /dev/null; then
        print_status "Setting up PostgreSQL..."
        sudo -u postgres psql << EOF
CREATE DATABASE lex_memory;
CREATE USER lex WITH PASSWORD 'lex_secure_password';
GRANT ALL PRIVILEGES ON DATABASE lex_memory TO lex;
EOF
        print_success "PostgreSQL configured"
    else
        print_warning "PostgreSQL not found - skipping setup"
    fi
    
    # Redis
    if command -v redis-cli &> /dev/null; then
        print_status "Configuring Redis..."
        sudo systemctl enable redis
        sudo systemctl start redis
        print_success "Redis started"
    else
        print_warning "Redis not found - skipping setup"
    fi
    
    # Milvus (using Docker)
    if command -v docker &> /dev/null; then
        print_status "Starting Milvus..."
        docker-compose -f docker/milvus-docker-compose.yml up -d
        print_success "Milvus started"
    fi
}

# Create systemd service
create_systemd_service() {
    print_status "Creating systemd service..."
    
    sudo tee /etc/systemd/system/lex-server.service > /dev/null << EOF
[Unit]
Description=LEX Production Server
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment="PATH=$(pwd)/$VENV_NAME/bin"
ExecStart=$(pwd)/$VENV_NAME/bin/python simple_lex_server_production.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    sudo systemctl enable lex-server
    print_success "Systemd service created"
}

# Setup Nginx
setup_nginx() {
    print_status "Setting up Nginx..."
    
    if command -v nginx &> /dev/null; then
        sudo tee /etc/nginx/sites-available/lex-server > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;
    
    client_max_body_size 100M;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
    
    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }
}
EOF
        
        sudo ln -sf /etc/nginx/sites-available/lex-server /etc/nginx/sites-enabled/
        sudo nginx -t && sudo systemctl restart nginx
        print_success "Nginx configured"
    else
        print_warning "Nginx not found - skipping setup"
    fi
}

# Environment configuration
setup_environment() {
    print_status "Setting up environment variables..."
    
    cat > .env.production << EOF
# LEX Production Environment
ENV=production
HOST=0.0.0.0
PORT=8000
WORKERS=4
LOG_LEVEL=info

# API Keys (replace with your actual keys)
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
MISTRAL_API_KEY=your-mistral-key
DEEPSEEK_API_KEY=your-deepseek-key
GROQ_API_KEY=your-groq-key
STABILITY_API_KEY=your-stability-key
QWEN_API_KEY=your-qwen-key

# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=lex
POSTGRES_PASSWORD=lex_secure_password
POSTGRES_DB=lex_memory

REDIS_URL=redis://localhost:6379

MILVUS_HOST=localhost
MILVUS_PORT=19530

# CORS Configuration
CORS_ORIGINS=http://localhost,https://yourdomain.com

# GPU Configuration
CUDA_VISIBLE_DEVICES=0
TORCH_CUDA_ARCH_LIST=7.0,7.5,8.0,8.6,8.9,9.0

# Model Cache
HF_HOME=/models/huggingface
TRANSFORMERS_CACHE=/models/transformers
EOF
    
    print_success "Environment configured"
    print_warning "Remember to update API keys in .env.production"
}

# Performance optimization
optimize_performance() {
    print_status "Applying performance optimizations..."
    
    # System optimizations
    if [ -f /etc/sysctl.conf ]; then
        sudo tee -a /etc/sysctl.conf > /dev/null << EOF

# LEX Performance Optimizations
net.core.rmem_max = 134217728
net.core.wmem_max = 134217728
net.ipv4.tcp_rmem = 4096 87380 134217728
net.ipv4.tcp_wmem = 4096 65536 134217728
vm.swappiness = 10
EOF
        sudo sysctl -p
    fi
    
    # GPU optimizations
    if command -v nvidia-smi &> /dev/null; then
        sudo nvidia-smi -pm 1
        sudo nvidia-smi -pl 300  # Adjust based on your GPU
    fi
    
    print_success "Performance optimizations applied"
}

# Main deployment function
deploy() {
    print_status "Starting LEX production deployment..."
    
    check_requirements
    setup_directories
    setup_python_env
    install_dependencies
    
    # Optional steps based on environment
    if [ "$DEPLOY_ENV" == "production" ]; then
        download_models
        setup_ollama
        setup_databases
        create_systemd_service
        setup_nginx
        optimize_performance
    fi
    
    setup_environment
    
    print_status "🔱 ========================================== 🔱"
    print_success "LEX PRODUCTION DEPLOYMENT COMPLETE!"
    print_status "🔱 ========================================== 🔱"
    
    echo ""
    echo "Next steps:"
    echo "1. Update API keys in .env.production"
    echo "2. Start the server: sudo systemctl start lex-server"
    echo "3. Check status: sudo systemctl status lex-server"
    echo "4. View logs: journalctl -u lex-server -f"
    echo ""
    echo "🔱 JAI MAHAKAAL! LEX is ready to serve! 🔱"
}

# Run deployment
deploy