"""
System monitoring and environmental awareness for Luminous Nix.

This module provides real-time system state collection and monitoring,
enabling context-aware assistance and predictive suggestions.
"""

import asyncio
import json
import logging
import os
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

import psutil
import distro

logger = logging.getLogger(__name__)


@dataclass
class CPUState:
    """CPU information and current state"""
    count: int
    count_logical: int
    percent: float
    freq_current: float
    freq_min: float
    freq_max: float
    load_avg: Tuple[float, float, float]
    temperature: Optional[float] = None
    
    @classmethod
    def collect(cls) -> "CPUState":
        """Collect current CPU state"""
        freq = psutil.cpu_freq()
        temps = psutil.sensors_temperatures() if hasattr(psutil, "sensors_temperatures") else {}
        
        # Try to get CPU temperature
        temp = None
        if temps:
            for name, entries in temps.items():
                if 'coretemp' in name.lower() or 'cpu' in name.lower():
                    if entries:
                        temp = entries[0].current
                        break
        
        return cls(
            count=psutil.cpu_count(logical=False),
            count_logical=psutil.cpu_count(logical=True),
            percent=psutil.cpu_percent(interval=0.1),
            freq_current=freq.current if freq else 0,
            freq_min=freq.min if freq else 0,
            freq_max=freq.max if freq else 0,
            load_avg=os.getloadavg(),
            temperature=temp
        )


@dataclass
class MemoryState:
    """Memory information and current state"""
    total: int
    available: int
    used: int
    percent: float
    swap_total: int
    swap_used: int
    swap_percent: float
    
    @classmethod
    def collect(cls) -> "MemoryState":
        """Collect current memory state"""
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return cls(
            total=mem.total,
            available=mem.available,
            used=mem.used,
            percent=mem.percent,
            swap_total=swap.total,
            swap_used=swap.used,
            swap_percent=swap.percent
        )


@dataclass
class DiskState:
    """Disk information for a single mount point"""
    device: str
    mount_point: str
    fstype: str
    total: int
    used: int
    free: int
    percent: float
    
    @classmethod
    def collect_all(cls) -> List["DiskState"]:
        """Collect state for all disk partitions"""
        disks = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disks.append(cls(
                    device=partition.device,
                    mount_point=partition.mountpoint,
                    fstype=partition.fstype,
                    total=usage.total,
                    used=usage.used,
                    free=usage.free,
                    percent=usage.percent
                ))
            except PermissionError:
                # Some mount points may not be accessible
                continue
        return disks


@dataclass
class NetworkInterface:
    """Network interface information"""
    name: str
    is_up: bool
    addresses: List[str]
    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int
    
    @classmethod
    def collect_all(cls) -> List["NetworkInterface"]:
        """Collect state for all network interfaces"""
        interfaces = []
        stats = psutil.net_if_stats()
        addrs = psutil.net_if_addrs()
        io_counters = psutil.net_io_counters(pernic=True)
        
        for name, stat in stats.items():
            addr_list = []
            if name in addrs:
                for addr in addrs[name]:
                    if addr.family == 2:  # AF_INET (IPv4)
                        addr_list.append(addr.address)
            
            io = io_counters.get(name)
            interfaces.append(cls(
                name=name,
                is_up=stat.isup,
                addresses=addr_list,
                bytes_sent=io.bytes_sent if io else 0,
                bytes_recv=io.bytes_recv if io else 0,
                packets_sent=io.packets_sent if io else 0,
                packets_recv=io.packets_recv if io else 0
            ))
        
        return interfaces


@dataclass
class ServiceState:
    """Systemd service state"""
    name: str
    status: str  # active, inactive, failed
    is_enabled: bool
    description: str
    
    @classmethod
    def collect_key_services(cls) -> List["ServiceState"]:
        """Collect state for key system services"""
        # Skip slow subprocess calls for now
        # In production, this should be done via D-Bus or async
        return []  # Will be populated asynchronously
    
    @classmethod
    async def collect_key_services_async(cls) -> List["ServiceState"]:
        """Collect service state asynchronously"""
        try:
            from .async_system_collector import get_service_collector
            collector = get_service_collector()
            services_data = await collector.get_key_services()
            
            services = []
            for data in services_data:
                services.append(cls(
                    name=data['name'],
                    status=data['status'],
                    is_enabled=data['is_enabled'],
                    description=data['description']
                ))
            return services
        except Exception as e:
            logger.warning(f"Failed to collect services async: {e}")
            return []


