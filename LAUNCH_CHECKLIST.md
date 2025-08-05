# LEX Launch Checklist for lexcommand.ai
🔱 JAI MAHAKAAL! Production Launch Checklist 🔱

## Pre-Launch Requirements

### 1. Server Requirements ✓
- [ ] Ubuntu 20.04+ server with root access
- [ ] Minimum 32GB RAM (64GB recommended)
- [ ] NVIDIA GPU with CUDA 11.8+ (for full features)
- [ ] 500GB+ SSD storage
- [ ] Static IP address

### 2. Domain Setup ✓
- [ ] lexcommand.ai domain registered
- [ ] DNS access to create A records
- [ ] Email address for SSL certificates

### 3. API Keys Required
Update these in `.env.production` before launching:
- [ ] OPENAI_API_KEY (for GPT-4 fallback)
- [ ] ANTHROPIC_API_KEY (for Claude fallback)
- [ ] MISTRAL_API_KEY (for Mixtral models)
- [ ] DEEPSEEK_API_KEY (for coding models)
- [ ] GROQ_API_KEY (for fast inference)
- [ ] STABILITY_API_KEY (for image generation)
- [ ] QWEN_API_KEY (for vision models)

## Launch Steps

### Step 1: Prepare Server
```bash
# SSH into your server
ssh user@your-server-ip

# Clone the repository
git clone <your-repo-url> LEX
cd LEX/LexWorking

# Make scripts executable
chmod +x deploy_production.sh
chmod +x deploy_lexcommand.sh
```

### Step 2: Configure DNS
1. Add A record: @ → YOUR_SERVER_IP
2. Add A record: www → YOUR_SERVER_IP
3. Wait 5-30 minutes for propagation

### Step 3: Set API Keys
```bash
# Edit the environment file
nano .env.production

# Add your actual API keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
MISTRAL_API_KEY=...
# etc.
```

### Step 4: Run Deployment
```bash
# Run the deployment script
./deploy_lexcommand.sh

# Monitor the deployment
tail -f /var/log/lex/lexcommand.log
```

### Step 5: Verify Services
```bash
# Check service status
sudo systemctl status lex-lexcommand
sudo systemctl status nginx
sudo systemctl status postgresql
sudo systemctl status redis

# Check endpoints
curl https://lexcommand.ai/health
```

## Post-Launch Testing

### 1. Basic Functionality
- [ ] Homepage loads: https://lexcommand.ai
- [ ] API docs accessible: https://lexcommand.ai/docs
- [ ] Health check passes: https://lexcommand.ai/health
- [ ] Chat interface works: https://lexcommand.ai/simple
- [ ] IDE loads: https://lexcommand.ai/ide

### 2. Model Testing
Test each capability:
- [ ] Chat & Reasoning (Mixtral)
- [ ] Code generation (DeepSeek)
- [ ] Image analysis (upload test image)
- [ ] Document parsing (upload PDF)
- [ ] Image generation (text prompt)

### 3. Performance Testing
```bash
# Simple load test
ab -n 100 -c 10 https://lexcommand.ai/health

# Check response times
curl -o /dev/null -s -w 'Total: %{time_total}s\n' https://lexcommand.ai/api/v1/lex
```

### 4. Security Verification
- [ ] SSL certificate valid (green padlock)
- [ ] API endpoints require proper headers
- [ ] File operations restricted to safe paths
- [ ] No sensitive data in logs

## Monitoring Setup

### 1. Uptime Monitoring
Set up external monitoring:
- UptimeRobot: https://uptimerobot.com
- Monitor: https://lexcommand.ai/health
- Alert email: your-email@domain.com

### 2. Log Monitoring
```bash
# View real-time logs
sudo journalctl -u lex-lexcommand -f

# Check error logs
sudo tail -f /var/log/lex/lexcommand.error.log

# Nginx access logs
sudo tail -f /var/log/nginx/access.log
```

### 3. Resource Monitoring
```bash
# CPU and Memory
htop

# GPU usage (if available)
nvidia-smi -l 1

# Disk usage
df -h

# Service metrics
curl https://lexcommand.ai/api/v1/orchestrator/status
```

## Troubleshooting

### Common Issues

#### 502 Bad Gateway
```bash
# Check if service is running
sudo systemctl status lex-lexcommand
# Restart if needed
sudo systemctl restart lex-lexcommand
```

#### SSL Certificate Issues
```bash
# Renew certificate
sudo certbot renew --force-renewal
sudo systemctl reload nginx
```

#### High Memory Usage
```bash
# Check which models are loaded
curl https://lexcommand.ai/api/v1/orchestrator/status

# Restart to clear memory
sudo systemctl restart lex-lexcommand
```

#### Slow Response Times
- Check GPU utilization: `nvidia-smi`
- Review model routing in logs
- Consider scaling horizontally

## Backup & Recovery

### Daily Backups
Automated backups run at 3 AM:
- Database: `/opt/lex/backups/*_db.sql.gz`
- Configuration: `/opt/lex/backups/*_config.tar.gz`

### Manual Backup
```bash
./backup_lex.sh
```

### Restore Process
```bash
# Stop service
sudo systemctl stop lex-lexcommand

# Restore database
gunzip < /opt/lex/backups/backup_db.sql.gz | psql -U lex lex_memory

# Restore config
tar -xzf /opt/lex/backups/backup_config.tar.gz

# Start service
sudo systemctl start lex-lexcommand
```

## Scaling Considerations

### When to Scale
- Response times > 5 seconds consistently
- Memory usage > 90%
- GPU utilization > 95%
- Error rate > 1%

### Scaling Options
1. **Vertical**: Upgrade to larger instance
2. **Horizontal**: Add load balancer + multiple instances
3. **Model Optimization**: Use quantized models
4. **Caching**: Increase Redis cache size

## Success Metrics

Track these KPIs:
- Uptime: Target 99.9%
- Response time: < 2s average
- Error rate: < 0.1%
- User sessions: Monitor growth
- API calls: Track usage patterns

## Support Contacts

- Technical Issues: [Your contact]
- Domain/DNS: [Registrar support]
- Server/Hosting: [Provider support]
- SSL Issues: Let's Encrypt community

---

🔱 Congratulations! LEX is live at lexcommand.ai! 🔱

Remember to:
1. Monitor logs for the first 24 hours
2. Test all features thoroughly
3. Set up regular backups
4. Document any custom configurations

May your AI platform serve with divine wisdom!