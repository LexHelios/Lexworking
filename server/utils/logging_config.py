
"""
Production Logging Configuration
Structured logging with JSON format for production monitoring
"""
import logging
import logging.handlers
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "process_id": os.getpid(),
            "thread_id": record.thread,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "extra_fields"):
            log_entry.update(record.extra_fields)
        
        # Add request context if available
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id
        
        if hasattr(record, "user_id"):
            log_entry["user_id"] = record.user_id
        
        if hasattr(record, "client_ip"):
            log_entry["client_ip"] = record.client_ip
        
        return json.dumps(log_entry, ensure_ascii=False)


class ContextFilter(logging.Filter):
    """Filter to add context information to log records"""
    
    def __init__(self, service_name: str = "lexos-api", version: str = "2.0.0"):
        super().__init__()
        self.service_name = service_name
        self.version = version
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add context to log record"""
        record.service_name = self.service_name
        record.service_version = self.version
        record.hostname = os.uname().nodename
        return True


def setup_logging(
    log_level: str = "INFO",
    log_dir: str = "/app/logs",
    service_name: str = "lexos-api",
    version: str = "2.0.0",
    enable_console: bool = True,
    enable_file: bool = True,
    enable_json: bool = True,
    max_file_size: int = 100 * 1024 * 1024,  # 100MB
    backup_count: int = 10
) -> logging.Logger:
    """Setup production logging configuration"""
    
    # Create logs directory
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatters
    if enable_json:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    # Add context filter
    context_filter = ContextFilter(service_name, version)
    
    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.addFilter(context_filter)
        root_logger.addHandler(console_handler)
    
    # File handlers
    if enable_file:
        # Main log file
        file_handler = logging.handlers.RotatingFileHandler(
            log_path / "lexos.log",
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        file_handler.setFormatter(formatter)
        file_handler.addFilter(context_filter)
        root_logger.addHandler(file_handler)
        
        # Error log file
        error_handler = logging.handlers.RotatingFileHandler(
            log_path / "lexos-error.log",
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        error_handler.addFilter(context_filter)
        root_logger.addHandler(error_handler)
        
        # Security log file
        security_handler = logging.handlers.RotatingFileHandler(
            log_path / "lexos-security.log",
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        security_handler.setFormatter(formatter)
        security_handler.addFilter(context_filter)
        
        # Add security handler to security logger
        security_logger = logging.getLogger("security")
        security_logger.addHandler(security_handler)
        security_logger.setLevel(logging.INFO)
    
    # Configure specific loggers
    loggers_config = {
        "uvicorn": logging.INFO,
        "uvicorn.access": logging.INFO,
        "fastapi": logging.INFO,
        "sqlalchemy": logging.WARNING,
        "redis": logging.WARNING,
        "httpx": logging.WARNING,
        "openai": logging.WARNING,
        "anthropic": logging.WARNING,
    }
    
    for logger_name, level in loggers_config.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
    
    return root_logger


class RequestContextLogger:
    """Logger with request context"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.request_id: Optional[str] = None
        self.user_id: Optional[str] = None
        self.client_ip: Optional[str] = None
    
    def set_context(self, request_id: str = None, user_id: str = None, client_ip: str = None):
        """Set request context"""
        self.request_id = request_id
        self.user_id = user_id
        self.client_ip = client_ip
    
    def _add_context(self, extra: Dict[str, Any] = None) -> Dict[str, Any]:
        """Add context to extra fields"""
        context = {}
        if self.request_id:
            context["request_id"] = self.request_id
        if self.user_id:
            context["user_id"] = self.user_id
        if self.client_ip:
            context["client_ip"] = self.client_ip
        
        if extra:
            context.update(extra)
        
        return context
    
    def debug(self, msg: str, extra: Dict[str, Any] = None):
        """Log debug message with context"""
        self.logger.debug(msg, extra={"extra_fields": self._add_context(extra)})
    
    def info(self, msg: str, extra: Dict[str, Any] = None):
        """Log info message with context"""
        self.logger.info(msg, extra={"extra_fields": self._add_context(extra)})
    
    def warning(self, msg: str, extra: Dict[str, Any] = None):
        """Log warning message with context"""
        self.logger.warning(msg, extra={"extra_fields": self._add_context(extra)})
    
    def error(self, msg: str, extra: Dict[str, Any] = None, exc_info: bool = False):
        """Log error message with context"""
        self.logger.error(msg, extra={"extra_fields": self._add_context(extra)}, exc_info=exc_info)
    
    def critical(self, msg: str, extra: Dict[str, Any] = None, exc_info: bool = False):
        """Log critical message with context"""
        self.logger.critical(msg, extra={"extra_fields": self._add_context(extra)}, exc_info=exc_info)


# Global logger instance
logger = RequestContextLogger(logging.getLogger(__name__))
