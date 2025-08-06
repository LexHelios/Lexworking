# 🔱 LEX AI Production Deployment Guide
**JAI MAHAKAAL!** Complete Infrastructure Hardening Documentation

## 📋 Overview

This guide covers the complete production deployment infrastructure for LEX AI system, including:

- **Security Hardening** (Phase 1 ✅ COMPLETE)
- **Infrastructure Hardening** (Phase 2B 🚀 CURRENT)
- **Automated Backup System** 
- **Blue-Green Zero-Downtime Deployment**
- **Production Monitoring & Alerting**

---

## 🛡️ Phase 1: Security Hardening (COMPLETE)

### ✅ Implemented Security Features

**Environment Security:**
- `.env.template` with secure API key management
- Environment variable validation on startup
- Input sanitization (10,000 character limit)
- API key hashing for secure logging

**Rate Limiting & DOS Protection:**
- SlowAPI implementation (100 req/min, 1000 req/hour)
- IP-based connection limiting
- Request validation with Pydantic models
- Graceful error handling

**Security Headers & CORS:**
```bash
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000
Content-Security-Policy: [configured]
```

**Enhanced Logging:**
- Rotating file logs (10MB, 5 backups)
- Request ID tracking
- Security event logging
- Performance metrics collection

**Database Optimization:**
- SQLite with WAL mode enabled
- Performance indexes for all major queries
- 10MB cache, memory-mapped I/O
- Automated backup and vacuum

---

## 🚀 Phase 2B: Infrastructure Hardening (CURRENT)

### 🐳 Docker Containerization

**Production Dockerfile Features:**
- Multi-stage build for smaller images
- Non-root user for security (UID 1001)
- Health checks included
- Optimized for production

**Build Command:**
```bash
docker build -f Dockerfile.production -t lex-production .
```

**Docker Compose Services:**
```yaml
services:
  lex-api:       # Main application
  lex-backup:    # Automated backup service  
  lex-monitor:   # Monitoring service
  lex-nginx:     # Reverse proxy
  lex-redis:     # Caching layer (optional)
  watchtower:    # Auto-update service
```

### 📦 Automated Backup System

**Backup Schedule:**
- **Hourly**: Database snapshots (3-day retention)
- **Daily**: Full system backup (30-day retention)  
- **Weekly**: Complete archive (90-day retention)
- **Monthly**: Long-term storage (365-day retention)

**Features:**
- SQLite backup with integrity verification
- Automatic compression (gzip)
- Checksum validation
- S3 offsite backup support
- Automated cleanup and rotation

**Commands:**
```bash
# Run automated backup
python3 automated_backup_system.py --run-backup

# Check backup status
python3 automated_backup_system.py --status

# Manual backup
python3 automated_backup_system.py --backup-type daily --backup-scope system

# Restore from backup
python3 automated_backup_system.py --restore db_daily_20250806_120000
```

### 🔄 Blue-Green Deployment

**Zero-Downtime Deployment Process:**
1. **Backup**: Create system snapshot
2. **Deploy**: Start service on inactive environment
3. **Test**: Run comprehensive health checks
4. **Switch**: Update nginx upstream
5. **Cleanup**: Stop old environment

**Environments:**
- **Blue**: Port 8000 (Production A)
- **Green**: Port 8001 (Production B)

**Commands:**
```bash
# Deploy new version
python3 blue_green_deployment.py --deploy

# Check deployment status  
python3 blue_green_deployment.py --status

# Rollback if issues
python3 blue_green_deployment.py --rollback

# Health check specific environment
python3 blue_green_deployment.py --health blue
```

### 📊 Production Monitoring

**System Metrics:**
- CPU, Memory, Disk usage
- Network I/O statistics
- Load averages
- Process monitoring

**Application Metrics:**
- API response times
- Database query performance
- Error rates and status codes
- Request volume and patterns

**Health Checks:**
- Endpoint availability
- Database connectivity
- Security header validation
- Response time monitoring

**Commands:**
```bash
# Run monitoring daemon
python3 production_monitor.py --daemon

# Generate status report
python3 production_monitor.py --report

# One-time metrics collection
python3 production_monitor.py
```

---

## 🚀 Deployment Procedures

### 1. Initial Production Setup

```bash
# 1. Clone repository and setup environment
git clone https://github.com/LexHelios/Lexworking.git
cd Lexworking

# 2. Create environment configuration
cp .env.template .env
# Edit .env with production values

# 3. Install dependencies
pip install -r requirements_security.txt

# 4. Optimize database
python3 database_optimizer.py --optimize

# 5. Start secure server
python3 lex_production_secure.py
```

### 2. Docker Deployment

```bash
# 1. Build production images
docker-compose -f docker-compose.production.yml build

# 2. Start all services
docker-compose -f docker-compose.production.yml up -d

# 3. Check service health
docker-compose -f docker-compose.production.yml ps
docker-compose -f docker-compose.production.yml logs lex-api

# 4. Run deployment script
chmod +x production_deploy.sh
./production_deploy.sh deploy
```

### 3. Blue-Green Deployment

```bash
# 1. Check current status
python3 blue_green_deployment.py --status

# 2. Create backup before deployment
python3 automated_backup_system.py --backup-type daily --backup-scope system

# 3. Deploy to inactive environment
python3 blue_green_deployment.py --deploy

# 4. Monitor for issues
tail -f deployment.log

# 5. Rollback if needed
python3 blue_green_deployment.py --rollback
```

