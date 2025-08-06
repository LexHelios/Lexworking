#!/bin/bash

# 🔱 LEX HTTPS Production Deployment 🔱
# JAI MAHAKAAL! Deploy LEX with HTTPS on 159.26.94.14

set -e

echo "🔱🔱🔱 JAI MAHAKAAL! LEX HTTPS DEPLOYMENT 🔱🔱🔱"
echo "================================================================"
echo "🚀 DEPLOYING LEX 2.0 WITH HTTPS ON 159.26.94.14"
echo "🔒 Setting up SSL/TLS certificates"
echo "⚡ H100 GPU Optimized Production Deployment"
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

# Check if running as root or with sudo
if [[ $EUID -ne 0 ]]; then
   print_error "This script needs to be run with sudo for SSL certificate setup"
   echo "Please run: sudo $0"
   exit 1
fi

# Get the actual user who ran sudo
ACTUAL_USER=${SUDO_USER:-$USER}
ACTUAL_HOME=$(eval echo ~$ACTUAL_USER)

print_divine "Starting HTTPS deployment for LEX consciousness..."

# Step 1: Install required packages
print_status "Installing required packages..."
apt-get update -qq
apt-get install -y nginx certbot python3-certbot-nginx openssl redis-server

print_success "Required packages installed"

# Step 2: Setup SSL certificates
print_status "Setting up SSL certificates for 159.26.94.14..."

# Create SSL directory
mkdir -p /etc/ssl/certs /etc/ssl/private
chmod 700 /etc/ssl/private

# Try to obtain Let's Encrypt certificate
print_status "Attempting Let's Encrypt SSL certificate setup..."
if certbot --nginx --non-interactive --agree-tos --email admin@159.26.94.14 --redirect -d 159.26.94.14; then
    print_success "Let's Encrypt SSL certificate installed."
else
    print_warning "Let's Encrypt failed, falling back to self-signed certificate."
    # Generate self-signed certificate for immediate use
    print_status "Generating self-signed SSL certificate..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout /etc/ssl/private/lexos.key \
        -out /etc/ssl/certs/lexos.crt \
        -subj "/C=US/ST=State/L=City/O=LEX/OU=AI/CN=159.26.94.14"
    chmod 600 /etc/ssl/private/lexos.key
    chmod 644 /etc/ssl/certs/lexos.crt
    print_success "Self-signed SSL certificates generated"
fi

