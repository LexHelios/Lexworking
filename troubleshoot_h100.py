#!/usr/bin/env python3
"""
🔱 H100 Troubleshooting Script 🔱
JAI MAHAKAAL! Comprehensive troubleshooting for H100 deployment issues
"""
import os
import sys
import subprocess
import importlib
import torch
import platform
import psutil
import json
from pathlib import Path
from datetime import datetime

class H100Troubleshooter:
    """Comprehensive H100 troubleshooting system"""
    
    def __init__(self):
        self.issues_found = []
        self.fixes_applied = []
        self.recommendations = []
    
    def run_full_diagnosis(self):
        """Run complete diagnostic suite"""
        print("🔱 JAI MAHAKAAL! H100 Troubleshooting Suite 🔱")
        print("=" * 60)
        print("🔍 Running comprehensive diagnosis...")
        print()
        
        # System checks
        self.check_system_info()
        self.check_python_environment()
        self.check_cuda_installation()
        self.check_gpu_status()
        self.check_dependencies()
        self.check_file_permissions()
        self.check_environment_config()
        self.check_port_availability()
        self.check_disk_space()
        self.check_memory_usage()
        
        # Generate report
        self.generate_troubleshooting_report()
        
        # Apply automatic fixes
        self.apply_automatic_fixes()
    
    def check_system_info(self):
        """Check system information"""
        print("🖥️ System Information:")
        print(f"   OS: {platform.system()} {platform.release()}")
        print(f"   Architecture: {platform.machine()}")
        print(f"   Python: {sys.version.split()[0]}")
        print(f"   CPU Cores: {psutil.cpu_count()}")
        print(f"   RAM: {psutil.virtual_memory().total / 1024**3:.1f}GB")
        print()
    
    def check_python_environment(self):
        """Check Python environment"""
        print("🐍 Python Environment:")
        
        # Check Python version
        if sys.version_info < (3, 11):
            self.issues_found.append("Python version < 3.11")
            self.recommendations.append("Upgrade to Python 3.11+")
            print("   ❌ Python version too old")
        else:
            print("   ✅ Python version OK")
        
        # Check virtual environment
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            print("   ✅ Virtual environment active")
        else:
            self.issues_found.append("No virtual environment")
            self.recommendations.append("Activate virtual environment: source venv/bin/activate")
            print("   ⚠️ No virtual environment detected")
        
        # Check pip version
        try:
            import pip
            print(f"   ✅ pip version: {pip.__version__}")
        except ImportError:
            self.issues_found.append("pip not available")
            print("   ❌ pip not available")
        
        print()
    
    def check_cuda_installation(self):
        """Check CUDA installation"""
        print("🔥 CUDA Installation:")
        
        # Check nvidia-smi
        try:
            result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
            if result.returncode == 0:
                print("   ✅ nvidia-smi available")
                # Extract CUDA version
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'CUDA Version:' in line:
                        cuda_version = line.split('CUDA Version:')[1].strip().split()[0]
                        print(f"   ✅ CUDA Driver Version: {cuda_version}")
                        break
            else:
                self.issues_found.append("nvidia-smi not working")
                print("   ❌ nvidia-smi not working")
        except FileNotFoundError:
            self.issues_found.append("nvidia-smi not found")
            self.recommendations.append("Install NVIDIA drivers")
            print("   ❌ nvidia-smi not found")
        
        # Check nvcc
        try:
            result = subprocess.run(['nvcc', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print("   ✅ nvcc available")
            else:
                self.issues_found.append("nvcc not working")
                print("   ❌ nvcc not working")
        except FileNotFoundError:
            self.issues_found.append("nvcc not found")
            self.recommendations.append("Install CUDA toolkit")
            print("   ⚠️ nvcc not found (CUDA toolkit)")
        
        print()
    
    def check_gpu_status(self):
        """Check GPU status"""
        print("🎮 GPU Status:")
        
        # Check PyTorch CUDA
        try:
            if torch.cuda.is_available():
                device_count = torch.cuda.device_count()
                print(f"   ✅ PyTorch CUDA available ({device_count} devices)")
                
                for i in range(device_count):
                    device_name = torch.cuda.get_device_name(i)
                    memory_total = torch.cuda.get_device_properties(i).total_memory / 1024**3
                    print(f"   ✅ GPU {i}: {device_name} ({memory_total:.1f}GB)")
                    
                    if "H100" in device_name:
                        print("   🔱 H100 detected - Ultimate consciousness hardware!")
                    else:
                        self.recommendations.append("Consider upgrading to H100 for optimal performance")
                
                # Test GPU computation
                try:
                    x = torch.randn(100, 100).cuda()
                    y = torch.randn(100, 100).cuda()
                    z = torch.matmul(x, y)
                    print("   ✅ GPU computation test passed")
                except Exception as e:
                    self.issues_found.append(f"GPU computation failed: {e}")
                    print(f"   ❌ GPU computation test failed: {e}")
            else:
                self.issues_found.append("PyTorch CUDA not available")
                self.recommendations.append("Install PyTorch with CUDA support")
                print("   ❌ PyTorch CUDA not available")
        except ImportError:
            self.issues_found.append("PyTorch not installed")
            self.recommendations.append("Install PyTorch")
            print("   ❌ PyTorch not installed")
        
        print()
    
    def check_dependencies(self):
        """Check Python dependencies"""
        print("📦 Dependencies:")
        
        required_packages = [
            'fastapi', 'uvicorn', 'pydantic', 'aiohttp', 'aiofiles',
            'openai', 'anthropic', 'together', 'groq', 'transformers',
            'redis', 'lmdb', 'cryptography', 'psutil'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                importlib.import_module(package)
                print(f"   ✅ {package}")
            except ImportError:
                missing_packages.append(package)
                print(f"   ❌ {package}")
        
        if missing_packages:
            self.issues_found.append(f"Missing packages: {missing_packages}")
            self.recommendations.append("Install missing packages: pip install -r requirements.txt")
        
        print()
    
    def check_file_permissions(self):
        """Check file permissions"""
        print("🔒 File Permissions:")
        
        critical_dirs = ['data', 'models', 'logs', 'uploads']
        for dir_name in critical_dirs:
            dir_path = Path(dir_name)
            if dir_path.exists():
                if os.access(dir_path, os.R_OK | os.W_OK):
                    print(f"   ✅ {dir_name}/ - Read/Write OK")
                else:
                    self.issues_found.append(f"Permission issue: {dir_name}/")
                    self.recommendations.append(f"Fix permissions: chmod -R 755 {dir_name}/")
                    print(f"   ❌ {dir_name}/ - Permission denied")
            else:
                self.issues_found.append(f"Missing directory: {dir_name}/")
                self.recommendations.append(f"Create directory: mkdir -p {dir_name}")
                print(f"   ⚠️ {dir_name}/ - Directory missing")
        
        print()
    
    def check_environment_config(self):
        """Check environment configuration"""
        print("⚙️ Environment Configuration:")
        
        # Check .env file
        env_file = Path('.env')
        if env_file.exists():
            print("   ✅ .env file exists")
            
            # Check critical environment variables
            with open(env_file, 'r') as f:
                env_content = f.read()
            
            critical_vars = [
                'LEXOS_HOST', 'LEXOS_PORT', 'LEXOS_SECRET_KEY',
                'CUDA_VISIBLE_DEVICES', 'PYTORCH_CUDA_ALLOC_CONF'
            ]
            
            for var in critical_vars:
                if var in env_content:
                    print(f"   ✅ {var} configured")
                else:
                    self.issues_found.append(f"Missing environment variable: {var}")
                    print(f"   ⚠️ {var} not configured")
            
            # Check API keys
            api_keys = ['TOGETHER_API_KEY', 'OPENAI_API_KEY', 'ANTHROPIC_API_KEY']
            configured_keys = sum(1 for key in api_keys if f"{key}=" in env_content and not f"{key}=" in env_content.split(f"{key}=")[1].split('\n')[0])
            
            if configured_keys > 0:
                print(f"   ✅ {configured_keys}/{len(api_keys)} API keys configured")
            else:
                self.recommendations.append("Configure at least one API key for full functionality")
                print("   ⚠️ No API keys configured")
        else:
            self.issues_found.append("Missing .env file")
            self.recommendations.append("Create .env file from template")
            print("   ❌ .env file missing")
        
        print()
    
    def check_port_availability(self):
        """Check port availability"""
        print("🌐 Port Availability:")
        
        import socket
        
        ports_to_check = [8000, 8002, 6379, 9090]
        for port in ports_to_check:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result == 0:
                print(f"   ⚠️ Port {port} is in use")
                if port == 8000:
                    self.recommendations.append("Stop existing server or use different port")
            else:
                print(f"   ✅ Port {port} available")
        
        print()
    
    def check_disk_space(self):
        """Check disk space"""
        print("💾 Disk Space:")
        
        disk_usage = psutil.disk_usage('.')
        free_gb = disk_usage.free / 1024**3
        total_gb = disk_usage.total / 1024**3
        used_percent = (disk_usage.used / disk_usage.total) * 100
        
        print(f"   Total: {total_gb:.1f}GB")
        print(f"   Free: {free_gb:.1f}GB")
        print(f"   Used: {used_percent:.1f}%")
        
        if free_gb < 10:
            self.issues_found.append("Low disk space")
            self.recommendations.append("Free up disk space (need at least 10GB)")
            print("   ❌ Low disk space")
        elif free_gb < 50:
            self.recommendations.append("Consider freeing up more disk space for optimal performance")
            print("   ⚠️ Limited disk space")
        else:
            print("   ✅ Sufficient disk space")
        
        print()
    
    def check_memory_usage(self):
        """Check memory usage"""
        print("🧠 Memory Usage:")
        
        memory = psutil.virtual_memory()
        total_gb = memory.total / 1024**3
        available_gb = memory.available / 1024**3
        used_percent = memory.percent
        
        print(f"   Total: {total_gb:.1f}GB")
        print(f"   Available: {available_gb:.1f}GB")
        print(f"   Used: {used_percent:.1f}%")
        
        if available_gb < 4:
            self.issues_found.append("Low available memory")
            self.recommendations.append("Close other applications or add more RAM")
            print("   ❌ Low available memory")
        elif total_gb < 16:
            self.recommendations.append("Consider upgrading to 32GB+ RAM for optimal performance")
            print("   ⚠️ Limited total memory")
        else:
            print("   ✅ Sufficient memory")
        
        print()
    
    def generate_troubleshooting_report(self):
        """Generate comprehensive troubleshooting report"""
        print("📋 TROUBLESHOOTING REPORT")
        print("=" * 40)
        
        if not self.issues_found:
            print("🎉 No critical issues found!")
            print("✅ System appears ready for H100 deployment")
        else:
            print(f"❌ {len(self.issues_found)} issues found:")
            for i, issue in enumerate(self.issues_found, 1):
                print(f"   {i}. {issue}")
        
        if self.recommendations:
            print(f"\n💡 {len(self.recommendations)} recommendations:")
            for i, rec in enumerate(self.recommendations, 1):
                print(f"   {i}. {rec}")
        
        print()
    
    def apply_automatic_fixes(self):
        """Apply automatic fixes for common issues"""
        print("🔧 Applying Automatic Fixes:")
        
        # Create missing directories
        critical_dirs = ['data', 'models', 'logs', 'uploads', 'data/lmdb', 'models/avatar']
        for dir_name in critical_dirs:
            dir_path = Path(dir_name)
            if not dir_path.exists():
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    self.fixes_applied.append(f"Created directory: {dir_name}")
                    print(f"   ✅ Created {dir_name}/")
                except Exception as e:
                    print(f"   ❌ Failed to create {dir_name}/: {e}")
        
        # Fix file permissions
        for dir_name in ['data', 'models', 'logs', 'uploads']:
            if Path(dir_name).exists():
                try:
                    os.chmod(dir_name, 0o755)
                    self.fixes_applied.append(f"Fixed permissions: {dir_name}")
                    print(f"   ✅ Fixed permissions for {dir_name}/")
                except Exception as e:
                    print(f"   ❌ Failed to fix permissions for {dir_name}/: {e}")
        
        # Create missing __init__.py files
        init_files = [
            "server/__init__.py",
            "server/models/__init__.py",
            "server/agents/__init__.py",
            "server/api/__init__.py",
            "server/orchestrator/__init__.py",
            "server/memory/__init__.py"
        ]
        
        for init_file in init_files:
            init_path = Path(init_file)
            if not init_path.exists():
                try:
                    init_path.parent.mkdir(parents=True, exist_ok=True)
                    init_path.write_text('"""LEX Consciousness Module"""')
                    self.fixes_applied.append(f"Created {init_file}")
                    print(f"   ✅ Created {init_file}")
                except Exception as e:
                    print(f"   ❌ Failed to create {init_file}: {e}")
        
        if self.fixes_applied:
            print(f"\n✅ Applied {len(self.fixes_applied)} automatic fixes")
        else:
            print("\n💡 No automatic fixes needed")
        
        print()
    
    def save_diagnostic_report(self):
        """Save diagnostic report to file"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "system_info": {
                "os": platform.system(),
                "python_version": sys.version.split()[0],
                "cpu_cores": psutil.cpu_count(),
                "total_memory_gb": psutil.virtual_memory().total / 1024**3
            },
            "issues_found": self.issues_found,
            "recommendations": self.recommendations,
            "fixes_applied": self.fixes_applied
        }
        
        report_file = f"diagnostic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Diagnostic report saved: {report_file}")

def main():
    """Main troubleshooting function"""
    troubleshooter = H100Troubleshooter()
    troubleshooter.run_full_diagnosis()
    troubleshooter.save_diagnostic_report()
    
    if troubleshooter.issues_found:
        print("\n🔧 Run this script again after addressing the issues above")
        return False
    else:
        print("\n🔱 JAI MAHAKAAL! System ready for H100 deployment! 🔱")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)