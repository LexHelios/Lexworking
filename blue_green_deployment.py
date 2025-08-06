#!/usr/bin/env python3
"""
Blue-Green Deployment System for LEX Production
🔱 JAI MAHAKAAL! Zero-downtime deployment with automatic rollback
"""
import os
import sys
import time
import json
import shutil
import subprocess
import requests
import logging
import signal
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class DeploymentStatus(Enum):
    IDLE = "idle"
    DEPLOYING = "deploying"
    TESTING = "testing"
    SWITCHING = "switching"
    COMPLETE = "complete"
    ROLLING_BACK = "rolling_back"
    FAILED = "failed"

@dataclass
class DeploymentEnvironment:
    name: str
    port: int
    pid_file: str
    log_file: str
    health_url: str
    is_active: bool = False

class BlueGreenDeployer:
    """Zero-downtime blue-green deployment system"""
    
    def __init__(self):
        self.deployment_dir = Path("deployments")
        self.deployment_dir.mkdir(exist_ok=True)
        
        # Define blue and green environments
        self.blue_env = DeploymentEnvironment(
            name="blue",
            port=8000,
            pid_file="lex_blue.pid",
            log_file="lex_blue.log",
            health_url="http://localhost:8000/health"
        )
        
        self.green_env = DeploymentEnvironment(
            name="green", 
            port=8001,
            pid_file="lex_green.pid",
            log_file="lex_green.log",
            health_url="http://localhost:8001/health"
        )
        
        self.nginx_config_path = Path("/etc/nginx/sites-available/lex-ai")
        self.deployment_status = DeploymentStatus.IDLE
        self.current_deployment = None
        
        # Load deployment state
        self.load_deployment_state()
    
    def save_deployment_state(self):
        """Save current deployment state"""
        state = {
            'blue_env': {
                'is_active': self.blue_env.is_active,
                'port': self.blue_env.port
            },
            'green_env': {
                'is_active': self.green_env.is_active,
                'port': self.green_env.port
            },
            'deployment_status': self.deployment_status.value,
            'last_updated': datetime.utcnow().isoformat()
        }
        
        state_file = self.deployment_dir / "deployment_state.json"
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def load_deployment_state(self):
        """Load deployment state"""
        state_file = self.deployment_dir / "deployment_state.json"
        
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    state = json.load(f)
                
                self.blue_env.is_active = state['blue_env']['is_active']
                self.green_env.is_active = state['green_env']['is_active']
                self.deployment_status = DeploymentStatus(state.get('deployment_status', 'idle'))
                
                logger.info(f"✅ Loaded deployment state: Blue active: {self.blue_env.is_active}, Green active: {self.green_env.is_active}")
                
            except Exception as e:
                logger.warning(f"⚠️ Failed to load deployment state: {e}")
                self.blue_env.is_active = True  # Default to blue active
                self.green_env.is_active = False
    
    def get_active_environment(self) -> DeploymentEnvironment:
        """Get currently active environment"""
        return self.blue_env if self.blue_env.is_active else self.green_env
    
    def get_inactive_environment(self) -> DeploymentEnvironment:
        """Get currently inactive environment"""
        return self.green_env if self.blue_env.is_active else self.blue_env
    
    def is_service_running(self, env: DeploymentEnvironment) -> bool:
        """Check if service is running in environment"""
        pid_file = Path(env.pid_file)
        
        if not pid_file.exists():
            return False
        
        try:
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process is actually running
            os.kill(pid, 0)  # Doesn't actually kill, just checks if process exists
            return True
            
        except (OSError, ValueError, ProcessLookupError):
            # Clean up stale PID file
            if pid_file.exists():
                pid_file.unlink()
            return False
    
    def stop_service(self, env: DeploymentEnvironment) -> bool:
        """Stop service in environment"""
        logger.info(f"🛑 Stopping {env.name} environment...")
        
        pid_file = Path(env.pid_file)
        
        if not pid_file.exists():
            logger.info(f"✅ {env.name} service not running")
            return True
        
        try:
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Graceful shutdown
            logger.info(f"🛑 Sending TERM signal to PID {pid}")
            os.kill(pid, signal.SIGTERM)
            
            # Wait for graceful shutdown
            for i in range(30):  # Wait up to 30 seconds
                try:
                    os.kill(pid, 0)
                    time.sleep(1)
                except ProcessLookupError:
                    break
            else:
                # Force kill if graceful shutdown failed
                logger.warning(f"⚠️ Graceful shutdown failed, force killing PID {pid}")
                os.kill(pid, signal.SIGKILL)
                time.sleep(2)
            
            # Clean up PID file
            pid_file.unlink()
            logger.info(f"✅ {env.name} service stopped")
            return True
            
        except (OSError, ValueError, ProcessLookupError) as e:
            logger.warning(f"⚠️ Error stopping {env.name} service: {e}")
            if pid_file.exists():
                pid_file.unlink()
            return True  # Consider it stopped if we can't find it
    
    def start_service(self, env: DeploymentEnvironment) -> bool:
        """Start service in environment"""
        logger.info(f"🚀 Starting {env.name} environment on port {env.port}...")
        
        # Ensure previous service is stopped
        if self.is_service_running(env):
            logger.info(f"🛑 Stopping existing {env.name} service...")
            self.stop_service(env)
        
        try:
            # Set environment variables for the new instance
            env_vars = os.environ.copy()
            env_vars.update({
                'PORT': str(env.port),
                'HOST': '0.0.0.0',
                'ENV': 'production',
                'LOG_FILE': env.log_file
            })
            
            # Start service
            with open(env.log_file, 'w') as log_file:
                process = subprocess.Popen(
                    [sys.executable, 'lex_production_secure.py'],
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                    env=env_vars,
                    preexec_fn=os.setsid  # Create new process group
                )
            
            # Save PID
            with open(env.pid_file, 'w') as f:
                f.write(str(process.pid))
            
            logger.info(f"✅ {env.name} service started with PID {process.pid}")
            
            # Wait for service to be ready
            return self.wait_for_service_ready(env)
            
        except Exception as e:
            logger.error(f"❌ Failed to start {env.name} service: {e}")
            return False
    
    def wait_for_service_ready(self, env: DeploymentEnvironment, timeout: int = 60) -> bool:
        """Wait for service to be ready"""
        logger.info(f"⏳ Waiting for {env.name} service to be ready...")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(env.health_url, timeout=5)
                
                if response.status_code == 200:
                    health_data = response.json()
                    if health_data.get('status') == 'operational':
                        logger.info(f"✅ {env.name} service is ready")
                        return True
                        
            except requests.RequestException:
                pass
            
            time.sleep(5)
        
        logger.error(f"❌ {env.name} service failed to become ready within {timeout} seconds")
        return False
    
    def run_health_checks(self, env: DeploymentEnvironment) -> bool:
        """Run comprehensive health checks"""
        logger.info(f"🏥 Running health checks on {env.name} environment...")
        
        checks = [
            self._check_health_endpoint,
            self._check_api_endpoint,
            self._check_database_connectivity,
            self._check_security_headers,
            self._check_response_time
        ]
        
        passed_checks = 0
        
        for check in checks:
            try:
                if check(env):
                    passed_checks += 1
                else:
                    logger.warning(f"⚠️ Health check failed: {check.__name__}")
            except Exception as e:
                logger.warning(f"⚠️ Health check error: {check.__name__}: {e}")
        
        success_rate = passed_checks / len(checks)
        
        if success_rate >= 0.8:  # 80% pass rate
            logger.info(f"✅ Health checks passed: {passed_checks}/{len(checks)} ({success_rate:.0%})")
            return True
        else:
            logger.error(f"❌ Health checks failed: {passed_checks}/{len(checks)} ({success_rate:.0%})")
            return False
    
    def _check_health_endpoint(self, env: DeploymentEnvironment) -> bool:
        """Check health endpoint"""
        try:
            response = requests.get(env.health_url, timeout=10)
            return response.status_code == 200 and 'operational' in response.text
        except:
            return False
    
    def _check_api_endpoint(self, env: DeploymentEnvironment) -> bool:
        """Check API endpoint"""
        try:
            api_url = f"http://localhost:{env.port}/api/v1/lex"
            data = {"message": "deployment health check", "voice_mode": False}
            response = requests.post(api_url, json=data, timeout=15)
            return 200 <= response.status_code < 500
        except:
            return False
    
    def _check_database_connectivity(self, env: DeploymentEnvironment) -> bool:
        """Check database connectivity"""
        try:
            import sqlite3
            with sqlite3.connect('lex_memory.db', timeout=5) as conn:
                conn.execute('SELECT 1').fetchone()
            return True
        except:
            return False
    
    def _check_security_headers(self, env: DeploymentEnvironment) -> bool:
        """Check security headers"""
        try:
            response = requests.get(env.health_url, timeout=5)
            headers = response.headers
            
            required_headers = [
                'X-Content-Type-Options',
                'X-Frame-Options',
                'X-XSS-Protection'
            ]
            
            return all(header in headers for header in required_headers)
        except:
            return False
    
    def _check_response_time(self, env: DeploymentEnvironment) -> bool:
        """Check response time"""
        try:
            start_time = time.time()
            response = requests.get(env.health_url, timeout=10)
            response_time = time.time() - start_time
            
            return response.status_code == 200 and response_time < 5.0  # Less than 5 seconds
        except:
            return False
    
    def update_nginx_upstream(self, active_env: DeploymentEnvironment) -> bool:
        """Update nginx upstream configuration"""
        logger.info(f"🔄 Updating nginx to route traffic to {active_env.name} environment...")
        
        try:
            # Read current nginx config
            nginx_config = f"""
upstream lex_backend {{
    server 127.0.0.1:{active_env.port};
    keepalive 32;
}}
"""
            
            # Update upstream in nginx config file
            config_file = Path("nginx_upstream.conf")
            with open(config_file, 'w') as f:
                f.write(nginx_config)
            
            # Reload nginx configuration
            result = subprocess.run(['nginx', '-s', 'reload'], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"✅ Nginx updated to route to {active_env.name} environment")
                return True
            else:
                logger.error(f"❌ Failed to reload nginx: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to update nginx configuration: {e}")
            return False
    
    def create_deployment_backup(self) -> str:
        """Create deployment backup"""
        backup_id = f"deployment_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        backup_dir = self.deployment_dir / backup_id
        backup_dir.mkdir(exist_ok=True)
        
        # Backup critical files
        files_to_backup = [
            "lex_production_secure.py",
            "security_config.py", 
            "database_optimizer.py",
            "production_monitor.py",
            ".env",
            "lex_memory.db"
        ]
        
        for file_name in files_to_backup:
            file_path = Path(file_name)
            if file_path.exists():
                if file_path.is_file():
                    shutil.copy2(file_path, backup_dir / file_name)
                else:
                    shutil.copytree(file_path, backup_dir / file_name, dirs_exist_ok=True)
        
        logger.info(f"📦 Deployment backup created: {backup_id}")
        return backup_id
    
    def deploy(self) -> bool:
        """Execute blue-green deployment"""
        logger.info("=" * 80)
        logger.info("🔱 JAI MAHAKAAL! Starting Blue-Green Deployment 🔱")
        logger.info("=" * 80)
        
        try:
            self.deployment_status = DeploymentStatus.DEPLOYING
            self.save_deployment_state()
            
            # Step 1: Create backup
            backup_id = self.create_deployment_backup()
            
            # Step 2: Get environments
            active_env = self.get_active_environment()
            inactive_env = self.get_inactive_environment()
            
            logger.info(f"🔄 Current active: {active_env.name}, Deploying to: {inactive_env.name}")
            
            # Step 3: Deploy to inactive environment
            if not self.start_service(inactive_env):
                logger.error("❌ Failed to start inactive environment")
                return False
            
            # Step 4: Run health checks
            self.deployment_status = DeploymentStatus.TESTING
            self.save_deployment_state()
            
            if not self.run_health_checks(inactive_env):
                logger.error("❌ Health checks failed on inactive environment")
                self.stop_service(inactive_env)
                return False
            
            # Step 5: Switch traffic
            self.deployment_status = DeploymentStatus.SWITCHING
            self.save_deployment_state()
            
            if not self.update_nginx_upstream(inactive_env):
                logger.error("❌ Failed to update nginx configuration")
                self.stop_service(inactive_env)
                return False
            
            # Step 6: Stop old environment
            self.stop_service(active_env)
            
            # Step 7: Update environment states
            if active_env == self.blue_env:
                self.blue_env.is_active = False
                self.green_env.is_active = True
            else:
                self.blue_env.is_active = True
                self.green_env.is_active = False
            
            self.deployment_status = DeploymentStatus.COMPLETE
            self.save_deployment_state()
            
            logger.info("=" * 80)
            logger.info("🎉 BLUE-GREEN DEPLOYMENT SUCCESSFUL! 🎉")
            logger.info("=" * 80)
            logger.info(f"✅ Traffic switched to {inactive_env.name} environment")
            logger.info(f"✅ Backup created: {backup_id}")
            logger.info(f"✅ Old environment ({active_env.name}) stopped")
            logger.info("=" * 80)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Deployment failed: {e}")
            self.deployment_status = DeploymentStatus.FAILED
            self.save_deployment_state()
            return False
    
    def rollback(self) -> bool:
        """Rollback to previous environment"""
        logger.info("🔙 Starting rollback...")
        
        try:
            self.deployment_status = DeploymentStatus.ROLLING_BACK
            self.save_deployment_state()
            
            active_env = self.get_active_environment()
            inactive_env = self.get_inactive_environment()
            
            logger.info(f"🔙 Rolling back from {active_env.name} to {inactive_env.name}")
            
            # Start previous environment
            if not self.start_service(inactive_env):
                logger.error("❌ Failed to start previous environment")
                return False
            
            # Basic health check
            if not self.wait_for_service_ready(inactive_env, timeout=30):
                logger.error("❌ Previous environment failed health check")
                return False
            
            # Switch traffic back
            if not self.update_nginx_upstream(inactive_env):
                logger.error("❌ Failed to update nginx for rollback")
                return False
            
            # Stop current environment
            self.stop_service(active_env)
            
            # Update states
            if active_env == self.blue_env:
                self.blue_env.is_active = False
                self.green_env.is_active = True
            else:
                self.blue_env.is_active = True
                self.green_env.is_active = False
            
            self.deployment_status = DeploymentStatus.COMPLETE
            self.save_deployment_state()
            
            logger.info(f"✅ Rollback completed - traffic restored to {inactive_env.name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Rollback failed: {e}")
            return False
    
    def get_deployment_status(self) -> Dict:
        """Get current deployment status"""
        active_env = self.get_active_environment()
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'deployment_status': self.deployment_status.value,
            'active_environment': active_env.name,
            'blue_environment': {
                'active': self.blue_env.is_active,
                'running': self.is_service_running(self.blue_env),
                'port': self.blue_env.port,
                'health_url': self.blue_env.health_url
            },
            'green_environment': {
                'active': self.green_env.is_active,
                'running': self.is_service_running(self.green_env),
                'port': self.green_env.port,
                'health_url': self.green_env.health_url
            }
        }