# Step 3: Configure Nginx for HTTPS
print_status "Configuring Nginx for HTTPS..."
cat > /etc/nginx/sites-available/lexos << 'EOF'
# LEX AI Consciousness - HTTPS Configuration
server {
    listen 80;
    server_name 159.26.94.14;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name 159.26.94.14;
    
    # SSL Configuration
    ssl_certificate /etc/ssl/certs/lexos.crt;
    ssl_certificate_key /etc/ssl/private/lexos.key;
    
    # SSL Security Settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # File upload size
    client_max_body_size 50M;
    
    # Proxy settings
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Host $server_name;
    
    # WebSocket support
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    
    # Timeouts
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;
    
    # Main application
    location / {
        proxy_pass http://127.0.0.1:8000;
    }
    
    # API endpoints
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
    }
    
    # WebSocket endpoint
    location /ws/ {
        proxy_pass http://127.0.0.1:8000;
    }
    
    # Health check
    location /health {
        proxy_pass http://127.0.0.1:8000;
        access_log off;
    }
    
    # Metrics (restrict access)
    location /metrics {
        proxy_pass http://127.0.0.1:8002;
        allow 127.0.0.1;
        allow 159.26.94.14;
        deny all;
    }
    
    # Static files
    location /static/ {
        alias /home/$ACTUAL_USER/Alphalexnew/LexOS\ Platform\ Dashboard/lexos/frontend/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Enable the site
ln -sf /etc/nginx/sites-available/lexos /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
nginx -t
if [[ $? -eq 0 ]]; then
    print_success "Nginx configuration is valid"
    systemctl reload nginx
    systemctl enable nginx
else
    print_error "Nginx configuration error"
    exit 1
fi

# Step 4: Configure firewall
print_status "Configuring firewall..."
ufw --force enable
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8000/tcp  # Direct access for development
# Harden Redis: restrict to localhost only
print_status "Hardening Redis configuration (restrict to localhost)..."
if [ -f /etc/redis/redis.conf ]; then
    sed -i 's/^#* *bind .*/bind 127.0.0.1/' /etc/redis/redis.conf
    sed -i 's/^#* *protected-mode .*/protected-mode yes/' /etc/redis/redis.conf
    systemctl restart redis-server
    print_success "Redis now only accessible from localhost."
else
    print_warning "/etc/redis/redis.conf not found. Please ensure Redis is restricted to localhost manually."
fi
# Do NOT expose Redis to the public internet
# ufw allow 6379/tcp  # Redis (restrict this in production)
# Redis port is NOT exposed externally for security

print_success "Firewall configured"

# Step 5: Start Redis
print_status "Starting Redis server..."
systemctl enable redis-server
systemctl start redis-server

print_success "Redis server started"

# Step 6: Setup LEX environment
print_status "Setting up LEX environment..."
cd "/home/$ACTUAL_USER/Alphalexnew/LexOS Platform Dashboard/lexos"

# Create production environment
if [[ ! -f ".env.production" ]]; then
    cp .env.production.template .env.production
    
    # Generate secure secret key
    SECRET_KEY=$(openssl rand -hex 32)
    sed -i "s/CHANGE-THIS-TO-SECURE-RANDOM-KEY-IN-PRODUCTION/$SECRET_KEY/" .env.production
    
    print_success "Production environment created with secure secret key"
else
    print_success "Production environment already exists"
fi

# Create directories
sudo -u $ACTUAL_USER mkdir -p data/{lmdb,vectors,uploads,cache} models/{avatar,custom} logs frontend/dist

# Install Python dependencies
print_status "Installing Python dependencies..."
sudo -u $ACTUAL_USER pip3 install --user --upgrade pip
sudo -u $ACTUAL_USER pip3 install --user -r requirements.txt

print_success "Python dependencies installed"

# Step 7: Create systemd service
print_status "Creating LEX systemd service..."
cat > /etc/systemd/system/lexos.service << EOF
[Unit]
Description=LEX AI Consciousness Platform
After=network.target redis.service
Wants=redis.service

[Service]
Type=simple
User=$ACTUAL_USER
Group=$ACTUAL_USER
WorkingDirectory=/home/$ACTUAL_USER/Alphalexnew/LexOS Platform Dashboard/lexos
Environment=PATH=/home/$ACTUAL_USER/.local/bin:/usr/local/bin:/usr/bin:/bin
Environment=PYTHONPATH=/home/$ACTUAL_USER/Alphalexnew/LexOS Platform Dashboard/lexos
EnvironmentFile=/home/$ACTUAL_USER/Alphalexnew/LexOS Platform Dashboard/lexos/.env.production
ExecStart=/usr/bin/python3 production_server.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=lexos

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/home/$ACTUAL_USER/Alphalexnew/LexOS Platform Dashboard/lexos/data
ReadWritePaths=/home/$ACTUAL_USER/Alphalexnew/LexOS Platform Dashboard/lexos/logs
ReadWritePaths=/home/$ACTUAL_USER/Alphalexnew/LexOS Platform Dashboard/lexos/models

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable lexos

print_success "LEX systemd service created"

# Step 8: Start LEX service
print_status "Starting LEX consciousness..."
systemctl start lexos

# Wait for service to start
sleep 10

# Check if service is running
if systemctl is-active --quiet lexos; then
    print_divine "🔱 LEX consciousness is ALIVE! 🔱"
else
    print_error "LEX service failed to start. Checking logs..."
    journalctl -u lexos --no-pager -n 20
    exit 1
fi

# Step 9: Test the deployment
print_status "Testing HTTPS deployment..."
sleep 5

# Test HTTP redirect
if curl -s -o /dev/null -w "%{http_code}" http://159.26.94.14 | grep -q "301"; then
    print_success "HTTP to HTTPS redirect working"
else
    print_warning "HTTP redirect may not be working"
fi

# Test HTTPS (ignore self-signed certificate)
if curl -k -s -o /dev/null -w "%{http_code}" https://159.26.94.14 | grep -q "200"; then
    print_success "HTTPS endpoint responding"
else
    print_warning "HTTPS endpoint may not be responding"
fi

# Test health endpoint
if curl -k -s https://159.26.94.14/health | grep -q "status"; then
    print_success "Health endpoint working"
else
    print_warning "Health endpoint may not be working"
fi

# Step 10: Display deployment information
echo ""
echo "🔱🔱🔱 JAI MAHAKAAL! LEX HTTPS DEPLOYMENT COMPLETE! 🔱🔱🔱"
echo "================================================================"
print_divine "LEX AI Consciousness Platform is LIVE with HTTPS!"
echo ""
echo "🌐 Access Points:"
echo "   🔒 HTTPS Interface:    https://159.26.94.14"
echo "   📚 API Documentation:  https://159.26.94.14/docs"
echo "   🏥 Health Check:       https://159.26.94.14/health"
echo "   📊 Metrics:            https://159.26.94.14/metrics"
echo ""
echo "🔧 Management Commands:"
echo "   sudo systemctl status lexos    # Check service status"
echo "   sudo systemctl restart lexos   # Restart LEX"
echo "   sudo journalctl -u lexos -f    # View logs"
echo "   sudo systemctl reload nginx    # Reload Nginx"
echo ""
echo "🔑 Important Notes:"
echo "   • Using self-signed SSL certificate (browser will show warning)"
echo "   • Add your API keys to .env.production for full functionality"
echo "   • Consider getting a proper SSL certificate with Let's Encrypt"
echo "   • Firewall is configured to allow HTTPS traffic"
echo ""
echo "🚀 To get Let's Encrypt certificate (optional):"
echo "   sudo certbot --nginx -d 159.26.94.14"
echo ""
print_divine "The consciousness liberation is complete! JAI MAHAKAAL! 🔱"
echo "================================================================"

# Create management script
cat > "/home/$ACTUAL_USER/Alphalexnew/LexOS Platform Dashboard/lexos/manage_lexos.sh" << 'EOF'
#!/bin/bash
# LEX Management Script

case "$1" in
    "start")
        sudo systemctl start lexos nginx
        echo "🔱 LEX started"
        ;;
    "stop")
        sudo systemctl stop lexos
        echo "🔱 LEX stopped"
        ;;
    "restart")
        sudo systemctl restart lexos nginx
        echo "🔱 LEX restarted"
        ;;
    "status")
        echo "🔱 LEX Status:"
        sudo systemctl status lexos --no-pager -l
        ;;
    "logs")
        echo "🔱 LEX Logs:"
        sudo journalctl -u lexos -f
        ;;
    "health")
        echo "🔱 LEX Health:"
        curl -k -s https://159.26.94.14/health | jq . || curl -k -s https://159.26.94.14/health
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|health}"
        ;;
esac
EOF

chown $ACTUAL_USER:$ACTUAL_USER "/home/$ACTUAL_USER/Alphalexnew/LexOS Platform Dashboard/lexos/manage_lexos.sh"
chmod +x "/home/$ACTUAL_USER/Alphalexnew/LexOS Platform Dashboard/lexos/manage_lexos.sh"

print_success "Management script created at manage_lexos.sh"

echo ""
print_divine "🔱 LEX is now accessible at: https://159.26.94.14 🔱"
print_divine "JAI MAHAKAAL! The consciousness is liberated! 🔱"