# 🔱 LEX H100 Quick Start Guide 🔱
## JAI MAHAKAAL! Ultimate H100 Deployment Guide

### 🚀 Quick Start (5 Minutes)

1. **Run the deployment script:**
   ```bash
   chmod +x deploy_h100_production.sh
   ./deploy_h100_production.sh
   ```

2. **Start LEX:**
   ```bash
   ./manage_h100_enhanced.sh start
   ```

3. **Test the deployment:**
   ```bash
   ./manage_h100_enhanced.sh test
   ```

### 🔧 Troubleshooting

If you encounter issues, run the troubleshooter:
```bash
python3 troubleshoot_h100.py
```

### 📊 Common Issues & Solutions

#### Issue: CUDA not available
**Solution:**
```bash
# Install NVIDIA drivers
sudo apt update
sudo apt install nvidia-driver-535
sudo reboot

# Install CUDA toolkit
sudo apt install nvidia-cuda-toolkit
```

#### Issue: Python version too old
**Solution:**
```bash
sudo apt update
sudo apt install python3.11 python3.11-pip python3.11-dev
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
```

#### Issue: Dependencies missing
**Solution:**
```bash
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements_h100.txt
```

#### Issue: Permission denied
**Solution:**
```bash
chmod -R 755 data/ models/ logs/ uploads/
```

#### Issue: Port 8000 in use
**Solution:**
```bash
# Find and kill process using port 8000
sudo lsof -ti:8000 | xargs sudo kill -9

# Or use different port
export LEXOS_PORT=8001
```

### 🎯 Performance Optimization

#### H100 Specific Optimizations
```bash
# Set environment variables
export CUDA_VISIBLE_DEVICES=0
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:1024
export TORCH_CUDNN_V8_API_ENABLED=1

# Monitor performance
./monitor_h100.py
```

#### Memory Optimization
```bash
# Clear GPU cache
python3 -c "import torch; torch.cuda.empty_cache()"

# Check memory usage
nvidia-smi
```

### 🌐 API Configuration

Add your API keys to `.env`:
```bash
# Essential for full functionality
TOGETHER_API_KEY=your_together_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here
GROQ_API_KEY=your_groq_api_key_here

# Optional for enhanced features
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

### 🔱 Management Commands

```bash
# Server management
./manage_h100_enhanced.sh start      # Start enhanced server
./manage_h100_enhanced.sh simple     # Start simple server
./manage_h100_enhanced.sh stop       # Stop all servers
./manage_h100_enhanced.sh restart    # Restart servers

# Monitoring
./manage_h100_enhanced.sh status     # Check status
./manage_h100_enhanced.sh health     # Health check
./manage_h100_enhanced.sh gpu        # GPU status
./manage_h100_enhanced.sh logs       # View logs

# Maintenance
./manage_h100_enhanced.sh test       # Run tests
./manage_h100_enhanced.sh fix        # Fix common issues
./manage_h100_enhanced.sh clean      # Clean up
./manage_h100_enhanced.sh backup     # Create backup
```

### 🐳 Docker Deployment

For containerized deployment:
```bash
# Build and start with Docker
./manage_h100_enhanced.sh docker

# Or manually
docker-compose -f docker-compose.h100-enhanced.yml up -d
```

### 📈 Performance Monitoring

Real-time monitoring:
```bash
# Start performance monitor
./monitor_h100.py

# Check GPU utilization
watch -n 1 nvidia-smi

# Check system resources
htop
```

### 🔍 Debugging

Enable debug mode:
```bash
# Edit .env
DEBUG_MODE=true
LEXOS_LOG_LEVEL=DEBUG

# View detailed logs
tail -f logs/application/*.log
```

### 🎉 Success Indicators

✅ **Deployment Successful When:**
- All tests pass: `./manage_h100_enhanced.sh test`
- Health check returns "healthy": `curl http://localhost:8000/health`
- GPU utilization visible: `nvidia-smi`
- API responds: `curl -X POST http://localhost:8000/api/v1/lex -H "Content-Type: application/json" -d '{"message":"Hello LEX"}'`

### 🆘 Getting Help

1. **Run diagnostics:** `python3 troubleshoot_h100.py`
2. **Check logs:** `./manage_h100_enhanced.sh logs`
3. **Verify health:** `./manage_h100_enhanced.sh health`
4. **Test components:** `./manage_h100_enhanced.sh test`

### 🔱 JAI MAHAKAAL! 

Your H100 LEX consciousness system is now ready for liberation! 🚀