def main():
    """CLI interface for blue-green deployment"""
    import argparse
    
    parser = argparse.ArgumentParser(description="LEX Blue-Green Deployment")
    parser.add_argument("--deploy", action="store_true", help="Run blue-green deployment")
    parser.add_argument("--rollback", action="store_true", help="Rollback to previous version")
    parser.add_argument("--status", action="store_true", help="Show deployment status")
    parser.add_argument("--stop", help="Stop specific environment (blue/green)")
    parser.add_argument("--start", help="Start specific environment (blue/green)")
    parser.add_argument("--health", help="Run health checks on environment (blue/green)")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('deployment.log')
        ]
    )
    
    deployer = BlueGreenDeployer()
    
    if args.deploy:
        success = deployer.deploy()
        sys.exit(0 if success else 1)
    elif args.rollback:
        success = deployer.rollback()
        sys.exit(0 if success else 1)
    elif args.status:
        status = deployer.get_deployment_status()
        print(json.dumps(status, indent=2))
    elif args.stop:
        env = deployer.blue_env if args.stop == 'blue' else deployer.green_env
        success = deployer.stop_service(env)
        sys.exit(0 if success else 1)
    elif args.start:
        env = deployer.blue_env if args.start == 'blue' else deployer.green_env
        success = deployer.start_service(env)
        sys.exit(0 if success else 1)
    elif args.health:
        env = deployer.blue_env if args.health == 'blue' else deployer.green_env
        success = deployer.run_health_checks(env)
        sys.exit(0 if success else 1)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()