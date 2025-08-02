# 🎨 Adding Models to ComfyUI

## Quick Start - Download ONE Model First

Since you have ComfyUI running, you just need to add a model. Here's the easiest way:

### Option 1: Download SDXL Base (Recommended for Testing)
1. Go to: https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/tree/main
2. Download: `sd_xl_base_1.0.safetensors` (6.94 GB)
3. Place in: `ComfyUI_windows_portable\ComfyUI\models\checkpoints\`

### Option 2: Use CivitAI (More Models)
1. Go to: https://civitai.com/models
2. Search for "SDXL" or "Pony Diffusion"
3. Download any `.safetensors` file
4. Place in: `ComfyUI_windows_portable\ComfyUI\models\checkpoints\`

### Option 3: Quick Test Model (Smaller)
For quick testing, you can use SD 1.5 models (smaller ~2GB):
1. Go to: https://huggingface.co/runwayml/stable-diffusion-v1-5/tree/main
2. Download: `v1-5-pruned.safetensors`
3. Place in: `ComfyUI_windows_portable\ComfyUI\models\checkpoints\`

## After Adding a Model

1. **Restart ComfyUI** (or refresh the browser)
2. **Test in LEX**: "Generate an image of a dragon"
3. **Check ComfyUI UI**: http://localhost:8188

## Model Recommendations

### For General Use:
- **SDXL Base 1.0** - Good quality, versatile

### For Anime/Art:
- **Pony Diffusion V6 XL** - Great for stylized art
- **Anything V5** - Popular anime model

### For Photorealistic:
- **Realistic Vision V5.1** - Photorealistic humans
- **Juggernaut XL** - High quality realistic

### For NSFW/Uncensored:
- **Pony Diffusion V6 XL** - No content restrictions
- **Deliberate V3** - Uncensored realistic

## Troubleshooting

### "No models found"
- Make sure files are in: `models\checkpoints\`
- Files must be `.safetensors` or `.ckpt`
- Restart ComfyUI after adding

### "Out of memory"
- SDXL models need ~8GB VRAM
- Use SD 1.5 models for less VRAM
- Enable CPU mode if needed

### Models Not Showing in LEX
- Check ComfyUI is running: http://localhost:8188
- Verify model loaded in ComfyUI UI
- Restart LEX Docker container

## Quick Download Links

Copy these URLs to your browser:

**SDXL Base (6.94GB)**
```
https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors
```

**SD 1.5 (2GB) - For Testing**
```
https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned.safetensors
```

Once you have at least one model, LEX image generation will work!