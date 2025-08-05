#!/usr/bin/env python3
"""
Test LEX AI System Fixes
Tests memory persistence, response generation, thinking tag removal, and capabilities
"""

import asyncio
import aiohttp
import json
import time
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_lex_system():
    """Test the fixed LEX AI system"""
    print("🔱 Testing LEX AI System Fixes 🔱")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        
        # Test 1: Capabilities Query
        print("\n📋 Test 1: Capabilities Query")
        test_message = {
            "message": "What can you do?",
            "voice_mode": False
        }
        
        async with session.post(f"{base_url}/api/v1/lex", json=test_message) as resp:
            if resp.status == 200:
                data = await resp.json()
                response = data["response"]
                print("✅ Capabilities response received")
                print(f"📝 Response length: {len(response)} characters")
                
                # Check for key capabilities
                capabilities_found = []
                capability_keywords = [
                    "Core Intelligence", "Technical Capabilities", "Creative", 
                    "Business", "Research", "Communication", "Memory"
                ]
                
                for keyword in capability_keywords:
                    if keyword in response:
                        capabilities_found.append(keyword)
                
                print(f"✅ Found capabilities: {', '.join(capabilities_found)}")
                
                # Check for thinking tags
                if "<think>" in response or "<thinking>" in response:
                    print("❌ ERROR: Thinking tags found in response!")
                else:
                    print("✅ No thinking tags found")
            else:
                print(f"❌ Error: {resp.status}")
        
        # Test 2: Memory - Introduce name
        print("\n🧠 Test 2: Memory - Name Introduction")
        test_message = {
            "message": "Hi! My name is Alice and I'm a software developer.",
            "voice_mode": False
        }
        
        async with session.post(f"{base_url}/api/v1/lex", json=test_message) as resp:
            if resp.status == 200:
                data = await resp.json()
                response = data["response"]
                print("✅ Name introduction response received")
                print(f"📝 Response preview: {response[:200]}...")
                
                # Check for thinking tags
                if "<think>" in response or "<thinking>" in response:
                    print("❌ ERROR: Thinking tags found in response!")
                else:
                    print("✅ No thinking tags found")
            else:
                print(f"❌ Error: {resp.status}")
        
        # Wait a moment for memory processing
        await asyncio.sleep(1)
        
        # Test 3: Memory Recall
        print("\n🔄 Test 3: Memory Recall")
        test_message = {
            "message": "Do you remember my name?",
            "voice_mode": False
        }
        
        async with session.post(f"{base_url}/api/v1/lex", json=test_message) as resp:
            if resp.status == 200:
                data = await resp.json()
                response = data["response"]
                print("✅ Memory recall response received")
                print(f"📝 Response: {response}")
                
                # Check if name is remembered
                if "Alice" in response:
                    print("✅ Name successfully remembered!")
                else:
                    print("⚠️ Name not found in response (may still be learning)")
                
                # Check for thinking tags
                if "<think>" in response or "<thinking>" in response:
                    print("❌ ERROR: Thinking tags found in response!")
                else:
                    print("✅ No thinking tags found")
            else:
                print(f"❌ Error: {resp.status}")
        
        # Test 4: Direct Question Response
        print("\n❓ Test 4: Direct Question Response")
        test_message = {
            "message": "What is 2 + 2?",
            "voice_mode": False
        }
        
        async with session.post(f"{base_url}/api/v1/lex", json=test_message) as resp:
            if resp.status == 200:
                data = await resp.json()
                response = data["response"]
                print("✅ Direct question response received")
                print(f"📝 Response: {response}")
                
                # Check if answer is provided
                if "4" in response:
                    print("✅ Question answered correctly!")
                else:
                    print("⚠️ Answer not clearly provided")
                
                # Check for thinking tags
                if "<think>" in response or "<thinking>" in response:
                    print("❌ ERROR: Thinking tags found in response!")
                else:
                    print("✅ No thinking tags found")
            else:
                print(f"❌ Error: {resp.status}")
        
        # Test 5: Creative Task
        print("\n🎨 Test 5: Creative Task")
        test_message = {
            "message": "Write a short poem about coding.",
            "voice_mode": False
        }
        
        async with session.post(f"{base_url}/api/v1/lex", json=test_message) as resp:
            if resp.status == 200:
                data = await resp.json()
                response = data["response"]
                print("✅ Creative task response received")
                print(f"📝 Response preview: {response[:300]}...")
                
                # Check for thinking tags
                if "<think>" in response or "<thinking>" in response:
                    print("❌ ERROR: Thinking tags found in response!")
                else:
                    print("✅ No thinking tags found")
                
                # Check if it's actually a poem (basic check)
                if len(response.split('\n')) > 3:
                    print("✅ Multi-line creative content generated")
                else:
                    print("⚠️ Response may not be properly formatted")
            else:
                print(f"❌ Error: {resp.status}")
        
        # Test 6: Memory System Status
        print("\n📊 Test 6: Memory System Status")
        try:
            async with session.get(f"{base_url}/api/v1/lex/memory/api_user") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print("✅ Memory system accessible")
                    print(f"📈 Total interactions: {data.get('recent_interactions', 0)}")
                    print(f"🧠 Stored memories: {data.get('stored_memories', 0)}")
                    if data.get('profile', {}).get('name'):
                        print(f"👤 Remembered name: {data['profile']['name']}")
                else:
                    print(f"⚠️ Memory endpoint status: {resp.status}")
        except Exception as e:
            print(f"⚠️ Memory system test skipped: {e}")

async def test_health_check():
    """Test server health"""
    print("\n🏥 Health Check")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/health") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print("✅ Server is healthy")
                    print(f"📊 Status: {data.get('status', 'unknown')}")
                    if data.get('memory_system'):
                        memory_stats = data['memory_system']
                        print(f"🧠 Memory stats: {memory_stats}")
                else:
                    print(f"❌ Health check failed: {resp.status}")
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("💡 Make sure to start the server first:")
        print("   python simple_lex_server.py")
        print("   or")
        print("   python lex_ai_with_memory.py")
        return False
    
    return True

async def main():
    """Run all tests"""
    print("🔱 LEX AI System Test Suite 🔱")
    print("Testing fixes for:")
    print("✓ Persistent memory and user name recall")
    print("✓ Proper response generation")
    print("✓ Thinking tag removal")
    print("✓ Capabilities listing")
    print()
    
    # Check server health first
    if await test_health_check():
        await test_lex_system()
        
        print("\n" + "=" * 50)
        print("🔱 Test Suite Complete! 🔱")
        print("\n💡 To verify memory persistence:")
        print("1. Stop the server")
        print("2. Restart it")
        print("3. Ask 'Do you remember my name?' again")
        print("4. The system should recall Alice from previous session")
    else:
        print("\n❌ Cannot run tests - server not available")

if __name__ == "__main__":
    asyncio.run(main())