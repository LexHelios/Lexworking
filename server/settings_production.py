
"""
Production Settings Configuration
Enhanced settings with security, monitoring, and H100 GPU optimization
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
import os
import secrets
from pathlib import Path

class ProductionSettings(BaseModel):
    """Production-ready settings with comprehensive configuration"""

    model_config = {
        "extra": "allow", 
        "env_file": ".env.production",
        "env_file_encoding": "utf-8",
        "case_sensitive": True
    }

    # ============================================================================
    # CORE SERVER CONFIGURATION
    # ============================================================================
    HOST: str = Field(default="0.0.0.0", env="LEXOS_HOST")
    PORT: int = Field(default=8000, env="LEXOS_PORT")
    DEBUG: bool = Field(default=False, env="LEXOS_DEBUG")
    LOG_LEVEL: str = Field(default="INFO", env="LEXOS_LOG_LEVEL")
    WORKERS: int = Field(default=4, env="LEXOS_WORKERS")
    MAX_WORKERS: int = Field(default=8, env="LEXOS_MAX_WORKERS")
    WORKER_TIMEOUT: int = Field(default=300, env="LEXOS_WORKER_TIMEOUT")
    KEEPALIVE: int = Field(default=2, env="LEXOS_KEEPALIVE")
    
    # ============================================================================
    # SECURITY CONFIGURATION
    # ============================================================================
    SECRET_KEY: str = Field(env="LEXOS_SECRET_KEY")
    JWT_ALGORITHM: str = Field(default="HS256", env="LEXOS_JWT_ALGORITHM")
    JWT_EXPIRATION_HOURS: int = Field(default=24, env="LEXOS_JWT_EXPIRATION_HOURS")
    JWT_REFRESH_EXPIRATION_DAYS: int = Field(default=7, env="LEXOS_JWT_REFRESH_EXPIRATION_DAYS")
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = Field(
        default=["https://lexos.ai", "https://api.lexos.ai"],
        env="LEXOS_CORS_ORIGINS"
    )
    ALLOWED_HOSTS: List[str] = Field(
        default=["lexos.ai", "api.lexos.ai"],
        env="LEXOS_ALLOWED_HOSTS"
    )
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = Field(default=60, env="RATE_LIMIT_REQUESTS_PER_MINUTE")
    RATE_LIMIT_BURST: int = Field(default=10, env="RATE_LIMIT_BURST")
    
    # SSL/TLS Configuration
    SSL_ENABLED: bool = Field(default=True, env="SSL_ENABLED")
    SSL_CERT_PATH: str = Field(default="/etc/ssl/certs/lexos.crt", env="SSL_CERT_PATH")
    SSL_KEY_PATH: str = Field(default="/etc/ssl/private/lexos.key", env="SSL_KEY_PATH")
    SSL_CA_PATH: str = Field(default="/etc/ssl/certs/ca-bundle.crt", env="SSL_CA_PATH")
    FORCE_HTTPS: bool = Field(default=True, env="FORCE_HTTPS")
    
    # Security Headers
    SECURITY_HEADERS_ENABLED: bool = Field(default=True, env="SECURITY_HEADERS_ENABLED")
    HSTS_MAX_AGE: int = Field(default=31536000, env="HSTS_MAX_AGE")
    HSTS_INCLUDE_SUBDOMAINS: bool = Field(default=True, env="HSTS_INCLUDE_SUBDOMAINS")
    HSTS_PRELOAD: bool = Field(default=True, env="HSTS_PRELOAD")
    CONTENT_SECURITY_POLICY: str = Field(
        default="default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' https:; connect-src 'self' wss: https:;",
        env="CONTENT_SECURITY_POLICY"
    )
    X_FRAME_OPTIONS: str = Field(default="DENY", env="X_FRAME_OPTIONS")
    X_CONTENT_TYPE_OPTIONS: str = Field(default="nosniff", env="X_CONTENT_TYPE_OPTIONS")
    REFERRER_POLICY: str = Field(default="strict-origin-when-cross-origin", env="REFERRER_POLICY")
    
    # ============================================================================
    # DATABASE & STORAGE CONFIGURATION
    # ============================================================================
    # Redis Configuration
    REDIS_URL: str = Field(env="REDIS_URL")
    REDIS_PASSWORD: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")
    REDIS_MAX_CONNECTIONS: int = Field(default=100, env="REDIS_MAX_CONNECTIONS")
    REDIS_RETRY_ON_TIMEOUT: bool = Field(default=True, env="REDIS_RETRY_ON_TIMEOUT")
    REDIS_SOCKET_KEEPALIVE: bool = Field(default=True, env="REDIS_SOCKET_KEEPALIVE")
    
    # Vector Database (Milvus)
    MILVUS_HOST: str = Field(default="milvus-cluster", env="MILVUS_HOST")
    MILVUS_PORT: int = Field(default=19530, env="MILVUS_PORT")
    MILVUS_USER: Optional[str] = Field(default=None, env="MILVUS_USER")
    MILVUS_PASSWORD: Optional[str] = Field(default=None, env="MILVUS_PASSWORD")
    MILVUS_SECURE: bool = Field(default=True, env="MILVUS_SECURE")
    
    # PostgreSQL Configuration
    DATABASE_URL: str = Field(env="DATABASE_URL")
    DB_POOL_SIZE: int = Field(default=20, env="DB_POOL_SIZE")
    DB_MAX_OVERFLOW: int = Field(default=30, env="DB_MAX_OVERFLOW")
    DB_POOL_TIMEOUT: int = Field(default=30, env="DB_POOL_TIMEOUT")
    DB_POOL_RECYCLE: int = Field(default=3600, env="DB_POOL_RECYCLE")
    
    # Storage Configuration
    DATA_DIR: str = Field(default="/app/data", env="DATA_DIR")
    MODELS_DIR: str = Field(default="/app/models", env="MODELS_DIR")
    LOGS_DIR: str = Field(default="/app/logs", env="LOGS_DIR")
    UPLOAD_MAX_SIZE: str = Field(default="100MB", env="UPLOAD_MAX_SIZE")
    STORAGE_BACKEND: str = Field(default="s3", env="STORAGE_BACKEND")
    S3_BUCKET: Optional[str] = Field(default=None, env="S3_BUCKET")
    S3_REGION: Optional[str] = Field(default=None, env="S3_REGION")
    S3_ACCESS_KEY: Optional[str] = Field(default=None, env="S3_ACCESS_KEY")
    S3_SECRET_KEY: Optional[str] = Field(default=None, env="S3_SECRET_KEY")
    
    # ============================================================================
    # H100 GPU CONFIGURATION
    # ============================================================================
    # CUDA Configuration
    CUDA_VISIBLE_DEVICES: str = Field(default="0,1,2,3,4,5,6,7", env="CUDA_VISIBLE_DEVICES")
    CUDA_MEMORY_FRACTION: float = Field(default=0.9, env="CUDA_MEMORY_FRACTION")
    CUDA_ALLOW_GROWTH: bool = Field(default=True, env="CUDA_ALLOW_GROWTH")
    NCCL_DEBUG: str = Field(default="INFO", env="NCCL_DEBUG")
    NCCL_IB_DISABLE: int = Field(default=0, env="NCCL_IB_DISABLE")
    NCCL_NET_GDR_LEVEL: int = Field(default=2, env="NCCL_NET_GDR_LEVEL")
    
    # vLLM Configuration
    VLLM_HOST: str = Field(default="localhost", env="VLLM_HOST")
    VLLM_PORT: int = Field(default=8001, env="VLLM_PORT")
    VLLM_MODEL: str = Field(default="meta-llama/Llama-2-70b-chat-hf", env="VLLM_MODEL")
    VLLM_GPU_MEMORY_UTILIZATION: float = Field(default=0.85, env="VLLM_GPU_MEMORY_UTILIZATION")
    VLLM_MAX_MODEL_LEN: int = Field(default=8192, env="VLLM_MAX_MODEL_LEN")
    VLLM_TENSOR_PARALLEL_SIZE: int = Field(default=8, env="VLLM_TENSOR_PARALLEL_SIZE")
    VLLM_PIPELINE_PARALLEL_SIZE: int = Field(default=1, env="VLLM_PIPELINE_PARALLEL_SIZE")
    VLLM_MAX_NUM_SEQS: int = Field(default=256, env="VLLM_MAX_NUM_SEQS")
    VLLM_MAX_NUM_BATCHED_TOKENS: int = Field(default=8192, env="VLLM_MAX_NUM_BATCHED_TOKENS")
    VLLM_BLOCK_SIZE: int = Field(default=16, env="VLLM_BLOCK_SIZE")
    VLLM_SWAP_SPACE: int = Field(default=4, env="VLLM_SWAP_SPACE")
    VLLM_ENFORCE_EAGER: bool = Field(default=False, env="VLLM_ENFORCE_EAGER")
    VLLM_MAX_CONTEXT_LEN_TO_CAPTURE: int = Field(default=8192, env="VLLM_MAX_CONTEXT_LEN_TO_CAPTURE")
    
    # GPU Health Monitoring
    GPU_HEALTH_CHECK_INTERVAL: int = Field(default=30, env="GPU_HEALTH_CHECK_INTERVAL")
    GPU_MEMORY_THRESHOLD: float = Field(default=0.95, env="GPU_MEMORY_THRESHOLD")
    GPU_TEMPERATURE_THRESHOLD: int = Field(default=85, env="GPU_TEMPERATURE_THRESHOLD")
    GPU_UTILIZATION_THRESHOLD: float = Field(default=0.95, env="GPU_UTILIZATION_THRESHOLD")
    
    # ============================================================================
    # API KEYS & EXTERNAL SERVICES
    # ============================================================================
    TOGETHER_API_KEY: Optional[str] = Field(default=None, env="TOGETHER_API_KEY")
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    ELEVENLABS_API_KEY: Optional[str] = Field(default=None, env="ELEVENLABS_API_KEY")
    DEEPSEEK_API_KEY: Optional[str] = Field(default=None, env="DEEPSEEK_API_KEY")
    DEEPGRAM_API_KEY: Optional[str] = Field(default=None, env="DEEPGRAM_API_KEY")
    GROQ_API_KEY: Optional[str] = Field(default=None, env="GROQ_API_KEY")
    OPENROUTER_API_KEY: Optional[str] = Field(default=None, env="OPENROUTER_API_KEY")
    PERPLEXITY_API_KEY: Optional[str] = Field(default=None, env="PERPLEXITY_API_KEY")
    COHERE_API_KEY: Optional[str] = Field(default=None, env="COHERE_API_KEY")
    GEMINI_API_KEY: Optional[str] = Field(default=None, env="GEMINI_API_KEY")
    GLM_API_KEY: Optional[str] = Field(default=None, env="GLM_API_KEY")
    ALIBABA_API_KEY: Optional[str] = Field(default=None, env="ALIBABA_API_KEY")
    REPLICATE_API_TOKEN: Optional[str] = Field(default=None, env="REPLICATE_API_TOKEN")
    STABILITY_API_KEY: Optional[str] = Field(default=None, env="STABILITY_API_KEY")
    
    # ============================================================================
    # MONITORING & OBSERVABILITY
    # ============================================================================
    # Prometheus Configuration
    PROMETHEUS_ENABLED: bool = Field(default=True, env="PROMETHEUS_ENABLED")
    PROMETHEUS_PORT: int = Field(default=8002, env="PROMETHEUS_PORT")
    PROMETHEUS_METRICS_PATH: str = Field(default="/metrics", env="PROMETHEUS_METRICS_PATH")
    PROMETHEUS_SCRAPE_INTERVAL: str = Field(default="15s", env="PROMETHEUS_SCRAPE_INTERVAL")
    
    # Grafana Configuration
    GRAFANA_ENABLED: bool = Field(default=True, env="GRAFANA_ENABLED")
    GRAFANA_PORT: int = Field(default=3000, env="GRAFANA_PORT")
    GRAFANA_ADMIN_USER: str = Field(default="admin", env="GRAFANA_ADMIN_USER")
    GRAFANA_ADMIN_PASSWORD: str = Field(env="GRAFANA_ADMIN_PASSWORD")
    
    # Logging Configuration
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")
    LOG_ROTATION: bool = Field(default=True, env="LOG_ROTATION")
    LOG_MAX_SIZE: str = Field(default="100MB", env="LOG_MAX_SIZE")
    LOG_BACKUP_COUNT: int = Field(default=10, env="LOG_BACKUP_COUNT")
    LOG_COMPRESSION: bool = Field(default=True, env="LOG_COMPRESSION")
    STRUCTURED_LOGGING: bool = Field(default=True, env="STRUCTURED_LOGGING")
    
    # OpenTelemetry Configuration
    OTEL_ENABLED: bool = Field(default=True, env="OTEL_ENABLED")
    OTEL_SERVICE_NAME: str = Field(default="lexos-api", env="OTEL_SERVICE_NAME")
    OTEL_SERVICE_VERSION: str = Field(default="2.0.0", env="OTEL_SERVICE_VERSION")
    OTEL_EXPORTER_OTLP_ENDPOINT: str = Field(
        default="http://jaeger:14268/api/traces", 
        env="OTEL_EXPORTER_OTLP_ENDPOINT"
    )
    OTEL_RESOURCE_ATTRIBUTES: str = Field(
        default="service.name=lexos-api,service.version=2.0.0",
        env="OTEL_RESOURCE_ATTRIBUTES"
    )
    
    # Health Checks
    HEALTH_CHECK_ENABLED: bool = Field(default=True, env="HEALTH_CHECK_ENABLED")
    HEALTH_CHECK_INTERVAL: int = Field(default=30, env="HEALTH_CHECK_INTERVAL")
    HEALTH_CHECK_TIMEOUT: int = Field(default=10, env="HEALTH_CHECK_TIMEOUT")
    READINESS_CHECK_ENABLED: bool = Field(default=True, env="READINESS_CHECK_ENABLED")
    LIVENESS_CHECK_ENABLED: bool = Field(default=True, env="LIVENESS_CHECK_ENABLED")
    
    # ============================================================================
    # PERFORMANCE & SCALING
    # ============================================================================
    # Connection Pooling
    CONNECTION_POOL_SIZE: int = Field(default=50, env="CONNECTION_POOL_SIZE")
    CONNECTION_POOL_MAX_OVERFLOW: int = Field(default=100, env="CONNECTION_POOL_MAX_OVERFLOW")
    CONNECTION_POOL_TIMEOUT: int = Field(default=30, env="CONNECTION_POOL_TIMEOUT")
    CONNECTION_POOL_RECYCLE: int = Field(default=3600, env="CONNECTION_POOL_RECYCLE")
    
    # Caching Configuration
    CACHE_ENABLED: bool = Field(default=True, env="CACHE_ENABLED")
    CACHE_TTL: int = Field(default=3600, env="CACHE_TTL")
    CACHE_MAX_SIZE: int = Field(default=1000, env="CACHE_MAX_SIZE")
    CACHE_BACKEND: str = Field(default="redis", env="CACHE_BACKEND")
    
    # Background Tasks
    CELERY_BROKER_URL: str = Field(env="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = Field(env="CELERY_RESULT_BACKEND")
    CELERY_WORKER_CONCURRENCY: int = Field(default=4, env="CELERY_WORKER_CONCURRENCY")
    CELERY_TASK_SOFT_TIME_LIMIT: int = Field(default=300, env="CELERY_TASK_SOFT_TIME_LIMIT")
    CELERY_TASK_TIME_LIMIT: int = Field(default=600, env="CELERY_TASK_TIME_LIMIT")
    
    # ============================================================================
    # MOBILE APP CONFIGURATION
    # ============================================================================
    MOBILE_API_BASE_URL: str = Field(default="https://api.lexos.ai", env="MOBILE_API_BASE_URL")
    MOBILE_WS_URL: str = Field(default="wss://api.lexos.ai/ws", env="MOBILE_WS_URL")
    MOBILE_CDN_URL: str = Field(default="https://cdn.lexos.ai", env="MOBILE_CDN_URL")
    MOBILE_SENTRY_DSN: Optional[str] = Field(default=None, env="MOBILE_SENTRY_DSN")
    MOBILE_ANALYTICS_KEY: Optional[str] = Field(default=None, env="MOBILE_ANALYTICS_KEY")
    
    @validator("SECRET_KEY")
    def validate_secret_key(cls, v):
        """Validate secret key strength"""
        if not v or v == "your-secret-key-change-in-production":
            raise ValueError("SECRET_KEY must be set to a secure random value in production")
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v
    
    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list"""
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("ALLOWED_HOSTS", pre=True)
    def parse_allowed_hosts(cls, v):
        """Parse allowed hosts from string or list"""
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [host.strip() for host in v.split(",")]
        return v
    
    def create_directories(self):
        """Create necessary directories"""
        for dir_path in [self.DATA_DIR, self.MODELS_DIR, self.LOGS_DIR]:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    @property
    def redis_config(self) -> Dict[str, Any]:
        """Get Redis configuration"""
        config = {
            "url": self.REDIS_URL,
            "db": self.REDIS_DB,
            "max_connections": self.REDIS_MAX_CONNECTIONS,
            "retry_on_timeout": self.REDIS_RETRY_ON_TIMEOUT,
            "socket_keepalive": self.REDIS_SOCKET_KEEPALIVE,
        }
        if self.REDIS_PASSWORD:
            config["password"] = self.REDIS_PASSWORD
        return config
    
    @property
    def database_config(self) -> Dict[str, Any]:
        """Get database configuration"""
        return {
            "url": self.DATABASE_URL,
            "pool_size": self.DB_POOL_SIZE,
            "max_overflow": self.DB_MAX_OVERFLOW,
            "pool_timeout": self.DB_POOL_TIMEOUT,
            "pool_recycle": self.DB_POOL_RECYCLE,
        }
    
    @property
    def vllm_config(self) -> Dict[str, Any]:
        """Get vLLM configuration for H100"""
        return {
            "host": self.VLLM_HOST,
            "port": self.VLLM_PORT,
            "model": self.VLLM_MODEL,
            "gpu_memory_utilization": self.VLLM_GPU_MEMORY_UTILIZATION,
            "max_model_len": self.VLLM_MAX_MODEL_LEN,
            "tensor_parallel_size": self.VLLM_TENSOR_PARALLEL_SIZE,
            "pipeline_parallel_size": self.VLLM_PIPELINE_PARALLEL_SIZE,
            "max_num_seqs": self.VLLM_MAX_NUM_SEQS,
            "max_num_batched_tokens": self.VLLM_MAX_NUM_BATCHED_TOKENS,
            "block_size": self.VLLM_BLOCK_SIZE,
            "swap_space": self.VLLM_SWAP_SPACE,
            "enforce_eager": self.VLLM_ENFORCE_EAGER,
            "max_context_len_to_capture": self.VLLM_MAX_CONTEXT_LEN_TO_CAPTURE,
        }


# Global settings instance
settings = ProductionSettings()

# Create necessary directories on import
settings.create_directories()
