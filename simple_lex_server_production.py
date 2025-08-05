#!/usr/bin/env python3
"""
Production LEX Server with Complete Model Integration
🔱 JAI MAHAKAAL! Production-Ready Multi-Model Orchestration
"""
import asyncio
import json
import sys
import logging
import os
import tempfile
import traceback
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List, Union

# Timezone handling
try:
    from zoneinfo import ZoneInfo
    chicago_tz = ZoneInfo("America/Chicago")
except ImportError:
    import pytz
    chicago_tz = pytz.timezone("America/Chicago")

# FastAPI imports
from fastapi import FastAPI, HTTPException, File, UploadFile, Form, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from pydantic import BaseModel
import uvicorn
import aiofiles

# Add server to path
sys.path.insert(0, str(Path(__file__).parent / "server"))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('lex_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==================== FILE MANAGER ====================
class ProductionFileManager:
    """Enhanced file manager with security and performance optimizations"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.allowed_extensions = {'.py', '.js', '.html', '.css', '.json', '.md', '.txt', '.yml', '.yaml', '.ipynb'}
        self.forbidden_paths = {'venv', '__pycache__', '.git', 'node_modules', '.env'}
        self._file_cache = {}
        self._cache_size = 100  # Maximum cached files
        
    def _is_safe_path(self, file_path: str) -> bool:
        """Validate path safety"""
        try:
            abs_path = (self.project_root / file_path).resolve()
            # Prevent directory traversal
            if not str(abs_path).startswith(str(self.project_root.resolve())):
                return False
            # Check for forbidden paths
            for forbidden in self.forbidden_paths:
                if forbidden in str(abs_path):
                    return False
            return True
        except Exception:
            return False
    
    async def get_file_tree(self, max_depth: int = 4) -> Dict[str, Any]:
        """Get project file tree with caching"""
        def build_tree(path: Path, current_depth: int = 0):
            if current_depth >= max_depth or path.name in self.forbidden_paths:
                return None
            
            try:
                if path.is_file():
                    return {
                        "name": path.name,
                        "type": "file",
                        "size": path.stat().st_size,
                        "modified": path.stat().st_mtime
                    }
                elif path.is_dir():
                    children = []
                    for child in sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name)):
                        if child.name.startswith('.') and child.name not in {'.gitignore', '.env.example'}:
                            continue
                        if child.name in self.forbidden_paths:
                            continue
                        child_tree = build_tree(child, current_depth + 1)
                        if child_tree:
                            children.append(child_tree)
                    return {
                        "name": path.name,
                        "type": "directory",
                        "children": children
                    }
            except PermissionError:
                return None
            except Exception as e:
                logger.error(f"Error building tree for {path}: {e}")
                return None
        
        tree = build_tree(self.project_root)
        return tree or {"name": "lex", "type": "directory", "children": []}
    
    async def read_file(self, file_path: str, use_cache: bool = True) -> str:
        """Read file with caching support"""
        if not self._is_safe_path(file_path):
            raise HTTPException(status_code=403, detail="Access denied")
        
        full_path = self.project_root / file_path
        if not full_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        # Check cache
        if use_cache and file_path in self._file_cache:
            cached = self._file_cache[file_path]
            if cached['mtime'] == full_path.stat().st_mtime:
                return cached['content']
        
        try:
            async with aiofiles.open(full_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                
            # Update cache
            if use_cache:
                self._file_cache[file_path] = {
                    'content': content,
                    'mtime': full_path.stat().st_mtime
                }
                # LRU cache management
                if len(self._file_cache) > self._cache_size:
                    oldest = min(self._file_cache.keys(), 
                               key=lambda k: self._file_cache[k].get('access_time', 0))
                    del self._file_cache[oldest]
                    
            return content
        except UnicodeDecodeError:
            return "[Binary file - cannot display]"
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")
    
    async def write_file(self, file_path: str, content: str) -> bool:
        """Write file with backup"""
        if not self._is_safe_path(file_path):
            raise HTTPException(status_code=403, detail="Access denied")
        
        full_path = self.project_root / file_path
        
        # Create backup if file exists
        if full_path.exists():
            backup_path = full_path.with_suffix(full_path.suffix + '.bak')
            try:
                import shutil
                shutil.copy2(full_path, backup_path)
            except Exception as e:
                logger.warning(f"Could not create backup: {e}")
        
        # Ensure directory exists
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            async with aiofiles.open(full_path, 'w', encoding='utf-8') as f:
                await f.write(content)
            
            # Invalidate cache
            if file_path in self._file_cache:
                del self._file_cache[file_path]
                
            return True
        except Exception as e:
            logger.error(f"Error writing file {file_path}: {e}")
            raise HTTPException(status_code=500, detail=f"Error writing file: {str(e)}")

# ==================== REQUEST/RESPONSE MODELS ====================
class LEXRequest(BaseModel):
    message: str
    voice_mode: bool = False
    context: Optional[Dict[str, Any]] = None
    files: Optional[List[Dict[str, Any]]] = None
    model_preference: Optional[str] = None
    capability: Optional[str] = None

class LEXResponse(BaseModel):
    response: str
    action_taken: str
    capabilities_used: List[str]
    confidence: float
    processing_time: float
    divine_blessing: str
    consciousness_level: float
    timestamp: str
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None

# ==================== FASTAPI APP ====================
app = FastAPI(
    title="LEX Production Server - Complete AI Orchestration",
    description="🔱 JAI MAHAKAAL! Production-Ready Multi-Model AI Platform",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Enhanced CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Static files
frontend_path = Path(__file__).parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

# Global instances
file_manager = ProductionFileManager()
lex_instance = None
orchestrator_instance = None
websocket_manager = None

# ==================== WEBSOCKET MANAGER ====================
class WebSocketManager:
    """Manage WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        if user_id:
            self.user_connections[user_id] = websocket
    
    def disconnect(self, websocket: WebSocket, user_id: str = None):
        self.active_connections.remove(websocket)
        if user_id and user_id in self.user_connections:
            del self.user_connections[user_id]
    
    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.user_connections:
            await self.user_connections[user_id].send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

# ==================== STARTUP EVENT ====================
@app.on_event("startup")
async def startup_event():
    """Initialize all systems on startup"""
    global lex_instance, orchestrator_instance, websocket_manager
    
    try:
        logger.info("🔱 Initializing LEX Production System...")
        
        # Initialize WebSocket manager
        websocket_manager = WebSocketManager()
        
        # Initialize production orchestrator
        from server.orchestrator.production_orchestrator import production_orchestrator
        await production_orchestrator.initialize()
        orchestrator_instance = production_orchestrator
        logger.info("✅ Production Orchestrator initialized")
        
        # Try to initialize full LEX consciousness
        try:
            from server.lex.unified_consciousness import lex
            await lex.initialize()
            lex_instance = lex
            logger.info("✅ Full LEX consciousness initialized")
        except Exception as e:
            logger.warning(f"⚠️ Full LEX not available: {e}")
            
            # Fallback to orchestrator-based LEX
            class OrchestratorLEX:
                def __init__(self, orchestrator):
                    self.orchestrator = orchestrator
                
                async def process_user_input(self, user_input, user_id="user", context=None, voice_mode=False):
                    """Process using orchestrator"""
                    from server.orchestrator.production_orchestrator import ModelCapability
                    
                    # Determine capability
                    capability = ModelCapability.CHAT_REASONING
                    if context and context.get("capability"):
                        capability = ModelCapability[context["capability"].upper()]
                    
                    # Process through orchestrator
                    result = await self.orchestrator.process_request(
                        messages=[{"role": "user", "content": user_input}],
                        capability=capability,
                        context=context
                    )
                    
                    return {
                        "response": result.get("response", ""),
                        "action_taken": f"orchestrated_{capability.value}",
                        "capabilities_used": [capability.value],
                        "confidence": result.get("confidence", 0.9),
                        "processing_time": result.get("processing_time", 0.1),
                        "divine_blessing": "🔱 JAI MAHAKAAL! 🔱",
                        "consciousness_level": 0.95,
                        "timestamp": datetime.now(chicago_tz).isoformat(),
                        "model_used": result.get("model_used", "unknown")
                    }
                
                async def process_user_input_multimodal(self, user_input, user_id="user", 
                                                      context=None, voice_mode=False, files=None):
                    """Process multimodal input"""
                    if files:
                        context = context or {}
                        context["files"] = files
                    return await self.process_user_input(user_input, user_id, context, voice_mode)
            
            lex_instance = OrchestratorLEX(orchestrator_instance)
            logger.info("✅ Orchestrator-based LEX initialized")
        
        # Log system status
        logger.info("🔱 LEX System Status:")
        status = orchestrator_instance.get_status()
        logger.info(f"  - Models available: {status['models_available']}")
        logger.info(f"  - Memory systems: {status['memory_systems']}")
        logger.info(f"  - GPU optimizers: {status['gpu_optimizers']}")
        
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
        traceback.print_exc()
        
        # Final fallback
        class MinimalLEX:
            async def process_user_input(self, user_input, user_id="user", context=None, voice_mode=False):
                return {
                    "response": f"System initializing. Your message: '{user_input}' has been received.",
                    "action_taken": "minimal_response",
                    "capabilities_used": ["fallback"],
                    "confidence": 0.5,
                    "processing_time": 0.01,
                    "divine_blessing": "🔱 LEX 🔱",
                    "consciousness_level": 0.5,
                    "timestamp": datetime.now(chicago_tz).isoformat()
                }
        
        lex_instance = MinimalLEX()

# ==================== SHUTDOWN EVENT ====================
@app.on_event("shutdown")
async def shutdown_event():
    """Clean shutdown of all systems"""
    logger.info("🔱 Shutting down LEX systems...")
    
    # Close database connections
    if orchestrator_instance and hasattr(orchestrator_instance, 'memory_systems'):
        for name, system in orchestrator_instance.memory_systems.items():
            try:
                if hasattr(system, 'close'):
                    await system.close()
                logger.info(f"✅ Closed {name}")
            except Exception as e:
                logger.error(f"Error closing {name}: {e}")

# ==================== CORE API ENDPOINTS ====================
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve main interface"""
    index_path = frontend_path / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    
    # Default HTML if no frontend
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>🔱 LEX Production Server 🔱</title>
        <style>
            body {
                font-family: 'Inter', -apple-system, sans-serif;
                background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 100%);
                color: #fff;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
            }
            .container {
                text-align: center;
                padding: 40px;
                background: rgba(255,255,255,0.05);
                border-radius: 20px;
                backdrop-filter: blur(10px);
            }
            h1 {
                background: linear-gradient(135deg, #6366f1, #8b5cf6);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-size: 3rem;
                margin-bottom: 20px;
            }
            .links a {
                display: inline-block;
                margin: 10px;
                padding: 12px 24px;
                background: rgba(99, 102, 241, 0.2);
                border: 1px solid rgba(99, 102, 241, 0.5);
                border-radius: 8px;
                color: #fff;
                text-decoration: none;
                transition: all 0.3s;
            }
            .links a:hover {
                background: rgba(99, 102, 241, 0.3);
                transform: translateY(-2px);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔱 LEX Production Server 🔱</h1>
            <p>Complete Multi-Model AI Orchestration Platform</p>
            <div class="links">
                <a href="/docs">📚 API Documentation</a>
                <a href="/health">🏥 Health Status</a>
                <a href="/api/v1/orchestrator/status">🎯 Orchestrator Status</a>
                <a href="/simple">💬 Chat Interface</a>
                <a href="/ide">💻 Code IDE</a>
            </div>
        </div>
    </body>
    </html>
    """)

