#!/bin/bash
# LEX Production Deployment for lexcommand.ai
# 🔱 JAI MAHAKAAL! Deploy to lexcommand.ai 🔱

set -e

echo "🔱 ========================================== 🔱"
echo "   DEPLOYING LEX TO LEXCOMMAND.AI"
echo "   Production Multi-Model AI Platform"
echo "🔱 ========================================== 🔱"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Domain configuration
DOMAIN="lexcommand.ai"
EMAIL="admin@lexcommand.ai"  # Update this with your email

print_status() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Update Nginx configuration for lexcommand.ai
setup_nginx_domain() {
    print_status "Configuring Nginx for lexcommand.ai..."
    
    sudo tee /etc/nginx/sites-available/lexcommand > /dev/null << EOF
server {
    listen 80;
    server_name ${DOMAIN} www.${DOMAIN};
    
    # Redirect HTTP to HTTPS
    location / {
        return 301 https://\$server_name\$request_uri;
    }
    
    # Let's Encrypt challenge
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
}

server {
    listen 443 ssl http2;
    server_name ${DOMAIN} www.${DOMAIN};
    
    # SSL configuration will be added by Certbot
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    client_max_body_size 100M;
    client_body_timeout 120s;
    
    # Main application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 86400;
        proxy_buffering off;
    }
    
    # WebSocket support
    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_read_timeout 86400;
    }
    
    # API endpoints
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # CORS headers for API
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization' always;
        add_header 'Access-Control-Expose-Headers' 'Content-Length,Content-Range' always;
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }
}
EOF
    
    # Enable the site
    sudo ln -sf /etc/nginx/sites-available/lexcommand /etc/nginx/sites-enabled/
    
    # Test Nginx configuration
    sudo nginx -t
    
    print_success "Nginx configured for lexcommand.ai"
}

# Setup SSL with Let's Encrypt
setup_ssl() {
    print_status "Setting up SSL certificate for lexcommand.ai..."
    
    # Install certbot if not present
    if ! command -v certbot &> /dev/null; then
        sudo apt update
        sudo apt install -y certbot python3-certbot-nginx
    fi
    
    # Create webroot directory
    sudo mkdir -p /var/www/certbot
    
    # Reload Nginx
    sudo systemctl reload nginx
    
    # Get SSL certificate
    print_status "Obtaining SSL certificate from Let's Encrypt..."
    sudo certbot --nginx -d ${DOMAIN} -d www.${DOMAIN} \
        --non-interactive --agree-tos --email ${EMAIL} \
        --redirect --expand
    
    # Setup auto-renewal
    sudo systemctl enable certbot.timer
    sudo systemctl start certbot.timer
    
    print_success "SSL certificate installed and auto-renewal configured"
}

# Update environment configuration
update_environment() {
    print_status "Updating environment configuration for lexcommand.ai..."
    
    cat > .env.production << EOF
# LEX Production Environment - lexcommand.ai
ENV=production
HOST=0.0.0.0
PORT=8000
WORKERS=4
LOG_LEVEL=info

# Domain Configuration
DOMAIN=${DOMAIN}
ALLOWED_HOSTS=${DOMAIN},www.${DOMAIN},localhost
CORS_ORIGINS=https://${DOMAIN},https://www.${DOMAIN}

# API Keys (update these with your actual keys)
OPENAI_API_KEY=${OPENAI_API_KEY:-your-openai-key}
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-your-anthropic-key}
MISTRAL_API_KEY=${MISTRAL_API_KEY:-your-mistral-key}
DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY:-your-deepseek-key}
GROQ_API_KEY=${GROQ_API_KEY:-your-groq-key}
STABILITY_API_KEY=${STABILITY_API_KEY:-your-stability-key}
QWEN_API_KEY=${QWEN_API_KEY:-your-qwen-key}

# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=lex
POSTGRES_PASSWORD=lex_secure_password_$(openssl rand -base64 32)
POSTGRES_DB=lex_memory

REDIS_URL=redis://localhost:6379

MILVUS_HOST=localhost
MILVUS_PORT=19530

# Security
SECRET_KEY=$(openssl rand -base64 64)
JWT_SECRET=$(openssl rand -base64 32)

# GPU Configuration
CUDA_VISIBLE_DEVICES=0
TORCH_CUDA_ARCH_LIST=7.0,7.5,8.0,8.6,8.9,9.0

# Model Cache
HF_HOME=/opt/lex/models/huggingface
TRANSFORMERS_CACHE=/opt/lex/models/transformers
EOF
    
    print_success "Environment configuration updated"
}

