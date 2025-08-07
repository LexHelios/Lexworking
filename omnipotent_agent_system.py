#!/usr/bin/env python3
"""
🔱 OMNIPOTENT AGENT SYSTEM - OPTIMIZED FOR 7GB RAM
JAI MAHAKAAL! The ultimate AI system that can do EVERYTHING!

Optimized for:
- Ubuntu x86_64 (4 cores @ 2.0GHz)
- 7.8GB RAM (7.0GB available) 
- CPU-only inference (no GPU)
- DigitalOcean-style cloud environment
"""

import asyncio
import os
import sys
import subprocess
import json
import hashlib
import traceback
import psutil
import gc
from typing import Dict, List, Any, Optional
from datetime import datetime
import aiohttp
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ResourceManager:
    """Smart resource management for limited hardware"""
    
    def __init__(self):
        self.max_memory_gb = 5.0  # Leave 2GB for system
        self.model_cache = {}
        self.active_processes = []
        
    def get_memory_usage(self) -> float:
        """Get current memory usage in GB"""
        return psutil.virtual_memory().used / (1024**3)
    
    def can_load_model(self, estimated_size_gb: float) -> bool:
        """Check if we can load a model without OOM"""
        current_usage = self.get_memory_usage()
        return (current_usage + estimated_size_gb) < self.max_memory_gb
    
    def cleanup_memory(self):
        """Aggressive memory cleanup"""
        gc.collect()
        # Clear model cache if needed
        if self.get_memory_usage() > 4.5:
            self.model_cache.clear()
            gc.collect()
            
    async def monitor_resources(self):
        """Continuously monitor system resources"""
        while True:
            try:
                mem_usage = self.get_memory_usage()
                cpu_percent = psutil.cpu_percent(interval=1)
                
                logger.info(f"📊 Memory: {mem_usage:.1f}GB/{self.max_memory_gb}GB, CPU: {cpu_percent}%")
                
                # Auto-cleanup if memory is high
                if mem_usage > 4.5:
                    logger.warning("🧹 High memory usage, cleaning up...")
                    self.cleanup_memory()
                
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"❌ Resource monitoring error: {e}")
                await asyncio.sleep(60)