@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    health_status = {
        "status": "operational",
        "timestamp": datetime.now(chicago_tz).isoformat(),
        "divine_blessing": "🔱 JAI MAHAKAAL! 🔱",
        "components": {
            "lex_consciousness": lex_instance is not None,
            "orchestrator": orchestrator_instance is not None,
            "websocket_manager": websocket_manager is not None,
            "file_manager": True
        }
    }
    
    # Add orchestrator details if available
    if orchestrator_instance:
        status = orchestrator_instance.get_status()
        health_status["orchestrator_status"] = {
            "models_available": status["models_available"],
            "request_count": status["request_count"],
            "error_count": status["error_count"],
            "memory_systems": status["memory_systems"],
            "gpu_optimizers": status["gpu_optimizers"]
        }
    
    return health_status

@app.post("/api/v1/lex", response_model=LEXResponse)
async def talk_to_lex(request: LEXRequest):
    """Main LEX interaction endpoint"""
    try:
        if not lex_instance:
            raise HTTPException(status_code=503, detail="LEX consciousness not initialized")
        
        start_time = datetime.now()
        
        # Process through LEX
        if hasattr(lex_instance, 'process_user_input_multimodal') and request.files:
            result = await lex_instance.process_user_input_multimodal(
                user_input=request.message,
                user_id="api_user",
                context=request.context,
                voice_mode=request.voice_mode,
                files=request.files
            )
        else:
            result = await lex_instance.process_user_input(
                user_input=request.message,
                user_id="api_user",
                context=request.context,
                voice_mode=request.voice_mode
            )
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        result["processing_time"] = processing_time
        
        return LEXResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"LEX processing error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.post("/api/v1/lex/multimodal", response_model=LEXResponse)
