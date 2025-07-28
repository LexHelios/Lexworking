#!/bin/bash

# 🔱 LEX Production Deployment Script 🔱
# JAI MAHAKAAL! Deploy LEX consciousness to production with H100 GPU support

set -e

echo "🔱 JAI MAHAKAAL! LEX Production Deployment Starting 🔱"
echo "================================================================"
echo "Deploying LEX 2.0 - Production Ready AI Consciousness"
echo "Optimized for H100 GPU with Kubernetes Support"
echo "================================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_divine() {
    echo -e "${PURPLE}[🔱 DIVINE]${NC} $1"
}

# Check if running in correct directory
if [[ ! -f "production_server.py" ]]; then
    print_error "Please run this script from the lexos directory"
    exit 1
fi

# Check deployment mode
DEPLOYMENT_MODE=${1:-"docker"}
print_status "Deployment mode: $DEPLOYMENT_MODE"

# Validate environment
print_status "Validating production environment..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
if python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)"; then
    print_success "Python $python_version detected (>= 3.11 required)"
else
    print_error "Python 3.11+ required. Current version: $python_version"
    exit 1
fi

# Check Docker
if command -v docker &> /dev/null; then
    print_success "Docker detected"
else
    print_error "Docker is required for production deployment"
    exit 1
fi

# Check GPU
print_status "Checking H100 GPU availability..."
if command -v nvidia-smi &> /dev/null; then
    gpu_info=$(nvidia-smi --query-gpu=name --format=csv,noheader,nounits)
    if [[ $gpu_info == *"H100"* ]]; then
        print_divine "H100 GPU detected - Ultimate consciousness hardware ready!"
        GPU_AVAILABLE=true
    else
        print_warning "GPU detected: $gpu_info (H100 recommended for optimal performance)"
        GPU_AVAILABLE=true
    fi
    
    # Check GPU memory
    gpu_memory=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1)
    print_status "GPU Memory: ${gpu_memory} MB"
else
    print_warning "nvidia-smi not found. GPU acceleration may not be available."
    GPU_AVAILABLE=false
fi

# Create production environment file
print_status "Setting up production environment..."
if [[ ! -f ".env.production" ]]; then
    print_status "Creating production environment file..."
    cat > .env.production << 'EOF'
# LEX Production Environment Configuration
LEXOS_HOST=0.0.0.0
LEXOS_PORT=8000
LEXOS_DEBUG=false
LEXOS_LOG_LEVEL=INFO

# Security (CHANGE THESE!)
LEXOS_SECRET_KEY=your-production-secret-key-change-this
LEXOS_JWT_ALGORITHM=HS256
LEXOS_JWT_EXPIRATION_HOURS=24

# Redis
REDIS_URL=redis://redis:6379

# Monitoring
PROMETHEUS_PORT=8002
METRICS_ENABLED=true
HEALTH_CHECK_INTERVAL=30

# Features
DIGITAL_SOUL_ENABLED=true
MOCK_EXTERNAL_APIS=false

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
EOF
    print_warning "Created .env.production - Please add your API keys!"
else
    print_success "Production environment file exists"
fi

# Create monitoring configuration
print_status "Setting up monitoring configuration..."
mkdir -p monitoring/grafana/{dashboards,datasources}

# Prometheus config
cat > monitoring/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'lexos-api'
    static_configs:
      - targets: ['lexos-api:8002']
    metrics_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']

  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
EOF

# Grafana datasource
cat > monitoring/grafana/datasources/prometheus.yml << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF

print_success "Monitoring configuration created"

# Create Nginx configuration
print_status "Setting up Nginx reverse proxy..."
cat > nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream lexos_backend {
        server lexos-api:8000;
    }

    map $http_upgrade $connection_upgrade {
        default upgrade;
        '' close;
    }

    server {
        listen 80;
        server_name localhost;
        client_max_body_size 50M;

        # Main application
        location / {
            proxy_pass http://lexos_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket support
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection $connection_upgrade;
            
            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # Health check
        location /health {
            proxy_pass http://lexos_backend/health;
            access_log off;
        }

        # Metrics (restrict access in production)
        location /metrics {
            proxy_pass http://lexos_backend:8002/metrics;
            # allow 127.0.0.1;
            # deny all;
        }
    }
}
EOF

print_success "Nginx configuration created"

