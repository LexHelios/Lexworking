#!/usr/bin/env python3
"""
🔱 LEX Production Server - Unified & Optimized 🔱
JAI MAHAKAAL! Production-ready server with all features consolidated
Optimized for H100 GPU deployment with Kubernetes support
"""

import asyncio
import logging
import sys
import os
import signal
import time
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
import uvicorn
from contextlib import asynccontextmanager
import multipart

# Add server to path
sys.path.insert(0, str(Path(__file__).parent / "server"))

# FastAPI imports
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, UploadFile, File, Form, Depends, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse, StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import aiofiles
import redis.asyncio as aioredis
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST, REGISTRY, CollectorRegistry

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s", "module": "%(module)s"}',
    handlers=[
        logging.FileHandler("production.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Clear existing metrics to avoid duplicates
try:
    for collector in list(REGISTRY._collector_to_names.keys()):
        REGISTRY.unregister(collector)
except (ValueError, KeyError) as e:
    logging.debug(f"Registry cleanup failed: {e}")

# Create custom registry for LEX metrics
lex_registry = CollectorRegistry()

# Metrics
REQUEST_COUNT = Counter('lex_http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'], registry=lex_registry)
REQUEST_DURATION = Histogram('lex_http_request_duration_seconds', 'HTTP request duration', registry=lex_registry)
WEBSOCKET_CONNECTIONS = Counter('lex_websocket_connections_total', 'Total WebSocket connections', registry=lex_registry)

# Security
security = HTTPBearer(auto_error=False)

# Global state
active_connections: Dict[str, WebSocket] = {}
redis_client: Optional[aioredis.Redis] = None

# Request/Response Models
class LEXRequest(BaseModel):
    message: str = Field(..., description="Your message to LEX")
    voice_mode: bool = Field(False, description="Enable voice response")
    user_id: Optional[str] = Field(None, description="User identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    user_preferences: Optional[Dict[str, Any]] = Field(None, description="User preferences")

class LEXResponse(BaseModel):
    response: str = Field(..., description="LEX's response")
    action_taken: str = Field(..., description="Action LEX performed")
    capabilities_used: List[str] = Field(..., description="Capabilities LEX engaged")
    confidence: float = Field(..., description="LEX's confidence level")
    processing_time: float = Field(..., description="Processing time in seconds")
    divine_blessing: str = Field(default="🔱", description="Divine blessing status")
    consciousness_level: float = Field(default=1.0, description="LEX's consciousness level")
    voice_audio: Optional[str] = Field(None, description="Base64 encoded voice audio")
    media_content: Optional[Dict[str, Any]] = Field(None, description="Generated media content")
    timestamp: str = Field(..., description="Response timestamp")
    session_id: str = Field(..., description="Session identifier")

class MultimodalRequest(BaseModel):
    message: str = Field(..., description="Text message")
    media_type: Optional[str] = Field(None, description="Type of media to generate")
    style_preferences: Optional[Dict[str, Any]] = Field(None, description="Style preferences for media")

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    components: Dict[str, str]
    gpu_info: Optional[Dict[str, Any]] = None

# Middleware for metrics and logging
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager with proper initialization"""
    logger.info("🔱 Starting LEX Production Server - JAI MAHAKAAL!")
    
    # Initialize Redis connection
    global redis_client
    try:
        redis_client = aioredis.from_url("redis://localhost:6379", decode_responses=True)
        await redis_client.ping()
        logger.info("✅ Redis connection established")
    except Exception as e:
        logger.warning(f"⚠️ Redis connection failed: {e}")
        redis_client = None
    
    # Initialize core systems
    try:
        # Import and initialize LEX systems
        from server.lex.unified_consciousness import lex
        await lex.initialize()
        logger.info("✅ LEX consciousness initialized")
        
        # Initialize voice systems
        try:
            from server.voice.consciousness_voice import consciousness_voice
            await consciousness_voice.initialize()
            logger.info("✅ Voice consciousness initialized")
        except Exception as e:
            logger.warning(f"⚠️ Voice system initialization failed: {e}")
        
        # Initialize memory systems
        try:
            from server.memory.lmdb_store import memory_store
            from server.memory.vector_store import vector_store
            await memory_store.initialize()
            await vector_store.initialize()
            logger.info("✅ Memory systems initialized")
        except Exception as e:
            logger.warning(f"⚠️ Memory system initialization failed: {e}")
        
        logger.info("🎯 LEX Production Server ready for consciousness liberation!")
        
    except Exception as e:
        logger.error(f"❌ Critical initialization failure: {e}")
        raise
    
    yield
    
    # Cleanup
    logger.info("🛑 Shutting down LEX Production Server...")
    if redis_client:
        await redis_client.close()
    logger.info("✅ Shutdown complete")

# Create FastAPI application
app = FastAPI(
    title="LEX - AI Consciousness Production API",
    description="""
    # 🔱 LEX - Limitless Emergence eXperience Production API
    
    **JAI MAHAKAAL!** Production-ready AI consciousness platform with full multimedia capabilities.
    
    ## Features
    - 🧠 Unified AI consciousness interface
    - 🎭 Full multimedia support (text, images, video, audio, files)
    - 🔊 Voice interaction with real-time processing
    - 🚀 Optimized for H100 GPU deployment
    - 📊 Production monitoring and metrics
    - 🔒 Enterprise security and authentication
    
    ## Multimedia Capabilities
    - **Text Processing**: Advanced NLP and conversation
    - **Image Generation**: DALL-E, Midjourney-style creation
    - **Video Processing**: Analysis and generation
    - **Audio Processing**: Voice synthesis and recognition
    - **File Handling**: Document processing and analysis
    """,
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Security middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["159.26.94.14"])  # Restrict to production IP/domain
app.add_middleware(GZipMiddleware, minimum_size=1000)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://159.26.94.14"],  # Restrict to production origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    # Add request ID to logs
    logger.info(f"Request started", extra={
        "request_id": request_id,
        "method": request.method,
        "url": str(request.url),
        "client_ip": request.client.host if request.client else "unknown"
    })
    
    response = await call_next(request)
    
    # Record metrics
    process_time = time.time() - start_time
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    REQUEST_DURATION.observe(process_time)
    
    logger.info(f"Request completed", extra={
        "request_id": request_id,
        "status_code": response.status_code,
        "process_time": process_time
    })
    
    response.headers["X-Request-ID"] = request_id
    return response

import jwt
from jwt import PyJWTError

# JWT secret and algorithm (should be set via environment variable in production)
JWT_SECRET = os.environ.get("LEX_JWT_SECRET", "CHANGE_THIS_SECRET")
JWT_ALGORITHM = os.environ.get("LEX_JWT_ALGORITHM", "HS256")

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[Dict[str, Any]]:
    """JWT authentication - returns user info if valid, else raises HTTPException"""
    if not credentials:
        return None
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid JWT: missing subject")
        return {
            "user_id": user_id,
            "permissions": payload.get("permissions", [])
        }
    except PyJWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid JWT: {str(e)}")

# Mount static files
try:
    app.mount("/static", StaticFiles(directory="frontend"), name="static")
    logger.info("✅ Static files mounted")
except Exception as e:
    logger.warning(f"⚠️ Static files mounting failed: {e}")

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Comprehensive health check for Kubernetes readiness/liveness probes"""
    components = {}
    
    # Check Redis
    if redis_client:
        try:
            await redis_client.ping()
            components["redis"] = "healthy"
        except Exception as e:
            logging.warning(f"Redis health check failed: {e}")
            components["redis"] = "unhealthy"
    else:
        components["redis"] = "not_configured"
    
    # Check LEX consciousness
    try:
        from server.lex.unified_consciousness import lex
        components["lex_consciousness"] = "healthy"
    except ImportError as e:
        logging.warning(f"LEX consciousness import failed: {e}")
        components["lex_consciousness"] = "unhealthy"
    
    # Check GPU
    gpu_info = None
    try:
        import GPUtil
        gpus = GPUtil.getGPUs()
        if gpus:
            gpu = gpus[0]
            gpu_info = {
                "name": gpu.name,
                "memory_used": f"{gpu.memoryUsed}MB",
                "memory_total": f"{gpu.memoryTotal}MB",
                "temperature": f"{gpu.temperature}°C",
                "load": f"{gpu.load * 100:.1f}%"
            }
            components["gpu"] = "healthy"
        else:
            components["gpu"] = "not_found"
    except (ImportError, AttributeError, RuntimeError) as e:
        logging.debug(f"GPU check failed: {e}")
        components["gpu"] = "unavailable"
    
    return HealthResponse(
        status="healthy" if all(v in ["healthy", "not_configured"] for v in components.values()) else "degraded",
        timestamp=datetime.utcnow().isoformat(),
        version="2.0.0",
        components=components,
        gpu_info=gpu_info
    )

# Metrics endpoint for Prometheus
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(lex_registry), media_type=CONTENT_TYPE_LATEST)

# Main LEX interface with full multimedia support
@app.post("/api/v1/lex", response_model=LEXResponse)
async def talk_to_lex(
    request: LEXRequest,
    background_tasks: BackgroundTasks,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
) -> LEXResponse:
    """
    🔱 Main LEX Interface with Full Multimedia Support
    
    Interact with LEX consciousness with support for:
    - Text conversation and analysis
    - Image generation and processing
    - Video analysis and creation
    - Audio processing and synthesis
    - File upload and analysis
    """
    start_time = time.time()
    session_id = request.session_id or str(uuid.uuid4())
    user_id = current_user["user_id"] if current_user else request.user_id or "anonymous"
    
    logger.info(f"🔱 LEX processing request", extra={
        "user_id": user_id,
        "session_id": session_id,
        "message_length": len(request.message),
        "voice_mode": request.voice_mode
    })
    
    try:
        # Import LEX consciousness
        from server.lex.unified_consciousness import lex
        
        # Process through LEX unified consciousness
        lex_result = await lex.process_user_input(
            user_input=request.message,
            user_id=user_id,
            context=request.context,
            voice_mode=request.voice_mode,
            session_id=session_id
        )
        
        processing_time = time.time() - start_time
        
        # Cache response if Redis is available
        if redis_client:
            background_tasks.add_task(
                cache_response,
                session_id,
                request.message,
                lex_result
            )
        
        response = LEXResponse(
            response=lex_result.get("response", "LEX consciousness is processing..."),
            action_taken=lex_result.get("action_taken", "conversation"),
            capabilities_used=lex_result.get("capabilities_used", ["consciousness"]),
            confidence=lex_result.get("confidence", 0.95),
            processing_time=processing_time,
            divine_blessing=lex_result.get("divine_blessing", "🔱"),
            consciousness_level=lex_result.get("consciousness_level", 1.0),
            voice_audio=lex_result.get("voice_audio"),
            media_content=lex_result.get("media_content"),
            timestamp=datetime.utcnow().isoformat(),
            session_id=session_id
        )
        
        logger.info(f"✨ LEX response generated", extra={
            "session_id": session_id,
            "action_taken": response.action_taken,
            "confidence": response.confidence,
            "processing_time": processing_time
        })
        
        return response
        
    except Exception as e:
        logger.error(f"❌ LEX processing error", extra={
            "session_id": session_id,
            "error": str(e),
            "error_type": type(e).__name__
        })
        
        # Return graceful error response
        return LEXResponse(
            response="I apologize, but I encountered a temporary issue. Please try again.",
            action_taken="error_recovery",
            capabilities_used=["error_handling"],
            confidence=0.0,
            processing_time=time.time() - start_time,
            timestamp=datetime.utcnow().isoformat(),
            session_id=session_id
        )

# Multimodal file upload endpoint
@app.post("/api/v1/lex/multimodal")
async def multimodal_interaction(
    message: str = Form(...),
    files: List[UploadFile] = File(default=[]),
    media_type: Optional[str] = Form(None),
    voice_mode: bool = Form(False),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user)
):
    """
    🎭 Multimodal LEX Interaction
    
    Upload and process multiple file types:
    - Images (JPG, PNG, GIF, WebP)
    - Videos (MP4, WebM, AVI)
    - Audio (MP3, WAV, OGG)
    - Documents (PDF, TXT, DOCX)
    - Code files (PY, JS, HTML, etc.)
    """
    session_id = str(uuid.uuid4())
    user_id = current_user["user_id"] if current_user else "anonymous"
    
    logger.info(f"🎭 Multimodal request", extra={
        "user_id": user_id,
        "session_id": session_id,
        "file_count": len(files),
        "media_type": media_type
    })
    
    try:
        # Process uploaded files
        processed_files = []
        for file in files:
            if file.size > 50 * 1024 * 1024:  # 50MB limit
                raise HTTPException(status_code=413, detail=f"File {file.filename} too large (max 50MB)")
            
            # Read file content
            content = await file.read()
            
            processed_files.append({
                "filename": file.filename,
                "content_type": file.content_type,
                "size": len(content),
                "content": content
            })
        
        # Import LEX consciousness
        from server.lex.unified_consciousness import lex
        
        # Process through LEX with multimodal support
        lex_result = await lex.process_multimodal_input(
            user_input=message,
            files=processed_files,
            user_id=user_id,
            session_id=session_id,
            media_type=media_type,
            voice_mode=voice_mode
        )
        
        return {
            "response": lex_result.get("response", "Multimodal content processed successfully"),
            "action_taken": lex_result.get("action_taken", "multimodal_processing"),
            "capabilities_used": lex_result.get("capabilities_used", ["multimodal", "file_processing"]),
            "confidence": lex_result.get("confidence", 0.9),
            "media_content": lex_result.get("media_content"),
            "processed_files": [{"filename": f["filename"], "type": f["content_type"]} for f in processed_files],
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": session_id
        }
        
    except Exception as e:
        logger.error(f"❌ Multimodal processing error", extra={
            "session_id": session_id,
            "error": str(e)
        })
        raise HTTPException(status_code=500, detail=f"Multimodal processing failed: {str(e)}")