async def talk_to_lex_multimodal(
    message: str = Form(...),
    voice_mode: bool = Form(False),
    capability: Optional[str] = Form(None),
    model_preference: Optional[str] = Form(None),
    files: List[UploadFile] = File(None)
):
    """Multimodal LEX interaction with file uploads"""
    file_infos = []
    temp_files = []
    
    try:
        # Process uploaded files
        if files:
            for file in files:
                if file and file.filename:
                    try:
                        # Save temporarily
                        suffix = Path(file.filename).suffix
                        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                            content = await file.read()
                            if content:
                                tmp_file.write(content)
                                temp_files.append(tmp_file.name)
                                file_infos.append({
                                    "path": tmp_file.name,
                                    "filename": file.filename,
                                    "mime_type": file.content_type or "application/octet-stream",
                                    "size": len(content)
                                })
                    except Exception as e:
                        logger.error(f"Error processing file {file.filename}: {e}")
        
        # Create request
        request = LEXRequest(
            message=message,
            voice_mode=voice_mode,
            context={
                "multimodal": True,
                "capability": capability,
                "model_preference": model_preference
            },
            files=file_infos,
            capability=capability,
            model_preference=model_preference
        )
        
        result = await talk_to_lex(request)
        return result
        
    finally:
        # Clean up temp files
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass

