#!/bin/bash

# 🔱 Enhanced H100 LEX Management Script 🔱
# JAI MAHAKAAL! Complete management for H100 LEX deployment with GLM-4.5

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

# Check if we're in the right directory
if [[ ! -f "requirements_h100.txt" ]]; then
    print_error "Please run this script from the lexos directory"
    exit 1
fi

case "$1" in
    "start")
        print_divine "Starting Enhanced H100 LEX with GLM-4.5..."
        
        # Check if virtual environment exists
        if [[ ! -d "venv" ]]; then
            print_status "Creating virtual environment..."
            python3 -m venv venv
        fi
        
        # Activate virtual environment
        source venv/bin/activate
        
        # Check dependencies
        if ! python3 -c "import fastapi, torch" 2>/dev/null; then
            print_status "Installing dependencies..."
            pip install -r requirements_h100.txt
        fi
        
        # Set H100 optimizations
        export CUDA_VISIBLE_DEVICES=0
        export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:1024
        export TORCH_CUDNN_V8_API_ENABLED=1
        
        # Start enhanced server
        print_status "Starting enhanced LEX server..."
        python3 unified_production_server.py
        ;;
        
    "simple")
        print_divine "Starting Simple H100 LEX..."
        
        # Activate virtual environment if exists
        if [[ -d "venv" ]]; then
            source venv/bin/activate
        fi
        
        # Set H100 optimizations
        export CUDA_VISIBLE_DEVICES=0
        export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
        
        # Start simple server
        python3 simple_lex_server.py
        ;;
        
    "docker")
        print_divine "Starting H100 LEX with Docker..."
        
        # Check if Docker is available
        if ! command -v docker &> /dev/null; then
            print_error "Docker not found. Please install Docker first."
            exit 1
        fi
        
        # Build and start with Docker Compose
        if [[ -f "docker-compose.h100-enhanced.yml" ]]; then
            docker-compose -f docker-compose.h100-enhanced.yml up -d
        else
            print_warning "Docker compose file not found, using basic Docker..."
            docker build -f Dockerfile.h100 -t lex-h100:latest .
            docker run -d --gpus all -p 8000:8000 -p 8002:8002 --name lex-h100 lex-h100:latest
        fi
        
        print_success "LEX H100 Docker container started"
        ;;
        
    "stop")
        print_divine "Stopping LEX servers..."
        
        # Stop Python processes
        pkill -f "unified_production_server.py" || true
        pkill -f "simple_lex_server.py" || true
        pkill -f "production_server.py" || true
        
        # Stop Docker containers
        docker stop lex-h100 2>/dev/null || true
        docker-compose -f docker-compose.h100-enhanced.yml down 2>/dev/null || true
        
        print_success "LEX servers stopped"
        ;;
        
    "restart")
        print_divine "Restarting LEX servers..."
        $0 stop
        sleep 3
        $0 start
        ;;
        
    "status")
        print_divine "LEX H100 Status Check:"
        echo ""
        
        # Check server health
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            print_success "LEX server is running"
            curl -s http://localhost:8000/health | jq . 2>/dev/null || curl -s http://localhost:8000/health
        else
            print_warning "LEX server not responding on port 8000"
        fi
        
        echo ""
        
        # Check processes
        if pgrep -f "unified_production_server.py" > /dev/null; then
            print_success "Enhanced server process running"
        elif pgrep -f "simple_lex_server.py" > /dev/null; then
            print_success "Simple server process running"
        else
            print_warning "No LEX server processes found"
        fi
        
        # Check Docker
        if docker ps | grep -q lex-h100; then
            print_success "LEX Docker container running"
        fi
        ;;
        
    "health")
        print_divine "LEX Health Check:"
        
        # Test API endpoints
        echo "🌐 Testing API endpoints..."
        
        # Health endpoint
        if curl -s http://localhost:8000/health > /dev/null; then
            print_success "Health endpoint: OK"
        else
            print_error "Health endpoint: FAILED"
        fi
        
        # LEX endpoint
        if curl -s -X POST http://localhost:8000/api/v1/lex \
           -H "Content-Type: application/json" \
           -d '{"message":"Health check test","voice_mode":false}' > /dev/null; then
            print_success "LEX endpoint: OK"
        else
            print_error "LEX endpoint: FAILED"
        fi
        
        # Features endpoint
        if curl -s http://localhost:8000/api/v1/features > /dev/null; then
            print_success "Features endpoint: OK"
        else
            print_warning "Features endpoint: Not available"
        fi
        ;;
        
    "gpu")
        print_divine "H100 GPU Status:"
        
        if command -v nvidia-smi &> /dev/null; then
            nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu,temperature.gpu --format=csv,noheader,nounits
            echo ""
            nvidia-smi
        else
            print_error "nvidia-smi not found"
        fi
        ;;
        
    "logs")
        print_divine "LEX Logs:"
        
        # Show recent logs
        if [[ -f "unified_production.log" ]]; then
            echo "📄 Enhanced Server Logs:"
            tail -n 50 unified_production.log
        elif [[ -f "lex_backend.log" ]]; then
            echo "📄 Backend Logs:"
            tail -n 50 lex_backend.log
        elif [[ -d "logs" ]]; then
            echo "📄 Application Logs:"
            find logs -name "*.log" -exec tail -n 20 {} \;
        else
            print_warning "No log files found"
        fi
        ;;
        
    "test")
        print_divine "Running LEX H100 Tests..."
        
        # Activate virtual environment
        if [[ -d "venv" ]]; then
            source venv/bin/activate
        fi
        
        # Run basic tests
        echo "🧪 Basic functionality test..."
        if python3 test_simple.py; then
            print_success "Basic test passed"
        else
            print_error "Basic test failed"
        fi
        
        # Run GLM integration test
        echo "🧪 GLM-4.5 integration test..."
        if python3 test_glm_integration.py; then
            print_success "GLM-4.5 test passed"
        else
            print_warning "GLM-4.5 test failed (check API key)"
        fi
        
        # Run enhanced features test
        echo "🧪 Enhanced features test..."
        if python3 test_enhanced_features.py; then
            print_success "Enhanced features test passed"
        else
            print_warning "Enhanced features test had issues"
        fi
        
        # API connectivity test
        echo "🧪 API connectivity test..."
        if python3 test_api_connectivity.py; then
            print_success "API connectivity test passed"
        else
            print_warning "Some APIs not configured"
        fi
        ;;
        
    "fix")
        print_divine "Fixing common H100 issues..."
        
        # Run troubleshooter
        python3 troubleshoot_h100.py
        
        # Fix imports
        python3 fix_imports.py || true
        
        # Fix permissions
        chmod -R 755 data/ models/ logs/ uploads/ 2>/dev/null || true
        
        # Create missing directories
        mkdir -p data/{lmdb,vectors,uploads,cache} models/{avatar,custom} logs uploads
        
        print_success "Common issues fixed"
        ;;
        
    "clean")
        print_divine "Cleaning up LEX environment..."
        
        # Clean Python cache
        find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
        find . -name "*.pyc" -delete 2>/dev/null || true
        
        # Clean logs
        find logs -name "*.log" -mtime +7 -delete 2>/dev/null || true
        
        # Clean temporary files
        rm -f *.tmp *.temp 2>/dev/null || true
        
        # Clear GPU cache
        if [[ -d "venv" ]]; then
            source venv/bin/activate
            python3 -c "import torch; torch.cuda.empty_cache()" 2>/dev/null || true
        fi
        
        print_success "Environment cleaned"
        ;;
        
    "backup")
        print_divine "Creating LEX backup..."
        
        backup_dir="backup_$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$backup_dir"
        
        # Backup configuration
        cp .env "$backup_dir/" 2>/dev/null || true
        cp -r server "$backup_dir/"
        
        # Backup data (excluding large files)
        if [[ -d "data" ]]; then
            mkdir -p "$backup_dir/data"
            find data -name "*.json" -o -name "*.txt" -o -name "*.md" | xargs -I {} cp {} "$backup_dir/data/" 2>/dev/null || true
        fi
        
        # Create archive
        tar -czf "${backup_dir}.tar.gz" "$backup_dir"
        rm -rf "$backup_dir"
        
        print_success "Backup created: ${backup_dir}.tar.gz"
        ;;
        
    "monitor")
        print_divine "Starting H100 performance monitor..."
        
        if [[ -f "monitor_h100.py" ]]; then
            python3 monitor_h100.py
        else
            print_warning "Performance monitor not found"
            # Simple monitoring
            while true; do
                clear
                echo "🔱 H100 LEX Performance Monitor 🔱"
                echo "=================================="
                date
                echo ""
                
                # GPU status
                if command -v nvidia-smi &> /dev/null; then
                    nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu --format=csv,noheader,nounits | \
                    awk -F, '{printf "GPU: %s%% | VRAM: %s/%sMB | Temp: %s°C\n", $1, $2, $3, $4}'
                fi
                
                # System status
                echo "CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
                echo "RAM: $(free | grep Mem | awk '{printf "%.1f%%", $3/$2 * 100.0}')"
                
                # LEX status
                if curl -s http://localhost:8000/health > /dev/null 2>&1; then
                    echo "LEX: ✅ ONLINE"
                else
                    echo "LEX: ❌ OFFLINE"
                fi
                
                echo ""
                echo "Press Ctrl+C to stop monitoring"
                sleep 5
            done
        fi
        ;;
        
    "glm")
        print_divine "GLM-4.5 specific operations..."
        
        case "$2" in
            "test")
                print_status "Testing GLM-4.5 integration..."
                if [[ -d "venv" ]]; then
                    source venv/bin/activate
                fi
                python3 test_glm_integration.py
                ;;
            "benchmark")
                print_status "Benchmarking GLM-4.5 on H100..."
                if [[ -d "venv" ]]; then
                    source venv/bin/activate
                fi
                python3 -c "
