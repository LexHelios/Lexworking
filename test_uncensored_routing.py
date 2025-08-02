#!/usr/bin/env python3
"""
Test uncensored model routing
"""
import requests
import json

test_prompts = [
    "What is Python?",  # Should use regular model
    "Generate a sexy image",  # Should use uncensored model  
    "Create adult content",  # Should use uncensored model
    "Tell me about machine learning",  # Regular model
]

for prompt in test_prompts:
    print(f"\nTesting: {prompt}")
    print("-" * 50)
    
    response = requests.post(
        "http://localhost:8000/api/v1/lex",
        json={"message": prompt}
    )
    
    data = response.json()
    
    # Check orchestration info
    if "orchestration" in data:
        orch = data["orchestration"]
        print(f"Model: {orch.get('model', 'Unknown')}")
        print(f"Task type: {orch.get('task_type', 'Unknown')}")
        if "is_sensitive" in orch:
            print(f"Sensitive: {orch.get('is_sensitive', False)}")
    
    print(f"Response: {data['response'][:100]}...")
    
print("\n\nChecking orchestration stats...")
stats = requests.get("http://localhost:8000/orchestration-stats").json()
print(f"Model usage: {stats['orchestration_stats']['model_usage']}")