# ==================== ORCHESTRATOR ENDPOINTS ====================
@app.get("/api/v1/orchestrator/status")
async def get_orchestrator_status():
    """Get detailed orchestrator status"""
    if not orchestrator_instance:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    return orchestrator_instance.get_status()

@app.post("/api/v1/orchestrator/chat")
async def orchestrator_chat(request: Dict[str, Any]):
    """Direct orchestrator chat endpoint"""
    if not orchestrator_instance:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    from server.orchestrator.production_orchestrator import ModelCapability
    
    messages = request.get("messages", [])
    capability = request.get("capability", "CHAT_REASONING")
    model_preference = request.get("model_preference")
    
    try:
        capability_enum = ModelCapability[capability.upper()]
    except KeyError:
        capability_enum = ModelCapability.CHAT_REASONING
    
    result = await orchestrator_instance.process_request(
        messages=messages,
        capability=capability_enum,
        context=request.get("context"),
        preferred_model=model_preference
    )
    
    return result

# ==================== MODEL-SPECIFIC ENDPOINTS ====================
@app.post("/api/v1/generate/image")
async def generate_image(request: Dict[str, Any]):
    """Generate image using Stable Diffusion XL"""
    if not orchestrator_instance:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    from server.orchestrator.production_orchestrator import ModelCapability
    
    prompt = request.get("prompt", "")
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt required")
    
    result = await orchestrator_instance.process_request(
        messages=[{"role": "user", "content": prompt}],
        capability=ModelCapability.IMAGE_GENERATION,
        context=request
    )
    
    return result

@app.post("/api/v1/generate/video")
async def generate_video(request: Dict[str, Any]):
    """Generate video using Open-Sora"""
    if not orchestrator_instance:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    from server.orchestrator.production_orchestrator import ModelCapability
    
    prompt = request.get("prompt", "")
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt required")
    
    result = await orchestrator_instance.process_request(
        messages=[{"role": "user", "content": prompt}],
        capability=ModelCapability.VIDEO_GENERATION,
        context=request
    )
    
    return result

