"""
Production Error Handler for LEX
🔱 JAI MAHAKAAL! Comprehensive Error Management 🔱
"""

import logging
import traceback
import sys
import asyncio
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from functools import wraps
import json

logger = logging.getLogger(__name__)

class LEXError(Exception):
    """Base exception for LEX system"""
    def __init__(self, message: str, code: str = "LEX_ERROR", 
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.code = code
        self.details = details or {}
        self.timestamp = datetime.utcnow().isoformat()

class ModelError(LEXError):
    """Model-specific errors"""
    def __init__(self, model_name: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            f"Model {model_name} error: {message}",
            code="MODEL_ERROR",
            details={"model": model_name, **(details or {})}
        )

class MemoryError(LEXError):
    """Memory system errors"""
    def __init__(self, system: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            f"Memory system {system} error: {message}",
            code="MEMORY_ERROR",
            details={"system": system, **(details or {})}
        )

class OrchestrationError(LEXError):
    """Orchestration errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="ORCHESTRATION_ERROR", details=details)

class APIError(LEXError):
    """API-related errors"""
    def __init__(self, service: str, status_code: int, message: str, 
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(
            f"API {service} error ({status_code}): {message}",
            code="API_ERROR",
            details={"service": service, "status_code": status_code, **(details or {})}
        )

class ErrorHandler:
    """
    Comprehensive error handler with logging, recovery, and metrics
    """
    
    def __init__(self):
        self.error_count = 0
        self.error_history = []
        self.max_history = 1000
        self.recovery_strategies = {}
        self.error_callbacks = []
        
    def register_recovery(self, error_type: type, strategy: Callable):
        """Register recovery strategy for error type"""
        self.recovery_strategies[error_type] = strategy
        
    def add_callback(self, callback: Callable):
        """Add error callback for monitoring"""
        self.error_callbacks.append(callback)
        
    async def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle error with logging, recovery attempts, and notifications
        
        Returns:
            Dict with error details and recovery status
        """
        self.error_count += 1
        
        # Create error record
        error_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": type(error).__name__,
            "message": str(error),
            "context": context or {},
            "traceback": traceback.format_exc(),
            "recovery_attempted": False,
            "recovery_successful": False
        }
        
        # Add to history
        self.error_history.append(error_record)
        if len(self.error_history) > self.max_history:
            self.error_history.pop(0)
        
        # Log error
        if isinstance(error, LEXError):
            logger.error(f"LEX Error [{error.code}]: {error.message}", 
                        extra={"details": error.details})
        else:
            logger.error(f"Unexpected error: {error}", exc_info=True)
        
        # Attempt recovery
        recovery_strategy = self.recovery_strategies.get(type(error))
        if recovery_strategy:
            try:
                error_record["recovery_attempted"] = True
                recovery_result = await recovery_strategy(error, context)
                error_record["recovery_successful"] = True
                error_record["recovery_result"] = recovery_result
                logger.info(f"Recovery successful for {type(error).__name__}")
            except Exception as recovery_error:
                logger.error(f"Recovery failed: {recovery_error}")
                error_record["recovery_error"] = str(recovery_error)
        
        # Notify callbacks
        for callback in self.error_callbacks:
            try:
                asyncio.create_task(callback(error_record))
            except Exception as cb_error:
                logger.error(f"Error callback failed: {cb_error}")
        
        return error_record
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics"""
        if not self.error_history:
            return {
                "total_errors": 0,
                "error_rate": 0,
                "recent_errors": [],
                "error_types": {}
            }
        
        # Count error types
        error_types = {}
        for record in self.error_history:
            error_type = record["type"]
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        # Get recent errors
        recent_errors = [
            {
                "timestamp": record["timestamp"],
                "type": record["type"],
                "message": record["message"],
                "recovered": record["recovery_successful"]
            }
            for record in self.error_history[-10:]
        ]
        
        return {
            "total_errors": self.error_count,
            "error_rate": len(self.error_history) / max(1, self.error_count),
            "recent_errors": recent_errors,
            "error_types": error_types,
            "recovery_success_rate": sum(
                1 for r in self.error_history if r["recovery_successful"]
            ) / max(1, sum(1 for r in self.error_history if r["recovery_attempted"]))
        }

# Global error handler instance
error_handler = ErrorHandler()

# Decorator for error handling
def handle_errors(recovery_strategy: Optional[Callable] = None):
    """
    Decorator for automatic error handling
    
    Usage:
        @handle_errors()
        async def my_function():
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                context = {
                    "function": func.__name__,
                    "args": str(args)[:200],
                    "kwargs": str(kwargs)[:200]
                }
                
                error_record = await error_handler.handle_error(e, context)
                
                # If recovery was successful, return the result
                if error_record.get("recovery_successful") and "recovery_result" in error_record:
                    return error_record["recovery_result"]
                
                # Otherwise, re-raise
                raise
        
        # Register recovery strategy if provided
        if recovery_strategy:
            error_handler.register_recovery(Exception, recovery_strategy)
        
        return wrapper
    return decorator

