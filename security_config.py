#!/usr/bin/env python3
"""
Security Configuration for LEX Production System
🔱 JAI MAHAKAAL! Production-ready security hardening
"""
import os
import logging
import hashlib
import secrets
from typing import Optional, List
from functools import wraps
from datetime import datetime, timedelta

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

class SecurityConfig:
    """Production security configuration"""
    
    def __init__(self):
        self.validate_environment()
        self.setup_security_defaults()
    
    def validate_environment(self):
        """Validate critical environment variables"""
        required_vars = [
            'OPENROUTER_API_KEY',
            'LEXOS_SECRET_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"❌ Missing critical environment variables: {missing_vars}")
            raise EnvironmentError(f"Missing required environment variables: {missing_vars}")
        
        # Validate key strength
        secret_key = os.getenv('LEXOS_SECRET_KEY', '')
        if len(secret_key) < 32:
            logger.warning("⚠️ LEXOS_SECRET_KEY should be at least 32 characters long")
        
        logger.info("✅ Environment validation passed")
    
    def setup_security_defaults(self):
        """Setup security defaults"""
        self.allowed_origins = self._get_allowed_origins()
        self.rate_limits = self._get_rate_limits()
        self.security_headers = self._get_security_headers()
        self.request_timeout = int(os.getenv('REQUEST_TIMEOUT', '30'))
        
    def _get_allowed_origins(self) -> List[str]:
        """Get allowed CORS origins"""
        origins_str = os.getenv('ALLOWED_ORIGINS', 'https://lexcommand.ai,https://www.lexcommand.ai')
        origins = [origin.strip() for origin in origins_str.split(',')]
        
        # Add localhost for development if not in strict production mode
        if os.getenv('ENV') != 'production':
            origins.extend(['http://localhost:3000', 'http://127.0.0.1:3000'])
        
        logger.info(f"✅ CORS origins configured: {origins}")
        return origins
    
    def _get_rate_limits(self) -> dict:
        """Get rate limiting configuration"""
        return {
            'per_minute': int(os.getenv('RATE_LIMIT_PER_MINUTE', '100')),
            'per_hour': int(os.getenv('RATE_LIMIT_PER_HOUR', '1000')),
            'enabled': os.getenv('ENABLE_RATE_LIMITING', 'true').lower() == 'true'
        }
    
    def _get_security_headers(self) -> dict:
        """Get security headers configuration"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY", 
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
        }

# Input validation functions
def sanitize_input(text: str, max_length: int = 10000) -> str:
    """Sanitize user input"""
    if not isinstance(text, str):
        return ""
    
    # Remove control characters but keep newlines and tabs
    sanitized = ''.join(char for char in text if ord(char) >= 32 or char in ['\n', '\t'])
    
    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
        logger.warning(f"Input truncated to {max_length} characters")
    
    return sanitized.strip()

def validate_api_key_format(api_key: str) -> bool:
    """Validate API key format"""
    if not api_key or not isinstance(api_key, str):
        return False
    
    # Basic validation - should be at least 20 chars and contain alphanumeric + hyphens/underscores
    if len(api_key) < 20:
        return False
    
    # Check for suspicious patterns
    if api_key.count('x') > len(api_key) * 0.8:  # Too many x's (placeholder pattern)
        return False
    
    return True

def hash_sensitive_data(data: str) -> str:
    """Hash sensitive data for logging"""
    if not data:
        return "empty"
    
    # Return first 8 chars + hash of the rest
    if len(data) > 8:
        prefix = data[:8]
        suffix_hash = hashlib.sha256(data[8:].encode()).hexdigest()[:8]
        return f"{prefix}...{suffix_hash}"
    else:
        return f"{data[:4]}..."

def generate_request_id() -> str:
    """Generate unique request ID for tracking"""
    return f"req_{int(datetime.utcnow().timestamp())}_{secrets.token_hex(4)}"

# Security middleware decorator
def require_valid_input(max_length: int = 10000):
    """Decorator to validate and sanitize input"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Find request object in args
            for arg in args:
                if hasattr(arg, 'message'):
                    arg.message = sanitize_input(arg.message, max_length)
            
            # Check kwargs for message
            if 'message' in kwargs:
                kwargs['message'] = sanitize_input(kwargs['message'], max_length)
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Global security config instance
security_config = SecurityConfig()

def get_security_config():
    """Get global security configuration"""
    return security_config