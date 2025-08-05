#!/usr/bin/env python3
"""
Test LEX System on H100
🔱 JAI MAHAKAAL! System Test 🔱
"""

import asyncio
import sys
import os
from pathlib import Path

# Add server to path
sys.path.insert(0, str(Path(__file__).parent / "server"))

async def test_system():
    print("🔱 LEX SYSTEM TEST ON H100 🔱")
    print("=" * 60)
    
    # Test 1: Check Ollama models
    print("\n1. Testing Ollama Integration:")
    import aiohttp
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:11434/api/tags") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"✅ Ollama running with {len(data['models'])} models:")
                    for model in data['models'][:5]:  # Show first 5
                        print(f"   - {model['name']} ({model['details']['parameter_size']})")
                else:
                    print("❌ Ollama API not responding")
    except Exception as e:
        print(f"❌ Ollama error: {e}")
    
    # Test 2: Test our orchestrator
    print("\n2. Testing Production Orchestrator:")
    try:
        from server.orchestrator.production_orchestrator import production_orchestrator
        await production_orchestrator.initialize()
        status = production_orchestrator.get_status()
        print(f"✅ Orchestrator initialized")
        print(f"   - Models available: {status['models_available']}")
        print(f"   - Memory systems: {status['memory_systems']}")
        print(f"   - GPU optimizers: {status['gpu_optimizers']}")
    except Exception as e:
        print(f"❌ Orchestrator error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Test simple inference
    print("\n3. Testing Model Inference:")
    try:
        # Test with Ollama directly
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": "llama3.1:8b",
                "prompt": "Hello! Please respond with a single sentence.",
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 50
                }
            }
            async with session.post("http://localhost:11434/api/generate", json=payload) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    print(f"✅ Ollama inference successful:")
                    print(f"   Response: {result.get('response', '')[:100]}...")
                else:
                    print(f"❌ Ollama inference failed: {resp.status}")
    except Exception as e:
        print(f"❌ Inference error: {e}")
    
    # Test 4: Test server startup
    print("\n4. Testing Server Startup:")
    try:
        from simple_lex_server_production import app, startup_event
        print("✅ Server imports successful")
        # Don't actually start the server, just test imports
    except Exception as e:
        print(f"❌ Server import error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("🔱 TEST COMPLETE 🔱")

if __name__ == "__main__":
    asyncio.run(test_system())