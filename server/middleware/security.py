
"""
Production Security Middleware
Implements comprehensive security measures for production deployment
"""
import time
import hashlib
import hmac
import json
from typing import Dict, List, Optional, Callable
from fastapi import Request, Response, HTTPException, status
from fastapi.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
import redis
import logging
from datetime import datetime, timedelta
import ipaddress
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class SecurityMiddleware(BaseHTTPMiddleware):
    """Comprehensive security middleware for production"""
    
    def __init__(
        self,
        app,
        secret_key: str,
        allowed_origins: List[str],
        rate_limit_requests: int = 60,
        rate_limit_window: int = 60,
        redis_client: Optional[redis.Redis] = None,
        enable_csrf: bool = True,
        enable_rate_limiting: bool = True,
        enable_security_headers: bool = True,
        blocked_ips: Optional[List[str]] = None,
        allowed_ips: Optional[List[str]] = None
    ):
        super().__init__(app)
        self.secret_key = secret_key
        self.allowed_origins = allowed_origins
        self.rate_limit_requests = rate_limit_requests
        self.rate_limit_window = rate_limit_window
        self.redis_client = redis_client
        self.enable_csrf = enable_csrf
        self.enable_rate_limiting = enable_rate_limiting
        self.enable_security_headers = enable_security_headers
        self.blocked_ips = set(blocked_ips or [])
        self.allowed_ips = set(allowed_ips or [])
        
        # Security headers configuration
        self.security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' https:; "
                "connect-src 'self' wss: https:; "
                "frame-ancestors 'none';"
            ),
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": (
                "geolocation=(), microphone=(), camera=(), "
                "payment=(), usb=(), magnetometer=(), gyroscope=()"
            )
        }

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Main security middleware dispatch"""
        start_time = time.time()
        
        try:
            # IP filtering
            if not await self._check_ip_allowed(request):
                logger.warning(f"Blocked request from IP: {request.client.host}")
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"error": "Access denied"}
                )
            
            # Rate limiting
            if self.enable_rate_limiting and not await self._check_rate_limit(request):
                logger.warning(f"Rate limit exceeded for IP: {request.client.host}")
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={"error": "Rate limit exceeded"}
                )
            
            # CORS validation
            if not await self._validate_cors(request):
                logger.warning(f"CORS violation from origin: {request.headers.get('origin')}")
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"error": "CORS policy violation"}
                )
            
            # CSRF protection for state-changing operations
            if self.enable_csrf and request.method in ["POST", "PUT", "DELETE", "PATCH"]:
                if not await self._validate_csrf(request):
                    logger.warning(f"CSRF validation failed for {request.url}")
                    return JSONResponse(
                        status_code=status.HTTP_403_FORBIDDEN,
                        content={"error": "CSRF validation failed"}
                    )
            
            # Request validation
            await self._validate_request(request)
            
            # Process request
            response = await call_next(request)
            
            # Add security headers
            if self.enable_security_headers:
                self._add_security_headers(response)
            
            # Log request
            process_time = time.time() - start_time
            await self._log_request(request, response, process_time)
            
            return response
            
        except Exception as e:
            logger.error(f"Security middleware error: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": "Internal server error"}
            )

    async def _check_ip_allowed(self, request: Request) -> bool:
        """Check if IP is allowed"""
        client_ip = request.client.host
        
        # If allowed IPs are specified, only allow those
        if self.allowed_ips:
            return client_ip in self.allowed_ips
        
        # Check if IP is blocked
        if client_ip in self.blocked_ips:
            return False
        
        # Check for private/local IPs in production
        try:
            ip_obj = ipaddress.ip_address(client_ip)
            if ip_obj.is_private and not ip_obj.is_loopback:
                # Allow private IPs only in development
                return request.headers.get("x-forwarded-for") is not None
        except ValueError:
            return False
        
        return True

    async def _check_rate_limit(self, request: Request) -> bool:
        """Check rate limiting using Redis"""
        if not self.redis_client:
            return True
        
        client_ip = request.client.host
        key = f"rate_limit:{client_ip}"
        
        try:
            current = self.redis_client.get(key)
            if current is None:
                # First request
                self.redis_client.setex(key, self.rate_limit_window, 1)
                return True
            
            current_count = int(current)
            if current_count >= self.rate_limit_requests:
                return False
            
            # Increment counter
            self.redis_client.incr(key)
            return True
            
        except Exception as e:
            logger.error(f"Rate limiting error: {str(e)}")
            return True  # Allow request if Redis fails

    async def _validate_cors(self, request: Request) -> bool:
        """Validate CORS policy"""
        origin = request.headers.get("origin")
        if not origin:
            return True  # No origin header, likely same-origin
        
        # Check if origin is allowed
        for allowed_origin in self.allowed_origins:
            if origin == allowed_origin or origin.endswith(allowed_origin.replace("*", "")):
                return True
        
        return False

    async def _validate_csrf(self, request: Request) -> bool:
        """Validate CSRF token"""
        # Get CSRF token from header or form data
        csrf_token = request.headers.get("x-csrf-token")
        
        if not csrf_token:
            # Try to get from form data for multipart requests
            if request.headers.get("content-type", "").startswith("multipart/form-data"):
                form = await request.form()
                csrf_token = form.get("csrf_token")
        
        if not csrf_token:
            return False
        
        # Validate CSRF token
        return self._verify_csrf_token(csrf_token, request)

    def _verify_csrf_token(self, token: str, request: Request) -> bool:
        """Verify CSRF token using HMAC"""
        try:
            # Extract timestamp and signature from token
            parts = token.split(".")
            if len(parts) != 2:
                return False
            
            timestamp_str, signature = parts
            timestamp = int(timestamp_str)
            
            # Check if token is not too old (1 hour)
            if time.time() - timestamp > 3600:
                return False
            
            # Generate expected signature
            message = f"{timestamp_str}:{request.client.host}"
            expected_signature = hmac.new(
                self.secret_key.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception:
            return False

    async def _validate_request(self, request: Request):
        """Validate request structure and content"""
        # Check content length
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 100 * 1024 * 1024:  # 100MB
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Request too large"
            )
        
        # Validate content type for POST/PUT requests
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")
            allowed_types = [
                "application/json",
                "application/x-www-form-urlencoded",
                "multipart/form-data",
                "text/plain"
            ]
            
            if not any(content_type.startswith(t) for t in allowed_types):
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail="Unsupported media type"
                )

    def _add_security_headers(self, response: Response):
        """Add security headers to response"""
        for header, value in self.security_headers.items():
            response.headers[header] = value

    async def _log_request(self, request: Request, response: Response, process_time: float):
        """Log request for security monitoring"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "method": request.method,
            "url": str(request.url),
            "client_ip": request.client.host,
            "user_agent": request.headers.get("user-agent", ""),
            "status_code": response.status_code,
            "process_time": process_time,
            "content_length": response.headers.get("content-length", 0)
        }
        
        # Log suspicious activity
        if response.status_code >= 400:
            logger.warning(f"Security event: {json.dumps(log_data)}")
        else:
            logger.info(f"Request: {json.dumps(log_data)}")


class JWTMiddleware(BaseHTTPMiddleware):
    """JWT Authentication Middleware"""
    
    def __init__(self, app, secret_key: str, algorithm: str = "HS256", exclude_paths: List[str] = None):
        super().__init__(app)
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.exclude_paths = exclude_paths or ["/health", "/metrics", "/docs", "/openapi.json"]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """JWT validation dispatch"""
        # Skip authentication for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)
        
        # Extract JWT token
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": "Missing or invalid authorization header"}
            )
        
        token = auth_header.split(" ")[1]
        
        try:
            # Validate JWT token (implement your JWT validation logic here)
            payload = self._validate_jwt(token)
            request.state.user = payload
            
            response = await call_next(request)
            return response
            
        except Exception as e:
            logger.error(f"JWT validation error: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": "Invalid token"}
            )

    def _validate_jwt(self, token: str) -> Dict:
        """Validate JWT token (implement with your preferred JWT library)"""
        # This is a placeholder - implement with PyJWT or similar
        import jwt
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