@dataclass
class NixOSState:
    """NixOS-specific system information"""
    version: str
    current_generation: int
    available_generations: List[int]
    channels: List[Dict[str, str]]
    profile_path: str
    
    @classmethod
    def collect(cls) -> Optional["NixOSState"]:
        """Collect NixOS-specific state"""
        try:
            # Use async collector if available, otherwise return defaults
            # This will be populated by async update in SystemMonitor
            return cls(
                version="NixOS 25.11",  # Will be updated async
                current_generation=0,  # Will be populated async
                available_generations=[],  # Will be populated async
                channels=[],  # Will be populated async
                profile_path='/nix/var/nix/profiles/system'
            )
            
        except Exception as e:
            logger.warning(f"Failed to collect NixOS state: {e}")
            return None
    
    @classmethod
    async def collect_async(cls) -> Optional["NixOSState"]:
        """Collect NixOS state asynchronously"""
        try:
            from .async_system_collector import get_nixos_collector
            collector = get_nixos_collector()
            data = await collector.collect_all()
            
            return cls(
                version=data['version'],
                current_generation=data['current_generation'],
                available_generations=data['available_generations'],
                channels=data['channels'],
                profile_path=data['profile_path']
            )
        except Exception as e:
            logger.warning(f"Failed to collect NixOS state async: {e}")
            return None


