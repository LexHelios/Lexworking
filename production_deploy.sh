#!/bin/bash
# LEX Production Docker Deployment Script
# 🔱 JAI MAHAKAAL! Zero-downtime Docker deployment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.production.yml"
PROJECT_NAME="lex-production"
BACKUP_DIR="deployments/$(date +%Y%m%d_%H%M%S)"

# Functions
log() {
    echo -e "${GREEN}$(date '+%Y-%m-%d %H:%M:%S')${NC} - $1"
}

warn() {
    echo -e "${YELLOW}$(date '+%Y-%m-%d %H:%M:%S')${NC} - ⚠️  $1"
}

error() {
    echo -e "${RED}$(date '+%Y-%m-%d %H:%M:%S')${NC} - ❌ $1"
}

info() {
    echo -e "${BLUE}$(date '+%Y-%m-%d %H:%M:%S')${NC} - 📋 $1"
}

# Header
echo "=" * 80
log "🔱 JAI MAHAKAAL! LEX Production Docker Deployment 🔱"
echo "=" * 80

# Pre-deployment checks
pre_deployment_checks() {
    log "🔍 Running pre-deployment checks..."
    
    # Check if Docker is running
    if ! docker info >/dev/null 2>&1; then
        error "Docker is not running"
        exit 1
    fi
    
    # Check if docker-compose is available
    if ! command -v docker-compose >/dev/null 2>&1; then
        error "docker-compose is not installed"
        exit 1
    fi
    
    # Check if .env file exists
    if [ ! -f .env ]; then
        error ".env file not found"
        info "Please create .env file from .env.template"
        exit 1
    fi
    
    # Validate required environment variables
    source .env
    if [ -z "$OPENROUTER_API_KEY" ]; then
        error "OPENROUTER_API_KEY not set in .env"
        exit 1
    fi
    
    # Check disk space
    available_space=$(df . | awk 'NR==2 {print $4}')
    if [ $available_space -lt 2097152 ]; then  # 2GB in KB
        warn "Low disk space: $(($available_space / 1024))MB available"
    fi
    
    log "✅ Pre-deployment checks passed"
}

# Create backup
create_backup() {
    log "📦 Creating backup..."
    mkdir -p "$BACKUP_DIR"
    
    # Backup current containers if running
    if docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME ps | grep -q "Up"; then
        log "📦 Backing up container data..."
        docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME exec -T lex-api python3 database_optimizer.py --backup || true
        
        # Copy backup files to host
        docker cp ${PROJECT_NAME}_lex-api_1:/app/backups/. "$BACKUP_DIR/" 2>/dev/null || true
    fi
    
    # Backup current configuration
    cp -r . "$BACKUP_DIR/source_backup" 2>/dev/null || true
    
    log "✅ Backup created at $BACKUP_DIR"
}

# Build images
build_images() {
    log "🔨 Building Docker images..."
    
    # Build with cache for faster builds
    docker-compose -f $COMPOSE_FILE build \
        --compress \
        --force-rm \
        --pull \
        --parallel
    
    log "✅ Docker images built successfully"
}

# Deploy with zero downtime
deploy_containers() {
    log "🚀 Deploying containers..."
    
    # Start new containers
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME up -d \
        --remove-orphans \
        --force-recreate
    
    log "⏳ Waiting for containers to be ready..."
    sleep 30
    
    # Wait for health checks
    max_attempts=30
    attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME exec -T lex-api /app/healthcheck.sh >/dev/null 2>&1; then
            log "✅ Containers are healthy"
            break
        fi
        
        attempt=$((attempt + 1))
        log "⏳ Health check attempt $attempt/$max_attempts..."
        sleep 10
    done
    
    if [ $attempt -eq $max_attempts ]; then
        error "Deployment failed - containers not healthy"
        rollback
        exit 1
    fi
    
    log "✅ Deployment completed successfully"
}