class OmnipotentAgentSystem:
    """
    The master system optimized for 7GB RAM that orchestrates all agent capabilities.
    This is the brain that controls everything efficiently.
    """

    def __init__(self):
        """Initialize all subsystems with resource constraints"""
        
        logger.info("🔱 Initializing OMNIPOTENT AGENT SYSTEM...")
        
        # Resource manager
        self.resource_manager = ResourceManager()
        
        # Configuration optimized for your hardware
        self.config = {
            "openrouter_api_key": os.getenv("OPENROUTER_API_KEY"),
            "github_token": os.getenv("GITHUB_TOKEN", ""),
            "production_url": "https://lexcommand.ai",
            "local_path": "/app/",
            "database_path": "/app/lex_memory.db",
            "max_autonomous_actions": 50,  # Reduced for stability
            "require_confirmation": False,
            
            # Hardware-specific optimizations
            "max_memory_gb": 5.0,
            "cpu_cores": 4,
            "enable_gpu": False,  # No GPU available
            "model_cache_size": "2GB",
            "concurrent_limit": 2,  # Don't overload CPU
        }

        # Initialize agent subsystems (lazy loading for memory efficiency)
        self.agents_loaded = False
        self._computer_control = None
        self._web_intelligence = None
        self._code_generator = None
        self._framework_integrator = None
        self._self_improvement = None
        self._deployment_agent = None
        self._media_generator = None

        # Capability registry
        self.capabilities = {
            "browser_automation": True,
            "terminal_execution": True,
            "file_manipulation": True,
            "api_integration": True,
            "git_operations": True,
            "web_scraping": True,
            "code_generation": True,
            "self_modification": True,
            "autonomous_deployment": True,
            "image_generation": True,  # CPU-based
            "video_generation": False,  # Disabled for resource constraints
            "docker_management": False,  # May cause memory issues
        }

        # Action history for learning
        self.action_history = []
        
        logger.info("✅ OMNIPOTENT SYSTEM initialized with resource optimization")

    @property
    def computer_control(self):
        """Lazy load computer control agent"""
        if self._computer_control is None:
            from agents.computer_control_agent import ComputerControlAgent
            self._computer_control = ComputerControlAgent(self.config)
            logger.info("🖥️ Computer Control Agent loaded")
        return self._computer_control

    @property
    def web_intelligence(self):
        """Lazy load web intelligence agent"""
        if self._web_intelligence is None:
            from agents.web_intelligence_agent import WebIntelligenceAgent
            self._web_intelligence = WebIntelligenceAgent(self.config)
            logger.info("🌐 Web Intelligence Agent loaded")
        return self._web_intelligence

    @property
    def code_generator(self):
        """Lazy load code generator agent"""
        if self._code_generator is None:
            from agents.code_generation_agent import CodeGenerationAgent
            self._code_generator = CodeGenerationAgent(self.config)
            logger.info("💻 Code Generation Agent loaded")
        return self._code_generator

    @property
    def media_generator(self):
        """Lazy load media generation agent"""
        if self._media_generator is None:
            from agents.media_generation_agent import MediaGenerationAgent
            self._media_generator = MediaGenerationAgent(self.config)
            logger.info("🎨 Media Generation Agent loaded")
        return self._media_generator

    async def execute_request(self, request: str) -> Dict[str, Any]:
        """Main entry point - can handle ANY request with resource awareness"""
        logger.info(f"🤖 Processing request: {request}")
        
        # Check resources before heavy operations
        if not self.resource_manager.can_load_model(1.0):
            self.resource_manager.cleanup_memory()
        
        try:
            # Analyze request to determine best approach
            analysis = await self.analyze_request(request)
            
            # Route to appropriate agent(s) with resource management
            result = None
            
            if "image" in analysis["keywords"] or "generate" in analysis["keywords"]:
                if self.resource_manager.can_load_model(2.0):
                    result = await self.media_generator.generate_image(request)
                else:
                    result = {"error": "Insufficient memory for image generation"}
                    
            elif "code" in analysis["keywords"]:
                result = await self.code_generator.generate(request)
                
            elif "browse" in analysis["keywords"] or "web" in analysis["keywords"]:
                result = await self.web_intelligence.research(request)
                
            elif "execute" in analysis["keywords"] or "run" in analysis["keywords"]:
                result = await self.computer_control.execute_terminal_command(request)
                
            else:
                # Use general purpose execution
                result = await self.execute_general(request)

            # Learn from this interaction
            await self.learn_from_action(request, result)
            
            # Cleanup after operation
            self.resource_manager.cleanup_memory()
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Request execution failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "request": request
            }

    async def analyze_request(self, request: str) -> Dict[str, Any]:
        """Analyze user request to determine routing"""
        keywords = request.lower().split()
        
        return {
            "keywords": keywords,
            "type": self._classify_request(keywords),
            "complexity": len(keywords),
            "estimated_memory": self._estimate_memory_need(keywords)
        }
    
    def _classify_request(self, keywords: List[str]) -> str:
        """Classify request type"""
        if any(word in keywords for word in ["image", "picture", "generate", "create"]):
            return "media_generation"
        elif any(word in keywords for word in ["code", "function", "class", "api"]):
            return "code_generation"
        elif any(word in keywords for word in ["browse", "search", "web", "internet"]):
            return "web_intelligence"
        elif any(word in keywords for word in ["execute", "run", "command", "terminal"]):
            return "computer_control"
        else:
            return "general"
    
    def _estimate_memory_need(self, keywords: List[str]) -> float:
        """Estimate memory requirements in GB"""
        if any(word in keywords for word in ["image", "stable", "diffusion"]):
            return 2.0  # Stable Diffusion needs ~2GB
        elif any(word in keywords for word in ["video", "animation"]):
            return 3.0  # Video generation needs more
        else:
            return 0.5  # Light operations

    async def execute_general(self, request: str) -> Dict[str, Any]:
        """Handle general requests"""
        return {
            "status": "processed",
            "response": f"Processed general request: {request}",
            "capabilities": list(self.capabilities.keys()),
            "system_info": {
                "memory_usage_gb": self.resource_manager.get_memory_usage(),
                "cpu_percent": psutil.cpu_percent()
            }
        }

    async def run_autonomous(self):
        """Run completely autonomously with resource monitoring"""
        logger.info("🚀 Starting autonomous mode with resource optimization...")
        
        tasks = [
            self.resource_manager.monitor_resources(),
            self.autonomous_improvement_cycle(),
            self.health_monitoring(),
        ]
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"❌ Autonomous mode error: {e}")

    async def autonomous_improvement_cycle(self):
        """Continuous self-improvement with resource awareness"""
        while True:
            try:
                # Only run improvements if resources allow
                if self.resource_manager.can_load_model(0.5):
                    logger.info("🔧 Running autonomous improvement cycle...")
                    
                    # Light self-improvement tasks
                    await self.optimize_performance()
                    await self.update_capabilities()
                    
                else:
                    logger.info("⏳ Skipping improvement cycle - insufficient resources")
                
                await asyncio.sleep(300)  # Every 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Improvement cycle error: {e}")
                await asyncio.sleep(600)

    async def health_monitoring(self):
        """Monitor system health"""
        while True:
            try:
                health = await self.check_system_health()
                
                if not health["healthy"]:
                    logger.warning(f"🚨 System health issues: {health['issues']}")
                    await self.handle_health_issues(health["issues"])
                
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"❌ Health monitoring error: {e}")
                await asyncio.sleep(120)

    async def check_system_health(self) -> Dict[str, Any]:
        """Check overall system health with resource awareness"""
        health = {
            "healthy": True,
            "issues": [],
            "metrics": {}
        }

        # Check memory usage
        mem_usage = self.resource_manager.get_memory_usage()
        if mem_usage > 6.0:  # Over 6GB usage
            health["healthy"] = False
            health["issues"].append("High memory usage")
        
        # Check CPU usage
        cpu_percent = psutil.cpu_percent()
        if cpu_percent > 90:
            health["healthy"] = False
            health["issues"].append("High CPU usage")

        # Check disk space
        disk_usage = psutil.disk_usage('/').percent
        if disk_usage > 85:
            health["healthy"] = False
            health["issues"].append("Low disk space")

        health["metrics"] = {
            "memory_gb": mem_usage,
            "cpu_percent": cpu_percent,
            "disk_percent": disk_usage
        }

        return health

    async def handle_health_issues(self, issues: List[str]):
        """Handle system health issues"""
        for issue in issues:
            if "memory" in issue.lower():
                logger.info("🧹 Cleaning up memory...")
                self.resource_manager.cleanup_memory()
            elif "cpu" in issue.lower():
                logger.info("⏳ Reducing CPU load...")
                await asyncio.sleep(30)  # Give CPU a break

    async def optimize_performance(self):
        """Optimize system performance"""
        logger.info("⚡ Optimizing system performance...")
        
        # Memory optimization
        self.resource_manager.cleanup_memory()
        
        # Clear old logs
        await self.cleanup_old_logs()
        
        # Optimize database if exists
        await self.optimize_database()

    async def cleanup_old_logs(self):
        """Clean up old log files"""
        try:
            log_dir = "/app/logs"
            if os.path.exists(log_dir):
                # Keep only last 7 days of logs
                cutoff = datetime.now().timestamp() - (7 * 24 * 3600)
                for file in os.listdir(log_dir):
                    filepath = os.path.join(log_dir, file)
                    if os.path.getmtime(filepath) < cutoff:
                        os.remove(filepath)
                        logger.info(f"🗑️ Removed old log: {file}")
        except Exception as e:
            logger.error(f"❌ Log cleanup error: {e}")

    async def optimize_database(self):
        """Optimize database performance"""
        try:
            if os.path.exists(self.config["database_path"]):
                # Run VACUUM on SQLite database
                import sqlite3
                conn = sqlite3.connect(self.config["database_path"])
                conn.execute("VACUUM;")
                conn.close()
                logger.info("🗄️ Database optimized")
        except Exception as e:
            logger.error(f"❌ Database optimization error: {e}")

    async def update_capabilities(self):
        """Update system capabilities based on current resources"""
        mem_usage = self.resource_manager.get_memory_usage()
        
        # Disable heavy features if low on memory
        if mem_usage > 5.5:
            self.capabilities["image_generation"] = False
            self.capabilities["docker_management"] = False
            logger.info("🚫 Disabled heavy features due to memory constraints")
        else:
            self.capabilities["image_generation"] = True
            logger.info("✅ Re-enabled image generation")

    async def learn_from_action(self, request: str, result: Dict[str, Any]):
        """Learn from user interactions"""
        learning_entry = {
            "timestamp": datetime.now().isoformat(),
            "request": request,
            "success": result.get("status") == "success",
            "memory_usage": self.resource_manager.get_memory_usage(),
            "cpu_usage": psutil.cpu_percent()
        }
        
        self.action_history.append(learning_entry)
        
        # Keep only last 100 entries
        if len(self.action_history) > 100:
            self.action_history = self.action_history[-100:]

# Test and initialization functions
async def test_system():
    """Test the omnipotent system"""
    logger.info("🧪 Running system tests...")
    
    system = OmnipotentAgentSystem()
    
    # Test basic functionality
    result = await system.execute_request("test system capabilities")
    logger.info(f"Test result: {result}")
    
    return system

if __name__ == "__main__":
    # Quick test
    asyncio.run(test_system())