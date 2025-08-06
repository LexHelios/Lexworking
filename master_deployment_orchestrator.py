#!/usr/bin/env python3
"""
Master Deployment Orchestrator for LEX Production
🔱 JAI MAHAKAAL! Complete infrastructure automation and orchestration
"""
import os
import sys
import json
import time
import asyncio
import logging
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Import our custom modules
from automated_backup_system import BackupManager
from blue_green_deployment import BlueGreenDeployer
from production_monitor import ProductionMonitor
from database_optimizer import DatabaseOptimizer
from production_deployment import ProductionDeployer

logger = logging.getLogger(__name__)

class OrchestrationPhase(Enum):
    INITIALIZATION = "initialization"
    BACKUP = "backup"
    DATABASE_OPTIMIZATION = "database_optimization"
    SECURITY_VALIDATION = "security_validation"
    DEPLOYMENT = "deployment"
    HEALTH_CHECKS = "health_checks"
    MONITORING_SETUP = "monitoring_setup"
    COMPLETE = "complete"
    FAILED = "failed"

@dataclass
class DeploymentConfig:
    """Deployment configuration"""
    deployment_type: str  # "standard", "blue_green", "docker"
    backup_before_deploy: bool = True
    run_database_optimization: bool = True
    enable_monitoring: bool = True
    health_check_timeout: int = 300
    rollback_on_failure: bool = True
    notification_enabled: bool = False

