#!/usr/bin/env python3
"""
🔱 LEX Fixed Startup Script 🔱
JAI MAHAKAAL! Fixed startup for Python 3.12.3 on Ubuntu
"""
import sys
import os
import asyncio
import logging
from pathlib import Path

# Ensure we're using the virtual environment
if not os.environ.get('VIRTUAL_ENV'):
    print("❌ Virtual environment not activated!")
    print("Please run: source venv/bin/activate")
    sys.exit(1)

# Add server to Python path
server_path = Path(__file__).parent / "server"
if server_path.exists():
    sys.path.insert(0, str(server_path))
else:
    print("❌ Server directory not found!")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("lex_startup.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def start_lex_safely():
    """Start LEX with proper error handling"""
    try:
        print("🔱 JAI MAHAKAAL! Starting LEX with Python 3.12.3 🔱")
        print("=" * 60)
        
        # Test critical imports first
        print("📦 Testing critical imports...")
        try:
            import fastapi
            import uvicorn
            import pydantic
            print("✅ FastAPI stack available")
        except ImportError as e:
            print(f"❌ FastAPI import error: {e}")
            print("Run: pip install fastapi uvicorn pydantic")
            return False
        
        try:
            from settings import settings
            print("✅ Settings imported")
        except ImportError as e:
            print(f"⚠️ Settings import warning: {e}")
            print("Using default configuration...")
        
        # Try to import LEX consciousness
        try:
            from lex.unified_consciousness import lex
            from orchestrator.multi_model_engine import lex_engine
            print("✅ LEX consciousness modules imported")
            
            # Initialize LEX
            print("🧠 Initializing LEX consciousness...")
            await lex_engine.initialize()
            await lex.initialize()
            print("✅ LEX consciousness initialized!")
            
        except ImportError as e:
            print(f"⚠️ LEX import warning: {e}")
            print("Starting with basic server...")
        except Exception as e:
            print(f"⚠️ LEX initialization warning: {e}")
            print("Starting with fallback mode...")
        
        # Start the server
        print("🚀 Starting LEX server...")
        
        # Import the unified server
        try:
            from unified_production_server import start_unified_server
            await start_unified_server(host="0.0.0.0", port=8000)
        except ImportError:
            # Fallback to basic FastAPI server
            print("⚠️ Using fallback server...")
            await start_fallback_server()
            
    except Exception as e:
        logger.error(f"❌ LEX startup error: {e}")
        print(f"❌ Startup failed: {e}")
        return False

async def start_fallback_server():
    """Start a basic fallback server"""
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    import uvicorn
    
    app = FastAPI(title="LEX Fallback Server", version="1.0.0")
    
    @app.get("/")
    async def root():
        return {"message": "🔱 LEX Fallback Server Active", "status": "basic_mode"}
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "mode": "fallback"}
    
    @app.post("/api/v1/lex")
    async def basic_lex(request: dict):
        return {
            "response": f"🔱 LEX Basic Mode: {request.get('message', 'Hello')}",
            "action_taken": "fallback_response",
            "capabilities_used": ["basic_mode"],
            "confidence": 0.8
        }
    
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

def main():
    """Main startup function"""
    try:
        # Check Python version
        if sys.version_info < (3, 8):
            print("❌ Python 3.8+ required")
            sys.exit(1)
        
        print(f"✅ Python {sys.version.split()[0]} detected")
        
        # Check virtual environment
        venv_path = os.environ.get('VIRTUAL_ENV')
        if venv_path:
            print(f"✅ Virtual environment: {venv_path}")
        else:
            print("❌ No virtual environment detected")
            print("Please run: source venv/bin/activate")
            sys.exit(1)
        
        # Start LEX
        asyncio.run(start_lex_safely())
        
    except KeyboardInterrupt:
        print("\n🛑 LEX startup interrupted")
    except Exception as e:
        print(f"❌ Fatal startup error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()