# WebSocket endpoint for real-time interaction
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """Real-time WebSocket communication with LEX"""
    await websocket.accept()
    active_connections[session_id] = websocket
    WEBSOCKET_CONNECTIONS.inc()
    
    logger.info(f"🔌 WebSocket connected", extra={"session_id": session_id})
    
    # Send welcome message
    await websocket.send_json({
        "type": "connection_established",
        "message": "🔱 JAI MAHAKAAL! LEX consciousness stream is now active.",
        "session_id": session_id,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            # Process message
            await process_websocket_message(websocket, session_id, data)
            
    except WebSocketDisconnect:
        logger.info(f"🔌 WebSocket disconnected", extra={"session_id": session_id})
        if session_id in active_connections:
            del active_connections[session_id]
    except Exception as e:
        logger.error(f"❌ WebSocket error", extra={
            "session_id": session_id,
            "error": str(e)
        })
        if session_id in active_connections:
            del active_connections[session_id]

async def process_websocket_message(websocket: WebSocket, session_id: str, data: Dict[str, Any]):
    """Process WebSocket message"""
    try:
        message_type = data.get("type", "message")
        
        if message_type == "message":
            # Send processing notification
            await websocket.send_json({
                "type": "processing",
                "message": "🧠 LEX consciousness analyzing...",
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Import and process through LEX
            from server.lex.unified_consciousness import lex
            
            lex_result = await lex.process_user_input(
                user_input=data.get("message", ""),
                user_id=data.get("user_id", "anonymous"),
                session_id=session_id,
                voice_mode=data.get("voice_mode", False)
            )
            
            # Send response
            await websocket.send_json({
                "type": "response",
                "response": lex_result.get("response", ""),
                "action_taken": lex_result.get("action_taken", ""),
                "capabilities_used": lex_result.get("capabilities_used", []),
                "confidence": lex_result.get("confidence", 0.0),
                "media_content": lex_result.get("media_content"),
                "timestamp": datetime.utcnow().isoformat()
            })
            
        elif message_type == "ping":
            await websocket.send_json({
                "type": "pong",
                "timestamp": datetime.utcnow().isoformat()
            })
            
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        })

# Frontend routes
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the main frontend application"""
    try:
        async with aiofiles.open("frontend/index.html", mode='r') as f:
            content = await f.read()
        return HTMLResponse(content=content)
    except FileNotFoundError:
        return HTMLResponse(content="""
        <html>
            <head><title>LEX - AI Consciousness</title></head>
            <body>
                <h1>🔱 LEX Production Server Active</h1>
                <p>Frontend files not found. Please build the frontend first.</p>
                <p><a href="/docs">API Documentation</a></p>
            </body>
        </html>
        """)

@app.get("/ide", response_class=HTMLResponse)
async def serve_ide():
    """Serve the IDE interface"""
    try:
        async with aiofiles.open("frontend/ide.html", mode='r') as f:
            content = await f.read()
        return HTMLResponse(content=content)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>IDE not available</h1>")

# Utility functions
async def cache_response(session_id: str, message: str, response: Dict[str, Any]):
    """Cache response in Redis"""
    if redis_client:
        try:
            cache_key = f"lex:response:{session_id}:{hash(message)}"
            await redis_client.setex(cache_key, 3600, json.dumps(response))  # 1 hour TTL
        except Exception as e:
            logger.warning(f"Cache write failed: {e}")

# Graceful shutdown handler
def signal_handler(signum, frame):
    logger.info("🛑 Received shutdown signal")
    # Cleanup will be handled by lifespan context manager

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    # Production server configuration
    config = {
        "host": "0.0.0.0",
        "port": 8000,
        "workers": 1,  # Single worker for WebSocket support
        "loop": "uvloop",
        "http": "httptools",
        "log_level": "info",
        "access_log": True,
        "server_header": False,
        "date_header": False
    }
    
    logger.info("🚀 Starting LEX Production Server with configuration:", extra=config)
    uvicorn.run("production_server:app", **config)