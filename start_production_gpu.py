#!/usr/bin/env python3
"""
Start LEX Production Server with GPU Workaround
🔱 JAI MAHAKAAL! GPU-Optimized Launch 🔱
"""

import os
import sys
import asyncio
import subprocess
from pathlib import Path

# GPU Workaround for container environments
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:512"
os.environ["CUDA_LAUNCH_BLOCKING"] = "0"
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"

# vLLM settings
os.environ["VLLM_SKIP_CUDA_DEVICE_COUNT_CHECK"] = "1"
os.environ["VLLM_USE_CUDA_IPC"] = "0"

# Force Ollama to use different port since GPU isn't working for it
os.environ["OLLAMA_HOST"] = "127.0.0.1:11434"

# Add server to path
sys.path.insert(0, str(Path(__file__).parent / "server"))

async def start_server():
    print("🔱 ========================================== 🔱")
    print("   LEX PRODUCTION SERVER - H100 EDITION")
    print("   🔥 GPU-Optimized for lexcommand.ai 🔥")
    print("🔱 ========================================== 🔱")
    
    # Start Ollama in background (CPU mode for now)
    print("\n📦 Starting Ollama service (CPU mode)...")
    ollama_proc = subprocess.Popen(
        ["ollama", "serve"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    # Wait for Ollama to start
    await asyncio.sleep(3)
    
    # Import and configure the server
    from simple_lex_server_production import app
    import uvicorn
    
    # Initialize orchestrator with GPU workarounds
    try:
        from server.orchestrator.production_orchestrator import production_orchestrator
        from server.orchestrator.ollama_integration import ollama_integration
        
        # Initialize integrations
        await ollama_integration.initialize()
        print(f"✅ Ollama models available: {len(ollama_integration.available_models)}")
        
        # Show available models
        print("\n📦 Available Models:")
        for model_name, info in ollama_integration.available_models.items():
            print(f"   - {model_name} ({info['size']})")
        
        production_orchestrator.ollama = ollama_integration
        
        # Check for vLLM support
        try:
            import vllm
            print("\n✅ vLLM available for GPU inference")
            print("   Note: Individual model loading will use GPU when possible")
        except:
            print("\n⚠️  vLLM not fully initialized - using CPU fallback")
        
    except Exception as e:
        print(f"⚠️ Orchestrator update failed: {e}")
    
    # Server configuration
    port = int(os.getenv("PORT", "8080"))  # Use PORT env var or default to 8080
    
    print(f"\n🚀 Starting server on http://0.0.0.0:{port}")
    print("🌐 Configure your domain to point here for lexcommand.ai")
    print("\n📍 Endpoints:")
    print(f"   - Main: http://localhost:{port}/")
    print(f"   - Chat: http://localhost:{port}/simple")
    print(f"   - API: http://localhost:{port}/api/v1/lex")
    print(f"   - Docs: http://localhost:{port}/docs")
    print(f"   - IDE: http://localhost:{port}/ide")
    print("\n💡 GPU Status:")
    
    # Show GPU info
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total,utilization.gpu", "--format=csv,noheader"],
            capture_output=True, text=True
        )
        print(f"   {result.stdout.strip()}")
    except:
        print("   ⚠️  GPU info unavailable")
    
    print("\n🔥 Server starting...")
    
    # Run the server
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True,
        use_colors=True,
        reload=False,  # Disable reload for production
        workers=1  # Single worker for GPU
    )
    server = uvicorn.Server(config)
    
    try:
        await server.serve()
    finally:
        # Cleanup
        if ollama_proc:
            ollama_proc.terminate()

if __name__ == "__main__":
    print("\n🔥 LEX AI SYSTEM - PRODUCTION LAUNCH 🔥")
    print("━" * 50)
    
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        print("\n\n🔱 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        import traceback
        traceback.print_exc()