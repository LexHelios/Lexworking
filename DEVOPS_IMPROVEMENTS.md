# DevOps & Deployment Improvements

## Current Deployment Issues

### Problems Identified:
1. **Hardcoded API Keys** in deployment scripts
2. **No Container Strategy** - Missing Docker implementation
3. **Manual Deployment** - No CI/CD pipeline
4. **No Environment Management** - Development/staging/production not separated
5. **Missing Monitoring** - No observability stack
6. **No Backup Strategy** - Data loss risk

## Recommended DevOps Strategy

### 1. Containerization with Docker

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash lexos
RUN chown -R lexos:lexos /app
USER lexos

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  lexos-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379
      - MILVUS_HOST=milvus
    depends_on:
      - redis
      - milvus
    volumes:
      - ./data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  milvus:
    image: milvusdb/milvus:latest
    ports:
      - "19530:19530"
    environment:
      - ETCD_ENDPOINTS=etcd:2379
      - MINIO_ADDRESS=minio:9000
    depends_on:
      - etcd
      - minio
    volumes:
      - milvus_data:/var/lib/milvus
    restart: unless-stopped

  etcd:
    image: quay.io/coreos/etcd:latest
    environment:
      - ETCD_AUTO_COMPACTION_MODE=revision
      - ETCD_AUTO_COMPACTION_RETENTION=1000
    volumes:
      - etcd_data:/etcd
    restart: unless-stopped

  minio:
    image: minio/minio:latest
    environment:
      - MINIO_ACCESS_KEY=minioadmin
      - MINIO_SECRET_KEY=minioadmin
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/data
    command: minio server /data --console-address ":9001"
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - lexos-api
    restart: unless-stopped

volumes:
  redis_data:
  milvus_data:
  etcd_data:
  minio_data:
```

### 2. Environment Management

```bash
# environments/development/.env
LEXOS_DEBUG=true
LEXOS_LOG_LEVEL=DEBUG
MOCK_EXTERNAL_APIS=true

# environments/staging/.env
LEXOS_DEBUG=false
LEXOS_LOG_LEVEL=INFO
MOCK_EXTERNAL_APIS=false

# environments/production/.env
LEXOS_DEBUG=false
LEXOS_LOG_LEVEL=WARNING
MOCK_EXTERNAL_APIS=false
```

```yaml
# docker-compose.override.yml (for development)
version: '3.8'

services:
  lexos-api:
    volumes:
      - .:/app
    environment:
      - LEXOS_DEBUG=true
    command: ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

### 3. CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml
name: Deploy LexOS

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      redis:
        image: redis:alpine
        ports:
          - 6379:6379
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-asyncio pytest-cov
    
    - name: Run tests
      run: |
        pytest tests/ -v --cov=server --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3

  security-scan:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Run security scan
      uses: securecodewarrior/github-action-add-sarif@v1
      with:
        sarif-file: 'security-scan-results.sarif'

  build:
    needs: [test, security-scan]
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Log in to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v4
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=sha
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    
    steps:
    - name: Deploy to staging
      run: |
        echo "Deploying to staging environment"
        # Add staging deployment commands

  deploy-production:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - name: Deploy to production
      run: |
        echo "Deploying to production environment"
        # Add production deployment commands
```

### 4. Infrastructure as Code

```yaml
# kubernetes/deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: lexos-api
  labels:
    app: lexos-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: lexos-api
  template:
    metadata:
      labels:
        app: lexos-api
    spec:
      containers:
      - name: lexos-api
        image: ghcr.io/your-org/lexos:latest
        ports:
        - containerPort: 8000
        env:
        - name: REDIS_URL
          value: "redis://redis-service:6379"
        - name: MILVUS_HOST
          value: "milvus-service"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: lexos-api-service
spec:
  selector:
    app: lexos-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

### 5. Monitoring & Observability

```yaml
# monitoring/docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./grafana/datasources:/etc/grafana/provisioning/datasources

  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"
      - "14268:14268"
    environment:
      - COLLECTOR_OTLP_ENABLED=true

  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"
    volumes:
      - ./loki-config.yml:/etc/loki/local-config.yaml
    command: -config.file=/etc/loki/local-config.yaml

  promtail:
    image: grafana/promtail:latest
    volumes:
      - /var/log:/var/log:ro
      - ./promtail-config.yml:/etc/promtail/config.yml
    command: -config.file=/etc/promtail/config.yml

volumes:
  prometheus_data:
  grafana_data:
```

### 6. Backup & Disaster Recovery

```bash
#!/bin/bash
# scripts/backup.sh

set -e

BACKUP_DIR="/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "Starting LexOS backup..."

# Backup database
echo "Backing up LMDB database..."
tar -czf "$BACKUP_DIR/lmdb_backup.tar.gz" data/lmdb/

# Backup vector store
echo "Backing up vector store..."
docker exec milvus-container /opt/milvus/bin/milvus-backup create \
  --collection-name lexos_vectors \
  --backup-name "backup_$(date +%Y%m%d_%H%M%S)"

# Backup configuration
echo "Backing up configuration..."
cp -r environments/ "$BACKUP_DIR/"
cp docker-compose.yml "$BACKUP_DIR/"

# Upload to cloud storage (example with AWS S3)
if [ "$ENABLE_CLOUD_BACKUP" = "true" ]; then
  echo "Uploading to cloud storage..."
  aws s3 sync "$BACKUP_DIR" "s3://$BACKUP_BUCKET/lexos-backups/$(basename $BACKUP_DIR)/"
fi

echo "Backup completed: $BACKUP_DIR"

# Cleanup old backups (keep last 30 days)
find /backups -type d -mtime +30 -exec rm -rf {} \;
```

### 7. Security Hardening

```dockerfile
# Dockerfile.production
FROM python:3.11-slim

# Security updates
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    gcc g++ curl && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r lexos && useradd -r -g lexos lexos

# Set secure permissions
WORKDIR /app
COPY --chown=lexos:lexos . .
RUN chmod -R 755 /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Switch to non-root user
USER lexos

# Security headers
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 8. Performance Monitoring

```python
# monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import Request, Response
import time

# Metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
ACTIVE_CONNECTIONS = Gauge('websocket_connections_active', 'Active WebSocket connections')
MEMORY_USAGE = Gauge('memory_usage_bytes', 'Memory usage in bytes')

async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_DURATION.observe(time.time() - start_time)
    
    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

This comprehensive DevOps strategy will provide:
- **Scalable Infrastructure** with container orchestration
- **Automated Deployments** with CI/CD pipelines
- **Comprehensive Monitoring** with observability stack
- **Disaster Recovery** with automated backups
- **Security Hardening** with best practices
- **Environment Management** for different deployment stages