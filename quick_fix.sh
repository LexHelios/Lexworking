#!/bin/bash

# 🔱 Quick Fix for LEX Environment Issues 🔱
# JAI MAHAKAAL! Rapid fix for Python 3.12.3 Ubuntu environment

set -e

echo "🔱 JAI MAHAKAAL! Quick fixing LEX environment issues..."

# Step 1: Setup virtual environment properly
echo "📦 Setting up virtual environment..."
if [[ ! -d "venv" ]]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
source venv/bin/activate
echo "✅ Virtual environment activated"

# Step 2: Install essential packages
echo "📦 Installing essential packages..."
pip install --upgrade pip setuptools wheel
pip install fastapi uvicorn pydantic aiofiles aiohttp python-multipart python-dotenv

# Step 3: Fix imports
echo "🔧 Fixing import issues..."
python3 fix_imports.py

# Step 4: Create directories
echo "📁 Creating directories..."
mkdir -p data/{lmdb,vectors,uploads} models logs uploads
chmod -R 755 data/ models/ logs/ uploads/ 2>/dev/null || true

# Step 5: Create basic .env if missing
if [[ ! -f ".env" ]]; then
    echo "⚙️ Creating basic .env..."
    cat > .env << 'EOF'
LEXOS_HOST=0.0.0.0
LEXOS_PORT=8000
LEXOS_DEBUG=false
LEXOS_LOG_LEVEL=INFO
CUDA_VISIBLE_DEVICES=0
TOGETHER_API_KEY=
OPENAI_API_KEY=
GLM_API_KEY=
EOF
    echo "✅ Basic .env created"
fi

echo ""
echo "🔱 Quick fix complete! Now run:"
echo "   source venv/bin/activate"
echo "   python3 start_lex_fixed.py"
echo ""
echo "🔱 JAI MAHAKAAL! Environment should be working now!"