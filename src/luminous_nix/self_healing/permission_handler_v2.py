#!/usr/bin/env python3
"""
Simplified two-tier permission handler for NixOS.

This module provides a clean two-mode approach:
1. Production: SystemD service (default)
2. Development: Direct execution with sudo (explicit opt-in)

Since Luminous Nix is NixOS-specific, we can assume systemd is always available.
"""

import asyncio
import os
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ExecutionMode(Enum):
    """Execution modes for the healing system"""
    SERVICE = "service"      # Production mode using SystemD service
    DEVELOPMENT = "dev"       # Development mode with direct execution
    

@dataclass
class ExecutionResult:
    """Result from executing a healing action"""
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    mode: Optional[ExecutionMode] = None
    suggestion: Optional[str] = None
    duration_ms: int = 0


class NixOSPermissionHandler:
    """
    Simplified permission handler optimized for NixOS.
    
    Two modes:
    1. Service mode (default): Uses systemd service for all privileged operations
    2. Development mode: Direct execution with sudo for testing/debugging
    """
    
    def __init__(self):
        self.mode = self._determine_mode()
        self.executor = self._create_executor()
        
        # Log mode on initialization
        if self.mode == ExecutionMode.DEVELOPMENT:
            logger.warning(
                "🔧 Running in DEVELOPMENT mode - not for production use!\n"
                "   For production, enable the systemd service:\n"
                "   services.luminous-healing.enable = true;"
            )
        else:
            logger.info("✅ Running in production mode with systemd service")
    
    def _determine_mode(self) -> ExecutionMode:
        """Determine which mode to run in"""
        # Check for explicit dev mode
        if os.environ.get('LUMINOUS_DEV_MODE'):
            return ExecutionMode.DEVELOPMENT
        
        # Check for explicit service disable
        if os.environ.get('LUMINOUS_NO_SERVICE'):
            return ExecutionMode.DEVELOPMENT
        
        # Default to service mode (production)
        return ExecutionMode.SERVICE
    
    def _create_executor(self):
        """Create the appropriate executor based on mode"""
        if self.mode == ExecutionMode.SERVICE:
            return ServiceExecutor()
        else:
            return DevelopmentExecutor()
    
    async def execute(self, action: str, parameters: Dict[str, Any]) -> ExecutionResult:
        """
        Execute a healing action using the appropriate mode.
        
        Args:
            action: The healing action to perform
            parameters: Parameters for the action
            
        Returns:
            ExecutionResult with success status and details
        """
        try:
            result = await self.executor.execute(action, parameters)
            result.mode = self.mode
            return result
        except Exception as e:
            logger.error(f"Execution failed: {e}")
            return ExecutionResult(
                success=False,
                error=str(e),
                mode=self.mode,
                suggestion=self._get_error_suggestion(str(e))
            )
    
    def _get_error_suggestion(self, error: str) -> str:
        """Provide helpful suggestions for common errors"""
        if "service not running" in error.lower():
            return (
                "Enable the healing service in /etc/nixos/configuration.nix:\n"
                "  services.luminous-healing.enable = true;\n"
                "  Then run: sudo nixos-rebuild switch"
            )
        elif "permission denied" in error.lower():
            return (
                "For development, run with sudo or set LUMINOUS_DEV_MODE=1"
            )
        elif "socket not found" in error.lower():
            return (
                "Service socket not found. Check if service is running:\n"
                "  systemctl status luminous-healing"
            )
        return "Check logs for details: journalctl -u luminous-healing"
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the permission system"""
        return {
            'mode': self.mode.value,
            'mode_description': self._get_mode_description(),
            'executor_type': type(self.executor).__name__,
            'is_production': self.mode == ExecutionMode.SERVICE,
            'capabilities': self.executor.get_capabilities()
        }
    
    def _get_mode_description(self) -> str:
        """Get a human-readable description of the current mode"""
        if self.mode == ExecutionMode.SERVICE:
            return "Production mode using systemd service"
        else:
            return "Development mode with direct execution"


class ServiceExecutor:
    """
    Production executor that uses the systemd service.
    This is the default and recommended mode for NixOS.
    """
    
    def __init__(self):
        self.socket_path = Path("/run/luminous-healing.sock")
        self._client = None
    
    async def execute(self, action: str, parameters: Dict[str, Any]) -> ExecutionResult:
        """Execute action through systemd service"""
        # Lazy import to avoid circular dependencies
        from .privileged_client import PrivilegedHealingClient
        
        if not self._client:
            self._client = PrivilegedHealingClient()
        
        # Check if service is available
        if not await self._client.is_available():
            raise RuntimeError(
                "Luminous healing service not running.\n"
                "This is required for production mode."
            )
        
        # Execute through service
        result = await self._client.execute_privileged_action(action, parameters)
        
        return ExecutionResult(
            success=result.get('success', False),
            output=result.get('output'),
            error=result.get('error'),
            duration_ms=result.get('duration_ms', 0)
        )
    
    def get_capabilities(self) -> List[str]:
        """List capabilities available through the service"""
        return [
            "restart_service",
            "set_cpu_governor", 
            "clear_system_cache",
            "rollback_generation",
            "kill_process",
            "adjust_swappiness",
            "restart_network",
            "clean_nix_store"
        ]


class DevelopmentExecutor:
    """
    Development executor for testing and debugging.
    Uses sudo when available, provides clear feedback when not.
    
    ⚠️ NOT FOR PRODUCTION USE
    """
    
    def __init__(self):
        self.has_sudo = self._check_sudo()
        self.is_root = os.geteuid() == 0
        
        if not self.has_sudo and not self.is_root:
            logger.warning(
                "⚠️ Running without sudo or root privileges.\n"
                "   Some operations will fail or provide instructions only."
            )
    
    def _check_sudo(self) -> bool:
        """Check if sudo is available"""
        try:
            result = subprocess.run(
                ['sudo', '-n', 'true'],
                capture_output=True,
                timeout=1
            )
            return result.returncode == 0
        except:
            return False
    
    async def execute(self, action: str, parameters: Dict[str, Any]) -> ExecutionResult:
        """Execute action directly in development mode"""
        
        # Map actions to commands
        command_map = {
            'restart_service': self._restart_service,
            'set_cpu_governor': self._set_cpu_governor,
            'clear_system_cache': self._clear_cache,
            'rollback_generation': self._rollback_generation,
            'kill_process': self._kill_process,
            'adjust_swappiness': self._adjust_swappiness,
            'restart_network': self._restart_network,
            'clean_nix_store': self._clean_nix_store
        }
        
        handler = command_map.get(action)
        if not handler:
            return ExecutionResult(
                success=False,
                error=f"Unknown action: {action}"
            )
        
        return await handler(parameters)
    
    async def _restart_service(self, params: Dict[str, Any]) -> ExecutionResult:
        """Restart a systemd service"""
        service = params.get('service')
        if not service:
            return ExecutionResult(success=False, error="No service specified")
        
        if self.is_root or self.has_sudo:
            cmd = ['systemctl', 'restart', service]
            if not self.is_root:
                cmd = ['sudo'] + cmd
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                return ExecutionResult(
                    success=result.returncode == 0,
                    output=result.stdout,
                    error=result.stderr if result.returncode != 0 else None
                )
            except subprocess.TimeoutExpired:
                return ExecutionResult(success=False, error="Service restart timeout")
        else:
            return ExecutionResult(
                success=False,
                error="Insufficient privileges",
                suggestion=f"Run manually: sudo systemctl restart {service}"
            )
    
    async def _set_cpu_governor(self, params: Dict[str, Any]) -> ExecutionResult:
        """Set CPU frequency governor"""
        governor = params.get('governor', 'ondemand')
        
        if self.is_root or self.has_sudo:
            cmd = ['cpupower', 'frequency-set', '-g', governor]
            if not self.is_root:
                cmd = ['sudo'] + cmd
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                return ExecutionResult(
                    success=result.returncode == 0,
                    output=f"CPU governor set to {governor}",
                    error=result.stderr if result.returncode != 0 else None
                )
            except FileNotFoundError:
                # Try sysfs method
                return await self._set_governor_sysfs(governor)
        else:
            return ExecutionResult(
                success=False,
                error="Insufficient privileges",
                suggestion=f"Run manually: sudo cpupower frequency-set -g {governor}"
            )
    
    async def _set_governor_sysfs(self, governor: str) -> ExecutionResult:
        """Set governor via sysfs (fallback)"""
        try:
            cpu_count = os.cpu_count() or 1
            for cpu in range(cpu_count):
                gov_file = f'/sys/devices/system/cpu/cpu{cpu}/cpufreq/scaling_governor'
                
                if self.is_root:
                    with open(gov_file, 'w') as f:
                        f.write(governor)
                elif self.has_sudo:
                    subprocess.run(
                        ['sudo', 'sh', '-c', f'echo {governor} > {gov_file}'],
                        check=True
                    )
                else:
                    raise PermissionError("Need root or sudo")
            
            return ExecutionResult(
                success=True,
                output=f"Governor set to {governor} via sysfs"
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                error=str(e)
            )
    
    async def _clear_cache(self, params: Dict[str, Any]) -> ExecutionResult:
        """Clear system caches"""
        if self.is_root:
            try:
                subprocess.run(['sync'], check=True)
                with open('/proc/sys/vm/drop_caches', 'w') as f:
                    f.write('3')
                return ExecutionResult(success=True, output="System caches cleared")
            except Exception as e:
                return ExecutionResult(success=False, error=str(e))
        elif self.has_sudo:
            try:
                subprocess.run(['sudo', 'sync'], check=True)
                subprocess.run(
                    ['sudo', 'sh', '-c', 'echo 3 > /proc/sys/vm/drop_caches'],
                    check=True
                )
                return ExecutionResult(success=True, output="System caches cleared")
            except Exception as e:
                return ExecutionResult(success=False, error=str(e))
        else:
            # Clear user caches only
            import shutil
            cleared = []
            
            cache_dir = Path.home() / '.cache'
            if cache_dir.exists():
                try:
                    shutil.rmtree(cache_dir)
                    cache_dir.mkdir()
                    cleared.append("~/.cache")
                except:
                    pass
            
            return ExecutionResult(
                success=True,
                output=f"Cleared user caches: {', '.join(cleared)}",
                suggestion="For system cache: sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches'"
            )
    
    async def _rollback_generation(self, params: Dict[str, Any]) -> ExecutionResult:
        """Rollback NixOS generation"""
        if self.is_root or self.has_sudo:
            cmd = ['nixos-rebuild', 'switch', '--rollback']
            if not self.is_root:
                cmd = ['sudo'] + cmd
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                return ExecutionResult(
                    success=result.returncode == 0,
                    output="NixOS generation rolled back",
                    error=result.stderr if result.returncode != 0 else None
                )
            except subprocess.TimeoutExpired:
                return ExecutionResult(success=False, error="Rollback timeout")
        else:
            return ExecutionResult(
                success=False,
                error="Insufficient privileges",
                suggestion="Run manually: sudo nixos-rebuild switch --rollback"
            )
    
    async def _kill_process(self, params: Dict[str, Any]) -> ExecutionResult:
        """Kill a process"""
        pid = params.get('pid')
        signal = params.get('signal', 'TERM')
        
        if not pid:
            return ExecutionResult(success=False, error="No PID specified")
        
        try:
            import signal as sig
            sig_num = getattr(sig, f'SIG{signal}', sig.SIGTERM)
            os.kill(int(pid), sig_num)
            return ExecutionResult(success=True, output=f"Process {pid} killed with {signal}")
        except ProcessLookupError:
            return ExecutionResult(success=False, error=f"Process {pid} not found")
        except PermissionError:
            if self.has_sudo:
                try:
                    subprocess.run(['sudo', 'kill', f'-{signal}', str(pid)], check=True)
                    return ExecutionResult(success=True, output=f"Process {pid} killed with {signal}")
                except:
                    pass
            return ExecutionResult(
                success=False,
                error=f"Permission denied to kill {pid}",
                suggestion=f"Run manually: sudo kill -{signal} {pid}"
            )
    
    async def _adjust_swappiness(self, params: Dict[str, Any]) -> ExecutionResult:
        """Adjust system swappiness"""
        value = params.get('value', 60)
        
        if self.is_root:
            try:
                with open('/proc/sys/vm/swappiness', 'w') as f:
                    f.write(str(value))
                return ExecutionResult(success=True, output=f"Swappiness set to {value}")
            except Exception as e:
                return ExecutionResult(success=False, error=str(e))
        elif self.has_sudo:
            try:
                subprocess.run(
                    ['sudo', 'sh', '-c', f'echo {value} > /proc/sys/vm/swappiness'],
                    check=True
                )
                return ExecutionResult(success=True, output=f"Swappiness set to {value}")
            except Exception as e:
                return ExecutionResult(success=False, error=str(e))
        else:
            return ExecutionResult(
                success=False,
                error="Insufficient privileges",
                suggestion=f"Run manually: sudo sysctl vm.swappiness={value}"
            )
    
    async def _restart_network(self, params: Dict[str, Any]) -> ExecutionResult:
        """Restart network service"""
        if self.is_root or self.has_sudo:
            cmd = ['systemctl', 'restart', 'NetworkManager']
            if not self.is_root:
                cmd = ['sudo'] + cmd
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                return ExecutionResult(
                    success=result.returncode == 0,
                    output="Network service restarted",
                    error=result.stderr if result.returncode != 0 else None
                )
            except Exception as e:
                return ExecutionResult(success=False, error=str(e))
        else:
            return ExecutionResult(
                success=False,
                error="Insufficient privileges",
                suggestion="Run manually: sudo systemctl restart NetworkManager"
            )
    
    async def _clean_nix_store(self, params: Dict[str, Any]) -> ExecutionResult:
        """Clean Nix store garbage"""
        if self.is_root or self.has_sudo:
            cmd = ['nix-collect-garbage', '-d']
            if not self.is_root:
                cmd = ['sudo'] + cmd
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
                return ExecutionResult(
                    success=result.returncode == 0,
                    output=result.stdout,
                    error=result.stderr if result.returncode != 0 else None
                )
            except subprocess.TimeoutExpired:
                return ExecutionResult(success=False, error="Garbage collection timeout")
        else:
            # User-level garbage collection
            try:
                result = subprocess.run(
                    ['nix-collect-garbage'],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                return ExecutionResult(
                    success=result.returncode == 0,
                    output="User-level garbage collection completed",
                    suggestion="For system-wide: sudo nix-collect-garbage -d"
                )
            except Exception as e:
                return ExecutionResult(success=False, error=str(e))
    
    def get_capabilities(self) -> List[str]:
        """List capabilities available in dev mode"""
        if self.is_root:
            return [
                "restart_service",
                "set_cpu_governor",
                "clear_system_cache",
                "rollback_generation",
                "kill_process",
                "adjust_swappiness",
                "restart_network",
                "clean_nix_store"
            ]
        elif self.has_sudo:
            return [
                "restart_service (with prompt)",
                "set_cpu_governor (with prompt)",
                "clear_system_cache (with prompt)",
                "rollback_generation (with prompt)",
                "kill_process (limited)",
                "adjust_swappiness (with prompt)",
                "restart_network (with prompt)",
                "clean_nix_store (with prompt)"
            ]
        else:
            return [
                "kill_process (own processes)",
                "clear_user_cache",
                "clean_user_nix_store",
                "provide_manual_commands"
            ]


# Convenience functions
async def execute_healing_action(action: str, parameters: Dict[str, Any] = None) -> ExecutionResult:
    """
    Execute a healing action using the appropriate permission handler.
    
    This is the main entry point for the simplified permission system.
    """
    handler = NixOSPermissionHandler()
    return await handler.execute(action, parameters or {})


def get_permission_status() -> Dict[str, Any]:
    """Get the current status of the permission system"""
    handler = NixOSPermissionHandler()
    return handler.get_status()


# For backward compatibility
SimplifiedHealingHandler = NixOSPermissionHandler