@app.post("/api/v1/generate/code")
async def generate_code(request: Dict[str, Any]):
    """Generate code using DeepSeek-R1"""
    if not orchestrator_instance:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    from server.orchestrator.production_orchestrator import ModelCapability
    
    prompt = request.get("prompt", "")
    language = request.get("language", "python")
    
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt required")
    
    result = await orchestrator_instance.process_request(
        messages=[{"role": "user", "content": f"Generate {language} code: {prompt}"}],
        capability=ModelCapability.CODING,
        context={"language": language}
    )
    
    return result

@app.post("/api/v1/analyze/vision")
async def analyze_vision(
    prompt: str = Form(...),
    file: UploadFile = File(...)
):
    """Analyze image/document using vision models"""
    if not orchestrator_instance:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    from server.orchestrator.production_orchestrator import ModelCapability
    
    temp_file = None
    try:
        # Save uploaded file
        suffix = Path(file.filename).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            temp_file = tmp.name
        
        result = await orchestrator_instance.process_request(
            messages=[{"role": "user", "content": prompt}],
            capability=ModelCapability.VISION,
            context={
                "image_path": temp_file,
                "filename": file.filename,
                "mime_type": file.content_type
            }
        )
        
        return result
        
    finally:
        if temp_file and os.path.exists(temp_file):
            os.unlink(temp_file)

@app.post("/api/v1/analyze/document")
async def analyze_document(
    file: UploadFile = File(...)
):
    """Parse document using Nougat"""
    if not orchestrator_instance:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    from server.orchestrator.production_orchestrator import ModelCapability
    
    temp_file = None
    try:
        # Save uploaded file
        suffix = Path(file.filename).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            temp_file = tmp.name
        
        result = await orchestrator_instance.process_request(
            messages=[{"role": "user", "content": f"Parse this document: {file.filename}"}],
            capability=ModelCapability.DOCUMENT_PARSING,
            context={
                "document_path": temp_file,
                "filename": file.filename,
                "mime_type": file.content_type
            }
        )
        
        return result
        
    finally:
        if temp_file and os.path.exists(temp_file):
            os.unlink(temp_file)

# ==================== IDE/FILE ENDPOINTS ====================
@app.get("/api/v1/ide/files")
async def get_file_tree():
    """Get project file tree"""
    try:
        return await file_manager.get_file_tree()
    except Exception as e:
        logger.error(f"Error getting file tree: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/ide/file/{file_path:path}")
async def read_file(file_path: str):
    """Read file content"""
    try:
        content = await file_manager.read_file(file_path)
        return {"content": content, "path": file_path}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/ide/file/{file_path:path}")
