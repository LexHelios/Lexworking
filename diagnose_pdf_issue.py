#!/usr/bin/env python3
"""
Diagnose PDF processing issues
"""
import asyncio
import aiohttp

async def test_ollama_directly():
    """Test Ollama directly to see if it's a model issue"""
    
    print("Testing Ollama directly...")
    
    # Test prompt
    test_prompt = """You have been provided with a PDF document about insurance.

User Request: Provide a comprehensive summary of this document

CRITICAL INSTRUCTIONS:
1. You MUST provide a COMPREHENSIVE summary that is AT LEAST 500 words long
2. Include ALL sections of the document
3. List SPECIFIC numbers, dates, addresses, and names
4. Use headers and bullet points to organize information
5. DO NOT give short responses

Begin your comprehensive analysis:"""

    models_to_test = ["dolphin-mixtral:latest", "mixtral:8x7b", "llama2:13b", "mistral:latest"]
    
    for model in models_to_test:
        print(f"\n{'='*60}")
        print(f"Testing model: {model}")
        
        payload = {
            "model": model,
            "prompt": test_prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 8000,
                "stop": []  # No stop sequences
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post("http://localhost:11434/api/generate", json=payload, timeout=300) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get('response', '')
                        print(f"Response length: {len(response_text)} chars")
                        print(f"First 200 chars: {response_text[:200]}...")
                        print(f"Word count: {len(response_text.split())} words")
                        
                        # Check if response is complete
                        if response_text.endswith(('.', '!', '?', '"')):
                            print("✅ Response appears complete")
                        else:
                            print("⚠️ Response may be truncated")
                            print(f"Last 100 chars: ...{response_text[-100:]}")
                    else:
                        print(f"❌ Error: {response.status}")
        except Exception as e:
            print(f"❌ Model {model} not available: {e}")

async def check_model_configs():
    """Check model configurations"""
    print("\nChecking available models...")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:11434/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    print("\nAvailable models:")
                    for model in data.get('models', []):
                        print(f"- {model['name']} (size: {model.get('size', 'unknown')})")
    except Exception as e:
        print(f"❌ Could not get model list: {e}")

if __name__ == "__main__":
    print("PDF Response Diagnostic Tool")
    print("="*60)
    
    asyncio.run(check_model_configs())
    asyncio.run(test_ollama_directly())