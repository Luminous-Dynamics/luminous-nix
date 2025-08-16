"""
File system monitoring using watchdog for real-time change detection.

This module provides comprehensive file system monitoring capabilities
to detect configuration changes, corruption, and trigger self-healing.
"""

import asyncio
import hashlib
import json
import logging as stdlib_logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Callable, Set, Any
import time

# Check if watchdog is available
try:
    from watchdog.observers import Observer
    from watchdog.events import (
        FileSystemEventHandler,
        FileModifiedEvent,
        FileCreatedEvent,
        FileDeletedEvent,
        FileMovedEvent,
        DirModifiedEvent,
        DirCreatedEvent,
        DirDeletedEvent,
        DirMovedEvent
    )
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    Observer = None
    FileSystemEventHandler = object

logger = stdlib_logging.getLogger(__name__)


class FileEventType(Enum):
    """Types of file system events we track."""
    CREATED = "created"
    MODIFIED = "modified"
    DELETED = "deleted"
    MOVED = "moved"
    CORRUPTED = "corrupted"
    PERMISSION_CHANGED = "permission_changed"


@dataclass
class FileEvent:
    """Represents a file system event."""
    path: Path
    event_type: FileEventType
    timestamp: datetime
    size: Optional[int] = None
    checksum: Optional[str] = None
    old_path: Optional[Path] = None  # For move events
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MonitoredPath:
    """Configuration for a monitored path."""
    path: Path
    recursive: bool = True
    patterns: List[str] = field(default_factory=list)  # File patterns to watch
    ignore_patterns: List[str] = field(default_factory=list)  # Patterns to ignore
    events: Set[FileEventType] = field(default_factory=lambda: {FileEventType.MODIFIED, FileEventType.DELETED})
    callback: Optional[Callable] = None
    checksum_validation: bool = False
    debounce_seconds: float = 1.0  # Avoid duplicate events


