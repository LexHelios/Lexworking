#!/usr/bin/env python3
"""Test image generation detection"""

import requests
import json

# Test various prompts
test_prompts = [
    "Generate an image of a cyberpunk city",
    "Create a picture of a sunset",
    "Make an image of a cat",
    "Draw a beautiful woman",
    "Generate a big butt women",  # Testing uncensored
    "What is 2+2?",  # Should NOT trigger image gen
    "Explain quantum physics"  # Should NOT trigger image gen
]

print("Testing LEX Image Generation Detection")
print("=" * 50)

for prompt in test_prompts:
    print(f"\nPrompt: {prompt}")
    
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/lex",
            json={"message": prompt, "voice_mode": False},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if it detected image generation
            capabilities = data.get("capabilities_used", [])
            action = data.get("action_taken", "")
            
            is_image_gen = any("image" in cap.lower() or "comfyui" in cap.lower() for cap in capabilities)
            
            print(f"  Action: {action}")
            print(f"  Image Gen Detected: {'YES' if is_image_gen else 'NO'}")
            
            # Show partial response
            resp_text = data.get("response", "")[:100]
            if len(resp_text) == 100:
                resp_text += "..."
            print(f"  Response: {resp_text}")
            
        else:
            print(f"  ERROR: {response.status_code}")
            
    except Exception as e:
        print(f"  ERROR: {e}")

print("\n" + "=" * 50)
print("Test complete!")