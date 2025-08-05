# LEX Production Server - Complete Multi-Model AI Orchestration
🔱 JAI MAHAKAAL! Production-Ready AI Platform 🔱

## Overview

The LEX Production Server is a comprehensive AI orchestration platform that integrates multiple state-of-the-art models for various AI capabilities. This production-ready implementation provides:

- **Multi-Model Orchestration**: Intelligent routing between different AI models
- **Complete AI Capabilities**: Chat, vision, coding, image/video generation, document parsing
- **Production Infrastructure**: Error handling, logging, monitoring, caching
- **Scalable Architecture**: WebSocket support, async processing, distributed memory
- **GPU Optimization**: NVIDIA TensorRT, vLLM, Ollama integration

## Architecture

### Core Components

1. **Production Orchestrator** (`server/orchestrator/production_orchestrator.py`)
   - Manages all AI models with intelligent routing
   - Handles fallback and recovery strategies
   - Performance tracking and optimization

2. **Main Server** (`simple_lex_server_production.py`)
   - FastAPI-based production server
   - WebSocket support for real-time communication
   - Comprehensive API endpoints for all capabilities
   - Enhanced file management with caching

3. **Error Handler** (`server/utils/error_handler.py`)
   - Comprehensive error management
   - Recovery strategies for different error types
   - Circuit breaker implementation
   - Performance metrics logging

### Model Integration

| Capability Area | Primary Model | Secondary Model | Features |
|----------------|---------------|-----------------|----------|
| Chat & Reasoning | Mistral-8x22B (Mixtral) | Llama 4 Scout | General conversation, complex reasoning |
| Long-Context | Llama 4 Scout | - | 256K context window |
| Vision & OCR | Qwen2.5-VL | Llava-v1.6 | Image analysis, document understanding |
| Document Parsing | Nougat | Qwen2.5-VL | PDF/document extraction |
| Coding | DeepSeek-R1 | Mixtral | Code generation, debugging |
| Image Generation | Stable Diffusion XL | - | Text-to-image generation |
| Video Generation | Open-Sora | - | Text-to-video (experimental) |
| Search & Knowledge | Juggernaut XL | - | Advanced knowledge retrieval |
| Financial Modeling | DeepSeek-R1 | - | Financial analysis and modeling |

### Memory Systems

- **Milvus**: Vector database for semantic search
- **PostgreSQL**: Structured data and metadata
- **Redis**: High-performance caching

### GPU Optimization

- **NVIDIA NIM/TensorRT**: Optimized inference
- **vLLM**: High-throughput serving
- **Ollama**: Local model management

## Installation

### Prerequisites

- Ubuntu 20.04+ or similar Linux distribution
- Python 3.10+
- NVIDIA GPU with CUDA 11.8+ (recommended)
- 32GB+ RAM (64GB recommended)
- 500GB+ storage for models

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd LexWorking
   ```

2. **Run the deployment script**
   ```bash
   chmod +x deploy_production.sh
   ./deploy_production.sh production
   ```

3. **Configure API keys**
   Edit `.env.production` with your API keys:
   ```bash
   nano .env.production
   ```

4. **Start the server**
   ```bash
   sudo systemctl start lex-server
   ```

### Manual Installation

If you prefer manual setup:

```bash
# Create virtual environment
python3.10 -m venv venv_prod
source venv_prod/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup databases
# PostgreSQL
sudo -u postgres createdb lex_memory
sudo -u postgres createuser lex -P

# Redis
sudo apt install redis-server
sudo systemctl start redis

# Run the server
python simple_lex_server_production.py
```

## API Endpoints

### Core Endpoints

- `GET /` - Main web interface
- `GET /health` - Health check with detailed status
- `POST /api/v1/lex` - Main LEX interaction endpoint
- `POST /api/v1/lex/multimodal` - Multimodal input with file uploads
- `WebSocket /ws` - Real-time communication

### Specialized Endpoints

- `POST /api/v1/generate/image` - Image generation
- `POST /api/v1/generate/video` - Video generation  
- `POST /api/v1/generate/code` - Code generation
- `POST /api/v1/analyze/vision` - Vision analysis
- `POST /api/v1/analyze/document` - Document parsing

### Orchestrator Management

- `GET /api/v1/orchestrator/status` - Detailed orchestrator status
- `POST /api/v1/orchestrator/chat` - Direct orchestrator access

### IDE/File Operations

- `GET /api/v1/ide/files` - File tree
- `GET /api/v1/ide/file/{path}` - Read file
- `POST /api/v1/ide/file/{path}` - Write file
- `PUT /api/v1/ide/file/{path}` - Create file
- `DELETE /api/v1/ide/file/{path}` - Delete file

## Configuration

### Environment Variables

Key environment variables in `.env.production`:

```env
# Server Configuration
ENV=production
HOST=0.0.0.0
PORT=8000
WORKERS=4
LOG_LEVEL=info