class FileSystemMonitor:
    """
    Monitors file system changes using watchdog.
    
    Provides real-time detection of:
    - Configuration file changes
    - File corruption
    - Permission changes
    - Unexpected deletions
    """
    
    def __init__(self, healing_callback: Optional[Callable] = None):
        """
        Initialize the file system monitor.
        
        Args:
            healing_callback: Function to call when issues are detected
        """
        if not WATCHDOG_AVAILABLE:
            logger.warning("watchdog not available - file monitoring disabled")
            self.observer = None
            return
            
        self.observer = Observer()
        self.healing_callback = healing_callback
        self.monitored_paths: Dict[str, MonitoredPath] = {}
        self.event_handlers: Dict[str, FileSystemEventHandler] = {}
        self.event_cache: Dict[str, float] = {}  # For debouncing
        self.checksums: Dict[str, str] = {}  # Path -> checksum cache
        self.running = False
        
        # Statistics
        self.stats = {
            'events_detected': 0,
            'issues_found': 0,
            'heals_triggered': 0,
            'files_monitored': 0
        }
        
        # Critical NixOS paths to monitor
        self.critical_paths = [
            Path('/etc/nixos/configuration.nix'),
            Path('/etc/nixos/hardware-configuration.nix'),
            Path.home() / '.config/nixpkgs/home.nix',
            Path.home() / '.config/luminous-nix'
        ]
        
        logger.info("✅ File system monitor initialized")
    
    def is_available(self) -> bool:
        """Check if file monitoring is available."""
        return self.observer is not None
    
    def add_path(self, 
                 path: Path,
                 recursive: bool = True,
                 patterns: Optional[List[str]] = None,
                 ignore_patterns: Optional[List[str]] = None,
                 events: Optional[Set[FileEventType]] = None,
                 callback: Optional[Callable] = None,
                 checksum_validation: bool = False) -> bool:
        """
        Add a path to monitor.
        
        Args:
            path: Path to monitor
            recursive: Monitor subdirectories
            patterns: File patterns to watch (e.g., ['*.nix', '*.conf'])
            ignore_patterns: Patterns to ignore (e.g., ['*.swp', '*.tmp'])
            events: Event types to monitor
            callback: Custom callback for this path
            checksum_validation: Enable checksum validation for corruption detection
            
        Returns:
            True if path was added successfully
        """
        if not self.is_available():
            return False
            
        if not path.exists():
            logger.warning(f"Path does not exist: {path}")
            return False
            
        path_str = str(path)
        
        # Create monitored path configuration
        monitored = MonitoredPath(
            path=path,
            recursive=recursive,
            patterns=patterns or [],
            ignore_patterns=ignore_patterns or ['*.swp', '*.tmp', '*.lock', '.git'],
            events=events or {FileEventType.MODIFIED, FileEventType.DELETED},
            callback=callback,
            checksum_validation=checksum_validation
        )
        
        self.monitored_paths[path_str] = monitored
        
        # Create event handler
        handler = self._create_handler(monitored)
        self.event_handlers[path_str] = handler
        
        # Schedule with observer
        self.observer.schedule(handler, path_str, recursive=recursive)
        
        # Calculate initial checksums if needed
        if checksum_validation:
            self._update_checksums(path, recursive)
        
        logger.info(f"Added monitoring for: {path} (recursive={recursive})")
        self.stats['files_monitored'] += 1
        
        return True
    
    def _create_handler(self, monitored: MonitoredPath) -> FileSystemEventHandler:
        """Create an event handler for a monitored path."""
        monitor = self  # Capture self for closure
        
        class CustomHandler(FileSystemEventHandler):
            def on_any_event(self, event):
                # Debounce events
                event_key = f"{event.src_path}:{event.event_type}"
                now = time.time()
                
                if event_key in monitor.event_cache:
                    if now - monitor.event_cache[event_key] < monitored.debounce_seconds:
                        return
                
                monitor.event_cache[event_key] = now
                
                # Check patterns
                path = Path(event.src_path)
                
                # Check ignore patterns
                for pattern in monitored.ignore_patterns:
                    if path.match(pattern):
                        return
                
                # Check include patterns (if specified)
                if monitored.patterns:
                    matches = any(path.match(p) for p in monitored.patterns)
                    if not matches:
                        return
                
                # Process event
                monitor._process_event(event, monitored)
        
        return CustomHandler()
    
    def _process_event(self, event, monitored: MonitoredPath):
        """Process a file system event."""
        self.stats['events_detected'] += 1
        
        # Convert to our event type
        file_event = self._convert_event(event)
        
        if file_event.event_type not in monitored.events:
            return
        
        logger.info(f"File event: {file_event.event_type.value} - {file_event.path}")
        
        # Check for corruption if using checksums
        if monitored.checksum_validation and file_event.event_type == FileEventType.MODIFIED:
            if self._check_corruption(file_event.path):
                file_event.event_type = FileEventType.CORRUPTED
                self.stats['issues_found'] += 1
        
        # Call custom callback if provided
        if monitored.callback:
            try:
                monitored.callback(file_event)
            except Exception as e:
                logger.error(f"Error in file event callback: {e}")
        
        # Check if this needs healing
        if self._needs_healing(file_event):
            self._trigger_healing(file_event)
    
    def _convert_event(self, event) -> FileEvent:
        """Convert watchdog event to our FileEvent."""
        path = Path(event.src_path)
        
        # Determine event type
        if isinstance(event, (FileCreatedEvent, DirCreatedEvent)):
            event_type = FileEventType.CREATED
        elif isinstance(event, (FileModifiedEvent, DirModifiedEvent)):
            event_type = FileEventType.MODIFIED
        elif isinstance(event, (FileDeletedEvent, DirDeletedEvent)):
            event_type = FileEventType.DELETED
        elif isinstance(event, (FileMovedEvent, DirMovedEvent)):
            event_type = FileEventType.MOVED
        else:
            event_type = FileEventType.MODIFIED
        
        # Get file size if it exists
        size = None
        if path.exists() and path.is_file():
            try:
                size = path.stat().st_size
            except:
                pass
        
        # Create FileEvent
        file_event = FileEvent(
            path=path,
            event_type=event_type,
            timestamp=datetime.now(),
            size=size
        )
        
        # Add old path for move events
        if isinstance(event, (FileMovedEvent, DirMovedEvent)):
            file_event.old_path = Path(event.dest_path)
        
        return file_event
    
    def _check_corruption(self, path: Path) -> bool:
        """Check if a file has been corrupted by comparing checksums."""
        if not path.exists() or not path.is_file():
            return False
            
        path_str = str(path)
        
        # Calculate current checksum
        try:
            current_checksum = self._calculate_checksum(path)
        except Exception as e:
            logger.error(f"Failed to calculate checksum for {path}: {e}")
            return True  # Assume corrupted if we can't read it
        
        # Compare with cached checksum
        if path_str in self.checksums:
            if self.checksums[path_str] != current_checksum:
                logger.warning(f"Checksum mismatch for {path} - possible corruption!")
                return True
        
        # Update cache
        self.checksums[path_str] = current_checksum
        return False
    
    def _calculate_checksum(self, path: Path) -> str:
        """Calculate SHA256 checksum of a file."""
        sha256 = hashlib.sha256()
        
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        
        return sha256.hexdigest()
    
    def _update_checksums(self, path: Path, recursive: bool):
        """Update checksums for all files in a path."""
        if path.is_file():
            try:
                self.checksums[str(path)] = self._calculate_checksum(path)
            except Exception as e:
                logger.error(f"Failed to calculate checksum for {path}: {e}")
        elif path.is_dir() and recursive:
            for file_path in path.rglob('*'):
                if file_path.is_file():
                    try:
                        self.checksums[str(file_path)] = self._calculate_checksum(file_path)
                    except Exception as e:
                        logger.error(f"Failed to calculate checksum for {file_path}: {e}")
    
    def _needs_healing(self, event: FileEvent) -> bool:
        """Determine if an event requires healing."""
        # Critical file deleted
        if event.event_type == FileEventType.DELETED:
            for critical_path in self.critical_paths:
                if event.path == critical_path or str(critical_path) in str(event.path):
                    return True
        
        # File corrupted
        if event.event_type == FileEventType.CORRUPTED:
            return True
        
        # Configuration file modified unexpectedly
        if event.event_type == FileEventType.MODIFIED:
            if event.path.suffix in ['.nix', '.conf', '.yaml', '.json']:
                # Could add more logic here to detect malicious changes
                pass
        
        return False
    
    def _trigger_healing(self, event: FileEvent):
        """Trigger healing for a file event."""
        self.stats['heals_triggered'] += 1
        
        if self.healing_callback:
            # Create issue for healing engine
            issue_data = {
                'type': 'file_system_issue',
                'severity': 'high' if event.event_type in [FileEventType.DELETED, FileEventType.CORRUPTED] else 'medium',
                'description': f"File {event.event_type.value}: {event.path}",
                'file_path': str(event.path),
                'event_type': event.event_type.value,
                'timestamp': event.timestamp.isoformat()
            }
            
            try:
                self.healing_callback(issue_data)
                logger.info(f"Triggered healing for: {event.path}")
            except Exception as e:
                logger.error(f"Failed to trigger healing: {e}")
    
    def monitor_critical_paths(self):
        """Start monitoring critical NixOS paths."""
        for path in self.critical_paths:
            if path.exists():
                self.add_path(
                    path=path,
                    recursive=False,
                    events={FileEventType.MODIFIED, FileEventType.DELETED, FileEventType.CORRUPTED},
                    checksum_validation=True
                )
    
    def add_hot_reload(self, config_path: Path, reload_callback: Callable):
        """
        Add hot-reload capability for a configuration file.
        
        Args:
            config_path: Path to configuration file
            reload_callback: Function to call when config changes
        """
        def on_config_change(event: FileEvent):
            if event.event_type == FileEventType.MODIFIED:
                logger.info(f"Configuration changed: {config_path}")
                try:
                    reload_callback(config_path)
                    logger.info(f"Successfully reloaded configuration")
                except Exception as e:
                    logger.error(f"Failed to reload configuration: {e}")
        
        self.add_path(
            path=config_path,
            recursive=False,
            events={FileEventType.MODIFIED},
            callback=on_config_change
        )
    
    def start(self):
        """Start the file system monitor."""
        if not self.is_available():
            return
            
        if self.running:
            logger.warning("File monitor already running")
            return
        
        self.observer.start()
        self.running = True
        logger.info("🔍 File system monitor started")
        
        # Monitor critical paths by default
        self.monitor_critical_paths()
    
    def stop(self):
        """Stop the file system monitor."""
        if not self.is_available() or not self.running:
            return
        
        self.observer.stop()
        self.observer.join(timeout=5)
        self.running = False
        logger.info("🔍 File system monitor stopped")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get monitoring statistics."""
        return {
            **self.stats,
            'paths_monitored': len(self.monitored_paths),
            'is_running': self.running,
            'checksums_tracked': len(self.checksums)
        }
    
    def get_monitored_paths(self) -> List[str]:
        """Get list of monitored paths."""
        return list(self.monitored_paths.keys())


# Singleton instance
_file_monitor = None

def get_file_monitor(healing_callback: Optional[Callable] = None) -> FileSystemMonitor:
    """Get the singleton file monitor instance."""
    global _file_monitor
    if _file_monitor is None:
        _file_monitor = FileSystemMonitor(healing_callback)
    return _file_monitor


async def test_file_monitoring():
    """Test file monitoring capabilities."""
    
    # Create test directory
    test_dir = Path('/tmp/luminous-test-monitor')
    test_dir.mkdir(exist_ok=True)
    
    # Track events
    events = []
    
    def event_callback(event: FileEvent):
        events.append(event)
        print(f"Event: {event.event_type.value} - {event.path}")
    
    # Create monitor
    monitor = FileSystemMonitor()
    
    if not monitor.is_available():
        print("❌ Watchdog not available")
        return
    
    # Add monitoring
    monitor.add_path(
        path=test_dir,
        recursive=True,
        patterns=['*.txt', '*.conf'],
        callback=event_callback,
        checksum_validation=True
    )
    
    # Start monitoring
    monitor.start()
    
    print("✅ Monitoring started")
    print(f"Watching: {test_dir}")
    
    # Create some events
    await asyncio.sleep(1)
    
    # Create file
    test_file = test_dir / 'test.txt'
    test_file.write_text('Hello, world!')
    print(f"Created: {test_file}")
    
    await asyncio.sleep(2)
    
    # Modify file
    test_file.write_text('Modified content')
    print(f"Modified: {test_file}")
    
    await asyncio.sleep(2)
    
    # Delete file
    test_file.unlink()
    print(f"Deleted: {test_file}")
    
    await asyncio.sleep(2)
    
    # Stop monitoring
    monitor.stop()
    
    # Print statistics
    print("\n📊 Statistics:")
    stats = monitor.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print(f"\n📝 Events captured: {len(events)}")
    for event in events:
        print(f"  - {event.event_type.value}: {event.path.name}")
    
    # Cleanup
    test_dir.rmdir()


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_file_monitoring())