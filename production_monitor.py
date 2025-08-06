#!/usr/bin/env python3
"""
Production Monitoring for LEX System
🔱 JAI MAHAKAAL! Real-time system monitoring and alerting
"""
import asyncio
import logging
import psutil
import sqlite3
import json
import time
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class SystemMetric:
    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str] = None
    component: str = "system"

class ProductionMonitor:
    """Comprehensive production monitoring"""
    
    def __init__(self, db_path: str = "lex_memory.db"):
        self.db_path = db_path
        self.metrics_buffer = []
        self.alert_thresholds = {
            'cpu_usage': 80.0,      # 80% CPU
            'memory_usage': 85.0,   # 85% Memory  
            'disk_usage': 90.0,     # 90% Disk
            'response_time': 5.0,   # 5 seconds
            'error_rate': 10.0,     # 10% error rate
            'request_rate': 1000    # 1000 requests/minute
        }
        self.monitoring_active = False
        
    async def start_monitoring(self, interval: int = 60):
        """Start continuous monitoring"""
        self.monitoring_active = True
        logger.info("🔍 Starting production monitoring...")
        
        while self.monitoring_active:
            try:
                await self.collect_system_metrics()
                await self.collect_application_metrics()
                await self.check_health_endpoints()
                await self.flush_metrics()
                await self.check_alerts()
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"❌ Monitoring error: {e}")
                await asyncio.sleep(5)  # Short delay before retry
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring_active = False
        logger.info("🛑 Monitoring stopped")
    
    async def collect_system_metrics(self):
        """Collect system performance metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            self.add_metric("cpu_usage", cpu_percent, component="system")
            
            # Memory metrics
            memory = psutil.virtual_memory()
            self.add_metric("memory_usage", memory.percent, component="system")
            self.add_metric("memory_available_mb", memory.available / 1024 / 1024, component="system")
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.add_metric("disk_usage", disk_percent, component="system")
            self.add_metric("disk_free_gb", disk.free / 1024 / 1024 / 1024, component="system")
            
            # Network metrics
            network = psutil.net_io_counters()
            self.add_metric("network_bytes_sent", network.bytes_sent, component="system")
            self.add_metric("network_bytes_recv", network.bytes_recv, component="system")
            
            # Load average (Linux/Unix)
            try:
                load1, load5, load15 = psutil.getloadavg()
                self.add_metric("load_1min", load1, component="system")
                self.add_metric("load_5min", load5, component="system")
                self.add_metric("load_15min", load15, component="system")
            except AttributeError:
                # Windows doesn't have getloadavg
                pass
                
            logger.debug(f"✅ System metrics collected: CPU {cpu_percent:.1f}%, Memory {memory.percent:.1f}%")
            
        except Exception as e:
            logger.error(f"❌ Failed to collect system metrics: {e}")
    
    async def collect_application_metrics(self):
        """Collect application-specific metrics"""
        try:
            # Database metrics
            if Path(self.db_path).exists():
                db_size = Path(self.db_path).stat().st_size / 1024 / 1024  # MB
                self.add_metric("database_size_mb", db_size, component="database")
                
                # Query database for app metrics
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Count recent messages (last hour)
                    cursor.execute("""
                        SELECT COUNT(*) FROM messages 
                        WHERE timestamp > datetime('now', '-1 hour')
                    """)
                    recent_messages = cursor.fetchone()[0] if cursor.fetchone() else 0
                    self.add_metric("messages_last_hour", recent_messages, component="application")
                    
                    # Count total conversations
                    cursor.execute("SELECT COUNT(*) FROM conversations")
                    total_conversations = cursor.fetchone()[0] if cursor.fetchone() else 0
                    self.add_metric("total_conversations", total_conversations, component="application")
                    
            # Process metrics
            process_count = len([p for p in psutil.process_iter(['name']) if 'python' in p.info['name'].lower()])
            self.add_metric("python_processes", process_count, component="application")
            
            # Log file sizes
            for log_file in ['lex.log', 'lex_production.log']:
                if Path(log_file).exists():
                    log_size = Path(log_file).stat().st_size / 1024 / 1024  # MB
                    self.add_metric(f"log_size_mb_{log_file.replace('.', '_')}", log_size, component="logging")
            
        except Exception as e:
            logger.error(f"❌ Failed to collect application metrics: {e}")
    
    async def check_health_endpoints(self):
        """Check application health endpoints"""
        endpoints = [
            {"url": "http://localhost:8000/health", "name": "main_api"},
            {"url": "http://localhost:8000/api/v1/lex", "name": "lex_endpoint", "method": "POST"}
        ]
        
        for endpoint in endpoints:
            try:
                start_time = time.time()
                
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                    if endpoint.get("method") == "POST":
                        # Test POST with minimal data
                        async with session.post(
                            endpoint["url"],
                            json={"message": "health check", "voice_mode": False}
                        ) as response:
                            status_code = response.status
                            response_time = time.time() - start_time
                    else:
                        # Test GET
                        async with session.get(endpoint["url"]) as response:
                            status_code = response.status
                            response_time = time.time() - start_time
                
                # Record metrics
                self.add_metric(f"endpoint_response_time_{endpoint['name']}", response_time, component="api")
                self.add_metric(f"endpoint_status_{endpoint['name']}", status_code, component="api")
                
                # Health status (1 for healthy, 0 for unhealthy)
                health_status = 1 if 200 <= status_code < 400 else 0
                self.add_metric(f"endpoint_health_{endpoint['name']}", health_status, component="api")
                
                if health_status:
                    logger.debug(f"✅ {endpoint['name']} healthy ({status_code}) in {response_time:.3f}s")
                else:
                    logger.warning(f"⚠️ {endpoint['name']} unhealthy ({status_code}) in {response_time:.3f}s")
                    
            except Exception as e:
                # Record failure
                self.add_metric(f"endpoint_health_{endpoint['name']}", 0, component="api")
                self.add_metric(f"endpoint_response_time_{endpoint['name']}", 10.0, component="api")  # Timeout value
                logger.error(f"❌ Health check failed for {endpoint['name']}: {e}")
    
    def add_metric(self, name: str, value: float, component: str = "system", tags: Dict[str, str] = None):
        """Add metric to buffer"""
        metric = SystemMetric(
            name=name,
            value=value,
            timestamp=datetime.utcnow(),
            tags=tags or {},
            component=component
        )
        self.metrics_buffer.append(metric)
    
    async def flush_metrics(self):
        """Save buffered metrics to database"""
        if not self.metrics_buffer:
            return
            
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Ensure performance_metrics table exists
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS performance_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        metric_name TEXT NOT NULL,
                        value REAL NOT NULL,
                        tags TEXT,
                        component TEXT
                    )
                """)
                
                # Insert metrics
                for metric in self.metrics_buffer:
                    cursor.execute("""
                        INSERT INTO performance_metrics (timestamp, metric_name, value, tags, component)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        metric.timestamp,
                        metric.name,
                        metric.value,
                        json.dumps(metric.tags) if metric.tags else None,
                        metric.component
                    ))
                
                conn.commit()
                logger.debug(f"✅ Flushed {len(self.metrics_buffer)} metrics to database")
                
        except Exception as e:
            logger.error(f"❌ Failed to flush metrics: {e}")
        finally:
            self.metrics_buffer.clear()
    
    async def check_alerts(self):
        """Check for alert conditions"""
        try:
            # Get recent metrics for alerting
            recent_metrics = await self.get_recent_metrics(minutes=5)
            
            for metric_name, threshold in self.alert_thresholds.items():
                if metric_name in recent_metrics:
                    value = recent_metrics[metric_name]
                    
                    if self._should_alert(metric_name, value, threshold):
                        await self.send_alert(metric_name, value, threshold)
                        
        except Exception as e:
            logger.error(f"❌ Alert check failed: {e}")
    
    def _should_alert(self, metric_name: str, value: float, threshold: float) -> bool:
        """Determine if alert should be sent"""
        if metric_name in ['cpu_usage', 'memory_usage', 'disk_usage', 'error_rate']:
            return value > threshold
        elif metric_name == 'response_time':
            return value > threshold
        elif metric_name == 'request_rate':
            return value > threshold
        return False
    
    async def send_alert(self, metric_name: str, value: float, threshold: float):
        """Send alert (log for now, could extend to email/slack/etc)"""
        alert_message = f"🚨 ALERT: {metric_name} = {value:.2f} (threshold: {threshold:.2f})"
        logger.warning(alert_message)
        
        # Log alert to database
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO system_logs (level, message, component, metadata)
                    VALUES (?, ?, ?, ?)
                """, (
                    "ALERT",
                    alert_message,
                    "monitor",
                    json.dumps({"metric": metric_name, "value": value, "threshold": threshold})
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"❌ Failed to log alert: {e}")
    
    async def get_recent_metrics(self, minutes: int = 5) -> Dict[str, float]:
        """Get recent metric averages"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT metric_name, AVG(value) as avg_value
                    FROM performance_metrics
                    WHERE timestamp > datetime('now', '-{} minutes')
                    GROUP BY metric_name
                """.format(minutes))
                
                return {row[0]: row[1] for row in cursor.fetchall()}
                
        except Exception as e:
            logger.error(f"❌ Failed to get recent metrics: {e}")
            return {}
    
    async def generate_status_report(self) -> Dict:
        """Generate comprehensive status report"""
        try:
            recent_metrics = await self.get_recent_metrics(minutes=15)
            
            report = {
                "timestamp": datetime.utcnow().isoformat(),
                "system": {
                    "cpu_usage": recent_metrics.get("cpu_usage", 0),
                    "memory_usage": recent_metrics.get("memory_usage", 0),
                    "disk_usage": recent_metrics.get("disk_usage", 0),
                    "load_1min": recent_metrics.get("load_1min", 0)
                },
                "application": {
                    "database_size_mb": recent_metrics.get("database_size_mb", 0),
                    "messages_last_hour": recent_metrics.get("messages_last_hour", 0),
                    "total_conversations": recent_metrics.get("total_conversations", 0)
                },
                "api": {
                    "main_api_health": recent_metrics.get("endpoint_health_main_api", 0),
                    "main_api_response_time": recent_metrics.get("endpoint_response_time_main_api", 0),
                    "lex_endpoint_health": recent_metrics.get("endpoint_health_lex_endpoint", 0)
                },
                "alerts": []
            }
            
            # Check for active alerts
            for metric_name, threshold in self.alert_thresholds.items():
                if metric_name in recent_metrics:
                    value = recent_metrics[metric_name]
                    if self._should_alert(metric_name, value, threshold):
                        report["alerts"].append({
                            "metric": metric_name,
                            "value": value,
                            "threshold": threshold,
                            "severity": "high" if value > threshold * 1.2 else "medium"
                        })
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Failed to generate status report: {e}")
            return {"error": str(e)}

async def main():
    """CLI interface for monitoring"""
    import argparse
    
    parser = argparse.ArgumentParser(description="LEX Production Monitor")
    parser.add_argument("--db", default="lex_memory.db", help="Database path")
    parser.add_argument("--interval", type=int, default=60, help="Monitoring interval in seconds")
    parser.add_argument("--report", action="store_true", help="Generate status report")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('monitor.log')
        ]
    )
    
    monitor = ProductionMonitor(args.db)
    
    if args.report:
        report = await monitor.generate_status_report()
        print(json.dumps(report, indent=2))
    elif args.daemon:
        logger.info("🔍 Starting monitoring daemon...")
        await monitor.start_monitoring(args.interval)
    else:
        # One-time collection
        await monitor.collect_system_metrics()
        await monitor.collect_application_metrics()
        await monitor.check_health_endpoints()
        await monitor.flush_metrics()
        
        report = await monitor.generate_status_report()
        print(json.dumps(report, indent=2))

if __name__ == "__main__":
    asyncio.run(main())