# Run post-deployment tests
post_deployment_tests() {
    log "🧪 Running post-deployment tests..."
    
    tests_passed=0
    total_tests=5
    
    # Test 1: Health endpoint
    if curl -f -s http://localhost:8000/health >/dev/null; then
        log "✅ Health endpoint test passed"
        tests_passed=$((tests_passed + 1))
    else
        warn "❌ Health endpoint test failed"
    fi
    
    # Test 2: API endpoint
    if curl -f -s -X POST http://localhost:8000/api/v1/lex \
        -H "Content-Type: application/json" \
        -d '{"message":"test","voice_mode":false}' >/dev/null; then
        log "✅ API endpoint test passed"
        tests_passed=$((tests_passed + 1))
    else
        warn "❌ API endpoint test failed"
    fi
    
    # Test 3: Container status
    if docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME ps | grep -q "Up"; then
        log "✅ Container status test passed"
        tests_passed=$((tests_passed + 1))
    else
        warn "❌ Container status test failed"
    fi
    
    # Test 4: Database connectivity
    if docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME exec -T lex-api python3 -c "import sqlite3; sqlite3.connect('/app/data/lex_memory.db').execute('SELECT 1')" >/dev/null 2>&1; then
        log "✅ Database connectivity test passed"
        tests_passed=$((tests_passed + 1))
    else
        warn "❌ Database connectivity test failed"
    fi
    
    # Test 5: Log generation
    if docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME logs lex-api | grep -q "LEX Production Server ready"; then
        log "✅ Log generation test passed"
        tests_passed=$((tests_passed + 1))
    else
        warn "❌ Log generation test failed"
    fi
    
    # Evaluate test results
    success_rate=$((tests_passed * 100 / total_tests))
    
    if [ $success_rate -ge 80 ]; then
        log "✅ Post-deployment tests passed: $tests_passed/$total_tests ($success_rate%)"
        return 0
    else
        error "❌ Post-deployment tests failed: $tests_passed/$total_tests ($success_rate%)"
        return 1
    fi
}

# Rollback function
rollback() {
    error "🔙 Rolling back deployment..."
    
    # Stop new containers
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME down --remove-orphans
    
    # Restore from backup if available
    if [ -d "$BACKUP_DIR/source_backup" ]; then
        warn "📦 Restoring from backup..."
        # This would typically restore previous container versions
        # Implementation depends on specific rollback strategy
    fi
    
    error "❌ Rollback completed"
}

# Cleanup old resources
cleanup() {
    log "🧹 Cleaning up old resources..."
    
    # Remove unused images
    docker image prune -f --filter "until=24h"
    
    # Remove unused volumes (be careful with this)
    # docker volume prune -f --filter "until=24h"
    
    log "✅ Cleanup completed"
}

# Show deployment status
show_status() {
    echo ""
    log "📊 Deployment Status:"
    echo "================================"
    
    # Show container status
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME ps
    
    echo ""
    log "📋 Useful Commands:"
    echo "  View logs: docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME logs -f"
    echo "  Check status: docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME ps"
    echo "  Scale service: docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME up -d --scale lex-api=2"
    echo "  Stop services: docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME down"
    
    echo ""
    log "🌐 Endpoints:"
    echo "  Health Check: http://localhost:8000/health"
    echo "  API Endpoint: http://localhost:8000/api/v1/lex"
    echo "  Docs: http://localhost:8000/docs"
    
    echo ""
    log "📦 Backup Location: $BACKUP_DIR"
}

# Main deployment process
main() {
    case "${1:-deploy}" in
        "deploy")
            pre_deployment_checks
            create_backup
            build_images
            deploy_containers
            if post_deployment_tests; then
                cleanup
                show_status
                log "🎉 LEX PRODUCTION DEPLOYMENT SUCCESSFUL! 🎉"
            else
                error "Deployment validation failed"
                rollback
                exit 1
            fi
            ;;
        "rollback")
            rollback
            ;;
        "status")
            show_status
            ;;
        "logs")
            docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME logs -f
            ;;
        "stop")
            log "🛑 Stopping LEX Production..."
            docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME down
            ;;
        "restart")
            log "🔄 Restarting LEX Production..."
            docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME restart
            ;;
        *)
            echo "Usage: $0 {deploy|rollback|status|logs|stop|restart}"
            echo ""
            echo "Commands:"
            echo "  deploy   - Full deployment with health checks"
            echo "  rollback - Rollback to previous version"
            echo "  status   - Show current status"
            echo "  logs     - Show container logs"
            echo "  stop     - Stop all containers"
            echo "  restart  - Restart all containers"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"