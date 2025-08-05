#!/bin/bash

# Simple production start script for LEX
set -e

echo "🔱 Starting LEX Production Server (Simplified) 🔱"
echo "================================================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install minimal requirements
echo "Installing minimal requirements..."
pip install --upgrade pip
pip install -r requirements_minimal.txt

# Create necessary directories
mkdir -p logs lex_vault/memories

# Check for .env file
if [ ! -f ".env" ]; then
    cp .env.production .env
    echo "Created .env file from template"
fi

# Find the appropriate server file
if [ -f "simple_lex_server.py" ]; then
    SERVER_FILE="simple_lex_server.py"
elif [ -f "production_server.py" ]; then
    SERVER_FILE="production_server.py"
elif [ -f "server/main.py" ]; then
    SERVER_FILE="server.main"
else
    echo "No suitable server file found!"
    exit 1
fi

echo "Starting server with: $SERVER_FILE"

# Export Python path
export PYTHONPATH=$PWD:$PYTHONPATH

# Start with uvicorn directly (simpler than gunicorn)
uvicorn ${SERVER_FILE%%.py}:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 2 \
    --log-level info \
    --access-log

echo "Server started on http://localhost:8000"