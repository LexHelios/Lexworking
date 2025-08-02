#!/usr/bin/env python3
"""Test ComfyUI directly"""
import requests
import json

# Simple SDXL workflow
workflow = {
    "3": {
        "inputs": {
            "seed": 123456,
            "steps": 20,
            "cfg": 7.0,
            "sampler_name": "euler",
            "scheduler": "normal",
            "denoise": 1,
            "model": ["4", 0],
            "positive": ["6", 0],
            "negative": ["7", 0],
            "latent_image": ["5", 0]
        },
        "class_type": "KSampler"
    },
    "4": {
        "inputs": {
            "ckpt_name": "sd_xl_base_1.0.safetensors"
        },
        "class_type": "CheckpointLoaderSimple"
    },
    "5": {
        "inputs": {
            "width": 1024,
            "height": 1024,
            "batch_size": 1
        },
        "class_type": "EmptyLatentImage"
    },
    "6": {
        "inputs": {
            "text": "a beautiful sunset over mountains",
            "clip": ["4", 1]
        },
        "class_type": "CLIPTextEncode"
    },
    "7": {
        "inputs": {
            "text": "bad quality, blurry",
            "clip": ["4", 1]
        },
        "class_type": "CLIPTextEncode"
    },
    "8": {
        "inputs": {
            "samples": ["3", 0],
            "vae": ["4", 2]
        },
        "class_type": "VAEDecode"
    },
    "9": {
        "inputs": {
            "filename_prefix": "ComfyUI",
            "images": ["8", 0]
        },
        "class_type": "SaveImage"
    }
}

print("Testing ComfyUI direct API...")
print(f"Workflow nodes: {list(workflow.keys())}")

# Queue the prompt
response = requests.post(
    "http://localhost:8188/prompt",
    json={"prompt": workflow}
)

print(f"\nResponse status: {response.status_code}")
print(f"Response: {response.text[:500]}...")

if response.status_code == 200:
    result = response.json()
    print(f"\nPrompt ID: {result.get('prompt_id', 'None')}")
    print("✅ Successfully queued!")
else:
    print(f"\n❌ Failed: {response.text}")