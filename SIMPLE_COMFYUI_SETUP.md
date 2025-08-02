# 🎨 SIMPLE COMFYUI SETUP FOR LEX

## Option 1: Manual Download (Easiest)

1. **Download ComfyUI Portable**
   - Go to: https://github.com/comfyanonymous/ComfyUI/releases
   - Download: `ComfyUI_windows_portable_nvidia_cu124_or_cpu.7z`
   - Size: ~2GB

2. **Extract**
   - Install 7-Zip from: https://www.7-zip.org/
   - Right-click the .7z file → 7-Zip → Extract Here
   - You'll get a folder: `ComfyUI_windows_portable`

3. **Move to LEX**
   - Move the entire `ComfyUI_windows_portable` folder to:
   - `C:\Users\Vince\Documents\lexos-core\lexcommand-shadow-autonomy\lexworking\`

4. **Run ComfyUI**
   - Open the folder
   - Double-click: `run_nvidia_gpu.bat`
   - ComfyUI will start at: http://localhost:8188

## Option 2: Direct URL Download

Copy and paste this into your browser:
```
https://github.com/comfyanonymous/ComfyUI/releases/latest/download/ComfyUI_windows_portable_nvidia_cu124_or_cpu.7z
```

## Option 3: Use Git Clone (Developers)

```bash
cd lexworking
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
pip install -r requirements.txt
python main.py --listen 0.0.0.0 --port 8188
```

## Once ComfyUI is Running

1. Check it's working: http://localhost:8188
2. Test in LEX:
   - "Generate an image of a sunset"
   - "Create a picture of a dragon"
   - "Make an image of a beautiful woman"

## Troubleshooting

### Port 8188 Already in Use
```bash
netstat -ano | findstr :8188
taskkill /PID <process_id> /F
```

### GPU Not Detected
- ComfyUI will fall back to CPU (slower)
- Make sure NVIDIA drivers are updated

### Missing Models
- ComfyUI comes with basic models
- For uncensored models, run: `download_uncensored_models.py`

## Quick Test

Once ComfyUI is running, test with:
```bash
curl http://localhost:8188/system_stats
```

You should see GPU info!