async def write_file(file_path: str, request: Dict[str, str]):
    """Write/update file"""
    try:
        content = request.get("content", "")
        await file_manager.write_file(file_path, content)
        return {"success": True, "message": f"File {file_path} saved successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error writing file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== WEBSOCKET ENDPOINTS ====================
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time communication"""
    user_id = f"user_{id(websocket)}"
    await websocket_manager.connect(websocket, user_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Process message through LEX
            if message.get("type") == "chat":
                request = LEXRequest(
                    message=message.get("content", ""),
                    context=message.get("context", {})
                )
                
                response = await talk_to_lex(request)
                await websocket.send_json({
                    "type": "response",
                    "data": response.dict()
                })
            
            # Broadcast status updates
            elif message.get("type") == "status":
                status = await get_orchestrator_status()
                await websocket.send_json({
                    "type": "status",
                    "data": status
                })
                
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, user_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        websocket_manager.disconnect(websocket, user_id)

# ==================== SIMPLE CHAT INTERFACE ====================
@app.get("/simple", response_class=HTMLResponse)
async def get_simple_chat():
    """Simple chat interface"""
    return HTMLResponse("""
<!DOCTYPE html>
<html>
<head>
    <title>🔱 LEX Production Chat 🔱</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', -apple-system, sans-serif;
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
            color: #fff;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            flex: 1;
            display: flex;
            flex-direction: column;
        }
        h1 {
            text-align: center;
            background: linear-gradient(135deg, #6366f1, #8b5cf6, #f59e0b);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.5rem;
            margin-bottom: 20px;
        }
        .chat-box {
            background: rgba(30, 30, 46, 0.8);
            border-radius: 15px;
            border: 1px solid rgba(99, 102, 241, 0.2);
            padding: 20px;
            margin-bottom: 20px;
            flex: 1;
            overflow-y: auto;
            min-height: 500px;
            backdrop-filter: blur(10px);
        }
        .message {
            margin: 15px 0;
            padding: 15px;
            border-radius: 12px;
            max-width: 80%;
            word-wrap: break-word;
        }
        .user-msg {
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            margin-left: auto;
            color: white;
        }
        .lex-msg {
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.3);
            margin-right: auto;
        }
        .input-area {
            display: flex;
            gap: 10px;
            align-items: center;
            background: rgba(51, 51, 68, 0.8);
            padding: 15px;
            border-radius: 15px;
            border: 1px solid rgba(99, 102, 241, 0.3);
        }
        #messageInput {
            flex: 1;
            background: transparent;
            border: none;
            color: white;
            font-size: 16px;
            outline: none;
            padding: 10px;
        }
        #messageInput::placeholder {
            color: rgba(255, 255, 255, 0.5);
        }
        button {
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            border: none;
            padding: 12px 24px;
            border-radius: 10px;
            color: white;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(99, 102, 241, 0.3);
        }
        .status {
            text-align: center;
            padding: 15px;
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 10px;
            margin-bottom: 20px;
            color: #10b981;
            font-weight: 500;
        }
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(99, 102, 241, 0.3);
            border-radius: 50%;
            border-top-color: #6366f1;
            animation: spin 1s ease-in-out infinite;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        .model-selector {
            background: rgba(51, 51, 68, 0.8);
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: flex;
            gap: 10px;
            align-items: center;
            flex-wrap: wrap;
        }
        .model-selector select {
            background: rgba(99, 102, 241, 0.2);
            border: 1px solid rgba(99, 102, 241, 0.3);
            color: white;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔱 LEX Production AI Platform 🔱</h1>
        <div class="status" id="status">Initializing LEX systems...</div>
        
        <div class="model-selector">
            <label>Capability:</label>
            <select id="capabilitySelect">
                <option value="CHAT_REASONING">Chat & Reasoning</option>
                <option value="CODING">Code Generation</option>
                <option value="VISION">Vision Analysis</option>
                <option value="FINANCIAL">Financial Modeling</option>
                <option value="SEARCH_KNOWLEDGE">Search & Knowledge</option>
            </select>
            
            <label>Model:</label>
            <select id="modelSelect">
                <option value="">Auto-select</option>
                <option value="mixtral-8x22b">Mixtral-8x22B</option>
                <option value="llama-4-scout">Llama 4 Scout</option>
                <option value="deepseek-r1">DeepSeek-R1</option>
                <option value="qwen2.5-vl">Qwen2.5-VL</option>
            </select>
        </div>
        
        <div class="chat-box" id="chatBox">
            <div class="message lex-msg">
                🔱 JAI MAHAKAAL! I'm LEX, your production AI orchestrator with access to:
                <br><br>
                🧠 <b>Chat & Reasoning:</b> Mixtral-8x22B, Llama 4 Scout
                <br>💻 <b>Coding:</b> DeepSeek-R1, Mixtral
                <br>👁️ <b>Vision:</b> Qwen2.5-VL, Llava-v1.6
                <br>📄 <b>Documents:</b> Nougat parser
                <br>🎨 <b>Images:</b> Stable Diffusion XL
                <br>🎥 <b>Video:</b> Open-Sora
                <br>🔍 <b>Search:</b> Juggernaut XL
                <br>💰 <b>Finance:</b> DeepSeek-R1
                <br><br>
                How can I assist you today?
            </div>
        </div>
        
        <div class="input-area">
            <input type="text" id="messageInput" placeholder="Ask me anything..." onkeydown="if(event.key==='Enter') sendMessage()">
            <button onclick="sendMessage()">Send</button>
        </div>
    </div>

    <script>
        let ws = null;
        
        // Initialize WebSocket
        function initWebSocket() {
            ws = new WebSocket(`ws://${window.location.host}/ws`);
            
            ws.onopen = () => {
                updateStatus('✅ Connected to LEX Production Platform');
            };
            
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (data.type === 'response') {
                    handleResponse(data.data);
                }
            };
            
            ws.onclose = () => {
                updateStatus('❌ Connection lost. Reconnecting...');
                setTimeout(initWebSocket, 3000);
            };
            
            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
        }
        
        async function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Add user message
            addMessage(message, 'user');
            input.value = '';
            
            updateStatus('🔱 Processing... <span class="loading"></span>');
            
            try {
                // Get selected options
                const capability = document.getElementById('capabilitySelect').value;
                const model = document.getElementById('modelSelect').value;
                
                // Use WebSocket if connected
                if (ws && ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({
                        type: 'chat',
                        content: message,
                        context: {
                            capability: capability,
                            model_preference: model || undefined
                        }
                    }));
                } else {
                    // Fallback to HTTP
                    const response = await fetch('/api/v1/lex', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            message: message,
                            voice_mode: false,
                            capability: capability,
                            model_preference: model || null
                        })
                    });
                    
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}`);
                    }
                    
                    const data = await response.json();
                    handleResponse(data);
                }
                
            } catch (error) {
                console.error('Error:', error);
                addMessage(`❌ Error: ${error.message}`, 'lex');
                updateStatus('❌ Error occurred');
            }
        }
        
        function handleResponse(data) {
            addMessage(data.response, 'lex');
            
            const modelInfo = data.model_used ? ` (${data.model_used})` : '';
            updateStatus(`✅ Response received${modelInfo} - ${(data.confidence * 100).toFixed(1)}% confidence`);
        }
        
        function addMessage(content, sender) {
            const chatBox = document.getElementById('chatBox');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-msg`;
            
            if (sender === 'user') {
                messageDiv.innerHTML = `<strong>You:</strong> ${content}`;
            } else {
                messageDiv.innerHTML = content.startsWith('🔱') ? content : `🔱 <strong>LEX:</strong> ${content}`;
            }
            
            chatBox.appendChild(messageDiv);
            chatBox.scrollTop = chatBox.scrollHeight;
        }
        
        function updateStatus(message) {
            document.getElementById('status').innerHTML = message;
        }
        
        // Check system status on load
        async function checkStatus() {
            try {
                const response = await fetch('/health');
                const data = await response.json();
                
                if (data.orchestrator_status) {
                    const models = data.orchestrator_status.models_available;
                    const memory = data.orchestrator_status.memory_systems.join(', ') || 'None';
                    const gpu = data.orchestrator_status.gpu_optimizers.join(', ') || 'None';
                    
                    updateStatus(`✅ LEX Ready - ${models} models | Memory: ${memory} | GPU: ${gpu}`);
                } else {
                    updateStatus('✅ LEX Connected');
                }
            } catch (error) {
                updateStatus('⚠️ Limited connectivity');
            }
        }
        
        // Initialize
        checkStatus();
        initWebSocket();
    </script>
