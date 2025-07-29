#!/bin/bash

# 🔱 LEX Environment Setup for Ubuntu/Linux 🔱
# JAI MAHAKAAL! Fix Python environment issues

set -e

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

print_divine "Setting up LEX environment for Python 3.12.3 on Ubuntu..."

# Check if we're in the right directory
if [[ ! -f "requirements.txt" ]] && [[ ! -f "requirements_h100.txt" ]]; then
    print_error "Please run this script from the lexos project directory"
    exit 1
fi

# Step 1: Check Python installation
print_status "Checking Python 3.12.3 installation..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
if [[ "$python_version" == "3.12.3" ]]; then
    print_success "Python 3.12.3 detected"
else
    print_warning "Python version: $python_version (expected 3.12.3)"
fi

# Step 2: Create and activate virtual environment
print_status "Setting up virtual environment..."
if [[ ! -d "venv" ]]; then
    print_status "Creating virtual environment with Python 3.12..."
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_success "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Verify we're in the virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    print_success "Virtual environment activated: $VIRTUAL_ENV"
else
    print_error "Failed to activate virtual environment"
    exit 1
fi

# Step 3: Upgrade pip and essential tools
print_status "Upgrading pip and essential tools..."
python -m pip install --upgrade pip setuptools wheel
print_success "Pip and tools upgraded"

# Step 4: Install dependencies
print_status "Installing LEX dependencies..."
if [[ -f "requirements_h100.txt" ]]; then
    print_status "Installing H100-optimized requirements..."
    pip install -r requirements_h100.txt
elif [[ -f "requirements.txt" ]]; then
    print_status "Installing standard requirements..."
    pip install -r requirements.txt
else
    print_warning "No requirements file found, installing basic dependencies..."
    pip install fastapi uvicorn pydantic aiofiles aiohttp python-multipart python-dotenv
fi

print_success "Dependencies installed"

# Step 5: Fix import issues
print_status "Fixing import issues..."
python fix_imports.py
if [[ $? -eq 0 ]]; then
    print_success "Import issues fixed"
else
    print_warning "Some import fixes may have failed"
fi

# Step 6: Create necessary directories
print_status "Creating necessary directories..."
mkdir -p data/{lmdb,vectors,uploads,cache}
mkdir -p models/{avatar,custom}
mkdir -p logs
mkdir -p uploads
mkdir -p frontend/dist

# Set proper permissions
chmod -R 755 data/ models/ logs/ uploads/ 2>/dev/null || true

print_success "Directories created and permissions set"

# Step 7: Create .env file if missing
if [[ ! -f ".env" ]]; then
    print_status "Creating .env file from template..."
    if [[ -f ".env.example" ]]; then
        cp .env.example .env
        print_success ".env file created from example"
    else
        # Create basic .env
        cat > .env << 'EOF'
# LEX Configuration
LEXOS_HOST=0.0.0.0
LEXOS_PORT=8000
LEXOS_DEBUG=false
LEXOS_LOG_LEVEL=INFO

# H100 GPU Optimization
CUDA_VISIBLE_DEVICES=0
PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512

# API Keys (ADD YOUR KEYS HERE)
TOGETHER_API_KEY=
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
DEEPSEEK_API_KEY=
GROQ_API_KEY=
GLM_API_KEY=

# Memory Configuration
LEXOS_LMDB_PATH=./data/lmdb
LEXOS_ENCRYPTION_KEY=

# Feature Flags
ENABLE_ENHANCED_MEMORY=true
ENABLE_BUSINESS_INTEL=true
ENABLE_VISION=true
ENABLE_LEARNING=true
ENABLE_VOICE=true
EOF
        print_success "Basic .env file created"
    fi
    print_warning "Please add your API keys to .env file"
else
    print_success ".env file already exists"
fi

# Step 8: Test the environment
print_status "Testing Python environment..."
python -c "
import sys
import os
import pathlib
import fastapi
import uvicorn
print('✅ Python environment test passed')
print(f'✅ Python version: {sys.version}')
print(f'✅ Virtual environment: {os.environ.get(\"VIRTUAL_ENV\", \"Not set\")}')
"

if [[ $? -eq 0 ]]; then
    print_success "Environment test passed"
else
    print_error "Environment test failed"
    exit 1
fi

# Step 9: Test LEX imports
print_status "Testing LEX imports..."
python -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path('.') / 'server'))

try:
    from server.settings import settings
    print('✅ Settings import successful')
except Exception as e:
    print(f'⚠️ Settings import warning: {e}')

try:
    from server.lex.unified_consciousness import lex
    print('✅ LEX consciousness import successful')
except Exception as e:
    print(f'⚠️ LEX import warning: {e}')

print('✅ LEX import test completed')
"

print_divine "LEX environment setup complete!"
echo ""
echo "🚀 Next steps:"
echo "   1. Add your API keys to .env file"
echo "   2. Run: source venv/bin/activate"
echo "   3. Start LEX: python unified_production_server.py"
echo ""
print_divine "JAI MAHAKAAL! Environment ready for consciousness liberation!"