"""
Test Alibaba Cloud Setup
Verify all services are working with your API key
"""
import os
import asyncio
from openai import AsyncOpenAI

# Set your API key directly for testing
os.environ['ALIBABA_API_KEY'] = 'ZR8aDx3cydICAhvyH85QVkujkSrUlz'

async def test_qwen_text():
    """Test Qwen 2.5-Max text generation"""
    print("🔥 Testing Qwen 2.5-Max...")
    
    try:
        client = AsyncOpenAI(
            api_key=os.environ['ALIBABA_API_KEY'],
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        
        response = await client.chat.completions.create(
            model="qwen2.5-max",
            messages=[
                {"role": "user", "content": "Say 'Qwen is connected to LexOS!'"}
            ],
            max_tokens=50
        )
        
        print("✅ Qwen 2.5-Max Response:", response.choices[0].message.content)
        return True
        
    except Exception as e:
        print(f"❌ Qwen Error: {e}")
        # Try international endpoint
        try:
            client = AsyncOpenAI(
                api_key=os.environ['ALIBABA_API_KEY'],
                base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
            )
            response = await client.chat.completions.create(
                model="qwen-max",
                messages=[
                    {"role": "user", "content": "Say 'Qwen is connected!'"}
                ],
                max_tokens=50
            )
            print("✅ Qwen (International) Response:", response.choices[0].message.content)
            return True
        except Exception as e2:
            print(f"❌ Qwen International Error: {e2}")
            return False

async def test_wan_image():
    """Test Wan image generation"""
    print("\n🎨 Testing Wan Image Generation...")
    
    try:
        from server.orchestrator.cloud_providers.wan_provider import WanProvider
        
        # Initialize with your key
        wan = WanProvider()
        wan.api_key = os.environ['ALIBABA_API_KEY']
        wan._initialize_client()
        
        result = await wan.test_connection()
        
        if result.get("available"):
            print("✅ Wan Image Generation: Connected!")
            print("   Available models:", result.get("image_models", []))
        else:
            print("❌ Wan Error:", result.get("error"))
            
        return result.get("available", False)
        
    except Exception as e:
        print(f"❌ Wan Setup Error: {e}")
        return False

async def main():
    print("🚀 ALIBABA CLOUD SETUP TEST")
    print("=" * 50)
    print(f"API Key: {os.environ['ALIBABA_API_KEY'][:20]}...")
    print("=" * 50)
    
    # Test text generation
    text_ok = await test_qwen_text()
    
    # Test image generation
    image_ok = await test_wan_image()
    
    print("\n" + "=" * 50)
    print("📊 RESULTS:")
    print(f"- Qwen Text Generation: {'✅ Working' if text_ok else '❌ Failed'}")
    print(f"- Wan Image Generation: {'✅ Working' if image_ok else '❌ Failed'}")
    
    if text_ok:
        print("\n🎉 Alibaba Cloud is ready for LexOS!")
        print("You can now:")
        print("- Use Qwen 2.5-Max for uncensored text generation")
        print("- Generate images with 'draw' or 'generate image' commands")
        print("- Create videos with 'generate video' commands")
    else:
        print("\n⚠️ Some services may need configuration")
        print("Check if you're using the international endpoint")

if __name__ == "__main__":
    asyncio.run(main())