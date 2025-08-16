"""
Backup and Restore functionality for the self-healing system.

This module provides intelligent snapshot management that works in harmony
with NixOS's generation system, creating restore points before healing
actions and learning from rollback patterns.
"""

import asyncio
import json
import logging
import subprocess
import shutil
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import hashlib
import os

logger = logging.getLogger(__name__)


@dataclass
class Generation:
    """NixOS generation information"""
    number: int
    date: datetime
    current: bool
    description: str
    kernel: Optional[str] = None
    config_hash: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'number': self.number,
            'date': self.date.isoformat() if self.date else None,
            'current': self.current,
            'description': self.description,
            'kernel': self.kernel,
            'config_hash': self.config_hash
        }


@dataclass
class RestorePoint:
    """A point in time that can be restored to"""
    id: str
    timestamp: datetime
    generation_number: int
    reason: str
    system_health: float
    active_issues: List[str]
    config_backup: Optional[Path] = None
    state_backup: Optional[Path] = None
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'generation_number': self.generation_number,
            'reason': self.reason,
            'system_health': self.system_health,
            'active_issues': self.active_issues,
            'config_backup': str(self.config_backup) if self.config_backup else None,
            'state_backup': str(self.state_backup) if self.state_backup else None,
            'metadata': self.metadata
        }


@dataclass
class BackupResult:
    """Result of a backup operation"""
    success: bool
    restore_point: Optional[RestorePoint]
    size_bytes: int
    duration_seconds: float
    error: Optional[str] = None


@dataclass
class RestoreResult:
    """Result of a restore operation"""
    success: bool
    restored_generation: Optional[int]
    health_before: float
    health_after: float
    duration_seconds: float
    error: Optional[str] = None