@dataclass
class SystemState:
    """Complete system state snapshot"""
    timestamp: datetime
    hostname: str
    os_info: Dict[str, str]
    cpu: CPUState
    memory: MemoryState
    disks: List[DiskState]
    network: List[NetworkInterface]
    services: List[ServiceState]
    nixos: Optional[NixOSState]
    uptime_seconds: float
    boot_time: datetime
    
    @classmethod
    def collect(cls) -> "SystemState":
        """Collect complete system state"""
        return cls(
            timestamp=datetime.now(),
            hostname=os.uname().nodename,
            os_info={
                'name': distro.name(),
                'version': distro.version(),
                'codename': distro.codename(),
                'platform': os.uname().sysname,
                'kernel': os.uname().release,
                'arch': os.uname().machine
            },
            cpu=CPUState.collect(),
            memory=MemoryState.collect(),
            disks=DiskState.collect_all(),
            network=NetworkInterface.collect_all(),
            services=ServiceState.collect_key_services(),
            nixos=NixOSState.collect(),
            uptime_seconds=time.time() - psutil.boot_time(),
            boot_time=datetime.fromtimestamp(psutil.boot_time())
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['boot_time'] = self.boot_time.isoformat()
        return data


class SystemMonitor:
    """Real-time system monitoring with caching and alerts"""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or Path.home() / '.cache' / 'luminous-nix' / 'monitoring'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.state_cache: Dict[str, Any] = {}
        self.last_update: Dict[str, float] = {}
        self.update_intervals = {
            'cpu': 1,         # Every second
            'memory': 5,      # Every 5 seconds
            'disk': 30,       # Every 30 seconds
            'network': 5,     # Every 5 seconds
            'services': 30,   # Every 30 seconds
            'nixos': 300,     # Every 5 minutes
            'full': 60        # Full state every minute
        }
        
        self._monitoring = False
        self._tasks: List[asyncio.Task] = []
    
    def get_state(self, category: Optional[str] = None) -> Any:
        """Get cached state for a category or full state"""
        if category:
            return self.state_cache.get(category)
        return self.state_cache
    
    def should_update(self, category: str) -> bool:
        """Check if a category needs updating based on interval"""
        last = self.last_update.get(category, 0)
        interval = self.update_intervals.get(category, 60)
        return (time.time() - last) >= interval
    
    async def update_category(self, category: str) -> Any:
        """Update a specific category of system state"""
        try:
            if category == 'cpu':
                data = CPUState.collect()
            elif category == 'memory':
                data = MemoryState.collect()
            elif category == 'disk':
                data = DiskState.collect_all()
            elif category == 'network':
                data = NetworkInterface.collect_all()
            elif category == 'services':
                # Use async collection for services
                data = await ServiceState.collect_key_services_async()
            elif category == 'nixos':
                # Use async collection for NixOS
                data = await NixOSState.collect_async()
            elif category == 'full':
                # Collect most things synchronously, but NixOS and services async
                nixos_data = await NixOSState.collect_async()
                services_data = await ServiceState.collect_key_services_async()
                
                data = SystemState(
                    timestamp=datetime.now(),
                    hostname=os.uname().nodename,
                    os_info={
                        'name': distro.name(),
                        'version': distro.version(),
                        'codename': distro.codename(),
                        'platform': os.uname().sysname,
                        'kernel': os.uname().release,
                        'arch': os.uname().machine
                    },
                    cpu=CPUState.collect(),
                    memory=MemoryState.collect(),
                    disks=DiskState.collect_all(),
                    network=NetworkInterface.collect_all(),
                    services=services_data,
                    nixos=nixos_data,
                    uptime_seconds=time.time() - psutil.boot_time(),
                    boot_time=datetime.fromtimestamp(psutil.boot_time())
                )
            else:
                return None
            
            self.state_cache[category] = data
            self.last_update[category] = time.time()
            
            # Check for alerts
            await self.check_alerts(category, data)
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to update {category}: {e}")
            return None
    
    async def check_alerts(self, category: str, data: Any) -> List[str]:
        """Check for conditions that need user attention"""
        alerts = []
        
        if category == 'memory' and isinstance(data, MemoryState):
            if data.percent > 90:
                alerts.append(f"⚠️ Memory usage critical: {data.percent:.1f}%")
            elif data.percent > 80:
                alerts.append(f"⚠️ Memory usage high: {data.percent:.1f}%")
            
            if data.swap_percent > 50:
                alerts.append(f"⚠️ High swap usage: {data.swap_percent:.1f}%")
        
        elif category == 'disk' and isinstance(data, list):
            for disk in data:
                if disk.percent > 95:
                    alerts.append(f"🚨 Disk {disk.mount_point} critical: {disk.percent:.1f}% full")
                elif disk.percent > 90:
                    alerts.append(f"⚠️ Disk {disk.mount_point} nearly full: {disk.percent:.1f}%")
        
        elif category == 'cpu' and isinstance(data, CPUState):
            if data.percent > 90:
                alerts.append(f"⚠️ CPU usage high: {data.percent:.1f}%")
            
            if data.temperature and data.temperature > 80:
                alerts.append(f"🔥 CPU temperature high: {data.temperature}°C")
        
        elif category == 'services' and isinstance(data, list):
            failed = [s for s in data if s.status == 'failed']
            if failed:
                names = ', '.join(s.name for s in failed)
                alerts.append(f"🚨 Failed services: {names}")
        
        # Log alerts
        for alert in alerts:
            logger.warning(alert)
        
        return alerts
    
    async def monitor_category(self, category: str) -> None:
        """Continuously monitor a category"""
        interval = self.update_intervals[category]
        
        while self._monitoring:
            try:
                await self.update_category(category)
            except Exception as e:
                logger.error(f"Monitor error for {category}: {e}")
            
            await asyncio.sleep(interval)
    
    async def start_monitoring(self) -> None:
        """Start all monitoring tasks"""
        if self._monitoring:
            return
        
        self._monitoring = True
        self._tasks = []
        
        # Start monitoring tasks for each category
        for category in self.update_intervals.keys():
            if category != 'full':  # Full is handled separately
                task = asyncio.create_task(self.monitor_category(category))
                self._tasks.append(task)
        
        logger.info("System monitoring started")
    
    async def stop_monitoring(self) -> None:
        """Stop all monitoring tasks"""
        self._monitoring = False
        
        # Cancel all tasks
        for task in self._tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
        
        self._tasks = []
        logger.info("System monitoring stopped")
    
    def get_quick_status(self) -> Dict[str, Any]:
        """Get a quick system status summary"""
        cpu = self.state_cache.get('cpu')
        memory = self.state_cache.get('memory')
        disks = self.state_cache.get('disk', [])
        
        return {
            'cpu_percent': cpu.percent if cpu else 0,
            'memory_percent': memory.percent if memory else 0,
            'memory_available_gb': (memory.available / (1024**3)) if memory else 0,
            'disk_usage': {
                disk.mount_point: disk.percent 
                for disk in disks
            } if disks else {},
            'load_average': cpu.load_avg if cpu else (0, 0, 0),
            'uptime_hours': (time.time() - psutil.boot_time()) / 3600
        }
    
    def save_snapshot(self, filename: Optional[str] = None) -> Path:
        """Save current state snapshot to file"""
        if not filename:
            filename = f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = self.cache_dir / filename
        state = SystemState.collect()
        
        with open(filepath, 'w') as f:
            json.dump(state.to_dict(), f, indent=2)
        
        logger.info(f"Saved system snapshot to {filepath}")
        return filepath


# Singleton instance
_monitor = None

def get_system_monitor() -> SystemMonitor:
    """Get or create the global system monitor instance"""
    global _monitor
    if _monitor is None:
        _monitor = SystemMonitor()
    return _monitor