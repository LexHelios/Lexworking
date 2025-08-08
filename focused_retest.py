#!/usr/bin/env python3
"""
Focused retest for API Keys and Image Generation after credits were added
"""

import asyncio
import aiohttp
import json
import sys

async def test_api_keys():
    """Test API keys verification"""
    print("🔑 Testing API Keys Verification...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8001/api/v1/omnipotent/status", timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    system_status = data.get("system_status", {})
                    api_keys_status = system_status.get("api_keys", {})
                    
                    configured_keys = 0
                    key_details = {}
                    
                    for key_name, key_status in api_keys_status.items():
                        if key_status and key_status != "not_configured":
                            configured_keys += 1
                            key_details[key_name] = "✅ configured"
                        else:
                            key_details[key_name] = "❌ missing"
                    
                    print(f"   API Keys Status: {configured_keys} configured keys found")
                    for key, status in key_details.items():
                        print(f"   {key}: {status}")
                    
                    return configured_keys > 0
                else:
                    print(f"   ❌ HTTP {response.status}")
                    return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

async def test_image_generation():
    """Test image generation with educational prompt"""
    print("🎨 Testing Unrestricted Image Generation...")
    try:
        # Simple educational image prompt
        test_prompt = "anatomical diagram of a cell"
        
        form_data = aiohttp.FormData()
        form_data.add_field('prompt', test_prompt)
        form_data.add_field('style', 'educational')
        form_data.add_field('model', 'flux-dev-uncensored')
        form_data.add_field('safety_level', 'unrestricted')
        form_data.add_field('user_id', 'test_user')
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:8001/api/v1/omnipotent/image",
                data=form_data,
                timeout=60
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("status") == "success":
                        image_url = data.get("image_url", "")
                        model_used = data.get("model_used", "unknown")
                        
                        print(f"   ✅ Image generated successfully using {model_used}")
                        print(f"   Image URL available: {bool(image_url)}")
                        if image_url:
                            print(f"   URL: {image_url[:80]}...")
                        return True
                    else:
                        error = data.get("error", "Unknown error")
                        print(f"   ❌ Generation failed: {error}")
                        return False
                else:
                    error_text = await response.text()
                    print(f"   ❌ HTTP {response.status}: {error_text}")
                    return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

async def test_system_status():
    """Test overall system status"""
    print("🔱 Testing Overall System Status...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8001/api/v1/omnipotent/status", timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    status = data.get("status")
                    omnipotent_mode = data.get("omnipotent_mode", False)
                    unrestricted_models = data.get("unrestricted_models", False)
                    educational_mode = data.get("educational_mode", False)
                    
                    print(f"   System Status: {status}")
                    print(f"   Omnipotent Mode: {omnipotent_mode}")
                    print(f"   Unrestricted Models: {unrestricted_models}")
                    print(f"   Educational Mode: {educational_mode}")
                    
                    return status in ["success", "operational"]
                else:
                    print(f"   ❌ HTTP {response.status}")
                    return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

async def main():
    print("🔱 FOCUSED RETEST: API Keys & Image Generation 🔱")
    print("=" * 60)
    
    # Test the three areas requested
    system_ok = await test_system_status()
    print()
    
    api_keys_ok = await test_api_keys()
    print()
    
    image_gen_ok = await test_image_generation()
    print()
    
    print("=" * 60)
    print("📊 FOCUSED TEST RESULTS:")
    print(f"   Overall System Status: {'✅ WORKING' if system_ok else '❌ FAILED'}")
    print(f"   API Keys Verification: {'✅ WORKING' if api_keys_ok else '❌ FAILED'}")
    print(f"   Image Generation: {'✅ WORKING' if image_gen_ok else '❌ FAILED'}")
    
    if api_keys_ok and image_gen_ok:
        print("\n🎉 Credits appear to have resolved the issues!")
    elif image_gen_ok and not api_keys_ok:
        print("\n⚡ Image generation is working! API keys still need configuration.")
    else:
        print("\n💔 Issues still persist - may need further investigation.")
    
    return system_ok and api_keys_ok and image_gen_ok

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)