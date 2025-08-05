#!/bin/bash

# LEX Production Local Deployment Script
# Simplified deployment for local production environment

set -e

echo "🔱 LEX Production Local Deployment Starting 🔱"
echo "================================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check Python version
print_status "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
print_success "Python $python_version detected"

# Create virtual environment if it doesn't exist
print_status "Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_success "Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install requirements
print_status "Installing Python dependencies..."
pip install -r requirements.txt

# Check if H100 requirements exist and install if GPU is available
if command -v nvidia-smi &> /dev/null; then
    print_status "GPU detected, installing GPU-specific dependencies..."
    if [ -f "requirements_h100.txt" ]; then
        pip install -r requirements_h100.txt
    fi
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p lex_vault/{changes,conversations,documents,embeddings,generated,index,knowledge,media,memories,predictions}
mkdir -p logs
mkdir -p data
mkdir -p models
mkdir -p cache

# Set up environment
print_status "Setting up environment..."
if [ ! -f ".env" ]; then
    cp .env.production .env
    print_success "Environment file created from production template"
fi

# Install additional production dependencies
print_status "Installing production server dependencies..."
pip install gunicorn uvloop httptools

# Start Redis if not running (check if redis is installed)
if command -v redis-cli &> /dev/null; then
    if ! redis-cli ping > /dev/null 2>&1; then
        print_status "Starting Redis server..."
        redis-server --daemonize yes
        sleep 2
    fi
    print_success "Redis is running"
else
    print_error "Redis is not installed. Please install Redis for caching support."
fi

# Run database migrations if needed
print_status "Setting up database..."
python -c "import sqlite3; conn = sqlite3.connect('lex_data.db'); conn.close()"

# Start the production server
print_status "Starting LEX production server..."
export PYTHONPATH=$PWD:$PYTHONPATH

# Check if we should use production_server.py or simple_lex_server.py
if [ -f "production_server.py" ]; then
    SERVER_FILE="production_server.py"
elif [ -f "simple_lex_server.py" ]; then
    SERVER_FILE="simple_lex_server.py"
else
    print_error "No suitable server file found!"
    exit 1
fi

print_success "Using server file: $SERVER_FILE"

# Start with gunicorn for production
print_status "Starting LEX with Gunicorn..."
gunicorn ${SERVER_FILE%%.py}:app \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --timeout 120 \
    --keep-alive 5 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --log-level info \
    --daemon

# Wait for server to start
print_status "Waiting for server to start..."
sleep 5

# Check if server is running
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_success "LEX server is running!"
    
    echo ""
    echo "🔱 LEX PRODUCTION DEPLOYMENT COMPLETE 🔱"
    echo "================================================================"
    echo "🌐 Access Points:"
    echo "   Main Interface:    http://localhost:8000"
    echo "   API Documentation: http://localhost:8000/docs"
    echo "   Health Check:      http://localhost:8000/health"
    echo ""
    echo "📋 Next Steps:"
    echo "   1. Add your API keys to .env file"
    echo "   2. Configure your firewall for port 8000"
    echo "   3. Set up SSL/TLS with a reverse proxy (nginx/caddy)"
    echo "   4. Monitor logs in logs/ directory"
    echo ""
    echo "To stop the server: pkill -f gunicorn"
    echo "================================================================"
else
    print_error "Server failed to start. Check logs/error.log for details."
    exit 1
fi