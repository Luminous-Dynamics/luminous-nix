"""
Async system state collection to avoid subprocess timeouts.

This module provides non-blocking system state collection using
asyncio for long-running commands.
"""

import asyncio
import json
import logging
import re
from pathlib import Path
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


class AsyncNixOSCollector:
    """Collect NixOS-specific state asynchronously"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
        self.last_update = 0
    
    async def get_nixos_version(self) -> str:
        """Get NixOS version without blocking"""
        try:
            # Try fast method first - read from /etc/os-release
            if Path('/etc/os-release').exists():
                with open('/etc/os-release') as f:
                    for line in f:
                        if line.startswith('VERSION_ID='):
                            version = line.split('=')[1].strip().strip('"')
                            return f"NixOS {version}"
            
            # Fallback to cached default
            return "NixOS 25.11"
            
        except Exception as e:
            logger.debug(f"Failed to get NixOS version: {e}")
            return "NixOS 25.11"
    
    async def get_current_generation(self) -> int:
        """Get current system generation"""
        try:
            # Check symlink for current generation
            system_link = Path('/nix/var/nix/profiles/system')
            if system_link.exists() and system_link.is_symlink():
                target = str(system_link.resolve())
                # Extract generation number from path
                match = re.search(r'system-(\d+)-link', target)
                if match:
                    return int(match.group(1))
            
            # Try to get from boot loader
            grub_cfg = Path('/boot/grub/grub.cfg')
            if grub_cfg.exists():
                with open(grub_cfg) as f:
                    content = f.read()
                    # Find default generation
                    match = re.search(r'Generation (\d+)', content)
                    if match:
                        return int(match.group(1))
            
            return 0  # Unknown
            
        except Exception as e:
            logger.debug(f"Failed to get current generation: {e}")
            return 0
    
    async def get_available_generations(self) -> List[int]:
        """Get list of available generations"""
        try:
            generations = []
            profiles_dir = Path('/nix/var/nix/profiles')
            
            if profiles_dir.exists():
                for item in profiles_dir.iterdir():
                    if item.name.startswith('system-') and item.name.endswith('-link'):
                        match = re.search(r'system-(\d+)-link', item.name)
                        if match:
                            generations.append(int(match.group(1)))
            
            return sorted(generations, reverse=True)[:10]  # Return last 10
            
        except Exception as e:
            logger.debug(f"Failed to get generations: {e}")
            return []
    
    async def get_channels(self) -> List[Dict[str, str]]:
        """Get configured channels"""
        try:
            channels = []
            
            # Check user channels
            user_channels = Path.home() / '.nix-channels'
            if user_channels.exists():
                with open(user_channels) as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) >= 2:
                            channels.append({
                                'name': parts[1],
                                'url': parts[0]
                            })
            
            # Check system channels
            system_channels = Path('/root/.nix-channels')
            if system_channels.exists() and system_channels != user_channels:
                try:
                    with open(system_channels) as f:
                        for line in f:
                            parts = line.strip().split()
                            if len(parts) >= 2:
                                channels.append({
                                    'name': f"system.{parts[1]}",
                                    'url': parts[0]
                                })
                except PermissionError:
                    pass
            
            return channels if channels else [{'name': 'nixos', 'url': 'default'}]
            
        except Exception as e:
            logger.debug(f"Failed to get channels: {e}")
            return []
    
    async def collect_all(self) -> Dict[str, Any]:
        """Collect all NixOS state asynchronously"""
        # Run all collections in parallel
        results = await asyncio.gather(
            self.get_nixos_version(),
            self.get_current_generation(),
            self.get_available_generations(),
            self.get_channels(),
            return_exceptions=True
        )
        
        return {
            'version': results[0] if not isinstance(results[0], Exception) else "NixOS 25.11",
            'current_generation': results[1] if not isinstance(results[1], Exception) else 0,
            'available_generations': results[2] if not isinstance(results[2], Exception) else [],
            'channels': results[3] if not isinstance(results[3], Exception) else [],
            'profile_path': '/nix/var/nix/profiles/system'
        }


class AsyncServiceCollector:
    """Collect systemd service state asynchronously"""
    
    async def get_service_status(self, service_name: str) -> Dict[str, Any]:
        """Get status of a single service without subprocess"""
        try:
            # Try to read from systemd runtime directory
            runtime_dir = Path('/run/systemd/system')
            service_file = runtime_dir / f"{service_name}.service"
            
            if service_file.exists():
                # Service exists, check if active
                # This is a simplified check - in production use D-Bus
                return {
                    'name': service_name,
                    'status': 'active',  # Simplified
                    'is_enabled': True,
                    'description': f"{service_name} service"
                }
            
            return {
                'name': service_name,
                'status': 'inactive',
                'is_enabled': False,
                'description': f"{service_name} service"
            }
            
        except Exception as e:
            logger.debug(f"Failed to get service status for {service_name}: {e}")
            return {
                'name': service_name,
                'status': 'unknown',
                'is_enabled': False,
                'description': ''
            }
    
    async def get_key_services(self) -> List[Dict[str, Any]]:
        """Get status of key services"""
        key_services = [
            'NetworkManager',
            'sshd',
            'firewalld',
            'nix-daemon',
            'systemd-resolved'
        ]
        
        # Check services in parallel
        results = await asyncio.gather(
            *[self.get_service_status(s) for s in key_services],
            return_exceptions=True
        )
        
        services = []
        for result in results:
            if not isinstance(result, Exception):
                services.append(result)
        
        return services


class AsyncSystemPackageCollector:
    """Collect installed packages asynchronously"""
    
    async def get_installed_package_count(self) -> int:
        """Get count of installed packages without subprocess"""
        try:
            # Count packages in user profile
            user_profile = Path.home() / '.nix-profile' / 'manifest.json'
            if user_profile.exists():
                with open(user_profile) as f:
                    manifest = json.load(f)
                    return len(manifest.get('elements', []))
            
            # Estimate from profile size
            profile_path = Path.home() / '.nix-profile'
            if profile_path.exists():
                # Rough estimate: count symlinks
                count = sum(1 for _ in profile_path.iterdir() if _.is_symlink())
                return count // 10  # Rough estimate
            
            return 0
            
        except Exception as e:
            logger.debug(f"Failed to count packages: {e}")
            return 0
    
    async def get_recent_packages(self, limit: int = 5) -> List[str]:
        """Get recently installed packages"""
        try:
            packages = []
            
            # Try to read from manifest
            user_profile = Path.home() / '.nix-profile' / 'manifest.json'
            if user_profile.exists():
                with open(user_profile) as f:
                    manifest = json.load(f)
                    for element in manifest.get('elements', [])[:limit]:
                        name = element.get('attrPath', ['unknown'])
                        if isinstance(name, list):
                            name = '.'.join(name)
                        packages.append(name)
            
            return packages
            
        except Exception as e:
            logger.debug(f"Failed to get recent packages: {e}")
            return []


# Global collectors
_nixos_collector = None
_service_collector = None
_package_collector = None


def get_nixos_collector() -> AsyncNixOSCollector:
    """Get or create NixOS collector"""
    global _nixos_collector
    if _nixos_collector is None:
        _nixos_collector = AsyncNixOSCollector()
    return _nixos_collector


def get_service_collector() -> AsyncServiceCollector:
    """Get or create service collector"""
    global _service_collector
    if _service_collector is None:
        _service_collector = AsyncServiceCollector()
    return _service_collector


def get_package_collector() -> AsyncSystemPackageCollector:
    """Get or create package collector"""
    global _package_collector
    if _package_collector is None:
        _package_collector = AsyncSystemPackageCollector()
    return _package_collector


async def collect_full_system_state() -> Dict[str, Any]:
    """Collect complete system state asynchronously"""
    nixos_collector = get_nixos_collector()
    service_collector = get_service_collector()
    package_collector = get_package_collector()
    
    # Collect everything in parallel
    results = await asyncio.gather(
        nixos_collector.collect_all(),
        service_collector.get_key_services(),
        package_collector.get_installed_package_count(),
        package_collector.get_recent_packages(),
        return_exceptions=True
    )
    
    return {
        'nixos': results[0] if not isinstance(results[0], Exception) else {},
        'services': results[1] if not isinstance(results[1], Exception) else [],
        'package_count': results[2] if not isinstance(results[2], Exception) else 0,
        'recent_packages': results[3] if not isinstance(results[3], Exception) else []
    }