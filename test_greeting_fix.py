#!/usr/bin/env python3
"""
Test the greeting fix for LEX
"""
import asyncio
import aiohttp
import json

async def test_greeting():
    """Test that LEX responds properly to greetings"""
    print("Testing LEX greeting responses...")
    
    test_messages = [
        "hello",
        "Hello LEX",
        "hi there",
        "Hey",
        "Good morning",
        "Tell me about the size of the world",
        "Can you generate an image?"
    ]
    
    for message in test_messages:
        print(f"\n{'='*50}")
        print(f"Testing: '{message}'")
        print('='*50)
        
        try:
            async with aiohttp.ClientSession() as session:
                # Test the API endpoint
                async with session.post(
                    'http://localhost:8000/api/v1/lex',
                    json={
                        'message': message,
                        'voice_mode': False
                    },
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        response_text = data.get('response', '')
                        
                        # Check for thinking tags
                        if '<think>' in response_text:
                            print("❌ ERROR: Response contains thinking tags!")
                        
                        # Check greeting format
                        is_greeting = any(word in message.lower() for word in ['hello', 'hi', 'hey', 'good morning'])
                        if is_greeting:
                            if response_text.startswith('🔱 JAI MAHAKAAL!'):
                                print("✅ Greeting format correct")
                            else:
                                print("❌ Missing proper greeting format")
                        
                        print(f"\nResponse: {response_text[:200]}...")
                    else:
                        print(f"❌ HTTP Error: {response.status}")
                        
        except Exception as e:
            print(f"❌ Connection error: {e}")
            print("Make sure the LEX server is running on http://localhost:8000")

async def test_file_upload():
    """Test file upload handling"""
    print("\n\nTesting file upload error handling...")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Create form data
            data = aiohttp.FormData()
            data.add_field('message', 'Please analyze this document')
            data.add_field('voice_mode', 'false')
            
            # Test with empty file
            data.add_field('files',
                          b'',  # Empty content
                          filename='test.pdf',
                          content_type='application/pdf')
            
            async with session.post(
                'http://localhost:8000/api/v1/lex/multimodal',
                data=data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print("✅ Empty file handled without error")
                    print(f"Response: {result.get('response', '')[:100]}...")
                else:
                    print(f"❌ HTTP Error: {response.status}")
                    
    except Exception as e:
        print(f"❌ Error during file upload test: {e}")

if __name__ == "__main__":
    print("🔱 LEX Greeting Fix Test Suite 🔱")
    print("="*60)
    asyncio.run(test_greeting())
    asyncio.run(test_file_upload())
    print("\n✅ All tests completed!")