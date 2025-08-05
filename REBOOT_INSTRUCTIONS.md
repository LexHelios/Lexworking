# 🔄 System Reboot Required for H100 GPU

## Why Reboot is Needed
The ECC (Error Correcting Code) mode change on your H100 GPU requires a system restart to take effect. This will resolve the CUDA error 802.

## How to Reboot

### Option 1: Terminal Command (Recommended)
```bash
sudo reboot
```

### Option 2: Shutdown and Restart
```bash
sudo shutdown -r now
```

### Option 3: Schedule Reboot (1 minute warning)
```bash
sudo shutdown -r +1 "System rebooting to apply GPU changes"
```

## After Reboot Checklist

1. **Verify GPU is working:**
   ```bash
   cd /home/user/Alphalexnew/QodoLexosbuild-main/LexWorking
   source venv/bin/activate
   python3 -c "import torch; print(torch.cuda.is_available())"
   ```

2. **Start your LEX AI server:**
   ```bash
   ./start_lex_final.sh
   ```

3. **Verify GPU is being used:**
   ```bash
   nvidia-smi
   ```
   You should see processes using GPU memory.

## Important Notes
- Save any work before rebooting
- The reboot will apply the ECC disable setting
- GPU persistence mode will remain enabled
- Your LEX AI system will be ready to use GPU acceleration

Please run `sudo reboot` in your terminal now.