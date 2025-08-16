"""
Permission handler for gracefully managing privileged operations.

This module provides a unified interface for executing both privileged
and unprivileged operations, with automatic fallback strategies.
"""

import asyncio
import subprocess
import os
import logging
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class PermissionHandler:
    """
    Handles permission requirements for healing operations.
    
    Provides multiple strategies:
    1. Try without privileges first
    2. Check for passwordless sudo
    3. Request sudo with user prompt
    4. Fallback to user-space alternatives
    """
    
    def __init__(self):
        self.sudo_available = self._check_sudo_available()
        self.passwordless_sudo = self._check_passwordless_sudo()
        self.privileged_operations_log = []
        self.fallback_strategies = {}
        
        # Track what operations we can do without root
        self.unprivileged_capabilities = {
            'read_config': True,
            'create_backup': True,
            'monitor_system': True,
            'detect_issues': True,
            'plan_healing': True,
            'collect_metrics': True,
            'renice_own_processes': True,
            'kill_own_processes': True,
        }
        
        # Track what definitely needs root
        self.privileged_requirements = {
            'restart_service': True,
            'change_cpu_governor': True,
            'modify_system_config': True,
            'rollback_generation': True,
            'manage_network': True,
            'clear_system_cache': True,
            'kill_system_processes': True,
        }
    
    def _check_sudo_available(self) -> bool:
        """Check if sudo command is available"""
        try:
            result = subprocess.run(
                ['which', 'sudo'],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            return False
    
    def _check_passwordless_sudo(self) -> bool:
        """Check if we can sudo without password"""
        if not self.sudo_available:
            return False
        
        try:
            result = subprocess.run(
                ['sudo', '-n', 'true'],
                capture_output=True,
                stderr=subprocess.DEVNULL
            )
            return result.returncode == 0
        except:
            return False
    
    async def execute_command(self, command: List[str], 
                             operation_type: str = "unknown",
                             require_root: bool = False) -> Dict[str, Any]:
        """
        Execute a command with appropriate privileges.
        
        Args:
            command: Command and arguments
            operation_type: Type of operation for logging
            require_root: Whether this definitely needs root
            
        Returns:
            Dict with success, output, error, and method used
        """
        
        # First, try without privileges if not explicitly required
        if not require_root:
            result = await self._try_unprivileged(command)
            if result['success']:
                return result
        
        # Check if we need and can use sudo
        if require_root or result.get('permission_denied'):
            if self.passwordless_sudo:
                return await self._try_passwordless_sudo(command, operation_type)
            elif self.sudo_available:
                return await self._try_sudo_with_prompt(command, operation_type)
            else:
                return await self._try_fallback(command, operation_type)
        
        return result
    
    async def _try_unprivileged(self, command: List[str]) -> Dict[str, Any]:
        """Try to execute command without privileges"""
        try:
            result = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            # Check for permission errors
            permission_denied = (
                result.returncode == 1 and 
                ('permission denied' in stderr.decode().lower() or
                 'operation not permitted' in stderr.decode().lower())
            )
            
            return {
                'success': result.returncode == 0,
                'output': stdout.decode(),
                'error': stderr.decode(),
                'method': 'unprivileged',
                'permission_denied': permission_denied
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'unprivileged',
                'permission_denied': 'permission' in str(e).lower()
            }
    
    async def _try_passwordless_sudo(self, command: List[str], 
                                    operation_type: str) -> Dict[str, Any]:
        """Execute with passwordless sudo"""
        try:
            logger.info(f"🔐 Executing {operation_type} with passwordless sudo")
            
            result = await asyncio.create_subprocess_exec(
                'sudo', *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            # Log privileged operation
            self._log_privileged_operation(operation_type, command, result.returncode == 0)
            
            return {
                'success': result.returncode == 0,
                'output': stdout.decode(),
                'error': stderr.decode(),
                'method': 'passwordless_sudo'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'passwordless_sudo'
            }
    
    async def _try_sudo_with_prompt(self, command: List[str], 
                                   operation_type: str) -> Dict[str, Any]:
        """Execute with sudo, may prompt for password"""
        try:
            logger.warning(f"⚠️ {operation_type} requires sudo password")
            logger.info("Please enter sudo password if prompted...")
            
            # Use subprocess.run for interactive sudo
            result = subprocess.run(
                ['sudo'] + command,
                capture_output=True,
                text=True
            )
            
            # Log privileged operation
            self._log_privileged_operation(operation_type, command, result.returncode == 0)
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr,
                'method': 'sudo_with_prompt'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'sudo_with_prompt'
            }
    
    async def _try_fallback(self, command: List[str], 
                           operation_type: str) -> Dict[str, Any]:
        """Try fallback strategies for operations"""
        
        # Check if we have a registered fallback
        if operation_type in self.fallback_strategies:
            fallback = self.fallback_strategies[operation_type]
            logger.info(f"🔄 Using fallback strategy for {operation_type}")
            return await fallback(command)
        
        # Default fallback response
        logger.warning(f"❌ Cannot execute {operation_type}: requires privileges")
        return {
            'success': False,
            'error': f"Operation {operation_type} requires root privileges",
            'method': 'no_fallback',
            'suggestion': self._get_manual_suggestion(operation_type)
        }
    
    def _log_privileged_operation(self, operation_type: str, 
                                 command: List[str], success: bool):
        """Log privileged operations for audit trail"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation_type,
            'command': ' '.join(command),
            'success': success
        }
        
        self.privileged_operations_log.append(log_entry)
        
        # Also write to file for persistence
        log_file = Path.home() / '.local' / 'share' / 'luminous-nix' / 'privileged_ops.log'
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def _get_manual_suggestion(self, operation_type: str) -> str:
        """Get manual command suggestion for user"""
        suggestions = {
            'restart_service': "Run manually: sudo systemctl restart <service>",
            'change_cpu_governor': "Run manually: sudo cpupower frequency-set -g <governor>",
            'rollback_generation': "Run manually: sudo nixos-rebuild switch --rollback",
            'clear_system_cache': "Run manually: sudo sync && sudo sysctl -w vm.drop_caches=3",
        }
        
        return suggestions.get(operation_type, 
                              f"Manual intervention required for {operation_type}")
    
    def register_fallback(self, operation_type: str, 
                         fallback_func: Callable) -> None:
        """Register a fallback strategy for an operation type"""
        self.fallback_strategies[operation_type] = fallback_func
    
    def can_execute_privileged(self) -> bool:
        """Check if we can execute privileged operations"""
        return self.passwordless_sudo or self.sudo_available
    
    def get_capabilities_summary(self) -> Dict[str, Any]:
        """Get summary of what we can and can't do"""
        return {
            'sudo_available': self.sudo_available,
            'passwordless_sudo': self.passwordless_sudo,
            'can_execute_privileged': self.can_execute_privileged(),
            'unprivileged_capabilities': list(self.unprivileged_capabilities.keys()),
            'requires_privileges': list(self.privileged_requirements.keys()),
            'fallback_strategies': list(self.fallback_strategies.keys()),
            'operations_performed': len(self.privileged_operations_log)
        }


class GracefulHealingAdapter:
    """
    Adapter that wraps healing operations with graceful permission handling.
    """
    
    def __init__(self, permission_handler: Optional[PermissionHandler] = None):
        self.permission_handler = permission_handler or PermissionHandler()
        
    async def restart_service(self, service_name: str) -> Dict[str, Any]:
        """Restart a service with graceful permission handling"""
        command = ['systemctl', 'restart', service_name]
        
        result = await self.permission_handler.execute_command(
            command,
            operation_type='restart_service',
            require_root=True
        )
        
        if not result['success'] and result.get('method') == 'no_fallback':
            # Try user service as fallback
            user_command = ['systemctl', '--user', 'restart', service_name]
            result = await self.permission_handler.execute_command(
                user_command,
                operation_type='restart_user_service',
                require_root=False
            )
        
        return result
    
    async def set_cpu_governor(self, governor: str) -> Dict[str, Any]:
        """Set CPU governor with graceful permission handling"""
        command = ['cpupower', 'frequency-set', '-g', governor]
        
        result = await self.permission_handler.execute_command(
            command,
            operation_type='change_cpu_governor',
            require_root=True
        )
        
        if not result['success']:
            logger.info(f"💡 Tip: To enable CPU governor changes without password:")
            logger.info(f"    echo '{os.getlogin()} ALL=(ALL) NOPASSWD: /usr/bin/cpupower' | sudo tee /etc/sudoers.d/luminous-cpu")
        
        return result
    
    async def clear_caches(self) -> Dict[str, Any]:
        """Clear system caches with graceful permission handling"""
        
        # Try system cache first
        command = ['sh', '-c', 'sync && sysctl -w vm.drop_caches=3']
        result = await self.permission_handler.execute_command(
            command,
            operation_type='clear_system_cache',
            require_root=True
        )
        
        if not result['success']:
            # Fallback: clear user caches only
            logger.info("Falling back to user cache clearing")
            user_cache_cleared = False
            
            # Clear user's cache directories
            cache_dirs = [
                Path.home() / '.cache',
                Path('/tmp') / f'luminous-{os.getuid()}'
            ]
            
            for cache_dir in cache_dirs:
                if cache_dir.exists():
                    try:
                        import shutil
                        shutil.rmtree(cache_dir)
                        cache_dir.mkdir(exist_ok=True)
                        user_cache_cleared = True
                    except:
                        pass
            
            return {
                'success': user_cache_cleared,
                'output': 'User caches cleared',
                'method': 'user_space_fallback'
            }
        
        return result


# Singleton instance for easy import
permission_handler = PermissionHandler()
healing_adapter = GracefulHealingAdapter(permission_handler)


# Convenience functions
async def execute_with_privileges(command: List[str], 
                                 operation_type: str = "unknown") -> Dict[str, Any]:
    """Execute a command that requires privileges"""
    return await permission_handler.execute_command(
        command, 
        operation_type=operation_type,
        require_root=True
    )


async def execute_safe(command: List[str], 
                       operation_type: str = "unknown") -> Dict[str, Any]:
    """Execute a command safely, trying unprivileged first"""
    return await permission_handler.execute_command(
        command,
        operation_type=operation_type,
        require_root=False
    )


def check_capabilities() -> Dict[str, Any]:
    """Check what capabilities are available"""
    return permission_handler.get_capabilities_summary()