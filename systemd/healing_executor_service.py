#!/usr/bin/env python3
"""
Privileged Healing Executor Service for SystemD.

This service runs with elevated privileges and executes healing actions
requested by the unprivileged monitoring service through a secure Unix socket.
"""

import asyncio
import json
import logging
import os
import signal
import socket
import subprocess
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import hashlib
import hmac

# Set up logging to journal
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('luminous-healing-executor')


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
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HealingRequest':
        return cls(**data)


@dataclass
class HealingResponse:
    """Response from executing a healing action"""
    request_id: str
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    duration_ms: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SecureHealingExecutor:
    """
    Executes privileged healing actions with security controls.
    """
    
    def __init__(self, socket_path: str = "/run/luminous-healing.sock",
                 secret_key: Optional[str] = None):
        self.socket_path = Path(socket_path)
        self.secret_key = secret_key or os.environ.get('LUMINOUS_HEALING_SECRET', 'default-dev-key')
        self.allowed_actions = self._load_allowed_actions()
        self.rate_limiter = {}
        self.audit_log = []
        
    def _load_allowed_actions(self) -> Dict[str, callable]:
        """Load allowed healing actions"""
        return {
            'restart_service': self._restart_service,
            'set_cpu_governor': self._set_cpu_governor,
            'clear_system_cache': self._clear_system_cache,
            'rollback_generation': self._rollback_generation,
            'kill_process': self._kill_process,
            'adjust_swappiness': self._adjust_swappiness,
            'restart_network': self._restart_network,
            'clean_nix_store': self._clean_nix_store,
        }
    
    def _verify_signature(self, request: HealingRequest) -> bool:
        """Verify request signature for security"""
        if not request.signature:
            logger.warning(f"Request {request.id} has no signature")
            return False
        
        # Create the message to sign
        message = f"{request.id}:{request.action}:{request.timestamp}"
        expected_signature = hmac.new(
            self.secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(request.signature, expected_signature)
    
    def _check_rate_limit(self, action: str) -> bool:
        """Check if action is rate limited"""
        now = datetime.now()
        
        # Clean old entries
        self.rate_limiter = {
            k: v for k, v in self.rate_limiter.items()
            if (now - v).seconds < 300  # 5 minute window
        }
        
        # Check limit (max 10 per action per 5 minutes)
        action_count = sum(1 for k in self.rate_limiter if k.startswith(action))
        if action_count >= 10:
            logger.warning(f"Rate limit exceeded for {action}")
            return False
        
        # Record this action
        self.rate_limiter[f"{action}:{now.isoformat()}"] = now
        return True
    
    def _audit_action(self, request: HealingRequest, response: HealingResponse):
        """Log action for audit trail"""
        audit_entry = {
            'timestamp': datetime.now().isoformat(),
            'request_id': request.id,
            'action': request.action,
            'parameters': request.parameters,
            'success': response.success,
            'duration_ms': response.duration_ms,
            'error': response.error
        }
        
        self.audit_log.append(audit_entry)
        
        # Also log to journal
        if response.success:
            logger.info(f"✅ Executed {request.action} (request {request.id})")
        else:
            logger.error(f"❌ Failed {request.action}: {response.error}")
        
        # Persist audit log
        audit_file = Path('/var/log/luminous-healing-audit.json')
        try:
            with open(audit_file, 'a') as f:
                f.write(json.dumps(audit_entry) + '\n')
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
    
    async def execute_request(self, request: HealingRequest) -> HealingResponse:
        """Execute a healing request with security checks"""
        start_time = datetime.now()
        
        # Security checks
        if not self._verify_signature(request):
            return HealingResponse(
                request_id=request.id,
                success=False,
                error="Invalid signature"
            )
        
        if request.action not in self.allowed_actions:
            return HealingResponse(
                request_id=request.id,
                success=False,
                error=f"Action {request.action} not allowed"
            )
        
        if not self._check_rate_limit(request.action):
            return HealingResponse(
                request_id=request.id,
                success=False,
                error="Rate limit exceeded"
            )
        
        # Execute the action
        try:
            logger.info(f"Executing {request.action} (request {request.id})")
            handler = self.allowed_actions[request.action]
            result = await handler(request.parameters)
            
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            
            response = HealingResponse(
                request_id=request.id,
                success=result.get('success', False),
                output=result.get('output'),
                error=result.get('error'),
                duration_ms=duration_ms
            )
            
        except Exception as e:
            logger.error(f"Exception executing {request.action}: {e}")
            response = HealingResponse(
                request_id=request.id,
                success=False,
                error=str(e),
                duration_ms=int((datetime.now() - start_time).total_seconds() * 1000)
            )
        
        # Audit the action
        self._audit_action(request, response)
        
        return response
    
    # Healing action implementations
    
    async def _restart_service(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Restart a systemd service"""
        service_name = params.get('service')
        if not service_name:
            return {'success': False, 'error': 'No service specified'}
        
        # Validate service name (prevent injection)
        if not service_name.replace('-', '').replace('_', '').isalnum():
            return {'success': False, 'error': 'Invalid service name'}
        
        try:
            result = subprocess.run(
                ['systemctl', 'restart', service_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr if result.returncode != 0 else None
            }
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Service restart timeout'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _set_cpu_governor(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Set CPU frequency governor"""
        governor = params.get('governor', 'ondemand')
        
        # Validate governor
        valid_governors = ['performance', 'powersave', 'ondemand', 'conservative']
        if governor not in valid_governors:
            return {'success': False, 'error': f'Invalid governor: {governor}'}
        
        try:
            result = subprocess.run(
                ['cpupower', 'frequency-set', '-g', governor],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return {
                'success': result.returncode == 0,
                'output': f"CPU governor set to {governor}",
                'error': result.stderr if result.returncode != 0 else None
            }
        except FileNotFoundError:
            # Try alternative method
            try:
                cpu_count = os.cpu_count() or 1
                for cpu in range(cpu_count):
                    gov_file = f'/sys/devices/system/cpu/cpu{cpu}/cpufreq/scaling_governor'
                    with open(gov_file, 'w') as f:
                        f.write(governor)
                
                return {'success': True, 'output': f"Governor set to {governor} via sysfs"}
            except Exception as e:
                return {'success': False, 'error': f"Failed to set governor: {e}"}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _clear_system_cache(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Clear system caches"""
        try:
            # Sync first
            subprocess.run(['sync'], check=True)
            
            # Clear caches
            with open('/proc/sys/vm/drop_caches', 'w') as f:
                f.write('3')
            
            return {'success': True, 'output': 'System caches cleared'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _rollback_generation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Rollback NixOS generation"""
        try:
            result = subprocess.run(
                ['nixos-rebuild', 'switch', '--rollback'],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return {
                'success': result.returncode == 0,
                'output': 'NixOS generation rolled back',
                'error': result.stderr if result.returncode != 0 else None
            }
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Rollback timeout (>5 minutes)'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _kill_process(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Kill a process by PID"""
        pid = params.get('pid')
        signal_type = params.get('signal', 'TERM')
        
        if not pid:
            return {'success': False, 'error': 'No PID specified'}
        
        try:
            pid = int(pid)
            
            # Validate signal
            valid_signals = ['TERM', 'KILL', 'HUP', 'INT']
            if signal_type not in valid_signals:
                signal_type = 'TERM'
            
            os.kill(pid, getattr(signal, f'SIG{signal_type}'))
            
            return {'success': True, 'output': f'Process {pid} killed with {signal_type}'}
        except ProcessLookupError:
            return {'success': False, 'error': f'Process {pid} not found'}
        except PermissionError:
            return {'success': False, 'error': f'Permission denied to kill {pid}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _adjust_swappiness(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Adjust system swappiness"""
        swappiness = params.get('value', 60)
        
        try:
            swappiness = int(swappiness)
            if not 0 <= swappiness <= 100:
                return {'success': False, 'error': 'Swappiness must be 0-100'}
            
            with open('/proc/sys/vm/swappiness', 'w') as f:
                f.write(str(swappiness))
            
            return {'success': True, 'output': f'Swappiness set to {swappiness}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _restart_network(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Restart network service"""
        try:
            # Try NetworkManager first
            result = subprocess.run(
                ['systemctl', 'restart', 'NetworkManager'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                # Try systemd-networkd
                result = subprocess.run(
                    ['systemctl', 'restart', 'systemd-networkd'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            
            return {
                'success': result.returncode == 0,
                'output': 'Network service restarted',
                'error': result.stderr if result.returncode != 0 else None
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _clean_nix_store(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Clean Nix store garbage"""
        try:
            result = subprocess.run(
                ['nix-collect-garbage', '-d'],
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes
            )
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr if result.returncode != 0 else None
            }
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Nix garbage collection timeout'}
        except Exception as e:
            return {'success': False, 'error': str(e)}


class HealingExecutorService:
    """
    Main service that listens on Unix socket for healing requests.
    """
    
    def __init__(self):
        self.executor = SecureHealingExecutor()
        self.socket_path = Path("/run/luminous-healing.sock")
        self.running = True
        
    async def start(self):
        """Start the Unix socket server"""
        logger.info("🚀 Luminous Healing Executor Service starting...")
        
        # Clean up old socket if exists
        if self.socket_path.exists():
            os.unlink(self.socket_path)
        
        # Create socket
        server = await asyncio.start_unix_server(
            self.handle_client,
            path=str(self.socket_path)
        )
        
        # Set permissions (allow luminous group)
        os.chmod(self.socket_path, 0o660)
        
        logger.info(f"✅ Listening on {self.socket_path}")
        
        # Handle shutdown signals
        for sig in (signal.SIGTERM, signal.SIGINT):
            signal.signal(sig, self._handle_signal)
        
        async with server:
            await server.serve_forever()
    
    def _handle_signal(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
        sys.exit(0)
    
    async def handle_client(self, reader, writer):
        """Handle a client connection"""
        addr = writer.get_extra_info('peername')
        logger.debug(f"Client connected: {addr}")
        
        try:
            # Read request (max 64KB)
            data = await reader.read(65536)
            if not data:
                return
            
            # Parse request
            try:
                request_data = json.loads(data.decode())
                request = HealingRequest.from_dict(request_data)
            except (json.JSONDecodeError, TypeError) as e:
                logger.error(f"Invalid request format: {e}")
                response = HealingResponse(
                    request_id="unknown",
                    success=False,
                    error="Invalid request format"
                )
            else:
                # Execute request
                response = await self.executor.execute_request(request)
            
            # Send response
            response_data = json.dumps(response.to_dict()).encode()
            writer.write(response_data)
            await writer.drain()
            
        except Exception as e:
            logger.error(f"Error handling client: {e}")
        finally:
            writer.close()
            await writer.wait_closed()


async def main():
    """Main entry point"""
    service = HealingExecutorService()
    await service.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Service interrupted by user")
    except Exception as e:
        logger.error(f"Service failed: {e}")
        sys.exit(1)