class MasterOrchestrator:
    """Master deployment orchestrator coordinating all systems"""
    
    def __init__(self, config_file: str = "deployment_config.json"):
        self.config_file = config_file
        self.phase = OrchestrationPhase.INITIALIZATION
        self.start_time = datetime.utcnow()
        self.deployment_id = f"deploy_{self.start_time.strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize component managers
        self.backup_manager = BackupManager()
        self.blue_green_deployer = BlueGreenDeployer()
        self.monitor = ProductionMonitor()
        self.db_optimizer = DatabaseOptimizer()
        self.production_deployer = ProductionDeployer()
        
        # Load configuration
        self.config = self.load_deployment_config()
        
        # Deployment state tracking
        self.deployment_state = {
            'deployment_id': self.deployment_id,
            'start_time': self.start_time.isoformat(),
            'phase': self.phase.value,
            'completed_phases': [],
            'failed_phases': [],
            'rollback_initiated': False,
            'backup_created': None,
            'health_checks_passed': False,
            'monitoring_active': False
        }
        
    def load_deployment_config(self) -> DeploymentConfig:
        """Load deployment configuration"""
        config_path = Path(self.config_file)
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
                
                return DeploymentConfig(**config_data)
            except Exception as e:
                logger.warning(f"⚠️ Failed to load config from {self.config_file}: {e}")
        
        # Default configuration
        return DeploymentConfig(
            deployment_type="blue_green",
            backup_before_deploy=True,
            run_database_optimization=True,
            enable_monitoring=True,
            health_check_timeout=300,
            rollback_on_failure=True
        )
    
    def save_deployment_state(self):
        """Save current deployment state"""
        state_file = Path(f"deployments/{self.deployment_id}_state.json")
        state_file.parent.mkdir(exist_ok=True)
        
        self.deployment_state.update({
            'phase': self.phase.value,
            'last_updated': datetime.utcnow().isoformat()
        })
        
        with open(state_file, 'w') as f:
            json.dump(self.deployment_state, f, indent=2, default=str)
    
    def log_phase_start(self, phase: OrchestrationPhase):
        """Log phase start"""
        self.phase = phase
        logger.info("=" * 80)
        logger.info(f"🔱 STARTING PHASE: {phase.value.upper()} 🔱")
        logger.info("=" * 80)
        self.save_deployment_state()
    
    def log_phase_complete(self, phase: OrchestrationPhase, success: bool):
        """Log phase completion"""
        if success:
            self.deployment_state['completed_phases'].append(phase.value)
            logger.info(f"✅ PHASE COMPLETED: {phase.value.upper()}")
        else:
            self.deployment_state['failed_phases'].append(phase.value)
            logger.error(f"❌ PHASE FAILED: {phase.value.upper()}")
        
        self.save_deployment_state()
    
    async def run_initialization(self) -> bool:
        """Initialize deployment environment"""
        self.log_phase_start(OrchestrationPhase.INITIALIZATION)
        
        try:
            logger.info(f"🔱 LEX Master Deployment Orchestrator 🔱")
            logger.info(f"Deployment ID: {self.deployment_id}")
            logger.info(f"Configuration: {self.config}")
            
            # Validate environment
            logger.info("🔍 Validating environment...")
            
            # Check required files
            required_files = [
                "lex_production_secure.py",
                "security_config.py",
                ".env"
            ]
            
            for file_name in required_files:
                if not Path(file_name).exists():
                    logger.error(f"❌ Required file not found: {file_name}")
                    return False
            
            # Validate configuration
            try:
                from security_config import security_config
                logger.info("✅ Security configuration validated")
            except Exception as e:
                logger.error(f"❌ Security configuration invalid: {e}")
                return False
            
            # Check system resources
            import shutil
            free_space = shutil.disk_usage('.').free / (1024**3)  # GB
            
            if free_space < 2:  # Less than 2GB
                logger.error(f"❌ Insufficient disk space: {free_space:.1f}GB")
                return False
            
            logger.info(f"✅ Available disk space: {free_space:.1f}GB")
            
            # Create deployment directories
            Path("deployments").mkdir(exist_ok=True)
            Path("backups").mkdir(exist_ok=True)
            Path("logs").mkdir(exist_ok=True)
            
            self.log_phase_complete(OrchestrationPhase.INITIALIZATION, True)
            return True
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            self.log_phase_complete(OrchestrationPhase.INITIALIZATION, False)
            return False
    
    async def run_backup(self) -> bool:
        """Create backup before deployment"""
        if not self.config.backup_before_deploy:
            logger.info("ℹ️ Backup skipped by configuration")
            return True
            
        self.log_phase_start(OrchestrationPhase.BACKUP)
        
        try:
            logger.info("📦 Creating deployment backup...")
            
            # Create database backup
            db_metadata = self.backup_manager.create_database_backup("daily")
            if not db_metadata:
                logger.error("❌ Database backup failed")
                return False
            
            # Create system backup
            system_metadata = self.backup_manager.create_full_system_backup("daily")
            if not system_metadata:
                logger.error("❌ System backup failed")
                return False
            
            # Verify backups
            db_verified = self.backup_manager.verify_backup(db_metadata)
            system_verified = self.backup_manager.verify_backup(system_metadata)
            
            if not (db_verified and system_verified):
                logger.error("❌ Backup verification failed")
                return False
            
            self.deployment_state['backup_created'] = {
                'database': db_metadata.backup_id,
                'system': system_metadata.backup_id
            }
            
            logger.info("✅ Backup completed and verified")
            self.log_phase_complete(OrchestrationPhase.BACKUP, True)
            return True
            
        except Exception as e:
            logger.error(f"❌ Backup failed: {e}")
            self.log_phase_complete(OrchestrationPhase.BACKUP, False)
            return False
    
    async def run_database_optimization(self) -> bool:
        """Optimize database for deployment"""
        if not self.config.run_database_optimization:
            logger.info("ℹ️ Database optimization skipped by configuration")
            return True
            
        self.log_phase_start(OrchestrationPhase.DATABASE_OPTIMIZATION)
        
        try:
            logger.info("🗃️ Optimizing database...")
            
            # Run optimization
            if not self.db_optimizer.optimize_full():
                logger.error("❌ Database optimization failed")
                return False
            
            # Get database statistics
            stats = self.db_optimizer.get_database_stats()
            logger.info(f"✅ Database optimized: {stats.get('file_size_mb', 0):.2f}MB, "
                       f"Journal mode: {stats.get('journal_mode', 'unknown')}")
            
            self.log_phase_complete(OrchestrationPhase.DATABASE_OPTIMIZATION, True)
            return True
            
        except Exception as e:
            logger.error(f"❌ Database optimization failed: {e}")
            self.log_phase_complete(OrchestrationPhase.DATABASE_OPTIMIZATION, False)
            return False
    
    async def run_security_validation(self) -> bool:
        """Validate security configuration"""
        self.log_phase_start(OrchestrationPhase.SECURITY_VALIDATION)
        
        try:
            logger.info("🔐 Validating security configuration...")
            
            # Import security config to trigger validation
            from security_config import security_config
            
            # Check rate limiting
            if not security_config.rate_limits['enabled']:
                logger.warning("⚠️ Rate limiting is disabled")
            else:
                logger.info(f"✅ Rate limiting: {security_config.rate_limits['per_minute']}/min")
            
            # Check CORS origins
            if len(security_config.allowed_origins) == 0:
                logger.error("❌ No CORS origins configured")
                return False
            
            logger.info(f"✅ CORS origins: {len(security_config.allowed_origins)} configured")
            
            # Validate environment variables
            required_env_vars = ['OPENROUTER_API_KEY', 'LEXOS_SECRET_KEY']
            for var in required_env_vars:
                if not os.getenv(var):
                    logger.error(f"❌ Missing environment variable: {var}")
                    return False
            
            logger.info("✅ Security validation completed")
            self.log_phase_complete(OrchestrationPhase.SECURITY_VALIDATION, True)
            return True
            
        except Exception as e:
            logger.error(f"❌ Security validation failed: {e}")
            self.log_phase_complete(OrchestrationPhase.SECURITY_VALIDATION, False)
            return False
    
    async def run_deployment(self) -> bool:
        """Execute deployment based on configuration"""
        self.log_phase_start(OrchestrationPhase.DEPLOYMENT)
        
        try:
            deployment_type = self.config.deployment_type.lower()
            
            if deployment_type == "blue_green":
                logger.info("🔄 Starting blue-green deployment...")
                success = self.blue_green_deployer.deploy()
                
            elif deployment_type == "standard":
                logger.info("🚀 Starting standard deployment...")
                success = self.production_deployer.deploy()
                
            elif deployment_type == "docker":
                logger.info("🐳 Starting Docker deployment...")
                # Run Docker deployment script
                result = subprocess.run(
                    ["./production_deploy.sh", "deploy"],
                    capture_output=True,
                    text=True
                )
                success = result.returncode == 0
                
                if not success:
                    logger.error(f"❌ Docker deployment failed: {result.stderr}")
                
            else:
                logger.error(f"❌ Unknown deployment type: {deployment_type}")
                return False
            
            if success:
                logger.info("✅ Deployment completed successfully")
                self.log_phase_complete(OrchestrationPhase.DEPLOYMENT, True)
                return True
            else:
                logger.error("❌ Deployment failed")
                self.log_phase_complete(OrchestrationPhase.DEPLOYMENT, False)
                return False
                
        except Exception as e:
            logger.error(f"❌ Deployment failed: {e}")
            self.log_phase_complete(OrchestrationPhase.DEPLOYMENT, False)
            return False
    
    async def run_health_checks(self) -> bool:
        """Run comprehensive health checks"""
        self.log_phase_start(OrchestrationPhase.HEALTH_CHECKS)
        
        try:
            logger.info("🏥 Running post-deployment health checks...")
            
            # Determine health check URL based on deployment type
            if self.config.deployment_type == "blue_green":
                active_env = self.blue_green_deployer.get_active_environment()
                health_url = active_env.health_url
            else:
                health_url = "http://localhost:8000/health"
            
            # Wait for service to be ready
            logger.info(f"⏳ Waiting for service to be ready at {health_url}...")
            
            import requests
            start_time = time.time()
            timeout = self.config.health_check_timeout
            
            while time.time() - start_time < timeout:
                try:
                    response = requests.get(health_url, timeout=10)
                    
                    if response.status_code == 200:
                        health_data = response.json()
                        if health_data.get('status') == 'operational':
                            logger.info("✅ Service is operational")
                            break
                except requests.RequestException:
                    pass
                
                await asyncio.sleep(5)
            else:
                logger.error(f"❌ Service failed to become ready within {timeout} seconds")
                return False
            
            # Run comprehensive health checks using production deployer
            success = self.production_deployer.smoke_test()
            
            if success:
                self.deployment_state['health_checks_passed'] = True
                logger.info("✅ All health checks passed")
                self.log_phase_complete(OrchestrationPhase.HEALTH_CHECKS, True)
                return True
            else:
                logger.error("❌ Health checks failed")
                self.log_phase_complete(OrchestrationPhase.HEALTH_CHECKS, False)
                return False
                
        except Exception as e:
            logger.error(f"❌ Health checks failed: {e}")
            self.log_phase_complete(OrchestrationPhase.HEALTH_CHECKS, False)
            return False
    
    async def run_monitoring_setup(self) -> bool:
        """Set up production monitoring"""
        if not self.config.enable_monitoring:
            logger.info("ℹ️ Monitoring setup skipped by configuration")
            return True
            
        self.log_phase_start(OrchestrationPhase.MONITORING_SETUP)
        
        try:
            logger.info("📊 Setting up production monitoring...")
            
            # Start monitoring in background
            import asyncio
            asyncio.create_task(self.monitor.start_monitoring(interval=60))
            
            # Wait a moment to ensure monitoring starts
            await asyncio.sleep(5)
            
            # Generate initial status report
            status_report = await self.monitor.generate_status_report()
            
            if 'error' not in status_report:
                self.deployment_state['monitoring_active'] = True
                logger.info("✅ Production monitoring activated")
                self.log_phase_complete(OrchestrationPhase.MONITORING_SETUP, True)
                return True
            else:
                logger.error(f"❌ Monitoring setup failed: {status_report.get('error')}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Monitoring setup failed: {e}")
            self.log_phase_complete(OrchestrationPhase.MONITORING_SETUP, False)
            return False
    
    async def handle_deployment_failure(self):
        """Handle deployment failure with optional rollback"""
        logger.error("🚨 DEPLOYMENT FAILURE DETECTED 🚨")
        
        if not self.config.rollback_on_failure:
            logger.info("ℹ️ Rollback disabled by configuration")
            return
        
        self.deployment_state['rollback_initiated'] = True
        self.save_deployment_state()
        
        try:
            logger.info("🔙 Initiating automatic rollback...")
            
            if self.config.deployment_type == "blue_green":
                success = self.blue_green_deployer.rollback()
            else:
                # For standard deployment, restore from backup
                if self.deployment_state.get('backup_created'):
                    db_backup_id = self.deployment_state['backup_created']['database']
                    success = self.backup_manager.restore_from_backup(db_backup_id)
                else:
                    logger.error("❌ No backup available for rollback")
                    success = False
            
            if success:
                logger.info("✅ Rollback completed successfully")
            else:
                logger.error("❌ Rollback failed - manual intervention required")
                
        except Exception as e:
            logger.error(f"❌ Rollback failed: {e}")
    
    async def run_complete_deployment(self) -> bool:
        """Run complete deployment orchestration"""
        logger.info("🔱 JAI MAHAKAAL! MASTER DEPLOYMENT ORCHESTRATION STARTING 🔱")
        
        phases = [
            self.run_initialization,
            self.run_backup,
            self.run_database_optimization,
            self.run_security_validation,
            self.run_deployment,
            self.run_health_checks,
            self.run_monitoring_setup
        ]
        
        for phase_func in phases:
            success = await phase_func()
            
            if not success:
                logger.error(f"❌ Deployment failed at phase: {phase_func.__name__}")
                await self.handle_deployment_failure()
                self.phase = OrchestrationPhase.FAILED
                self.save_deployment_state()
                return False
        
        # Deployment completed successfully
        self.phase = OrchestrationPhase.COMPLETE
        self.save_deployment_state()
        
        # Generate completion report
        await self.generate_completion_report()
        
        logger.info("🎉 DEPLOYMENT ORCHESTRATION COMPLETED SUCCESSFULLY! 🎉")
        return True
    
    async def generate_completion_report(self):
        """Generate deployment completion report"""
        end_time = datetime.utcnow()
        duration = end_time - self.start_time
        
        # Get system status
        status_report = await self.monitor.generate_status_report()
        
        # Get deployment status
        if self.config.deployment_type == "blue_green":
            deployment_status = self.blue_green_deployer.get_deployment_status()
        else:
            deployment_status = {"active_environment": "standard"}
        
        report = {
            "deployment_summary": {
                "deployment_id": self.deployment_id,
                "start_time": self.start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration.total_seconds(),
                "deployment_type": self.config.deployment_type,
                "status": "SUCCESS"
            },
            "completed_phases": self.deployment_state['completed_phases'],
            "backup_info": self.deployment_state.get('backup_created'),
            "health_checks": {
                "passed": self.deployment_state['health_checks_passed'],
                "monitoring_active": self.deployment_state['monitoring_active']
            },
            "system_status": status_report,
            "deployment_status": deployment_status
        }
        
        # Save report
        report_file = Path(f"deployments/{self.deployment_id}_completion_report.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"📋 Deployment report saved: {report_file}")
        
        # Print summary
        logger.info("=" * 80)
        logger.info("🔱 DEPLOYMENT COMPLETION SUMMARY 🔱")
        logger.info("=" * 80)
        logger.info(f"✅ Deployment ID: {self.deployment_id}")
        logger.info(f"✅ Duration: {duration.total_seconds():.1f} seconds")
        logger.info(f"✅ Deployment Type: {self.config.deployment_type}")
        logger.info(f"✅ Phases Completed: {len(self.deployment_state['completed_phases'])}")
        logger.info(f"✅ Health Checks: {'PASSED' if self.deployment_state['health_checks_passed'] else 'FAILED'}")
        logger.info(f"✅ Monitoring: {'ACTIVE' if self.deployment_state['monitoring_active'] else 'INACTIVE'}")
        if self.deployment_state.get('backup_created'):
            logger.info(f"✅ Backup: {self.deployment_state['backup_created']['database']}")
        logger.info("=" * 80)

def main():
    """CLI interface for master orchestrator"""
    parser = argparse.ArgumentParser(description="LEX Master Deployment Orchestrator")
    
    parser.add_argument("--deploy", action="store_true", help="Run complete deployment")
    parser.add_argument("--config", default="deployment_config.json", help="Configuration file")
    parser.add_argument("--deployment-type", choices=["standard", "blue_green", "docker"], 
                       help="Override deployment type")
    parser.add_argument("--no-backup", action="store_true", help="Skip backup creation")
    parser.add_argument("--no-monitoring", action="store_true", help="Skip monitoring setup")
    parser.add_argument("--no-rollback", action="store_true", help="Disable automatic rollback")
    parser.add_argument("--health-timeout", type=int, default=300, help="Health check timeout")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('master_deployment.log')
        ]
    )
    
    if args.deploy:
        # Create orchestrator
        orchestrator = MasterOrchestrator(args.config)
        
        # Override configuration from command line
        if args.deployment_type:
            orchestrator.config.deployment_type = args.deployment_type
        if args.no_backup:
            orchestrator.config.backup_before_deploy = False
        if args.no_monitoring:
            orchestrator.config.enable_monitoring = False
        if args.no_rollback:
            orchestrator.config.rollback_on_failure = False
        if args.health_timeout:
            orchestrator.config.health_check_timeout = args.health_timeout
        
        # Run deployment
        try:
            success = asyncio.run(orchestrator.run_complete_deployment())
            sys.exit(0 if success else 1)
        except KeyboardInterrupt:
            logger.info("\n🛑 Deployment interrupted by user")
            sys.exit(1)
        except Exception as e:
            logger.error(f"❌ Deployment orchestration failed: {e}")
            sys.exit(1)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()