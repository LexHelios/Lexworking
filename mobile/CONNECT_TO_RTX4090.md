# Connect LexOS Mobile to Your RTX 4090 PC

## 🚀 Overview

Your RTX 4090 can power advanced features for the mobile app by running a local LexOS server.

## 🖥️ PC Setup (RTX 4090)

### 1. Start LexOS Server
```bash
cd C:\Users\Vince\Documents\lexos-core\lexcommand-shadow-autonomy\lexworking
python start_production.py
```

The server will start on `http://localhost:8000`

### 2. Find Your PC's IP Address
```bash
# Windows
ipconfig
# Look for IPv4 Address (e.g., 192.168.1.100)
```

### 3. Configure Firewall
Allow port 8000 through Windows Firewall:
```bash
netsh advfirewall firewall add rule name="LexOS Server" dir=in action=allow protocol=TCP localport=8000
```

## 📱 Mobile App Setup

1. Open LexOS Mobile app
2. Go to Settings (gear icon)
3. Enter your PC's address:
   ```
   LexOS Server URL: http://192.168.1.100:8000
   ```
4. Save settings

## 🎯 RTX 4090 Enhanced Features

When connected to your PC, the app can:

### 1. **Local LLM Processing**
- Run uncensored models locally
- Faster response times on same network
- Privacy - data stays on your network

### 2. **Image Generation**
- FLUX models using RTX 4090
- ComfyUI integration
- Say "Generate an image of..."

### 3. **Advanced Processing**
- Document analysis with vision models
- Code generation with specialized models
- Multi-modal processing

### 4. **Voice Processing**
- Local Whisper models for transcription
- Custom voice models
- Real-time processing

## 📊 Performance Comparison

| Feature | Cloud Only | With RTX 4090 |
|---------|------------|---------------|
| Response Time | 1-3s | 0.1-0.5s (local network) |
| Image Generation | ❌ | ✅ FLUX, SDXL |
| Privacy | Cloud | Local |
| Offline Mode | ❌ | ✅ |
| Custom Models | ❌ | ✅ |
| Cost | ~$35-45/mo | Free (your hardware) |

## 🔧 Advanced Configuration

### Run Multiple Models
Edit `server/settings.py` on your PC:
```python
MODELS = {
    "primary": "qwen2.5-max",  # Cloud
    "local": "llama3:70b",      # RTX 4090
    "vision": "llava:34b",      # RTX 4090
    "uncensored": "dolphin-mixtral:8x7b"  # RTX 4090
}
```

### Optimize for RTX 4090
```python
# In start_production.py
CUDA_VISIBLE_DEVICES=0
PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
```

## 🏠 Home Network Tips

1. **Static IP**: Assign static IP to your PC
2. **Wake-on-LAN**: Enable to start PC remotely
3. **VPN**: Access from outside home network
4. **HTTPS**: Use nginx for secure connection

## 📱 Mobile App Code

The app automatically detects and uses local server when configured:

```javascript
// In LexService.js
if (this.serverUrl) {
  // Use RTX 4090 powered local server
  response = await fetch(`${this.serverUrl}/api/lex/chat`, {
    method: 'POST',
    body: JSON.stringify({ message, useGPU: true })
  });
} else {
  // Use cloud services
  response = await fetch(ALIBABA_API);
}
```

## 🚀 Quick Test

In the mobile app, try:
- "Generate an image of a cyberpunk city"
- "Analyze this photo" (take a picture)
- "Write code using the local GPU"

Your RTX 4090 will handle the heavy lifting while your phone provides the interface!