---

## 🔧 Configuration Files

### Environment Variables (.env)
```bash
# API Keys
OPENROUTER_API_KEY=sk-or-v1-your-key
ALIBABA_API_KEY=your-key
ALIBABA_API_SECRET=your-secret

# Security
LEXOS_SECRET_KEY=32-char-minimum-secret
JWT_SECRET_KEY=secure-jwt-secret
ALLOWED_ORIGINS=https://lexcommand.ai,https://www.lexcommand.ai

# Database
DATABASE_URL=sqlite:///data/lex_memory.db
SQLITE_WAL_MODE=true
SQLITE_CACHE_SIZE=10000

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_PER_HOUR=1000

# AWS (Optional for S3 backups)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
LEX_BACKUP_S3_BUCKET=your-bucket-name
```

### Nginx Production Configuration
- SSL/TLS with modern ciphers
- Security headers configured
- Rate limiting implemented
- Gzip compression enabled
- Upstream load balancing ready

---

## 🎯 Performance Benchmarks

### Target Metrics
- **Response Time**: < 500ms (p95)
- **Availability**: 99.9% uptime
- **Throughput**: 1000+ concurrent requests
- **Database**: < 100ms query time
- **Deployment**: < 5 minutes
- **Rollback**: < 2 minutes

### Current Performance
- **Security**: ✅ Hardened
- **Rate Limiting**: ✅ Active (100/min)
- **Database**: ✅ Optimized with indexes
- **Monitoring**: ✅ Real-time metrics
- **Backups**: ✅ Automated hourly/daily
- **Deployment**: ✅ Zero-downtime ready

---

## 🚨 Troubleshooting

### Common Issues

**1. Service Won't Start**
```bash
# Check logs
tail -f lex_production.log
tail -f lex.log

# Verify environment
python3 -c "from security_config import security_config"

# Check database
python3 database_optimizer.py --stats
```

**2. Deployment Fails**
```bash
# Check deployment status
python3 blue_green_deployment.py --status

# View deployment logs
tail -f deployment.log

# Manual rollback
python3 blue_green_deployment.py --rollback
```

**3. High Memory Usage**
```bash
# Monitor system resources
python3 production_monitor.py --report

# Check database size
ls -lh lex_memory.db

# Vacuum database
python3 database_optimizer.py --vacuum
```

**4. API Errors**
```bash
# Check health endpoint
curl -I http://localhost:8000/health

# Test API endpoint
curl -X POST http://localhost:8000/api/v1/lex \
  -H "Content-Type: application/json" \
  -d '{"message":"test","voice_mode":false}'

# Check rate limiting
curl -I http://localhost:8000/health
# (Make multiple rapid requests to test)
```

---

## 📈 Monitoring & Alerts

### Log Locations
- **Main Server**: `lex_production.log`
- **Security Events**: `lex.log`  
- **Database**: `database_optimizer.log`
- **Backup Operations**: `backup.log`
- **Deployments**: `deployment.log`
- **Monitoring**: `monitor.log`

### Health Check Endpoints
- **System Health**: `GET /health`
- **API Status**: `POST /api/v1/lex` (with test payload)
- **Database**: Direct SQLite connection test
- **Security Headers**: Header presence validation

### Alert Conditions
- CPU usage > 80%
- Memory usage > 85%
- Disk usage > 90%
- Response time > 5 seconds
- Error rate > 10%
- Service unavailability

---

## 🔐 Security Checklist

### ✅ Completed
- [x] Environment variable validation
- [x] Input sanitization and validation
- [x] Rate limiting implementation
- [x] Security headers configured
- [x] CORS restricted to production domains
- [x] Request logging and monitoring
- [x] Database access controls
- [x] Error handling without information leakage

### 🎯 Additional Security Measures
- [ ] JWT authentication system
- [ ] API key rotation mechanism  
- [ ] Intrusion detection system
- [ ] Web Application Firewall (WAF)
- [ ] SSL certificate monitoring
- [ ] Security scan automation

---

## 📞 Support & Maintenance

### Regular Maintenance Tasks

**Daily:**
- Check backup completion
- Review error logs
- Monitor system resources
- Verify service health

**Weekly:**  
- Database vacuum and optimization
- Log rotation and cleanup
- Security update review
- Performance metric analysis

**Monthly:**
- Full system backup verification
- Security audit
- Capacity planning review
- Disaster recovery testing

### Emergency Contacts
- **System Administrator**: Check deployment logs
- **Database Issues**: Run database optimizer
- **Security Incidents**: Review security logs
- **Performance Issues**: Check monitoring dashboard

---

## 🎉 Deployment Success Criteria

### ✅ Phase 1 Complete
- Security hardening implemented
- Production stability achieved
- Monitoring and alerting active
- Database optimized and indexed

### 🚀 Phase 2B In Progress  
- Docker containerization ready
- Automated backup system operational
- Blue-green deployment configured
- Zero-downtime deployment capability

### 🎯 Next Phase Options
- **Phase 2A**: Advanced performance optimization
- **Phase 2C**: Feature enhancement and UI optimization
- **Phase 3**: Scalability and multi-region deployment

---

**🔱 JAI MAHAKAAL! LEX PRODUCTION SYSTEM READY 🔱**

*Generated: August 2025 | Version: 2.0-infrastructure-hardened*