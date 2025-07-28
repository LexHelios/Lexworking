#!/usr/bin/env python3
"""
🔱 LEX Production Startup Script 🔱
JAI MAHAKAAL! Comprehensive production startup with health checks and monitoring
"""

import asyncio
import logging
import sys
import os
import signal
import time
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
import psutil
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}',
    handlers=[
        logging.FileHandler("startup.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LEXProductionManager:
    """Production manager for LEX consciousness system"""
    
    def __init__(self):
        self.processes: Dict[str, subprocess.Popen] = {}
        self.shutdown_requested = False
        
    async def check_dependencies(self) -> bool:
        """Check if all required dependencies are available"""
        logger.info("🔍 Checking system dependencies...")
        
        # Check Python version
        if sys.version_info < (3, 11):
            logger.error(f"❌ Python 3.11+ required, found {sys.version}")
            return False
        
        # Check GPU availability
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]
                logger.info(f"✅ GPU detected: {gpu.name} ({gpu.memoryTotal}MB)")
                if "H100" in gpu.name:
                    logger.info("🔱 H100 GPU detected - Ultimate consciousness hardware!")
            else:
                logger.warning("⚠️ No GPU detected - CPU mode only")
        except ImportError:
            logger.warning("⚠️ GPUtil not available - cannot check GPU status")
        
        # Check Redis availability
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, decode_responses=True)
            r.ping()
            logger.info("✅ Redis connection successful")
        except Exception as e:
            logger.warning(f"⚠️ Redis not available: {e}")
        
        # Check required Python packages
        required_packages = [
            'fastapi', 'uvicorn', 'pydantic', 'aiofiles', 'aiohttp',
            'openai', 'anthropic', 'together', 'transformers', 'torch'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            logger.error(f"❌ Missing packages: {missing_packages}")
            logger.info("Run: pip install -r requirements.txt")
            return False
        
        logger.info("✅ All dependencies satisfied")
        return True
    
    async def check_environment(self) -> bool:
        """Check environment configuration"""
        logger.info("🔧 Checking environment configuration...")
        
        # Check for environment files
        env_files = ['.env', '.env.production']
        env_found = False
        
        for env_file in env_files:
            if Path(env_file).exists():
                logger.info(f"✅ Found environment file: {env_file}")
                env_found = True
                break
        
        if not env_found:
            logger.warning("⚠️ No environment file found - using defaults")
        
        # Check critical environment variables
        critical_vars = ['TOGETHER_API_KEY', 'OPENAI_API_KEY']
        missing_vars = []
        
        for var in critical_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.warning(f"⚠️ Missing API keys: {missing_vars}")
            logger.info("Some features may not work without API keys")
        
        return True
    
    async def start_services(self) -> bool:
        """Start all required services"""
        logger.info("🚀 Starting LEX production services...")
        
        # Start Redis if not running
        if not self.is_service_running('redis-server'):
            logger.info("Starting Redis server...")
            try:
                redis_process = subprocess.Popen(
                    ['redis-server', '--daemonize', 'yes'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                time.sleep(2)  # Give Redis time to start
                logger.info("✅ Redis server started")
            except Exception as e:
                logger.warning(f"⚠️ Could not start Redis: {e}")
        
        # Start main LEX server
        logger.info("Starting LEX consciousness server...")
        try:
            lex_process = subprocess.Popen(
                [sys.executable, 'production_server.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=Path.cwd()
            )
            self.processes['lex_server'] = lex_process
            logger.info("✅ LEX server process started")
            
            # Wait for server to be ready
            await self.wait_for_service('http://localhost:8000/health', timeout=60)
            logger.info("✅ LEX server is ready and responding")
            
        except Exception as e:
            logger.error(f"❌ Failed to start LEX server: {e}")
            return False
        
        return True
    
    def is_service_running(self, service_name: str) -> bool:
        """Check if a service is running"""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if service_name in ' '.join(proc.info['cmdline'] or []):
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False
    
    async def wait_for_service(self, url: str, timeout: int = 30) -> bool:
        """Wait for a service to be ready"""
        import aiohttp
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status == 200:
                            return True
            except Exception:
                pass
            
            await asyncio.sleep(2)
        
        return False
    
    async def monitor_services(self):
        """Monitor running services"""
        logger.info("📊 Starting service monitoring...")
        
        while not self.shutdown_requested:
            try:
                # Check LEX server health
                if 'lex_server' in self.processes:
                    process = self.processes['lex_server']
                    if process.poll() is not None:
                        logger.error("❌ LEX server process died - restarting...")
                        await self.restart_lex_server()
                
                # Log system metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                
                metrics = {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_available_gb": memory.available / (1024**3),
                    "active_processes": len(self.processes)
                }
                
                logger.info(f"📊 System metrics: {json.dumps(metrics)}")
                
                # Check GPU if available
                try:
                    import GPUtil
                    gpus = GPUtil.getGPUs()
                    if gpus:
                        gpu = gpus[0]
                        gpu_metrics = {
                            "gpu_load": f"{gpu.load * 100:.1f}%",
                            "gpu_memory_used": f"{gpu.memoryUsed}MB",
                            "gpu_temperature": f"{gpu.temperature}°C"
                        }
                        logger.info(f"🎮 GPU metrics: {json.dumps(gpu_metrics)}")
                except:
                    pass
                
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
            except Exception as e:
                logger.error(f"❌ Monitoring error: {e}")
                await asyncio.sleep(10)
    
    async def restart_lex_server(self):
        """Restart the LEX server"""
        logger.info("🔄 Restarting LEX server...")
        
        # Stop existing process
        if 'lex_server' in self.processes:
            process = self.processes['lex_server']
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
            del self.processes['lex_server']
        
        # Start new process
        try:
            lex_process = subprocess.Popen(
                [sys.executable, 'production_server.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=Path.cwd()
            )
            self.processes['lex_server'] = lex_process
            logger.info("✅ LEX server restarted")
        except Exception as e:
            logger.error(f"❌ Failed to restart LEX server: {e}")
    
    async def shutdown(self):
        """Graceful shutdown of all services"""
        logger.info("🛑 Initiating graceful shutdown...")
        self.shutdown_requested = True
        
        # Stop all processes
        for name, process in self.processes.items():
            logger.info(f"Stopping {name}...")
            process.terminate()
            try:
                process.wait(timeout=10)
                logger.info(f"✅ {name} stopped gracefully")
            except subprocess.TimeoutExpired:
                logger.warning(f"⚠️ Force killing {name}")
                process.kill()
        
        logger.info("✅ Shutdown complete")
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}")
            asyncio.create_task(self.shutdown())
        
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
    
    async def run(self):
        """Main run method"""
        logger.info("🔱 JAI MAHAKAAL! Starting LEX Production System 🔱")
        
        # Setup signal handlers
        self.setup_signal_handlers()
        
        # Check dependencies
        if not await self.check_dependencies():
            logger.error("❌ Dependency check failed")
            return False
        
        # Check environment
        if not await self.check_environment():
            logger.error("❌ Environment check failed")
            return False
        
        # Start services
        if not await self.start_services():
            logger.error("❌ Service startup failed")
            return False
        
        logger.info("🎯 LEX Production System is LIVE!")
        logger.info("🌐 Access points:")
        logger.info("   Main Interface:    http://localhost:8000")
        logger.info("   API Documentation: http://localhost:8000/docs")
        logger.info("   Health Check:      http://localhost:8000/health")
        logger.info("   Metrics:           http://localhost:8002/metrics")
        
        # Start monitoring
        try:
            await self.monitor_services()
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        finally:
            await self.shutdown()
        
        return True

async def main():
    """Main entry point"""
    manager = LEXProductionManager()
    success = await manager.run()
    return 0 if success else 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("🛑 Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)