# API Keys
OPENAI_API_KEY=your-key
ANTHROPIC_API_KEY=your-key
MISTRAL_API_KEY=your-key
DEEPSEEK_API_KEY=your-key
GROQ_API_KEY=your-key
STABILITY_API_KEY=your-key
QWEN_API_KEY=your-key

# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=lex
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=lex_memory

REDIS_URL=redis://localhost:6379

MILVUS_HOST=localhost
MILVUS_PORT=19530

# GPU Configuration
CUDA_VISIBLE_DEVICES=0
TORCH_CUDA_ARCH_LIST=7.0,7.5,8.0,8.6,8.9,9.0
```

### Nginx Configuration

The deployment script sets up Nginx as a reverse proxy. Configuration is at:
`/etc/nginx/sites-available/lex-server`

### Systemd Service

The server runs as a systemd service for automatic startup and management:
- Start: `sudo systemctl start lex-server`
- Stop: `sudo systemctl stop lex-server`
- Status: `sudo systemctl status lex-server`
- Logs: `journalctl -u lex-server -f`

## Performance Optimization

### GPU Optimization

1. **Enable persistence mode**:
   ```bash
   sudo nvidia-smi -pm 1
   ```

2. **Set power limit** (adjust based on your GPU):
   ```bash
   sudo nvidia-smi -pl 300
   ```

3. **Monitor GPU usage**:
   ```bash
   nvidia-smi dmon -s pucvmet
   ```

### System Optimization

The deployment script applies several system optimizations:
- Increased network buffer sizes
- Reduced swappiness for better memory performance
- TCP optimization for high-throughput

### Caching Strategy

- **File caching**: LRU cache for frequently accessed files
- **Redis caching**: API responses and intermediate results
- **Model caching**: Keep frequently used models in GPU memory

## Monitoring

### Logs

- **Application logs**: `logs/lex_server.log`
- **System logs**: `journalctl -u lex-server`
- **Nginx logs**: `/var/log/nginx/access.log` and `error.log`

### Metrics

The server exposes metrics at `/metrics` (when configured) for Prometheus scraping.

### Health Checks

Regular health checks available at `/health` provide:
- Component status
- Model availability
- Memory system status
- Request/error counts
- Performance metrics

## Scaling

### Horizontal Scaling

1. **Load Balancer**: Use Nginx or HAProxy
2. **Multiple Workers**: Increase `WORKERS` in environment
3. **Distributed Memory**: Configure Milvus cluster

### Vertical Scaling

1. **GPU**: Add more GPUs and set `CUDA_VISIBLE_DEVICES`
2. **RAM**: Increase for larger model loading
3. **Storage**: Use SSD/NVMe for model storage

## Security

### Best Practices

1. **API Keys**: Keep all API keys secure and rotate regularly
2. **HTTPS**: Use SSL certificates in production
3. **Firewall**: Configure firewall rules appropriately
4. **Authentication**: Implement authentication for production use
5. **Rate Limiting**: Configure rate limits in Nginx

### SSL Setup

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com
```

## Troubleshooting

### Common Issues

1. **GPU not detected**:
   ```bash
   # Check CUDA installation
   nvcc --version
   nvidia-smi
   ```

2. **Model download failures**:
   ```bash
   # Manually download models
   python -c "from huggingface_hub import snapshot_download; snapshot_download('model-name', 'local-path')"
   ```

3. **Memory errors**:
   - Reduce batch size
   - Use smaller models
   - Enable model offloading

4. **Database connection issues**:
   ```bash
   # Check PostgreSQL
   sudo systemctl status postgresql
   psql -U lex -d lex_memory
   
   # Check Redis
   redis-cli ping
   ```

### Debug Mode

Run in debug mode for detailed logging:
```bash
LOG_LEVEL=debug python simple_lex_server_production.py
```

## Development

### Running Tests

```bash
# Unit tests
pytest tests/

# Integration tests
pytest tests/integration/

# Performance tests
pytest tests/performance/ -v
```

### Adding New Models

1. Add model configuration in `production_orchestrator.py`
2. Implement model-specific handler
3. Register with capability mapping
4. Test thoroughly

### Contributing

1. Fork the repository
2. Create feature branch
3. Implement changes with tests
4. Submit pull request

## Support

For issues and questions:
- GitHub Issues: [repository-issues]
- Documentation: This README
- Logs: Check application and system logs

## License

[Your License Here]

---

🔱 JAI MAHAKAAL! May your AI serve with divine wisdom! 🔱