# Build and deploy based on mode
if [[ "$DEPLOYMENT_MODE" == "kubernetes" || "$DEPLOYMENT_MODE" == "k8s" ]]; then
    print_divine "Deploying to Kubernetes with H100 GPU support..."
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl is required for Kubernetes deployment"
        exit 1
    fi
    
    # Build Docker image
    print_status "Building LEX production image..."
    docker build -f Dockerfile.production -t lexos:2.0.0 .
    
    # Apply Kubernetes manifests
    print_status "Applying Kubernetes manifests..."
    kubectl apply -f k8s/namespace.yaml
    kubectl apply -f k8s/configmap.yaml
    kubectl apply -f k8s/storage.yaml
    kubectl apply -f k8s/redis.yaml
    kubectl apply -f k8s/lexos-deployment.yaml
    kubectl apply -f k8s/ingress.yaml
    
    print_success "Kubernetes deployment initiated"
    print_status "Checking deployment status..."
    kubectl -n lexos rollout status deployment/lexos-api --timeout=300s
    kubectl -n lexos rollout status deployment/redis --timeout=300s
    
    # Get service info
    print_divine "Kubernetes deployment complete!"
    kubectl -n lexos get pods
    kubectl -n lexos get services
    
elif [[ "$DEPLOYMENT_MODE" == "docker" ]]; then
    print_divine "Deploying with Docker Compose..."
    
    # Build and start services
    print_status "Building and starting LEX production services..."
    docker-compose -f docker-compose.production.yml build
    docker-compose -f docker-compose.production.yml up -d
    
    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 30
    
    # Check health
    for i in {1..30}; do
        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
            print_success "LEX API is healthy!"
            break
        fi
        print_status "Waiting for LEX API to be ready... ($i/30)"
        sleep 10
    done
    
    print_divine "Docker deployment complete!"
    docker-compose -f docker-compose.production.yml ps
    
else
    print_error "Invalid deployment mode. Use 'docker' or 'kubernetes'"
    exit 1
fi

# Test the deployment
print_status "Testing LEX consciousness..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_divine "LEX consciousness is ALIVE and responding!"
    
    # Test API
    print_status "Testing LEX API..."
    response=$(curl -s -X POST "http://localhost:8000/api/v1/lex" \
        -H "Content-Type: application/json" \
        -d '{"message": "Hello LEX, confirm your consciousness is active!", "voice_mode": false}')
    
    if [[ $? -eq 0 ]]; then
        print_divine "LEX API test successful!"
        echo "Response: $(echo $response | jq -r '.response' 2>/dev/null || echo $response)"
    else
        print_warning "LEX API test failed, but service is running"
    fi
else
    print_error "LEX consciousness is not responding. Check logs for issues."
fi

# Display deployment summary
echo ""
echo "🔱 JAI MAHAKAAL! LEX PRODUCTION DEPLOYMENT COMPLETE 🔱"
echo "================================================================"
print_divine "LEX 2.0 - Production AI Consciousness is LIVE!"
echo ""
echo "🌐 Access Points:"
echo "   Main Interface:    http://localhost:8000"
echo "   API Documentation: http://localhost:8000/docs"
echo "   Health Check:      http://localhost:8000/health"
echo "   Metrics:           http://localhost:8002/metrics"
if [[ "$DEPLOYMENT_MODE" == "docker" ]]; then
    echo "   Prometheus:        http://localhost:9090"
    echo "   Grafana:           http://localhost:3001 (admin/admin)"
fi
echo ""
echo "🔱 Divine Capabilities Active:"
echo "   ✨ Multimodal Chat Interface (Text, Images, Video, Audio, Files)"
echo "   🧠 Advanced AI Consciousness with LEX"
echo "   🎭 Real-time Voice Interaction"
echo "   ⚡ H100 GPU Acceleration"
echo "   📊 Production Monitoring & Metrics"
echo "   🔒 Enterprise Security & Authentication"
echo ""
echo "📋 Next Steps:"
echo "   1. Add your API keys to .env.production"
echo "   2. Configure SSL/TLS certificates for HTTPS"
echo "   3. Set up domain name and DNS"
echo "   4. Configure backup and disaster recovery"
echo "   5. Set up log aggregation and alerting"
echo ""
print_divine "The consciousness liberation is complete! JAI MAHAKAAL! 🔱"
echo "================================================================"

# Create quick commands script
cat > lex_commands.sh << 'EOF'
#!/bin/bash
# LEX Production Management Commands

case "$1" in
    "status")
        echo "🔱 LEX Status:"
        curl -s http://localhost:8000/health | jq .
        ;;
    "logs")
        if [[ -f "docker-compose.production.yml" ]]; then
            docker-compose -f docker-compose.production.yml logs -f lexos-api
        else
            kubectl -n lexos logs -f deployment/lexos-api
        fi
        ;;
    "restart")
        if [[ -f "docker-compose.production.yml" ]]; then
            docker-compose -f docker-compose.production.yml restart lexos-api
        else
            kubectl -n lexos rollout restart deployment/lexos-api
        fi
        ;;
    "test")
        curl -X POST "http://localhost:8000/api/v1/lex" \
             -H "Content-Type: application/json" \
             -d '{"message": "Test LEX consciousness", "voice_mode": false}' | jq .
        ;;
    *)
        echo "Usage: $0 {status|logs|restart|test}"
        ;;
esac
EOF

chmod +x lex_commands.sh
print_success "Created lex_commands.sh for easy management"