# Recovery strategies
async def model_recovery_strategy(error: ModelError, context: Dict[str, Any]) -> Any:
    """Recovery strategy for model errors"""
    logger.info(f"Attempting model recovery for {error.details.get('model')}")
    
    # Try fallback model
    fallback_models = {
        "mixtral-8x22b": "llama-4-scout",
        "deepseek-r1": "mixtral-8x22b",
        "qwen2.5-vl": "llava-v1.6"
    }
    
    failed_model = error.details.get("model")
    fallback = fallback_models.get(failed_model)
    
    if fallback:
        logger.info(f"Switching from {failed_model} to {fallback}")
        context["model_preference"] = fallback
        return {"fallback_model": fallback, "retry": True}
    
    return {"retry": False}

async def memory_recovery_strategy(error: MemoryError, context: Dict[str, Any]) -> Any:
    """Recovery strategy for memory errors"""
    system = error.details.get("system")
    logger.info(f"Attempting memory recovery for {system}")
    
    # Try to reconnect
    if system == "redis":
        # Clear local cache and continue
        return {"use_local_cache": True}
    elif system == "postgres":
        # Use file-based fallback
        return {"use_file_storage": True}
    elif system == "milvus":
        # Use simple similarity search
        return {"use_simple_search": True}
    
    return {"degraded_mode": True}

async def api_recovery_strategy(error: APIError, context: Dict[str, Any]) -> Any:
    """Recovery strategy for API errors"""
    service = error.details.get("service")
    status_code = error.details.get("status_code")
    
    if status_code == 429:  # Rate limit
        logger.info(f"Rate limit hit for {service}, waiting...")
        await asyncio.sleep(5)
        return {"retry": True, "delay": 5}
    elif status_code >= 500:  # Server error
        logger.info(f"Server error for {service}, using fallback")
        return {"use_fallback": True}
    
    return {"retry": False}

# Register default recovery strategies
error_handler.register_recovery(ModelError, model_recovery_strategy)
error_handler.register_recovery(MemoryError, memory_recovery_strategy)
error_handler.register_recovery(APIError, api_recovery_strategy)

# Utility functions
def log_performance_metrics(func_name: str, duration: float, success: bool, 
                          model: Optional[str] = None):
    """Log performance metrics for monitoring"""
    metrics = {
        "function": func_name,
        "duration_ms": duration * 1000,
        "success": success,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if model:
        metrics["model"] = model
    
    logger.info(f"Performance metric: {json.dumps(metrics)}")

def create_error_response(error: Exception, request_id: Optional[str] = None) -> Dict[str, Any]:
    """Create standardized error response"""
    if isinstance(error, LEXError):
        return {
            "error": True,
            "code": error.code,
            "message": str(error),
            "details": error.details,
            "timestamp": error.timestamp,
            "request_id": request_id
        }
    else:
        return {
            "error": True,
            "code": "INTERNAL_ERROR",
            "message": "An unexpected error occurred",
            "details": {"type": type(error).__name__},
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id
        }

# Circuit breaker implementation
class CircuitBreaker:
    """Circuit breaker for external services"""
    
    def __init__(self, failure_threshold: int = 5, timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
        
    async def call(self, func: Callable, *args, **kwargs):
        """Call function with circuit breaker protection"""
        if self.state == "open":
            if (datetime.utcnow().timestamp() - self.last_failure_time) > self.timeout:
                self.state = "half-open"
            else:
                raise LEXError("Circuit breaker is open", code="CIRCUIT_OPEN")
        
        try:
            result = await func(*args, **kwargs)
            if self.state == "half-open":
                self.state = "closed"
                self.failures = 0
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure_time = datetime.utcnow().timestamp()
            
            if self.failures >= self.failure_threshold:
                self.state = "open"
                logger.warning(f"Circuit breaker opened after {self.failures} failures")
            
            raise