#!/usr/bin/env python3
"""
Automated Backup System for LEX Production
🔱 JAI MAHAKAAL! Comprehensive backup strategy with rotation and recovery
"""
import os
import sys
import shutil
import sqlite3
import gzip
import json
import boto3
import logging
import asyncio
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

@dataclass
class BackupMetadata:
    """Backup metadata structure"""
    backup_id: str
    timestamp: datetime
    backup_type: str  # hourly, daily, weekly, monthly
    size_bytes: int
    checksum: str
    files_included: List[str]
    compression: str
    location: str
    retention_days: int
    verified: bool = False

class BackupManager:
    """Comprehensive backup management system"""
    
    def __init__(self, config_path: str = ".env"):
        self.config_path = config_path
        self.backup_root = Path("backups")
        self.backup_root.mkdir(exist_ok=True)
        
        # Backup directories
        self.hourly_dir = self.backup_root / "hourly"
        self.daily_dir = self.backup_root / "daily" 
        self.weekly_dir = self.backup_root / "weekly"
        self.monthly_dir = self.backup_root / "monthly"
        self.offsite_dir = self.backup_root / "offsite"
        
        for dir_path in [self.hourly_dir, self.daily_dir, self.weekly_dir, self.monthly_dir, self.offsite_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # Backup configuration
        self.backup_config = {
            'hourly': {'retention_days': 3, 'compression': True},
            'daily': {'retention_days': 30, 'compression': True},
            'weekly': {'retention_days': 90, 'compression': True},
            'monthly': {'retention_days': 365, 'compression': True}
        }
        
        # Files to backup
        self.critical_files = [
            "lex_memory.db",
            "lex_memory.db-wal", 
            "lex_memory.db-shm",
            ".env",
            "lex_production_secure.py",
            "security_config.py",
            "database_optimizer.py",
            "production_monitor.py",
            "server/",
            "frontend/",
            "requirements.txt",
            "requirements_security.txt"
        ]
        
        # Initialize S3 client for offsite backups (optional)
        self.s3_client = self._init_s3_client()
        
    def _init_s3_client(self):
        """Initialize S3 client for offsite backups"""
        try:
            # Load AWS credentials from environment
            aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
            aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
            aws_region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
            
            if aws_access_key and aws_secret_key:
                return boto3.client(
                    's3',
                    aws_access_key_id=aws_access_key,
                    aws_secret_access_key=aws_secret_key,
                    region_name=aws_region
                )
            else:
                logger.warning("⚠️ AWS credentials not found - offsite backup disabled")
                return None
        except Exception as e:
            logger.warning(f"⚠️ S3 client initialization failed: {e}")
            return None
    
    def calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of a file"""
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    
    def compress_backup(self, source_path: Path, dest_path: Path) -> Path:
        """Compress backup using gzip"""
        compressed_path = dest_path.with_suffix(dest_path.suffix + '.gz')
        
        with open(source_path, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        logger.info(f"📦 Compressed {source_path.name}: {source_path.stat().st_size} → {compressed_path.stat().st_size} bytes")
        return compressed_path
    
    def create_database_backup(self, backup_type: str) -> Optional[BackupMetadata]:
        """Create database backup with consistency checks"""
        try:
            db_path = Path("lex_memory.db")
            if not db_path.exists():
                logger.warning("⚠️ Database file not found")
                return None
            
            # Generate backup ID
            backup_id = f"db_{backup_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Determine backup directory
            backup_dir = getattr(self, f"{backup_type}_dir")
            backup_file = backup_dir / f"{backup_id}.db"
            
            # Create database backup using SQLite backup API
            with sqlite3.connect(db_path) as source_db:
                with sqlite3.connect(backup_file) as backup_db:
                    source_db.backup(backup_db)
            
            # Verify backup integrity
            with sqlite3.connect(backup_file) as backup_db:
                cursor = backup_db.cursor()
                cursor.execute("PRAGMA integrity_check")
                result = cursor.fetchone()
                if result[0] != "ok":
                    logger.error(f"❌ Backup integrity check failed: {result[0]}")
                    backup_file.unlink()  # Delete corrupted backup
                    return None
            
            # Calculate checksum
            checksum = self.calculate_checksum(backup_file)
            
            # Compress if configured
            original_size = backup_file.stat().st_size
            final_path = backup_file
            
            if self.backup_config[backup_type]['compression']:
                final_path = self.compress_backup(backup_file, backup_file)
                backup_file.unlink()  # Remove uncompressed version
            
            # Create metadata
            metadata = BackupMetadata(
                backup_id=backup_id,
                timestamp=datetime.utcnow(),
                backup_type=backup_type,
                size_bytes=final_path.stat().st_size,
                checksum=checksum,
                files_included=[str(db_path)],
                compression='gzip' if self.backup_config[backup_type]['compression'] else 'none',
                location=str(final_path),
                retention_days=self.backup_config[backup_type]['retention_days'],
                verified=True
            )
            
            # Save metadata
            metadata_file = final_path.with_suffix('.json')
            with open(metadata_file, 'w') as f:
                json.dump(asdict(metadata), f, indent=2, default=str)
            
            logger.info(f"✅ Database backup created: {backup_id} ({original_size} bytes)")
            return metadata
            
        except Exception as e:
            logger.error(f"❌ Database backup failed: {e}")
            return None
    
    def create_full_system_backup(self, backup_type: str) -> Optional[BackupMetadata]:
        """Create full system backup"""
        try:
            # Generate backup ID
            backup_id = f"system_{backup_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Create backup directory
            backup_dir = getattr(self, f"{backup_type}_dir") / backup_id
            backup_dir.mkdir(exist_ok=True)
            
            files_included = []
            total_size = 0
            
            # Backup critical files
            for file_pattern in self.critical_files:
                file_path = Path(file_pattern)
                
                if file_path.exists():
                    if file_path.is_file():
                        # Copy single file
                        dest_file = backup_dir / file_path.name
                        shutil.copy2(file_path, dest_file)
                        files_included.append(str(file_path))
                        total_size += dest_file.stat().st_size
                        
                    elif file_path.is_dir():
                        # Copy entire directory
                        dest_dir = backup_dir / file_path.name
                        shutil.copytree(file_path, dest_dir, dirs_exist_ok=True)
                        files_included.append(str(file_path))
                        
                        # Calculate directory size
                        for root, dirs, files in os.walk(dest_dir):
                            for file in files:
                                total_size += Path(root, file).stat().st_size
            
            # Create archive
            archive_path = backup_dir.parent / f"{backup_id}.tar"
            
            # Use tar with compression
            import tarfile
            with tarfile.open(archive_path, 'w:gz' if self.backup_config[backup_type]['compression'] else 'w') as tar:
                tar.add(backup_dir, arcname=backup_id)
            
            # Remove temporary directory
            shutil.rmtree(backup_dir)
            
            # Calculate checksum
            checksum = self.calculate_checksum(archive_path)
            
            # Create metadata
            metadata = BackupMetadata(
                backup_id=backup_id,
                timestamp=datetime.utcnow(),
                backup_type=backup_type,
                size_bytes=archive_path.stat().st_size,
                checksum=checksum,
                files_included=files_included,
                compression='gzip' if self.backup_config[backup_type]['compression'] else 'none',
                location=str(archive_path),
                retention_days=self.backup_config[backup_type]['retention_days'],
                verified=False  # Will be verified separately
            )
            
            # Save metadata
            metadata_file = archive_path.with_suffix('.json')
            with open(metadata_file, 'w') as f:
                json.dump(asdict(metadata), f, indent=2, default=str)
            
            logger.info(f"✅ System backup created: {backup_id} ({len(files_included)} files, {total_size} bytes)")
            return metadata
            
        except Exception as e:
            logger.error(f"❌ System backup failed: {e}")
            return None
    
    def cleanup_old_backups(self):
        """Clean up old backups based on retention policy"""
        logger.info("🧹 Cleaning up old backups...")
        
        for backup_type in ['hourly', 'daily', 'weekly', 'monthly']:
            backup_dir = getattr(self, f"{backup_type}_dir")
            retention_days = self.backup_config[backup_type]['retention_days']
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            
            removed_count = 0
            removed_size = 0
            
            # Find old backup files
            for backup_file in backup_dir.glob("*"):
                if backup_file.suffix in ['.db', '.tar', '.gz']:
                    # Get file creation time
                    file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
                    
                    if file_time < cutoff_date:
                        # Remove old backup and its metadata
                        file_size = backup_file.stat().st_size
                        backup_file.unlink()
                        
                        # Remove metadata file
                        metadata_file = backup_file.with_suffix('.json')
                        if metadata_file.exists():
                            metadata_file.unlink()
                        
                        removed_count += 1
                        removed_size += file_size
            
            if removed_count > 0:
                logger.info(f"🗑️ Removed {removed_count} old {backup_type} backups ({removed_size} bytes)")
    
    def upload_to_s3(self, local_path: Path, s3_bucket: str, s3_key: str) -> bool:
        """Upload backup to S3 for offsite storage"""
        if not self.s3_client:
            logger.warning("⚠️ S3 client not available")
            return False
        
        try:
            logger.info(f"📤 Uploading to S3: {s3_key}")
            
            # Upload file with server-side encryption
            self.s3_client.upload_file(
                str(local_path),
                s3_bucket,
                s3_key,
                ExtraArgs={
                    'ServerSideEncryption': 'AES256',
                    'StorageClass': 'STANDARD_IA'  # Infrequent Access for backups
                }
            )
            
            logger.info(f"✅ Uploaded to S3: s3://{s3_bucket}/{s3_key}")
            return True
            
        except Exception as e:
            logger.error(f"❌ S3 upload failed: {e}")
            return False
    
    def verify_backup(self, metadata: BackupMetadata) -> bool:
        """Verify backup integrity"""
        try:
            backup_path = Path(metadata.location)
            
            if not backup_path.exists():
                logger.error(f"❌ Backup file not found: {backup_path}")
                return False
            
            # Verify checksum
            current_checksum = self.calculate_checksum(backup_path)
            if current_checksum != metadata.checksum:
                logger.error(f"❌ Checksum mismatch for {backup_path}")
                return False
            
            # For database backups, verify SQLite integrity
            if backup_path.suffix in ['.db', '.gz']:
                if backup_path.suffix == '.gz':
                    # Decompress temporarily for verification
                    temp_path = backup_path.with_suffix('')
                    with gzip.open(backup_path, 'rb') as f_in:
                        with open(temp_path, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    
                    verify_path = temp_path
                else:
                    verify_path = backup_path
                
                try:
                    with sqlite3.connect(verify_path) as conn:
                        result = conn.execute("PRAGMA integrity_check").fetchone()
                        if result[0] != "ok":
                            logger.error(f"❌ Database integrity check failed: {result[0]}")
                            return False
                finally:
                    if verify_path != backup_path and verify_path.exists():
                        verify_path.unlink()
            
            logger.info(f"✅ Backup verification successful: {backup_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Backup verification failed: {e}")
            return False
    
    def restore_from_backup(self, backup_id: str, restore_path: Optional[str] = None) -> bool:
        """Restore from backup"""
        try:
            logger.info(f"🔄 Restoring from backup: {backup_id}")
            
            # Find backup metadata
            metadata_file = None
            for backup_type in ['hourly', 'daily', 'weekly', 'monthly']:
                backup_dir = getattr(self, f"{backup_type}_dir")
                potential_metadata = backup_dir / f"{backup_id}.json"
                if potential_metadata.exists():
                    metadata_file = potential_metadata
                    break
            
            if not metadata_file:
                logger.error(f"❌ Backup metadata not found: {backup_id}")
                return False
            
            # Load metadata
            with open(metadata_file, 'r') as f:
                metadata_dict = json.load(f)
            
            backup_path = Path(metadata_dict['location'])
            
            if not backup_path.exists():
                logger.error(f"❌ Backup file not found: {backup_path}")
                return False
            
            # Verify backup before restore
            metadata = BackupMetadata(**metadata_dict)
            if not self.verify_backup(metadata):
                logger.error(f"❌ Backup verification failed, restore aborted")
                return False
            
            # Perform restore based on backup type
            if 'db_' in backup_id:
                # Database restore
                restore_target = Path(restore_path or "lex_memory.db")
                
                # Backup current database first
                if restore_target.exists():
                    backup_current = restore_target.with_suffix('.db.restore_backup')
                    shutil.copy2(restore_target, backup_current)
                    logger.info(f"📦 Current database backed up to {backup_current}")
                
                # Restore database
                if backup_path.suffix == '.gz':
                    with gzip.open(backup_path, 'rb') as f_in:
                        with open(restore_target, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                else:
                    shutil.copy2(backup_path, restore_target)
                
                logger.info(f"✅ Database restored from {backup_id}")
                
            elif 'system_' in backup_id:
                # System restore
                import tarfile
                
                restore_dir = Path(restore_path or ".")
                
                with tarfile.open(backup_path, 'r:gz' if backup_path.suffix == '.gz' else 'r') as tar:
                    tar.extractall(restore_dir)
                
                logger.info(f"✅ System restored from {backup_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Restore failed: {e}")
            return False
    
    async def run_automated_backup(self):
        """Run automated backup based on schedule"""
        logger.info("🔱 Starting automated backup cycle...")
        
        current_time = datetime.utcnow()
        
        # Determine what type of backup to run
        run_hourly = True  # Always run hourly
        run_daily = current_time.hour == 2  # Run daily at 2 AM
        run_weekly = run_daily and current_time.weekday() == 6  # Sunday
        run_monthly = run_daily and current_time.day == 1  # First of month
        
        backup_tasks = []
        
        if run_monthly:
            logger.info("📅 Running monthly backup...")
            backup_tasks.append(('monthly', 'system'))
        elif run_weekly:
            logger.info("📅 Running weekly backup...")
            backup_tasks.append(('weekly', 'system'))
        elif run_daily:
            logger.info("📅 Running daily backup...")
            backup_tasks.append(('daily', 'system'))
            backup_tasks.append(('daily', 'database'))
        
        if run_hourly:
            logger.info("📅 Running hourly backup...")
            backup_tasks.append(('hourly', 'database'))
        
        # Execute backups
        for backup_type, backup_scope in backup_tasks:
            try:
                if backup_scope == 'database':
                    metadata = self.create_database_backup(backup_type)
                else:
                    metadata = self.create_full_system_backup(backup_type)
                
                if metadata:
                    # Verify backup
                    if self.verify_backup(metadata):
                        logger.info(f"✅ {backup_type} {backup_scope} backup completed and verified")
                        
                        # Upload to S3 for daily+ backups
                        if backup_type in ['daily', 'weekly', 'monthly'] and self.s3_client:
                            s3_bucket = os.getenv('LEX_BACKUP_S3_BUCKET')
                            if s3_bucket:
                                s3_key = f"lex-backups/{backup_type}/{metadata.backup_id}"
                                self.upload_to_s3(Path(metadata.location), s3_bucket, s3_key)
                    else:
                        logger.error(f"❌ {backup_type} {backup_scope} backup verification failed")
                else:
                    logger.error(f"❌ {backup_type} {backup_scope} backup creation failed")
                    
            except Exception as e:
                logger.error(f"❌ {backup_type} {backup_scope} backup failed: {e}")
        
        # Cleanup old backups
        self.cleanup_old_backups()
        
        logger.info("✅ Automated backup cycle completed")
    
    def get_backup_status(self) -> Dict:
        """Get comprehensive backup status"""
        status = {
            'timestamp': datetime.utcnow().isoformat(),
            'backup_types': {}
        }
        
        for backup_type in ['hourly', 'daily', 'weekly', 'monthly']:
            backup_dir = getattr(self, f"{backup_type}_dir")
            backups = list(backup_dir.glob("*"))
            
            total_size = sum(f.stat().st_size for f in backups if f.is_file())
            
            # Find latest backup
            latest_backup = None
            if backups:
                latest_file = max((f for f in backups if f.suffix != '.json'), 
                                key=lambda x: x.stat().st_mtime, default=None)
                if latest_file:
                    latest_backup = {
                        'name': latest_file.name,
                        'timestamp': datetime.fromtimestamp(latest_file.stat().st_mtime).isoformat(),
                        'size_bytes': latest_file.stat().st_size
                    }
            
            status['backup_types'][backup_type] = {
                'count': len([f for f in backups if f.suffix != '.json']),
                'total_size_bytes': total_size,
                'latest_backup': latest_backup
            }
        
        return status

def main():
    """CLI interface for backup system"""
    import argparse
    
    parser = argparse.ArgumentParser(description="LEX Automated Backup System")
    parser.add_argument("--run-backup", action="store_true", help="Run automated backup")
    parser.add_argument("--backup-type", choices=['hourly', 'daily', 'weekly', 'monthly'], help="Specific backup type")
    parser.add_argument("--backup-scope", choices=['database', 'system'], default='database', help="Backup scope")
    parser.add_argument("--status", action="store_true", help="Show backup status")
    parser.add_argument("--cleanup", action="store_true", help="Clean up old backups")
    parser.add_argument("--verify", help="Verify specific backup by ID")
    parser.add_argument("--restore", help="Restore from specific backup ID")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('backup.log')
        ]
    )
    
    backup_manager = BackupManager()
    
    if args.run_backup:
        asyncio.run(backup_manager.run_automated_backup())
    elif args.backup_type:
        if args.backup_scope == 'database':
            backup_manager.create_database_backup(args.backup_type)
        else:
            backup_manager.create_full_system_backup(args.backup_type)
    elif args.status:
        status = backup_manager.get_backup_status()
        print(json.dumps(status, indent=2))
    elif args.cleanup:
        backup_manager.cleanup_old_backups()
    elif args.verify:
        # Find and verify backup
        for backup_type in ['hourly', 'daily', 'weekly', 'monthly']:
            metadata_file = getattr(backup_manager, f"{backup_type}_dir") / f"{args.verify}.json"
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata_dict = json.load(f)
                metadata = BackupMetadata(**metadata_dict)
                result = backup_manager.verify_backup(metadata)
                print(f"Verification result: {'PASSED' if result else 'FAILED'}")
                break
        else:
            print(f"Backup not found: {args.verify}")
    elif args.restore:
        success = backup_manager.restore_from_backup(args.restore)
        print(f"Restore result: {'SUCCESS' if success else 'FAILED'}")
    elif args.daemon:
        async def backup_daemon():
            while True:
                try:
                    await backup_manager.run_automated_backup()
                    # Wait 1 hour before next check
                    await asyncio.sleep(3600)
                except Exception as e:
                    logger.error(f"❌ Backup daemon error: {e}")
                    await asyncio.sleep(300)  # Wait 5 minutes on error
        
        logger.info("🔱 Starting backup daemon...")
        asyncio.run(backup_daemon())
    else:
        parser.print_help()

if __name__ == "__main__":
    main()