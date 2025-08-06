#!/usr/bin/env python3
"""
Database Optimizer for LEX Production
🔱 JAI MAHAKAAL! SQLite performance optimization
"""
import sqlite3
import logging
import os
import shutil
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class DatabaseOptimizer:
    """SQLite database optimizer for production performance"""
    
    def __init__(self, db_path: str = "lex_memory.db"):
        self.db_path = db_path
        self.backup_dir = Path("backups/database")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
    def backup_database(self) -> str:
        """Create database backup before optimization"""
        if not os.path.exists(self.db_path):
            logger.warning(f"Database {self.db_path} doesn't exist yet")
            return None
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"lex_memory_backup_{timestamp}.db"
        
        try:
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"✅ Database backed up to {backup_path}")
            return str(backup_path)
        except Exception as e:
            logger.error(f"❌ Backup failed: {e}")
            return None
    
    def create_tables(self):
        """Create optimized database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Memory/conversation table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    title TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT  -- JSON for additional data
                )
            """)
            
            # Messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,  -- 'user' or 'assistant'
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    model_used TEXT,
                    confidence REAL,
                    metadata TEXT,  -- JSON for additional data
                    FOREIGN KEY (conversation_id) REFERENCES conversations (id)
                )
            """)
            
            # System logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    component TEXT,
                    request_id TEXT,
                    metadata TEXT
                )
            """)
            
            # Performance metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metric_name TEXT NOT NULL,
                    value REAL NOT NULL,
                    tags TEXT,  -- JSON for additional tags
                    component TEXT
                )
            """)
            
            conn.commit()
            logger.info("✅ Database tables created/verified")
    
    def create_indexes(self):
        """Create performance indexes"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Indexes for conversations
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at)",
                "CREATE INDEX IF NOT EXISTS idx_conversations_updated_at ON conversations(updated_at)",
                
                # Indexes for messages
                "CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id)",
                "CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp)",
                "CREATE INDEX IF NOT EXISTS idx_messages_role ON messages(role)",
                "CREATE INDEX IF NOT EXISTS idx_messages_model_used ON messages(model_used)",
                
                # Composite indexes for common queries
                "CREATE INDEX IF NOT EXISTS idx_messages_conv_timestamp ON messages(conversation_id, timestamp)",
                "CREATE INDEX IF NOT EXISTS idx_conversations_user_updated ON conversations(user_id, updated_at)",
                
                # Indexes for system logs
                "CREATE INDEX IF NOT EXISTS idx_system_logs_timestamp ON system_logs(timestamp)",
                "CREATE INDEX IF NOT EXISTS idx_system_logs_level ON system_logs(level)",
                "CREATE INDEX IF NOT EXISTS idx_system_logs_component ON system_logs(component)",
                "CREATE INDEX IF NOT EXISTS idx_system_logs_request_id ON system_logs(request_id)",
                
                # Indexes for performance metrics
                "CREATE INDEX IF NOT EXISTS idx_performance_metrics_timestamp ON performance_metrics(timestamp)",
                "CREATE INDEX IF NOT EXISTS idx_performance_metrics_name ON performance_metrics(metric_name)",
                "CREATE INDEX IF NOT EXISTS idx_performance_metrics_component ON performance_metrics(component)"
            ]
            
            for index_sql in indexes:
                cursor.execute(index_sql)
                
            conn.commit()
            logger.info("✅ Database indexes created")
    
    def optimize_settings(self):
        """Apply SQLite optimization settings"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            optimizations = [
                # Enable WAL mode for better concurrency
                "PRAGMA journal_mode=WAL",
                
                # Increase cache size (10MB)
                "PRAGMA cache_size=10000",
                
                # Enable foreign key constraints
                "PRAGMA foreign_keys=ON",
                
                # Optimize synchronization for performance
                "PRAGMA synchronous=NORMAL",
                
                # Set page size for better performance
                "PRAGMA page_size=4096",
                
                # Enable memory-mapped I/O
                "PRAGMA mmap_size=268435456",  # 256MB
                
                # Optimize temp storage
                "PRAGMA temp_store=MEMORY",
                
                # Optimize locking mode
                "PRAGMA locking_mode=NORMAL",
                
                # Auto-vacuum for maintenance
                "PRAGMA auto_vacuum=INCREMENTAL"
            ]
            
            for pragma in optimizations:
                cursor.execute(pragma)
                result = cursor.fetchone()
                pragma_name = pragma.split('=')[0].split()[-1]
                logger.info(f"✅ {pragma_name}: {result[0] if result else 'Applied'}")
                
            conn.commit()
    
    def analyze_database(self):
        """Analyze database for query optimization"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("ANALYZE")
            conn.commit()
            logger.info("✅ Database analyzed for query optimization")
    
    def vacuum_database(self):
        """Vacuum database to reclaim space"""
        with sqlite3.connect(self.db_path) as conn:
            # WAL mode requires special handling for VACUUM
            cursor = conn.cursor()
            cursor.execute("PRAGMA journal_mode")
            mode = cursor.fetchone()[0]
            
            if mode.upper() == 'WAL':
                # Checkpoint WAL file first
                cursor.execute("PRAGMA wal_checkpoint(TRUNCATE)")
                logger.info("✅ WAL checkpoint completed")
            
            # Perform vacuum
            conn.execute("VACUUM")
            logger.info("✅ Database vacuumed")
    
    def get_database_stats(self) -> dict:
        """Get database statistics"""
        if not os.path.exists(self.db_path):
            return {"status": "Database doesn't exist"}
            
        stats = {}
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Database size
                stats['file_size_mb'] = os.path.getsize(self.db_path) / (1024 * 1024)
                
                # Page info
                cursor.execute("PRAGMA page_count")
                stats['page_count'] = cursor.fetchone()[0]
                
                cursor.execute("PRAGMA page_size")
                stats['page_size'] = cursor.fetchone()[0]
                
                cursor.execute("PRAGMA freelist_count")
                stats['freelist_count'] = cursor.fetchone()[0]
                
                # Journal mode
                cursor.execute("PRAGMA journal_mode")
                stats['journal_mode'] = cursor.fetchone()[0]
                
                # Cache size
                cursor.execute("PRAGMA cache_size")
                stats['cache_size'] = cursor.fetchone()[0]
                
                # Table counts
                tables = ['conversations', 'messages', 'system_logs', 'performance_metrics']
                for table in tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        stats[f'{table}_count'] = cursor.fetchone()[0]
                    except sqlite3.OperationalError:
                        stats[f'{table}_count'] = 0
                        
        except Exception as e:
            stats['error'] = str(e)
            logger.error(f"❌ Failed to get database stats: {e}")
        
        return stats
    
    def optimize_full(self):
        """Run complete database optimization"""
        logger.info("🔱 Starting full database optimization...")
        
        # Backup first
        backup_path = self.backup_database()
        if not backup_path and os.path.exists(self.db_path):
            logger.error("❌ Backup failed, aborting optimization")
            return False
        
        try:
            # Create tables and indexes
            self.create_tables()
            self.create_indexes()
            
            # Apply optimizations
            self.optimize_settings()
            
            # Analyze for query planner
            self.analyze_database()
            
            logger.info("✅ Database optimization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database optimization failed: {e}")
            
            # Restore backup if optimization failed
            if backup_path and os.path.exists(backup_path):
                try:
                    shutil.copy2(backup_path, self.db_path)
                    logger.info(f"✅ Database restored from backup: {backup_path}")
                except Exception as restore_error:
                    logger.error(f"❌ Failed to restore backup: {restore_error}")
            
            return False

def main():
    """CLI interface for database optimization"""
    import argparse
    
    parser = argparse.ArgumentParser(description="LEX Database Optimizer")
    parser.add_argument("--db", default="lex_memory.db", help="Database path")
    parser.add_argument("--backup", action="store_true", help="Create backup only")
    parser.add_argument("--optimize", action="store_true", help="Run full optimization")
    parser.add_argument("--stats", action="store_true", help="Show database statistics")
    parser.add_argument("--vacuum", action="store_true", help="Vacuum database")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    optimizer = DatabaseOptimizer(args.db)
    
    if args.backup:
        optimizer.backup_database()
    elif args.optimize:
        optimizer.optimize_full()
    elif args.stats:
        stats = optimizer.get_database_stats()
        print("\n🔱 Database Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    elif args.vacuum:
        optimizer.vacuum_database()
    else:
        print("No action specified. Use --help for options.")

if __name__ == "__main__":
    main()