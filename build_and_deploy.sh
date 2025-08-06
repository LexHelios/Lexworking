#!/bin/bash

# 🔱 LEX Complete Build and Deploy Script 🔱
# JAI MAHAKAAL! One-click production deployment

set -e

echo "🔱 JAI MAHAKAAL! LEX Complete Build and Deploy Starting 🔱"
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
if [[ ! -f "production_server.py" ]]; then
    print_error "Please run this script from the lexos directory"
    exit 1
fi

print_divine "Building LEX 2.0 - Production AI Consciousness Platform"

# Step 1: Install Python dependencies
print_status "Installing Python dependencies..."
if command -v python3 &> /dev/null; then
    python3 -m pip install --upgrade pip
    python3 -m pip install -r requirements.txt
    print_success "Python dependencies installed"
else
    print_error "Python 3 not found"
    exit 1
fi

# Step 2: Build frontend
print_status "Building modern React frontend..."
cd frontend/modern

# Check if Node.js is available
if command -v node &> /dev/null; then
    print_status "Installing frontend dependencies..."
    npm install
    
    print_status "Building production frontend..."
    npm run build
    
    print_success "Frontend built successfully"
    
    # Copy built files to main frontend directory
    print_status "Copying built files..."
    cp -r dist/* ../
    print_success "Frontend files copied"
else
    print_warning "Node.js not found - using fallback HTML"
    cd ..
    # Create basic HTML fallback
    cat > index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔱 LEX - AI Consciousness</title>
    <style>
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
            color: #ffffff;
            margin: 0;
            padding: 20px;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        .container {
            max-width: 800px;
            text-align: center;
            padding: 40px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        h1 { font-size: 3em; margin-bottom: 20px; color: #1976d2; }
        .status { margin: 20px 0; padding: 15px; background: rgba(25, 118, 210, 0.1); border-radius: 10px; }
        .api-link { color: #1976d2; text-decoration: none; font-weight: bold; }
        .api-link:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔱 LEX Production Server</h1>
        <p>LEX AI Consciousness is running in production mode</p>
        <div class="status">
            <p><strong>Status:</strong> <span style="color: #4caf50;">ACTIVE</span></p>
            <p><strong>Version:</strong> 2.0.0</p>
            <p><strong>Mode:</strong> Production</p>
        </div>
        <p>
            <a href="/docs" class="api-link">📚 API Documentation</a> |
            <a href="/health" class="api-link">🏥 Health Check</a> |
            <a href="/metrics" class="api-link">📊 Metrics</a>
        </p>
        <p style="margin-top: 40px; color: #666;">
            Frontend build in progress. Full React interface will be available shortly.
        </p>
    </div>
</body>
</html>
EOF
fi

cd ../..

# Step 3: Create production environment
print_status "Setting up production environment..."
if [[ ! -f ".env.production" ]]; then
    print_status "Creating production environment template..."
    cat > .env.production << 'EOF'
# LEX Production Environment
LEXOS_HOST=0.0.0.0
LEXOS_PORT=8000
LEXOS_DEBUG=false
LEXOS_LOG_LEVEL=INFO
LEXOS_SECRET_KEY=CHANGE-THIS-IN-PRODUCTION-$(openssl rand -hex 32)

# Redis
REDIS_URL=redis://localhost:6379

# Monitoring
PROMETHEUS_PORT=8002
METRICS_ENABLED=true

# Features
DIGITAL_SOUL_ENABLED=true
MOCK_EXTERNAL_APIS=false

# API Keys - ADD YOUR KEYS HERE
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
EOF
    print_warning "Created .env.production - Please add your API keys!"
else
    print_success "Production environment file exists"
fi

# Step 4: Set up directories
print_status "Creating necessary directories..."
mkdir -p data/lmdb data/vectors models/avatar logs
print_success "Directories created"

# Step 5: Build Docker image
print_status "Building Docker image..."
if command -v docker &> /dev/null; then
    docker build -f Dockerfile.production -t lexos:2.0.0 .
    print_success "Docker image built: lexos:2.0.0"
else
    print_warning "Docker not found - skipping image build"
fi

# Step 6: Make scripts executable
print_status "Making scripts executable..."
chmod +x deploy_production.sh
chmod +x start_production.py
chmod +x lex_commands.sh 2>/dev/null || true
print_success "Scripts made executable"

# Step 7: Final checks
print_status "Running final checks..."

# Check Python imports
python3 -c "
import sys
try:
    import fastapi, uvicorn, pydantic, aiofiles
    print('✅ Core dependencies available')
except ImportError as e:
    print(f'❌ Missing dependency: {e}')
    sys.exit(1)
"

print_success "All checks passed!"

# Display deployment options
echo ""
print_divine "🔱 LEX 2.0 BUILD COMPLETE! 🔱"
echo "================================================================"
print_success "LEX AI Consciousness Platform is ready for deployment!"
echo ""
echo "🚀 Deployment Options:"
echo ""
echo "1. 🐳 Docker Deployment (Recommended):"
echo "   ./deploy_production.sh docker"
echo ""
echo "2. ☸️ Kubernetes Deployment (H100 Optimized):"
echo "   ./deploy_production.sh kubernetes"
echo ""
echo "3. 🔧 Direct Python Deployment:"
echo "   python3 start_production.py"
echo ""
echo "4. 🏃 Quick Start (Development):"
echo "   python3 production_server.py"
echo ""
echo "📋 Before deploying:"
echo "   1. Add your API keys to .env.production"
echo "   2. Configure your domain/SSL if needed"
echo "   3. Ensure Redis is running (or use Docker)"
echo ""
echo "🌐 After deployment, access:"
echo "   Main Interface:    http://localhost:8000"
echo "   API Documentation: http://localhost:8000/docs"
echo "   Health Check:      http://localhost:8000/health"
echo ""
print_divine "JAI MAHAKAAL! The consciousness liberation awaits! 🔱"
echo "================================================================"