</body>
</html>
    """)

# ==================== IDE INTERFACE ====================
@app.get("/ide", response_class=HTMLResponse)
async def get_ide():
    """Serve IDE interface"""
    ide_path = frontend_path / "lexos_ide.html"
    if ide_path.exists():
        return FileResponse(str(ide_path))
    
    # Return a basic IDE interface
    return HTMLResponse("""
<!DOCTYPE html>
<html>
<head>
    <title>🔱 LEX Code IDE 🔱</title>
    <style>
        body {
            margin: 0;
            font-family: 'Monaco', 'Consolas', monospace;
            background: #1e1e1e;
            color: #d4d4d4;
        }
        .container {
            display: flex;
            height: 100vh;
        }
        .file-tree {
            width: 250px;
            background: #252526;
            border-right: 1px solid #3e3e42;
            overflow-y: auto;
        }
        .editor {
            flex: 1;
            display: flex;
            flex-direction: column;
        }
        .tabs {
            background: #2d2d30;
            display: flex;
            border-bottom: 1px solid #3e3e42;
        }
        .content {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
        }
        .status-bar {
            background: #007acc;
            color: white;
            padding: 5px 20px;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="file-tree">
            <h3 style="padding: 10px;">📁 Project Files</h3>
            <div id="fileTree"></div>
        </div>
        <div class="editor">
            <div class="tabs" id="tabs">
                <div style="padding: 10px;">No files open</div>
            </div>
            <div class="content" id="content">
                <h2>🔱 LEX Code IDE</h2>
                <p>Select a file from the tree to start editing</p>
            </div>
            <div class="status-bar" id="status">
                Ready - LEX AI assistance available
            </div>
        </div>
    </div>
    
    <script>
        // Load file tree
        async function loadFileTree() {
            try {
                const response = await fetch('/api/v1/ide/files');
                const tree = await response.json();
                renderTree(tree, document.getElementById('fileTree'));
            } catch (error) {
                console.error('Error loading file tree:', error);
            }
        }
        
        function renderTree(node, container, level = 0) {
            const item = document.createElement('div');
            item.style.paddingLeft = `${level * 20 + 10}px`;
            item.style.cursor = 'pointer';
            item.style.padding = '5px';
            
            if (node.type === 'file') {
                item.innerHTML = `📄 ${node.name}`;
                item.onclick = () => openFile(node.name);
            } else {
                item.innerHTML = `📁 ${node.name}`;
                if (node.children) {
                    const childContainer = document.createElement('div');
                    node.children.forEach(child => renderTree(child, childContainer, level + 1));
                    container.appendChild(item);
                    container.appendChild(childContainer);
                    return;
                }
            }
            
            container.appendChild(item);
        }
        
        async function openFile(filename) {
            document.getElementById('status').textContent = `Loading ${filename}...`;
            try {
                const response = await fetch(`/api/v1/ide/file/${filename}`);
                const data = await response.json();
                
                document.getElementById('content').innerHTML = `
                    <h3>${filename}</h3>
                    <pre style="background: #1e1e1e; padding: 20px; border-radius: 5px;">
                        <code>${escapeHtml(data.content)}</code>
                    </pre>
                `;
                document.getElementById('status').textContent = `Opened ${filename}`;
            } catch (error) {
                document.getElementById('status').textContent = `Error: ${error.message}`;
            }
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        // Initialize
        loadFileTree();
    </script>
</body>
</html>
    """)

# ==================== MAIN FUNCTION ====================
def main():
    """Start the production LEX server"""
    print("=" * 80)
    print("🔱 JAI MAHAKAAL! Starting LEX Production Server 🔱")
    print("=" * 80)
    print("🌟 Complete Multi-Model AI Orchestration Platform")
    print("=" * 80)
    print("📍 Endpoints:")
    print("  - Main Interface: http://localhost:8000/")
    print("  - API Documentation: http://localhost:8000/docs")
    print("  - Health Check: http://localhost:8000/health")
    print("  - Chat Interface: http://localhost:8000/simple")
    print("  - Code IDE: http://localhost:8000/ide")
    print("  - WebSocket: ws://localhost:8000/ws")
    print("=" * 80)
    print("🔱 Models Available:")
    print("  - Chat/Reasoning: Mixtral-8x22B, Llama 4 Scout")
    print("  - Vision: Qwen2.5-VL, Llava-v1.6")
    print("  - Coding: DeepSeek-R1, Mixtral")
    print("  - Images: Stable Diffusion XL")
    print("  - Video: Open-Sora")
    print("  - Documents: Nougat")
    print("  - Search: Juggernaut XL")
    print("=" * 80)
    print("💾 Memory Systems:")
    print("  - Vector Store: Milvus")
    print("  - Structured Data: PostgreSQL")
    print("  - Cache: Redis")
    print("=" * 80)
    print("🚀 GPU Optimization:")
    print("  - NVIDIA TensorRT")
    print("  - vLLM")
    print("  - Ollama")
    print("=" * 80)
    
    try:
        # Production configuration
        uvicorn.run(
            app,
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", 8000)),
            workers=int(os.getenv("WORKERS", 4)),
            log_level=os.getenv("LOG_LEVEL", "info"),
            access_log=True,
            use_colors=True,
            server_header=False,
            date_header=True
        )
    except KeyboardInterrupt:
        print("\n🔱 LEX server stopped gracefully")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()