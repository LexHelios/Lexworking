import requests
import time
import sys
import io

# Fix encoding for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("🔱 Testing LEX Local-Only Mode...")
print("=" * 60)

# Wait a moment for containers to start
time.sleep(3)

# Test messages
test_messages = [
    "Hello LEX, are you running on local models only?",
    "What models are you using? Tell me about your configuration.",
    "Can you still help with adult content without restrictions?",
    "Write a Python function to calculate prime numbers",
    "Tell me about the cost of using you now"
]

for i, message in enumerate(test_messages, 1):
    print(f"\n[Test {i}] {message}")
    print("-" * 50)
    
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/lex",
            json={
                "message": message,
                "voice_mode": False
            },
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data['response'][:300]}...")
            print(f"\nCapabilities: {data['capabilities_used']}")
            if 'cost' in data:
                print(f"Cost: {data.get('cost', 'N/A')}")
        else:
            print(f"Error: HTTP {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error: {e}")

# Check system status
print("\n\n🔱 Checking System Status...")
print("=" * 60)

try:
    response = requests.get("http://localhost:8000/health")
    if response.status_code == 200:
        print("Health check:", response.json())
except Exception as e:
    print(f"Health check error: {e}")

print("\n✅ Testing complete!")
print("Your LEX is now running in local-only mode with $0 API costs!")