# Create systemd service for lexcommand.ai
create_systemd_service() {
    print_status "Creating systemd service for LEX..."
    
    sudo tee /etc/systemd/system/lex-lexcommand.service > /dev/null << EOF
[Unit]
Description=LEX AI Platform - lexcommand.ai
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$(pwd)
Environment="PATH=$(pwd)/venv_prod/bin:/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONPATH=$(pwd)"
EnvironmentFile=$(pwd)/.env.production
ExecStart=$(pwd)/venv_prod/bin/python simple_lex_server_production.py
Restart=always
RestartSec=10
StandardOutput=append:/var/log/lex/lexcommand.log
StandardError=append:/var/log/lex/lexcommand.error.log

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/lex /var/log/lex

[Install]
WantedBy=multi-user.target
EOF
    
    # Create log directory
    sudo mkdir -p /var/log/lex
    sudo chown $USER:$USER /var/log/lex
    
    # Create model directory
    sudo mkdir -p /opt/lex/models
    sudo chown -R $USER:$USER /opt/lex
    
    sudo systemctl daemon-reload
    sudo systemctl enable lex-lexcommand.service
    
    print_success "Systemd service created"
}

# Setup monitoring
setup_monitoring() {
    print_status "Setting up monitoring for lexcommand.ai..."
    
    # Create monitoring script
    cat > monitor_lex.sh << 'EOF'
#!/bin/bash
# LEX Monitoring Script

# Check if service is running
if ! systemctl is-active --quiet lex-lexcommand; then
    echo "LEX service is down! Attempting restart..."
    systemctl restart lex-lexcommand
    
    # Send alert (configure your alert method)
    # curl -X POST https://your-webhook-url -d "LEX service restarted"
fi

# Check health endpoint
HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
if [ "$HEALTH_CHECK" != "200" ]; then
    echo "Health check failed with status: $HEALTH_CHECK"
    # Send alert
fi

# Check disk space
DISK_USAGE=$(df -h /opt/lex | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 80 ]; then
    echo "Disk usage critical: ${DISK_USAGE}%"
    # Send alert
fi
EOF
    
    chmod +x monitor_lex.sh
    
    # Add to crontab
    (crontab -l 2>/dev/null; echo "*/5 * * * * $(pwd)/monitor_lex.sh") | crontab -
    
    print_success "Monitoring configured"
}

# Setup backup
setup_backup() {
    print_status "Setting up backup for lexcommand.ai..."
    
    cat > backup_lex.sh << 'EOF'
#!/bin/bash
# LEX Backup Script

BACKUP_DIR="/opt/lex/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="lex_backup_${TIMESTAMP}"

mkdir -p ${BACKUP_DIR}

# Backup database
pg_dump -U lex lex_memory | gzip > ${BACKUP_DIR}/${BACKUP_NAME}_db.sql.gz

# Backup configuration
tar -czf ${BACKUP_DIR}/${BACKUP_NAME}_config.tar.gz \
    .env.production \
    *.py \
    server/ \
    --exclude='venv*' \
    --exclude='__pycache__'

# Keep only last 7 days of backups
find ${BACKUP_DIR} -name "lex_backup_*" -mtime +7 -delete

echo "Backup completed: ${BACKUP_NAME}"
EOF
    
    chmod +x backup_lex.sh
    
    # Add to crontab (daily at 3 AM)
    (crontab -l 2>/dev/null; echo "0 3 * * * $(pwd)/backup_lex.sh") | crontab -
    
    print_success "Backup configured"
}

# Main deployment
main() {
    print_status "Starting LEX deployment for lexcommand.ai..."
    
    # Check if running as root
    if [ "$EUID" -eq 0 ]; then 
        print_warning "Please run as regular user (not root)"
        exit 1
    fi
    
    # Update system
    print_status "Updating system packages..."
    sudo apt update && sudo apt upgrade -y
    
    # Install requirements
    print_status "Installing system requirements..."
    sudo apt install -y nginx postgresql redis-server python3.10 python3.10-venv python3-pip
    
    # Run base deployment
    print_status "Running base deployment..."
    if [ -f "deploy_production.sh" ]; then
        ./deploy_production.sh production
    else
        print_warning "Base deployment script not found!"
    fi
    
    # Configure for lexcommand.ai
    setup_nginx_domain
    update_environment
    create_systemd_service
    setup_ssl
    setup_monitoring
    setup_backup
    
    # Start services
    print_status "Starting LEX services..."
    sudo systemctl start lex-lexcommand
    sudo systemctl reload nginx
    
    # Show status
    print_status "🔱 ========================================== 🔱"
    print_success "LEX DEPLOYED TO LEXCOMMAND.AI!"
    print_status "🔱 ========================================== 🔱"
    
    echo ""
    echo "Access your LEX platform at:"
    echo "  🌐 https://lexcommand.ai"
    echo "  📚 https://lexcommand.ai/docs"
    echo "  💻 https://lexcommand.ai/ide"
    echo "  💬 https://lexcommand.ai/simple"
    echo ""
    echo "Service Management:"
    echo "  Start:   sudo systemctl start lex-lexcommand"
    echo "  Stop:    sudo systemctl stop lex-lexcommand"
    echo "  Status:  sudo systemctl status lex-lexcommand"
    echo "  Logs:    sudo journalctl -u lex-lexcommand -f"
    echo ""
    echo "Next Steps:"
    echo "  1. Update API keys in .env.production"
    echo "  2. Configure DNS to point to this server"
    echo "  3. Test all endpoints"
    echo ""
    echo "🔱 JAI MAHAKAAL! LEX is live at lexcommand.ai! 🔱"
}

# Run deployment
main "$@"