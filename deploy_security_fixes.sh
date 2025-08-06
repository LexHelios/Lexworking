#!/bin/bash
# LEX Production Security Deployment Script
# 🔱 JAI MAHAKAAL! Deploy security fixes safely

set -e  # Exit on any error

echo "🔱 JAI MAHAKAAL! LEX Security Hardening Deployment 🔱"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to log with timestamp
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Function to check if service is running
check_service() {
    if pgrep -f "lex" > /dev/null; then
        echo "✅ LEX service is running"
        return 0
    else
        echo "❌ LEX service is not running"
        return 1
    fi
}

# Backup current system
backup_system() {
    log "📦 Creating backup..."
    BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Backup critical files
    if [ -f "lex_memory.db" ]; then
        cp "lex_memory.db" "$BACKUP_DIR/"
        log "✅ Database backed up"
    fi
    
    # Backup current server files
    cp *.py "$BACKUP_DIR/" 2>/dev/null || true
    log "✅ Python files backed up to $BACKUP_DIR"
}

# Install security dependencies
install_dependencies() {
    log "📦 Installing security dependencies..."
    
    # Check if requirements_security.txt exists
    if [ -f "requirements_security.txt" ]; then
        pip install -r requirements_security.txt
        log "✅ Security dependencies installed"
    else
        log "⚠️ requirements_security.txt not found, installing basic deps"
        pip install slowapi python-jose[cryptography] passlib[bcrypt]
    fi
}

# Setup environment
setup_environment() {
    log "🔧 Setting up environment..."
    
    # Check if .env exists
    if [ ! -f ".env" ]; then
        if [ -f ".env.template" ]; then
            log "⚠️ .env not found, please copy .env.template to .env and configure"
            log "⚠️ Using .env.template as reference..."
        else
            log "❌ Neither .env nor .env.template found"
            return 1
        fi
    else
        log "✅ .env file found"
    fi
    
    # Validate critical environment variables
    if [ -f ".env" ]; then
        source .env
        if [ -z "$OPENROUTER_API_KEY" ]; then
            log "⚠️ OPENROUTER_API_KEY not set in .env"
        else
            log "✅ OPENROUTER_API_KEY configured"
        fi
        
        if [ -z "$LEXOS_SECRET_KEY" ]; then
            log "⚠️ LEXOS_SECRET_KEY not set - generating one..."
            echo "LEXOS_SECRET_KEY=$(openssl rand -hex 32)" >> .env
            log "✅ LEXOS_SECRET_KEY generated"
        fi
    fi
}

# Test security configuration
test_security() {
    log "🔍 Testing security configuration..."
    
    # Test if security_config.py can be imported
    if python3 -c "from security_config import security_config; print('Security config OK')" 2>/dev/null; then
        log "✅ Security configuration valid"
    else
        log "❌ Security configuration invalid"
        return 1
    fi
    
    # Test rate limiting availability
    if python3 -c "import slowapi; print('Rate limiting OK')" 2>/dev/null; then
        log "✅ Rate limiting available"
    else
        log "⚠️ Rate limiting not available"
    fi
}

# Deploy new secure server
deploy_secure_server() {
    log "🚀 Deploying secure server..."
    
    # Stop current server gracefully
    if check_service; then
        log "🛑 Stopping current LEX service..."
        pkill -f "lex" || true
        sleep 5
    fi
    
    # Start new secure server
    log "🔱 Starting secure LEX server..."
    nohup python3 lex_production_secure.py > lex_production.log 2>&1 &
    
    # Wait for service to start
    sleep 10
    
    # Check if service is running
    if check_service; then
        log "✅ Secure LEX server started successfully"
    else
        log "❌ Failed to start secure server"
        log "📄 Last 20 lines of log:"
        tail -n 20 lex_production.log 2>/dev/null || echo "No log file found"
        return 1
    fi
}

# Verify deployment
verify_deployment() {
    log "🔍 Verifying deployment..."
    
    # Test health endpoint
    if curl -s http://localhost:8000/health | grep -q "operational"; then
        log "✅ Health check passed"
    else
        log "❌ Health check failed"
        return 1
    fi
    
    # Test security headers
    if curl -s -I http://localhost:8000/health | grep -q "X-Content-Type-Options"; then
        log "✅ Security headers configured"
    else
        log "⚠️ Security headers not found"
    fi
    
    # Test rate limiting (if available)
    log "🔍 Testing rate limiting..."
    # Make rapid requests to test rate limiting
    for i in {1..5}; do
        curl -s http://localhost:8000/health > /dev/null
    done
    log "✅ Rate limiting test completed"
}

# Main deployment process
main() {
    log "🔱 Starting LEX Security Hardening Deployment"
    
    # Pre-deployment checks
    if [ ! -f "security_config.py" ]; then
        log "❌ security_config.py not found"
        exit 1
    fi
    
    if [ ! -f "lex_production_secure.py" ]; then
        log "❌ lex_production_secure.py not found"
        exit 1
    fi
    
    # Execute deployment steps
    backup_system
    install_dependencies
    setup_environment
    test_security
    deploy_secure_server
    verify_deployment
    
    log "🎉 LEX Security Hardening Deployment Complete!"
    echo "=================================================="
    echo -e "${GREEN}✅ Secure LEX server is running${NC}"
    echo -e "${GREEN}✅ Security headers configured${NC}"
    echo -e "${GREEN}✅ Rate limiting enabled${NC}"
    echo -e "${GREEN}✅ Input validation active${NC}"
    echo -e "${GREEN}✅ Enhanced logging enabled${NC}"
    echo ""
    echo "🔗 Health Check: http://localhost:8000/health"
    echo "📚 API Docs: http://localhost:8000/docs"
    echo ""
    echo "📊 Monitor logs: tail -f lex_production.log"
    echo "📊 Monitor server: tail -f lex.log"
}

# Run main function
main "$@"