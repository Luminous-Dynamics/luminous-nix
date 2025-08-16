"""
Client for communicating with the privileged healing executor service.

This module provides a secure client that connects to the SystemD service
through a Unix socket to request privileged healing operations.
"""

import asyncio
import json
import hashlib
import hmac
import logging
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import uuid

logger = logging.getLogger(__name__)


@dataclass
class HealingRequest:
    """A request to execute a healing action"""
    id: str
    action: str
    parameters: Dict[str, Any]
    timestamp: str
    signature: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass 
class HealingResponse:
    """Response from executing a healing action"""
    request_id: str
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    duration_ms: int = 0
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HealingResponse':
        return cls(**data)


class PrivilegedHealingClient:
    """
    Client for requesting privileged healing operations from the SystemD service.
    """
    
    def __init__(self, socket_path: str = "/run/luminous-healing.sock",
                 secret_key: Optional[str] = None):
        self.socket_path = Path(socket_path)
        self.secret_key = secret_key or os.environ.get('LUMINOUS_HEALING_SECRET', 'default-dev-key')
        self.connected = False
        
    def _sign_request(self, request: HealingRequest) -> str:
        """Sign a request for authentication"""
        message = f"{request.id}:{request.action}:{request.timestamp}"
        signature = hmac.new(
            self.secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    async def is_available(self) -> bool:
        """Check if the privileged service is available"""
        return self.socket_path.exists() and os.access(self.socket_path, os.W_OK)
    
    async def execute_privileged_action(self, action: str, 
                                       parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a privileged action through the SystemD service.
        
        Args:
            action: The healing action to execute
            parameters: Parameters for the action
            
        Returns:
            Dict with success, output, error, and metadata
        """
        
        # Check if service is available
        if not await self.is_available():
            logger.warning(f"Privileged service not available at {self.socket_path}")
            return {
                'success': False,
                'error': 'Privileged service not available',
                'fallback_required': True
            }
        
        # Create request
        request = HealingRequest(
            id=str(uuid.uuid4()),
            action=action,
            parameters=parameters,
            timestamp=datetime.now().isoformat()
        )
        
        # Sign the request
        request.signature = self._sign_request(request)
        
        try:
            # Connect to socket
            reader, writer = await asyncio.open_unix_connection(str(self.socket_path))
            
            # Send request
            request_data = json.dumps(request.to_dict()).encode()
            writer.write(request_data)
            await writer.drain()
            
            # Read response (max 64KB)
            response_data = await reader.read(65536)
            
            # Close connection
            writer.close()
            await writer.wait_closed()
            
            # Parse response
            response_dict = json.loads(response_data.decode())
            response = HealingResponse.from_dict(response_dict)
            
            # Convert to standard format
            result = {
                'success': response.success,
                'output': response.output,
                'error': response.error,
                'duration_ms': response.duration_ms,
                'method': 'privileged_service',
                'request_id': response.request_id
            }
            
            if response.success:
                logger.info(f"✅ Privileged action {action} succeeded via service")
            else:
                logger.warning(f"⚠️ Privileged action {action} failed: {response.error}")
            
            return result
            
        except FileNotFoundError:
            logger.error(f"Socket {self.socket_path} not found")
            return {
                'success': False,
                'error': 'Service socket not found',
                'fallback_required': True
            }
        except PermissionError:
            logger.error(f"Permission denied accessing {self.socket_path}")
            return {
                'success': False,
                'error': 'Permission denied to access service',
                'fallback_required': True
            }
        except json.JSONDecodeError as e:
            logger.error(f"Invalid response from service: {e}")
            return {
                'success': False,
                'error': 'Invalid response from service',
                'fallback_required': True
            }
        except Exception as e:
            logger.error(f"Error communicating with privileged service: {e}")
            return {
                'success': False,
                'error': str(e),
                'fallback_required': True
            }
    
    async def restart_service(self, service_name: str) -> Dict[str, Any]:
        """Restart a system service"""
        return await self.execute_privileged_action(
            'restart_service',
            {'service': service_name}
        )
    
    async def set_cpu_governor(self, governor: str) -> Dict[str, Any]:
        """Set CPU frequency governor"""
        return await self.execute_privileged_action(
            'set_cpu_governor',
            {'governor': governor}
        )
    
    async def clear_system_cache(self) -> Dict[str, Any]:
        """Clear system caches"""
        return await self.execute_privileged_action(
            'clear_system_cache',
            {}
        )
    
    async def rollback_generation(self) -> Dict[str, Any]:
        """Rollback NixOS generation"""
        return await self.execute_privileged_action(
            'rollback_generation',
            {}
        )
    
    async def kill_process(self, pid: int, signal: str = 'TERM') -> Dict[str, Any]:
        """Kill a process"""
        return await self.execute_privileged_action(
            'kill_process',
            {'pid': pid, 'signal': signal}
        )
    
    async def adjust_swappiness(self, value: int) -> Dict[str, Any]:
        """Adjust system swappiness"""
        return await self.execute_privileged_action(
            'adjust_swappiness',
            {'value': value}
        )
    
    async def restart_network(self) -> Dict[str, Any]:
        """Restart network service"""
        return await self.execute_privileged_action(
            'restart_network',
            {}
        )
    
    async def clean_nix_store(self) -> Dict[str, Any]:
        """Clean Nix store garbage"""
        return await self.execute_privileged_action(
            'clean_nix_store',
            {}
        )


class HybridPermissionHandler:
    """
    Enhanced permission handler that tries the privileged service first,
    then falls back to sudo or user-space alternatives.
    """
    
    def __init__(self):
        self.privileged_client = PrivilegedHealingClient()
        # Import the original permission handler for fallback
        from .permission_handler import PermissionHandler
        self.fallback_handler = PermissionHandler()
        
    async def execute_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an action with hybrid permission handling.
        
        Priority:
        1. Try privileged service (if available)
        2. Fall back to sudo (if available)
        3. Fall back to user-space alternatives
        """
        
        # First, try the privileged service
        if await self.privileged_client.is_available():
            result = await self.privileged_client.execute_privileged_action(action, parameters)
            
            if result.get('success') or not result.get('fallback_required'):
                return result
        
        # Fall back to the original permission handler
        # Map action to command
        command_map = {
            'restart_service': ['systemctl', 'restart', parameters.get('service', '')],
            'set_cpu_governor': ['cpupower', 'frequency-set', '-g', parameters.get('governor', 'ondemand')],
            'clear_system_cache': ['sh', '-c', 'sync && sysctl -w vm.drop_caches=3'],
            'rollback_generation': ['nixos-rebuild', 'switch', '--rollback'],
            'kill_process': ['kill', f"-{parameters.get('signal', 'TERM')}", str(parameters.get('pid', ''))],
            'restart_network': ['systemctl', 'restart', 'NetworkManager'],
            'clean_nix_store': ['nix-collect-garbage', '-d'],
        }
        
        command = command_map.get(action, [])
        if not command:
            return {
                'success': False,
                'error': f'Unknown action: {action}',
                'method': 'none'
            }
        
        # Use the fallback handler
        result = await self.fallback_handler.execute_command(
            command,
            operation_type=action,
            require_root=True
        )
        
        return result
    
    async def get_status(self) -> Dict[str, Any]:
        """Get the status of available permission methods"""
        status = {
            'privileged_service': await self.privileged_client.is_available(),
            'socket_path': str(self.privileged_client.socket_path),
            'fallback_available': True
        }
        
        # Add fallback handler status
        fallback_caps = self.fallback_handler.get_capabilities_summary()
        status.update({
            'sudo_available': fallback_caps['sudo_available'],
            'passwordless_sudo': fallback_caps['passwordless_sudo'],
            'can_execute_privileged': fallback_caps['can_execute_privileged'] or status['privileged_service']
        })
        
        return status


# Convenience functions
async def check_privileged_service() -> bool:
    """Check if the privileged service is available"""
    client = PrivilegedHealingClient()
    return await client.is_available()


async def execute_with_service(action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Execute an action through the privileged service"""
    client = PrivilegedHealingClient()
    return await client.execute_privileged_action(action, parameters)


async def get_hybrid_status() -> Dict[str, Any]:
    """Get status of all permission methods"""
    handler = HybridPermissionHandler()
    return await handler.get_status()