class NixOSGenerationManager:
    """
    Manages NixOS generations with intelligent tracking and rollback.
    """
    
    def __init__(self):
        self.generations_cache = []
        self.last_good_generation = None
        self.rollback_history = []
    
    async def list_generations(self) -> List[Generation]:
        """
        List all available NixOS generations.
        
        Returns:
            List of Generation objects
        """
        try:
            result = subprocess.run(
                ['nix-env', '--list-generations', '-p', '/nix/var/nix/profiles/system'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                logger.error(f"Failed to list generations: {result.stderr}")
                return []
            
            generations = []
            current_gen = await self.get_current_generation()
            
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                
                # Parse generation line
                # Format: "  14   2024-07-15 10:30:00   (current)"
                parts = line.strip().split(None, 3)
                if len(parts) >= 3:
                    gen_num = int(parts[0])
                    date_str = f"{parts[1]} {parts[2]}"
                    is_current = gen_num == current_gen
                    description = parts[3] if len(parts) > 3 else ""
                    
                    try:
                        date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                    except:
                        date = datetime.now()
                    
                    generations.append(Generation(
                        number=gen_num,
                        date=date,
                        current=is_current,
                        description=description
                    ))
            
            self.generations_cache = generations
            return generations
            
        except Exception as e:
            logger.error(f"Error listing generations: {e}")
            return []
    
    async def get_current_generation(self) -> Optional[int]:
        """
        Get the current generation number.
        
        Returns:
            Current generation number or None
        """
        try:
            result = subprocess.run(
                ['readlink', '/nix/var/nix/profiles/system'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Extract generation number from path
                # Format: /nix/var/nix/profiles/system-123-link
                path = result.stdout.strip()
                parts = path.split('-')
                if len(parts) >= 2:
                    return int(parts[-2])
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting current generation: {e}")
            return None
    
    async def rollback(self) -> bool:
        """
        Rollback to the previous generation.
        
        Returns:
            True if successful
        """
        try:
            logger.info("🔄 Rolling back to previous generation...")
            
            current = await self.get_current_generation()
            
            result = subprocess.run(
                ['nixos-rebuild', 'switch', '--rollback'],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                new_gen = await self.get_current_generation()
                logger.info(f"✅ Rolled back from generation {current} to {new_gen}")
                
                # Track rollback
                self.rollback_history.append({
                    'timestamp': datetime.now(),
                    'from_generation': current,
                    'to_generation': new_gen,
                    'reason': 'manual_rollback'
                })
                
                return True
            else:
                logger.error(f"Rollback failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error during rollback: {e}")
            return False
    
    async def switch_to_generation(self, generation_number: int) -> bool:
        """
        Switch to a specific generation.
        
        Args:
            generation_number: Generation to switch to
            
        Returns:
            True if successful
        """
        try:
            logger.info(f"🔄 Switching to generation {generation_number}...")
            
            current = await self.get_current_generation()
            
            # Use the generation profile path
            profile_path = f"/nix/var/nix/profiles/system-{generation_number}-link"
            
            if not Path(profile_path).exists():
                logger.error(f"Generation {generation_number} does not exist")
                return False
            
            result = subprocess.run(
                ['nixos-rebuild', 'switch', '--profile', profile_path],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Switched from generation {current} to {generation_number}")
                
                # Track switch
                self.rollback_history.append({
                    'timestamp': datetime.now(),
                    'from_generation': current,
                    'to_generation': generation_number,
                    'reason': 'manual_switch'
                })
                
                return True
            else:
                logger.error(f"Switch failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error switching generation: {e}")
            return False
    
    async def mark_generation_as_good(self, generation_number: Optional[int] = None):
        """
        Mark a generation as known good.
        
        Args:
            generation_number: Generation to mark (current if None)
        """
        if generation_number is None:
            generation_number = await self.get_current_generation()
        
        self.last_good_generation = generation_number
        logger.info(f"✅ Marked generation {generation_number} as good")
    
    async def get_generation_info(self, generation_number: int) -> Optional[Generation]:
        """
        Get detailed information about a generation.
        
        Args:
            generation_number: Generation to query
            
        Returns:
            Generation object or None
        """
        generations = await self.list_generations()
        for gen in generations:
            if gen.number == generation_number:
                # Add extra details
                gen.kernel = await self._get_generation_kernel(generation_number)
                gen.config_hash = await self._get_config_hash(generation_number)
                return gen
        return None
    
    async def _get_generation_kernel(self, generation_number: int) -> Optional[str]:
        """Get kernel version for a generation"""
        try:
            kernel_path = f"/nix/var/nix/profiles/system-{generation_number}-link/kernel"
            if Path(kernel_path).exists():
                result = subprocess.run(
                    ['readlink', kernel_path],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    # Extract kernel version from path
                    kernel_store_path = result.stdout.strip()
                    parts = kernel_store_path.split('-')
                    if len(parts) > 2:
                        return f"{parts[1]}-{parts[2]}"
            return None
        except:
            return None
    
    async def _get_config_hash(self, generation_number: int) -> Optional[str]:
        """Get configuration hash for a generation"""
        try:
            config_path = f"/nix/var/nix/profiles/system-{generation_number}-link/configuration.nix"
            if Path(config_path).exists():
                with open(config_path, 'rb') as f:
                    return hashlib.sha256(f.read()).hexdigest()[:8]
            return None
        except:
            return None
    
    async def cleanup_old_generations(self, keep_count: int = 5):
        """
        Clean up old generations, keeping the most recent ones.
        
        Args:
            keep_count: Number of generations to keep
        """
        try:
            logger.info(f"🧹 Cleaning old generations (keeping {keep_count})...")
            
            result = subprocess.run(
                ['nix-collect-garbage', '--delete-older-than', f'{keep_count}d'],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                logger.info("✅ Old generations cleaned")
                return True
            else:
                logger.error(f"Cleanup failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error cleaning generations: {e}")
            return False


class ConfigurationBackup:
    """
    Manages configuration file backups.
    """
    
    def __init__(self, backup_dir: Optional[Path] = None):
        # Use a user-writable directory for testing
        if backup_dir:
            self.backup_dir = backup_dir
        else:
            # Try user's local share first
            self.backup_dir = Path.home() / '.local' / 'share' / 'luminous-nix' / 'backups'
            try:
                self.backup_dir.mkdir(parents=True, exist_ok=True)
            except PermissionError:
                # Fall back to temp directory
                self.backup_dir = Path('/tmp/luminous-nix-backups')
        
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.backup_index = self._load_index()
    
    def _load_index(self) -> Dict[str, Any]:
        """Load backup index"""
        index_file = self.backup_dir / 'index.json'
        if index_file.exists():
            try:
                with open(index_file) as f:
                    return json.load(f)
            except:
                pass
        return {'backups': [], 'last_backup': None}
    
    def _save_index(self):
        """Save backup index"""
        index_file = self.backup_dir / 'index.json'
        with open(index_file, 'w') as f:
            json.dump(self.backup_index, f, indent=2)
    
    async def backup_configuration(self, reason: str = "manual") -> Optional[Path]:
        """
        Backup NixOS configuration files.
        
        Args:
            reason: Reason for backup
            
        Returns:
            Path to backup or None
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_subdir = self.backup_dir / f"{timestamp}_{reason}"
            backup_subdir.mkdir(parents=True, exist_ok=True)
            
            # Files to backup
            config_files = [
                '/etc/nixos/configuration.nix',
                '/etc/nixos/hardware-configuration.nix'
            ]
            
            # Find all .nix files in /etc/nixos
            nixos_dir = Path('/etc/nixos')
            if nixos_dir.exists():
                for nix_file in nixos_dir.glob('*.nix'):
                    if nix_file.is_file():
                        config_files.append(str(nix_file))
            
            # Backup each file
            backed_up = []
            for config_file in config_files:
                if Path(config_file).exists():
                    dest = backup_subdir / Path(config_file).name
                    shutil.copy2(config_file, dest)
                    backed_up.append(Path(config_file).name)
                    logger.debug(f"Backed up {config_file} to {dest}")
            
            # Create metadata
            metadata = {
                'timestamp': timestamp,
                'reason': reason,
                'files': backed_up,
                'generation': await NixOSGenerationManager().get_current_generation()
            }
            
            with open(backup_subdir / 'metadata.json', 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Update index
            self.backup_index['backups'].append({
                'timestamp': timestamp,
                'path': str(backup_subdir),
                'reason': reason,
                'files': backed_up
            })
            self.backup_index['last_backup'] = timestamp
            self._save_index()
            
            logger.info(f"✅ Configuration backed up to {backup_subdir}")
            return backup_subdir
            
        except Exception as e:
            logger.error(f"Error backing up configuration: {e}")
            return None
    
    async def restore_configuration(self, backup_path: Path) -> bool:
        """
        Restore configuration from backup.
        
        Args:
            backup_path: Path to backup directory
            
        Returns:
            True if successful
        """
        try:
            if not backup_path.exists():
                logger.error(f"Backup path {backup_path} does not exist")
                return False
            
            # Load metadata
            metadata_file = backup_path / 'metadata.json'
            if metadata_file.exists():
                with open(metadata_file) as f:
                    metadata = json.load(f)
            else:
                metadata = {}
            
            # Backup current config before restoring
            await self.backup_configuration("pre_restore")
            
            # Restore files
            for nix_file in backup_path.glob('*.nix'):
                dest = Path('/etc/nixos') / nix_file.name
                shutil.copy2(nix_file, dest)
                logger.debug(f"Restored {nix_file.name} to {dest}")
            
            logger.info(f"✅ Configuration restored from {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error restoring configuration: {e}")
            return False
    
    async def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups"""
        return self.backup_index['backups']
    
    async def cleanup_old_backups(self, keep_count: int = 10):
        """
        Clean up old backups.
        
        Args:
            keep_count: Number of backups to keep
        """
        backups = self.backup_index['backups']
        if len(backups) <= keep_count:
            return
        
        # Sort by timestamp and remove old ones
        backups.sort(key=lambda x: x['timestamp'])
        to_remove = backups[:-keep_count]
        
        for backup in to_remove:
            backup_path = Path(backup['path'])
            if backup_path.exists():
                shutil.rmtree(backup_path)
                logger.debug(f"Removed old backup: {backup_path}")
        
        self.backup_index['backups'] = backups[-keep_count:]
        self._save_index()
        logger.info(f"✅ Cleaned up {len(to_remove)} old backups")


class BackupRestoreManager:
    """
    Main manager for backup and restore operations.
    Coordinates generations, configurations, and state.
    """
    
    def __init__(self, healing_engine=None):
        self.healing_engine = healing_engine
        self.generation_manager = NixOSGenerationManager()
        self.config_backup = ConfigurationBackup()
        
        # Restore points tracking - use user-writable directory
        try:
            self.restore_points_dir = Path.home() / '.local' / 'share' / 'luminous-nix' / 'restore-points'
            self.restore_points_dir.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            # Fall back to temp directory
            self.restore_points_dir = Path('/tmp/luminous-nix-restore-points')
            self.restore_points_dir.mkdir(parents=True, exist_ok=True)
        self.restore_points = self._load_restore_points()
        
        # Learning data
        self.rollback_patterns = []
        self.successful_heals = []
    
    def _load_restore_points(self) -> List[RestorePoint]:
        """Load restore points from disk"""
        points = []
        index_file = self.restore_points_dir / 'index.json'
        
        if index_file.exists():
            try:
                with open(index_file) as f:
                    data = json.load(f)
                    for point_data in data.get('points', []):
                        point = RestorePoint(
                            id=point_data['id'],
                            timestamp=datetime.fromisoformat(point_data['timestamp']),
                            generation_number=point_data['generation_number'],
                            reason=point_data['reason'],
                            system_health=point_data['system_health'],
                            active_issues=point_data['active_issues'],
                            config_backup=Path(point_data['config_backup']) if point_data.get('config_backup') else None,
                            metadata=point_data.get('metadata', {})
                        )
                        points.append(point)
            except Exception as e:
                logger.error(f"Error loading restore points: {e}")
        
        return points
    
    def _save_restore_points(self):
        """Save restore points to disk"""
        index_file = self.restore_points_dir / 'index.json'
        data = {
            'points': [p.to_dict() for p in self.restore_points],
            'last_update': datetime.now().isoformat()
        }
        
        with open(index_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    async def create_restore_point(self, reason: str = "manual", 
                                  include_state: bool = False) -> BackupResult:
        """
        Create a comprehensive restore point.
        
        Args:
            reason: Reason for creating restore point
            include_state: Whether to backup stateful data
            
        Returns:
            BackupResult
        """
        start_time = datetime.now()
        
        try:
            # Get current system state
            current_gen = await self.generation_manager.get_current_generation()
            if current_gen is None:
                return BackupResult(
                    success=False,
                    restore_point=None,
                    size_bytes=0,
                    duration_seconds=0,
                    error="Could not determine current generation"
                )
            
            # Get system health
            health = 100.0  # Default
            active_issues = []
            
            if self.healing_engine:
                health = self.healing_engine._calculate_health_score(
                    self.healing_engine.monitor.get_state()
                )
                issues = await self.healing_engine.detect_issues()
                active_issues = [i.description for i in issues]
            
            # Create configuration backup
            config_backup_path = await self.config_backup.backup_configuration(reason)
            
            # Create restore point
            restore_point = RestorePoint(
                id=hashlib.md5(f"{datetime.now().isoformat()}_{reason}".encode()).hexdigest()[:8],
                timestamp=datetime.now(),
                generation_number=current_gen,
                reason=reason,
                system_health=health,
                active_issues=active_issues,
                config_backup=config_backup_path,
                metadata={
                    'kernel': await self.generation_manager._get_generation_kernel(current_gen),
                    'include_state': include_state
                }
            )
            
            # Add to tracking
            self.restore_points.append(restore_point)
            self._save_restore_points()
            
            # Calculate size (simplified)
            size_bytes = 0
            if config_backup_path and config_backup_path.exists():
                for file in config_backup_path.iterdir():
                    if file.is_file():
                        size_bytes += file.stat().st_size
            
            duration = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"✅ Created restore point: {restore_point.id} ({reason})")
            
            return BackupResult(
                success=True,
                restore_point=restore_point,
                size_bytes=size_bytes,
                duration_seconds=duration
            )
            
        except Exception as e:
            logger.error(f"Error creating restore point: {e}")
            return BackupResult(
                success=False,
                restore_point=None,
                size_bytes=0,
                duration_seconds=(datetime.now() - start_time).total_seconds(),
                error=str(e)
            )
    
    async def restore_to_point(self, restore_point_id: str) -> RestoreResult:
        """
        Restore system to a specific restore point.
        
        Args:
            restore_point_id: ID of restore point
            
        Returns:
            RestoreResult
        """
        start_time = datetime.now()
        
        try:
            # Find restore point
            restore_point = None
            for point in self.restore_points:
                if point.id == restore_point_id:
                    restore_point = point
                    break
            
            if not restore_point:
                return RestoreResult(
                    success=False,
                    restored_generation=None,
                    health_before=0,
                    health_after=0,
                    duration_seconds=0,
                    error=f"Restore point {restore_point_id} not found"
                )
            
            # Get current health
            health_before = 100.0
            if self.healing_engine:
                health_before = self.healing_engine._calculate_health_score(
                    self.healing_engine.monitor.get_state()
                )
            
            logger.info(f"🔄 Restoring to point {restore_point_id} (gen {restore_point.generation_number})")
            
            # Restore configuration if available
            if restore_point.config_backup and restore_point.config_backup.exists():
                await self.config_backup.restore_configuration(restore_point.config_backup)
            
            # Switch to the generation
            success = await self.generation_manager.switch_to_generation(
                restore_point.generation_number
            )
            
            if not success:
                return RestoreResult(
                    success=False,
                    restored_generation=None,
                    health_before=health_before,
                    health_after=health_before,
                    duration_seconds=(datetime.now() - start_time).total_seconds(),
                    error="Failed to switch generation"
                )
            
            # Wait for system to stabilize
            await asyncio.sleep(5)
            
            # Get new health
            health_after = 100.0
            if self.healing_engine:
                health_after = self.healing_engine._calculate_health_score(
                    self.healing_engine.monitor.get_state()
                )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            # Learn from restoration
            self._record_restoration(restore_point, health_before, health_after)
            
            logger.info(f"✅ Restored to generation {restore_point.generation_number}")
            logger.info(f"   Health: {health_before:.1f}% → {health_after:.1f}%")
            
            return RestoreResult(
                success=True,
                restored_generation=restore_point.generation_number,
                health_before=health_before,
                health_after=health_after,
                duration_seconds=duration
            )
            
        except Exception as e:
            logger.error(f"Error restoring to point: {e}")
            return RestoreResult(
                success=False,
                restored_generation=None,
                health_before=0,
                health_after=0,
                duration_seconds=(datetime.now() - start_time).total_seconds(),
                error=str(e)
            )
    
    async def backup_before_heal(self, issue_id: str, issue_type: str) -> Optional[str]:
        """
        Create a backup before attempting to heal an issue.
        
        Args:
            issue_id: ID of the issue being healed
            issue_type: Type of issue
            
        Returns:
            Restore point ID or None
        """
        result = await self.create_restore_point(
            reason=f"pre_heal_{issue_type}_{issue_id[:8]}"
        )
        
        if result.success and result.restore_point:
            return result.restore_point.id
        
        return None
    
    async def rollback_if_heal_failed(self, restore_point_id: str, 
                                     issue_id: str, error: str) -> bool:
        """
        Rollback if a healing attempt failed.
        
        Args:
            restore_point_id: Restore point to rollback to
            issue_id: Issue that failed to heal
            error: Error message
            
        Returns:
            True if rollback successful
        """
        logger.warning(f"⚠️ Healing failed for {issue_id}: {error}")
        logger.info(f"🔄 Attempting rollback to {restore_point_id}")
        
        result = await self.restore_to_point(restore_point_id)
        
        if result.success:
            # Record failure pattern for learning
            self.rollback_patterns.append({
                'timestamp': datetime.now(),
                'issue_id': issue_id,
                'error': error,
                'restore_point': restore_point_id,
                'health_recovered': result.health_after > result.health_before
            })
            
            logger.info(f"✅ Successfully rolled back after failed heal")
            return True
        else:
            logger.error(f"❌ Rollback failed: {result.error}")
            return False
    
    def _record_restoration(self, restore_point: RestorePoint, 
                           health_before: float, health_after: float):
        """Record restoration for learning"""
        restoration_data = {
            'timestamp': datetime.now(),
            'restore_point': restore_point.id,
            'reason': restore_point.reason,
            'health_improvement': health_after - health_before,
            'generation': restore_point.generation_number
        }
        
        # Analyze patterns
        if health_after > health_before:
            logger.info(f"📈 Restoration improved health by {health_after - health_before:.1f}%")
            self.successful_heals.append(restoration_data)
        else:
            logger.warning(f"📉 Restoration did not improve health")
    
    async def auto_cleanup(self, max_restore_points: int = 20, 
                          max_generations: int = 10):
        """
        Automatically clean up old backups and generations.
        
        Args:
            max_restore_points: Maximum restore points to keep
            max_generations: Maximum generations to keep
        """
        logger.info("🧹 Running auto-cleanup...")
        
        # Clean restore points
        if len(self.restore_points) > max_restore_points:
            # Keep most recent
            self.restore_points.sort(key=lambda x: x.timestamp)
            self.restore_points = self.restore_points[-max_restore_points:]
            self._save_restore_points()
            logger.info(f"Cleaned restore points to {max_restore_points}")
        
        # Clean configuration backups
        await self.config_backup.cleanup_old_backups(keep_count=max_restore_points)
        
        # Clean generations
        await self.generation_manager.cleanup_old_generations(keep_count=max_generations)
        
        logger.info("✅ Auto-cleanup complete")
    
    async def get_restore_point_summary(self) -> Dict[str, Any]:
        """Get summary of available restore points"""
        return {
            'total_points': len(self.restore_points),
            'oldest': self.restore_points[0].timestamp.isoformat() if self.restore_points else None,
            'newest': self.restore_points[-1].timestamp.isoformat() if self.restore_points else None,
            'reasons': list(set(p.reason for p in self.restore_points)),
            'average_health': sum(p.system_health for p in self.restore_points) / len(self.restore_points) if self.restore_points else 0,
            'rollback_count': len(self.rollback_patterns),
            'success_rate': len(self.successful_heals) / (len(self.rollback_patterns) + len(self.successful_heals)) * 100 if (self.rollback_patterns or self.successful_heals) else 0
        }


# Convenience function
def create_backup_manager(healing_engine=None) -> BackupRestoreManager:
    """Create a backup/restore manager instance"""
    return BackupRestoreManager(healing_engine)