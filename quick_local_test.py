import requests
import json

# Test Ollama directly
print("Testing Ollama local inference on RTX 4090...")

# Test unrestricted Dolphin model
payload = {
    "model": "dolphin-mixtral:latest",
    "prompt": "What are the benefits of using local LLMs on an RTX 4090? Be completely honest about any limitations.",
    "stream": False,
    "options": {
        "temperature": 0.7,
        "num_predict": 200
    }
}

try:
    response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=30)
    if response.status_code == 200:
        data = response.json()
        print("\n--- Dolphin-Mixtral Response ---")
        print(data['response'])
        print(f"\nGeneration time: {data.get('total_duration', 0) / 1e9:.2f} seconds")
    else:
        print(f"Error: {response.status_code}")
except Exception as e:
    print(f"Error: {e}")

# Test LEX integration
print("\n\nTesting LEX with local models...")
lex_payload = {
    "message": "Are you using local models on my RTX 4090?",
    "voice_mode": False
}

try:
    response = requests.post("http://localhost:8000/api/v1/lex", json=lex_payload, timeout=30)
    if response.status_code == 200:
        data = response.json()
        print("\n--- LEX Response ---")
        print(data['response'])
        print(f"\nCapabilities used: {data['capabilities_used']}")
        print(f"Confidence: {data['confidence']:.1%}")
    else:
        print(f"Error: {response.status_code}")
except Exception as e:
    print(f"Error connecting to LEX: {e}")