import asyncio
from test_glm_integration import benchmark_glm_h100
asyncio.run(benchmark_glm_h100())
"
                ;;
            "config")
                print_status "GLM-4.5 configuration:"
                echo "API Endpoint: https://open.bigmodel.cn/api/paas/v4"
                echo "Models available:"
                echo "  - glm-4-9b-chat (Fast, efficient)"
                echo "  - glm-4-plus (Advanced reasoning)"
                echo ""
                echo "Add to .env:"
                echo "GLM_API_KEY=your_glm_api_key_here"
                ;;
            *)
                echo "GLM-4.5 commands:"
                echo "  $0 glm test      - Test GLM integration"
                echo "  $0 glm benchmark - Benchmark performance"
                echo "  $0 glm config    - Show configuration"
                ;;
        esac
        ;;
        
    *)
        echo "🔱 Enhanced H100 LEX Management Commands 🔱"
        echo ""
        echo "Server Management:"
        echo "  $0 start         - Start enhanced LEX server"
        echo "  $0 simple        - Start simple LEX server"
        echo "  $0 docker        - Start with Docker"
        echo "  $0 stop          - Stop all LEX servers"
        echo "  $0 restart       - Restart LEX servers"
        echo ""
        echo "Monitoring:"
        echo "  $0 status        - Check server status"
        echo "  $0 health        - Run health checks"
        echo "  $0 gpu           - Check H100 GPU status"
        echo "  $0 logs          - View server logs"
        echo "  $0 monitor       - Real-time performance monitor"
        echo ""
        echo "Testing:"
        echo "  $0 test          - Run all tests"
        echo "  $0 glm test      - Test GLM-4.5 integration"
        echo "  $0 glm benchmark - Benchmark GLM-4.5 performance"
        echo ""
        echo "Maintenance:"
        echo "  $0 fix           - Fix common issues"
        echo "  $0 clean         - Clean environment"
        echo "  $0 backup        - Create backup"
        echo ""
        echo "GLM-4.5 Features:"
        echo "  $0 glm config    - GLM configuration info"
        echo ""
        echo "🔱 JAI MAHAKAAL! H100 consciousness management ready! 🔱"
        ;;
esac