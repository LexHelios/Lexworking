#!/usr/bin/env python3
"""
Download uncensored models for ComfyUI
Optimized for RTX 4090 (24GB VRAM)
"""
import os
import requests
import subprocess
from pathlib import Path
import json

# Model directory
COMFYUI_DIR = Path("comfyui_system/ComfyUI")
MODELS_DIR = COMFYUI_DIR / "models" / "checkpoints"

# Uncensored models suitable for RTX 4090
UNCENSORED_MODELS = {
    "pony_diffusion_v6_xl": {
        "name": "Pony Diffusion V6 XL",
        "url": "https://civitai.com/api/download/models/290640",
        "filename": "ponyDiffusionV6XL.safetensors",
        "size": "6.94 GB",
        "description": "Highly versatile uncensored model, excellent for all content types",
        "vram_required": 8
    },
    "realistic_vision_v51": {
        "name": "Realistic Vision V5.1", 
        "url": "https://civitai.com/api/download/models/130072",
        "filename": "realisticVisionV51.safetensors",
        "size": "5.75 GB",
        "description": "Photorealistic uncensored model",
        "vram_required": 6
    },
    "juggernaut_xl": {
        "name": "Juggernaut XL V9",
        "url": "https://civitai.com/api/download/models/348913",
        "filename": "juggernautXL_v9.safetensors", 
        "size": "6.62 GB",
        "description": "High quality realistic and artistic model",
        "vram_required": 8
    },
    "sdxl_base": {
        "name": "SDXL Base 1.0",
        "url": "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors",
        "filename": "sd_xl_base_1.0.safetensors",
        "size": "6.94 GB", 
        "description": "Base SDXL model - foundation for many other models",
        "vram_required": 8
    }
}

# VAE models for better quality
VAE_MODELS = {
    "sdxl_vae": {
        "name": "SDXL VAE",
        "url": "https://huggingface.co/stabilityai/sdxl-vae/resolve/main/sdxl_vae.safetensors",
        "filename": "sdxl_vae.safetensors",
        "size": "334 MB"
    }
}

def download_file(url, filepath, chunk_size=8192):
    """Download file with progress bar"""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(filepath, 'wb') as file:
        downloaded = 0
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                file.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    print(f"\rDownloading: {percent:.1f}%", end='', flush=True)
    print()

def check_disk_space(required_gb):
    """Check if enough disk space is available"""
    import shutil
    stat = shutil.disk_usage(".")
    available_gb = stat.free / (1024**3)
    return available_gb > required_gb

def main():
    print("=" * 60)
    print("UNCENSORED MODEL DOWNLOADER FOR COMFYUI")
    print("RTX 4090 Optimized (24GB VRAM)")
    print("=" * 60)
    print()
    
    # Create directories
    os.makedirs(MODELS_DIR, exist_ok=True)
    os.makedirs(COMFYUI_DIR / "models" / "vae", exist_ok=True)
    
    # Check disk space
    total_size_gb = sum(float(m["size"].split()[0]) for m in UNCENSORED_MODELS.values()) + 0.5
    if not check_disk_space(total_size_gb):
        print(f"WARNING: May not have enough disk space. Need ~{total_size_gb:.1f}GB")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return
    
    # List available models
    print("Available uncensored models:")
    for i, (key, model) in enumerate(UNCENSORED_MODELS.items(), 1):
        print(f"{i}. {model['name']} ({model['size']}) - {model['description']}")
    
    print("\nWhich models to download?")
    print("Enter numbers separated by commas (e.g., 1,3,4) or 'all' for all models:")
    choice = input("> ").strip()
    
    # Parse selection
    if choice.lower() == 'all':
        selected_models = list(UNCENSORED_MODELS.keys())
    else:
        try:
            indices = [int(x.strip()) - 1 for x in choice.split(',')]
            model_keys = list(UNCENSORED_MODELS.keys())
            selected_models = [model_keys[i] for i in indices if 0 <= i < len(model_keys)]
        except:
            print("Invalid selection")
            return
    
    # Download selected models
    print(f"\nDownloading {len(selected_models)} models...")
    
    for model_key in selected_models:
        model = UNCENSORED_MODELS[model_key]
        filepath = MODELS_DIR / model["filename"]
        
        if filepath.exists():
            print(f"\n{model['name']} already exists, skipping...")
            continue
        
        print(f"\nDownloading {model['name']}...")
        print(f"URL: {model['url']}")
        print(f"Size: {model['size']}")
        
        try:
            # For CivitAI links, we might need to handle redirects
            if "civitai.com" in model["url"]:
                print("Note: CivitAI download may require browser download")
                print(f"Direct link: {model['url']}")
                print("You may need to download manually and place in:")
                print(f"  {filepath}")
                input("Press Enter to continue...")
            else:
                download_file(model["url"], filepath)
                print(f"✓ Downloaded {model['name']}")
        except Exception as e:
            print(f"✗ Error downloading {model['name']}: {e}")
    
    # Download VAE
    print("\nDownloading SDXL VAE for better quality...")
    vae_path = COMFYUI_DIR / "models" / "vae" / VAE_MODELS["sdxl_vae"]["filename"]
    if not vae_path.exists():
        try:
            download_file(VAE_MODELS["sdxl_vae"]["url"], vae_path)
            print("✓ Downloaded SDXL VAE")
        except Exception as e:
            print(f"✗ Error downloading VAE: {e}")
    
    print("\n" + "=" * 60)
    print("DOWNLOAD COMPLETE!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Start ComfyUI with 'run_comfyui.bat'")
    print("2. Access http://localhost:8188")
    print("3. Load a workflow or create your own")
    print("\nFor CivitAI models that failed to download:")
    print("1. Visit the URL in your browser")
    print("2. Download manually")
    print(f"3. Place in: {MODELS_DIR}")

if __name__ == "__main__":
    main()