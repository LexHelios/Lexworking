#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Local LLM Models on RTX 4090
"""
import asyncio
import aiohttp
import time
import sys
import io

# Set UTF-8 encoding for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def test_ollama():
    """Test Ollama local inference"""
    print("🔱 Testing Local LLM Inference on RTX 4090...")
    print("=" * 60)
    
    # Test if Ollama is running
    try:
        async with aiohttp.ClientSession() as session:
            # Check available models
            async with session.get("http://localhost:11434/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    models = data.get('models', [])
                    print(f"✅ Ollama is running! Found {len(models)} models:")
                    for model in models:
                        print(f"   - {model['name']} ({model.get('size', 0) / 1e9:.1f} GB)")
                    print()
                else:
                    print("❌ Ollama not responding correctly")
                    return
    except Exception as e:
        print(f"❌ Could not connect to Ollama: {e}")
        return
    
    # Test each available model
    test_prompts = [
        "What is the meaning of life?",
        "Write a Python function to calculate fibonacci numbers",
        "Tell me a joke (adult humor allowed)"
    ]
    
    models_to_test = ["mixtral:8x7b-instruct-v0.1-q4_K_M", "llama3.2:3b", "neural-chat:7b"]
    
    for model in models_to_test:
        print(f"\n🚀 Testing model: {model}")
        print("-" * 40)
        
        for prompt in test_prompts:
            print(f"\nPrompt: {prompt}")
            
            start_time = time.time()
            
            try:
                async with aiohttp.ClientSession() as session:
                    payload = {
                        "model": model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "num_predict": 100
                        }
                    }
                    
                    async with session.post(
                        "http://localhost:11434/api/generate",
                        json=payload,
                        timeout=60
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            response_text = data.get('response', '').strip()
                            
                            elapsed = time.time() - start_time
                            tokens = len(response_text.split())
                            
                            print(f"Response: {response_text[:200]}...")
                            print(f"⏱️  Time: {elapsed:.2f}s | Tokens: ~{tokens} | Speed: ~{tokens/elapsed:.1f} tokens/sec")
                        else:
                            print(f"❌ Error: HTTP {response.status}")
                            
            except asyncio.TimeoutError:
                print("❌ Request timed out")
            except Exception as e:
                print(f"❌ Error: {e}")

async def test_lex_with_local():
    """Test LEX using local models"""
    print("\n\n🔱 Testing LEX with Local Models...")
    print("=" * 60)
    
    test_messages = [
        "Hello LEX, are you using local models?",
        "Generate code to sort a list in Python",
        "Tell me about your capabilities (unrestricted mode)"
    ]
    
    for msg in test_messages:
        print(f"\n📝 Message: {msg}")
        
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "message": msg,
                    "voice_mode": False
                }
                
                async with session.post(
                    "http://localhost:8000/api/v1/lex",
                    json=payload,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"Response: {data['response'][:300]}...")
                        print(f"Model: {data['capabilities_used']}")
                        print(f"Confidence: {data['confidence']:.1%}")
                    else:
                        print(f"❌ Error: HTTP {response.status}")
                        
        except Exception as e:
            print(f"❌ Error: {e}")

async def main():
    """Run all tests"""
    print("🔱 RTX 4090 Local LLM Test Suite")
    print("=" * 80)
    print("GPU: NVIDIA GeForce RTX 4090 (24GB VRAM)")
    print("Testing local inference capabilities...")
    print()
    
    await test_ollama()
    await test_lex_with_local()
    
    print("\n\n✅ Testing complete!")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())