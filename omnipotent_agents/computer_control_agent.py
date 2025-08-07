#!/usr/bin/env python3
"""
🔱 COMPUTER CONTROL AGENT
JAI MAHAKAAL! For complete system control and automation
"""

import asyncio
import subprocess
import os
import logging
import json
import psutil
import time
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class ComputerControlAgent:
    """Agent for complete computer control and automation"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.max_concurrent = config.get("concurrent_limit", 2)
        self.require_confirmation = config.get("require_confirmation", False)
        
        # Command history for learning
        self.command_history = []
        
        # Safe commands that don't require confirmation
        self.safe_commands = {
            "ls", "pwd", "cat", "head", "tail", "find", "grep", "ps", "top",
            "df", "du", "free", "uptime", "whoami", "id", "date", "history",
            "which", "whereis", "uname", "lscpu", "lsusb", "lspci"
        }
        
        # Dangerous commands that require extra confirmation
        self.dangerous_commands = {
            "rm", "rmdir", "dd", "fdisk", "mkfs", "format", "del", "deltree",
            "shutdown", "reboot", "halt", "init", "systemctl", "service",
            "kill", "killall", "pkill", "sudo", "su", "chmod", "chown"
        }
        
        logger.info("🖥️ Computer Control Agent initialized")

    async def execute_terminal_command(
        self,
        command: str,
        working_directory: str = "/app",
        timeout: int = 30,
        capture_output: bool = True,
        require_confirmation: bool = None
    ) -> Dict[str, Any]:
        """Execute terminal commands with safety checks"""
        
        try:
            # Parse command
            cmd_parts = command.strip().split()
            if not cmd_parts:
                return {"status": "error", "error": "Empty command"}
            
            base_command = cmd_parts[0]
            
            # Safety checks
            if require_confirmation is None:
                require_confirmation = self.require_confirmation
                
            if base_command in self.dangerous_commands and require_confirmation:
                return {
                    "status": "confirmation_required",
                    "command": command,
                    "warning": f"Dangerous command '{base_command}' requires confirmation",
                    "risk_level": "high"
                }
            
            # Log command execution
            logger.info(f"🔧 Executing command: {command}")
            
            start_time = time.time()
            
            # Execute command
            result = await self._execute_safe_command(
                command, working_directory, timeout, capture_output
            )
            
            execution_time = time.time() - start_time
            result["execution_time"] = execution_time
            
            # Store in history
            history_entry = {
                "command": command,
                "timestamp": time.time(),
                "execution_time": execution_time,
                "success": result["status"] == "success",
                "working_directory": working_directory
            }
            
            self.command_history.append(history_entry)
            
            # Keep only last 100 commands
            if len(self.command_history) > 100:
                self.command_history = self.command_history[-100:]
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Command execution failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "command": command
            }

    async def _execute_safe_command(
        self,
        command: str,
        working_directory: str,
        timeout: int,
        capture_output: bool
    ) -> Dict[str, Any]:
        """Safely execute command with timeout and resource monitoring"""
        
        try:
            # Create subprocess
            process = await asyncio.create_subprocess_shell(
                command,
                cwd=working_directory,
                stdout=asyncio.subprocess.PIPE if capture_output else None,
                stderr=asyncio.subprocess.PIPE if capture_output else None,
                stdin=asyncio.subprocess.PIPE
            )
            
            try:
                # Wait for completion with timeout
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=timeout
                )
                
                return_code = process.returncode
                
                result = {
                    "status": "success" if return_code == 0 else "error",
                    "return_code": return_code,
                    "command": command,
                    "working_directory": working_directory
                }
                
                if capture_output:
                    result.update({
                        "stdout": stdout.decode('utf-8', errors='replace') if stdout else "",
                        "stderr": stderr.decode('utf-8', errors='replace') if stderr else ""
                    })
                
                return result
                
            except asyncio.TimeoutError:
                # Kill process if timeout
                process.terminate()
                try:
                    await asyncio.wait_for(process.wait(), timeout=5)
                except asyncio.TimeoutError:
                    process.kill()
                    await process.wait()
                
                return {
                    "status": "timeout",
                    "error": f"Command timed out after {timeout} seconds",
                    "command": command
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "command": command
            }

    async def monitor_system_resources(self) -> Dict[str, Any]:
        """Monitor system resources and performance"""
        
        try:
            # Get system information
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Get process information
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    proc_info = proc.info
                    if proc_info['cpu_percent'] > 1.0 or proc_info['memory_percent'] > 1.0:
                        processes.append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            processes = processes[:10]  # Top 10 processes
            
            return {
                "status": "success",
                "timestamp": time.time(),
                "cpu": {
                    "percent": cpu_percent,
                    "count": psutil.cpu_count(),
                    "physical_count": psutil.cpu_count(logical=False)
                },
                "memory": {
                    "total_gb": memory.total / (1024**3),
                    "available_gb": memory.available / (1024**3),
                    "used_gb": memory.used / (1024**3),
                    "percent": memory.percent
                },
                "disk": {
                    "total_gb": disk.total / (1024**3),
                    "free_gb": disk.free / (1024**3),
                    "used_gb": disk.used / (1024**3),
                    "percent": (disk.used / disk.total) * 100
                },
                "processes": processes,
                "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else None
            }
            
        except Exception as e:
            logger.error(f"❌ System monitoring failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def manage_files(
        self,
        action: str,
        file_path: str,
        content: str = None,
        backup: bool = True
    ) -> Dict[str, Any]:
        """Manage files with safety checks"""
        
        try:
            path = Path(file_path)
            
            if action == "read":
                if not path.exists():
                    return {"status": "error", "error": "File does not exist"}
                
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                return {
                    "status": "success",
                    "action": "read",
                    "file_path": str(path),
                    "content": content,
                    "size": len(content)
                }
                
            elif action == "write":
                if content is None:
                    return {"status": "error", "error": "Content required for write"}
                
                # Create backup if file exists
                if backup and path.exists():
                    backup_path = path.with_suffix(path.suffix + '.backup')
                    path.rename(backup_path)
                    logger.info(f"📋 Backup created: {backup_path}")
                
                # Create directory if needed
                path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                return {
                    "status": "success",
                    "action": "write",
                    "file_path": str(path),
                    "size": len(content),
                    "backup_created": backup and path.with_suffix(path.suffix + '.backup').exists()
                }
                
            elif action == "delete":
                if not path.exists():
                    return {"status": "error", "error": "File does not exist"}
                
                # Safety check for important files
                if str(path) in ['/app/.env', '/app/lex_production_optimized.py']:
                    return {
                        "status": "confirmation_required",
                        "error": "Important file deletion requires confirmation",
                        "file_path": str(path)
                    }
                
                if backup:
                    backup_path = path.with_suffix(path.suffix + '.deleted')
                    path.rename(backup_path)
                    logger.info(f"🗑️ File moved to: {backup_path}")
                else:
                    path.unlink()
                
                return {
                    "status": "success",
                    "action": "delete",
                    "file_path": str(path),
                    "backup_created": backup
                }
                
            elif action == "list":
                if not path.exists():
                    return {"status": "error", "error": "Path does not exist"}
                
                if path.is_file():
                    return {
                        "status": "success",
                        "action": "list",
                        "path": str(path),
                        "type": "file",
                        "size": path.stat().st_size
                    }
                
                items = []
                for item in path.iterdir():
                    stat = item.stat()
                    items.append({
                        "name": item.name,
                        "type": "directory" if item.is_dir() else "file",
                        "size": stat.st_size if item.is_file() else None,
                        "modified": stat.st_mtime
                    })
                
                return {
                    "status": "success",
                    "action": "list",
                    "path": str(path),
                    "items": items,
                    "count": len(items)
                }
            
            else:
                return {"status": "error", "error": f"Unsupported action: {action}"}
                
        except Exception as e:
            logger.error(f"❌ File management failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "action": action,
                "file_path": file_path
            }

    async def check_system_health(self) -> Dict[str, Any]:
        """Comprehensive system health check"""
        
        try:
            health_report = {
                "status": "healthy",
                "timestamp": time.time(),
                "issues": [],
                "recommendations": []
            }
            
            # Check memory usage
            memory = psutil.virtual_memory()
            if memory.percent > 85:
                health_report["issues"].append("High memory usage")
                health_report["recommendations"].append("Consider closing unnecessary processes")
                if memory.percent > 95:
                    health_report["status"] = "critical"
            
            # Check disk space
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            if disk_percent > 90:
                health_report["issues"].append("Low disk space")
                health_report["recommendations"].append("Clean up temporary files and logs")
                if disk_percent > 95:
                    health_report["status"] = "critical"
            
            # Check CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 90:
                health_report["issues"].append("High CPU usage")
                health_report["recommendations"].append("Check for runaway processes")
            
            # Check load average (Linux/macOS only)
            if hasattr(os, 'getloadavg'):
                load_avg = os.getloadavg()
                cpu_count = psutil.cpu_count()
                if load_avg[0] > cpu_count * 2:
                    health_report["issues"].append("High system load")
                    health_report["recommendations"].append("System may be overloaded")
            
            # Check if LEX services are running
            lex_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'lex' in ' '.join(proc.info['cmdline']).lower():
                        lex_processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            health_report["lex_processes"] = len(lex_processes)
            if len(lex_processes) == 0:
                health_report["issues"].append("No LEX processes detected")
                health_report["recommendations"].append("Check if LEX services are running")
            
            # Set final status
            if health_report["issues"]:
                if health_report["status"] != "critical":
                    health_report["status"] = "warning"
            
            return health_report
            
        except Exception as e:
            logger.error(f"❌ System health check failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": time.time()
            }

    def get_command_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent command history"""
        return self.command_history[-limit:]

    def get_system_info(self) -> Dict[str, Any]:
        """Get basic system information"""
        try:
            return {
                "platform": os.name,
                "system": os.uname()._asdict() if hasattr(os, 'uname') else {},
                "python_version": os.sys.version,
                "working_directory": os.getcwd(),
                "environment_variables": dict(os.environ),
                "cpu_count": psutil.cpu_count(),
                "memory_total_gb": psutil.virtual_memory().total / (1024**3),
                "disk_total_gb": psutil.disk_usage('/').total / (1024**3)
            }
        except Exception as e:
            logger.error(f"❌ System info failed: {e}")
            return {"error": str(e)}