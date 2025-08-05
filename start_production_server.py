#!/usr/bin/env python3
"""
Start LEX Production Server
🔱 JAI MAHAKAAL! Launch with Power 🔱
"""

import os
import sys
import asyncio
from pathlib import Path

# Set environment variables for optimal performance
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
os.environ["OLLAMA_NUM_GPU"] = "999"  # Use all GPU layers
os.environ["OLLAMA_DEBUG"] = "INFO"

# Add server to path
sys.path.insert(0, str(Path(__file__).parent / "server"))

async def start_server():
    print("🔱 ========================================== 🔱")
    print("   STARTING LEX PRODUCTION SERVER")
    print("   On H100 80GB - lexcommand.ai")
    print("🔱 ========================================== 🔱")
    
    # Import and configure the server
    from simple_lex_server_production import app
    import uvicorn
    
    # Update orchestrator to use Ollama
    try:
        from server.orchestrator.production_orchestrator import production_orchestrator
        from server.orchestrator.ollama_integration import ollama_integration
        
        # Initialize Ollama integration
        await ollama_integration.initialize()
        print(f"✅ Ollama models available: {len(ollama_integration.available_models)}")
        
        # Show available models
        print("\n📦 Available Models:")
        for model_name, info in ollama_integration.available_models.items():
            print(f"   - {model_name} ({info['size']})")
        
        # Update orchestrator to use Ollama models
        production_orchestrator.ollama = ollama_integration
        
    except Exception as e:
        print(f"⚠️ Orchestrator update failed: {e}")
    
    print("\n🚀 Starting server on http://0.0.0.0:8000")
    print("🌐 Configure your domain to point here for lexcommand.ai")
    print("\n📍 Endpoints:")
    print("   - Main: http://localhost:8000/")
    print("   - Chat: http://localhost:8000/simple")
    print("   - API: http://localhost:8000/api/v1/lex")
    print("   - Docs: http://localhost:8000/docs")
    print("   - IDE: http://localhost:8000/ide")
    
    # Run the server
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True,
        use_colors=True
    )
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        print("\n🔱 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        import traceback
        traceback.print_exc()