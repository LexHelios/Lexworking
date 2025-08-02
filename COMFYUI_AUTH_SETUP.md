# 🔐 ComfyUI Authentication Setup

## The Issue
ComfyUI requires authentication when accessed remotely or with certain security settings enabled.

## Solution Options

### Option 1: Disable Authentication (Easiest for Local Use)

1. **Find ComfyUI Launch Script**
   - Look for `run_nvidia_gpu.bat` or `run_cpu.bat`
   - Edit the file

2. **Add No-Auth Flag**
   ```batch
   python main.py --listen 0.0.0.0 --port 8188 --disable-metadata
   ```
   
   Or if you want to keep it more secure:
   ```batch
   python main.py --listen 127.0.0.1 --port 8188
   ```

### Option 2: Use API Key Authentication

1. **Generate API Key in ComfyUI**
   ```batch
   python main.py --listen 0.0.0.0 --port 8188 --enable-cors-header "*"
   ```

2. **Update LEX Integration**
   Add authentication header to requests

### Option 3: Use ComfyUI's Built-in Auth

1. **Set Username/Password**
   Create `ComfyUI/user/default/comfyui.yaml`:
   ```yaml
   auth:
     username: "your_username"
     password: "your_password"
   ```

2. **Update LEX to Use Credentials**

## Quick Fix for Now

Since you're running locally, the easiest solution is to:

1. **Stop ComfyUI** (Ctrl+C in the terminal)

2. **Restart with Open Access**:
   ```batch
   cd ComfyUI_windows_portable
   python ComfyUI/main.py --listen 127.0.0.1 --port 8188 --preview-method auto
   ```

3. **Or Create a New Batch File**:
   `run_comfyui_no_auth.bat`:
   ```batch
   @echo off
   cd ComfyUI
   python main.py --listen 127.0.0.1 --port 8188 --preview-method auto
   pause
   ```

## If You Need Authentication

Let me know and I'll update the LEX integration to handle:
- Basic Auth (username/password)
- API Key authentication
- Session-based auth

## Testing After Changes

1. Restart ComfyUI with new settings
2. Check if http://localhost:8188 loads without login
3. Test LEX: "Generate an image of a cat"

Which approach would you prefer?