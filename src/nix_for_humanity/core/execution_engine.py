# Execution Engine
"""
Safe command execution with validation and sandboxing
"""

import subprocess
import os
import tempfile
import json
from typing import Dict, Tuple, Optional, List
from pathlib import Path
from .interface import Command, ExecutionMode


class ExecutionEngine:
    """Executes system commands safely"""
    
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.sandbox_enabled = True
        self.timeout = 300  # 5 minutes default
        
    def build_command(self, action: str, target: str = None) -> Optional[Command]:
        """Build a safe command from action and target"""
        
        commands = {
            'install': Command(
                program='nix',
                args=['profile', 'install', f'nixpkgs#{target}'],
                safe=True,
                requires_sudo=False,
                description=f"Install {target}"
            ),
            
            'remove': Command(
                program='nix',
                args=['profile', 'remove', target],
                safe=True,
                requires_sudo=False,
                description=f"Remove {target}"
            ),
            
            'update': Command(
                program='nixos-rebuild',
                args=['switch'],
                safe=True,
                requires_sudo=True,
                description="Update NixOS system"
            ),
            
            'search': Command(
                program='nix',
                args=['search', 'nixpkgs', target, '--json'],
                safe=True,
                requires_sudo=False,
                description=f"Search for {target}"
            ),
            
            'rollback': Command(
                program='nixos-rebuild',
                args=['switch', '--rollback'],
                safe=True,
                requires_sudo=True,
                description="Rollback to previous generation"
            ),
            
            'list': Command(
                program='nix',
                args=['profile', 'list'],
                safe=True,
                requires_sudo=False,
                description="List installed packages"
            ),
        }
        
        return commands.get(action)
        
    def validate_command(self, command: Command) -> Tuple[bool, Optional[str]]:
        """Validate command for safety"""
        
        # Check if command is marked as safe
        if not command.safe:
            return False, "Command is not marked as safe"
            
        # Check dangerous patterns
        dangerous_patterns = [
            'rm -rf',
            'dd if=',
            'mkfs.',
            '> /dev/',
            'curl | sh',
            'wget | sh',
        ]
        
        command_str = f"{command.program} {' '.join(command.args)}"
        for pattern in dangerous_patterns:
            if pattern in command_str:
                return False, f"Dangerous pattern detected: {pattern}"
                
        # Check for pipe character in args (potential command injection)
        if any('|' in arg for arg in command.args):
            return False, "Dangerous pattern detected: pipe character in arguments"
                
        # Validate program exists
        if not self._command_exists(command.program):
            return False, f"Command not found: {command.program}"
            
        return True, None
        
    def execute(self, command: Command, mode: ExecutionMode = ExecutionMode.DRY_RUN) -> Dict:
        """Execute command with specified mode"""
        
        # Validate first
        valid, error = self.validate_command(command)
        if not valid:
            return {
                'success': False,
                'error': error,
                'output': '',
                'exit_code': 1
            }
            
        # Build full command
        cmd_parts = [command.program] + command.args
        
        # Add sudo if required
        if command.requires_sudo:
            cmd_parts = ['sudo'] + cmd_parts
            
        # Add dry-run flag for nix commands
        if mode == ExecutionMode.DRY_RUN and command.program in ['nix', 'nixos-rebuild']:
            cmd_parts.append('--dry-run')
            
        # Log what we're doing
        if mode == ExecutionMode.EXPLAIN:
            return {
                'success': True,
                'explanation': self._explain_command(command),
                'command': ' '.join(cmd_parts),
                'would_execute': False  # EXPLAIN mode never executes
            }
            
        # Execute the command
        try:
            result = subprocess.run(
                cmd_parts,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                env=self._get_safe_env()
            )
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr,
                'exit_code': result.returncode,
                'command': ' '.join(cmd_parts)
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': f"Command timed out after {self.timeout} seconds",
                'output': '',
                'exit_code': -1
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'output': '',
                'exit_code': -1
            }
            
    def execute_safe_search(self, search_term: str) -> Tuple[bool, List[Dict], str]:
        """Execute package search safely"""
        
        cmd = Command(
            program='nix',
            args=['search', 'nixpkgs', search_term, '--json'],
            safe=True,
            requires_sudo=False,
            description=f"Search for {search_term}"
        )
        
        result = self.execute(cmd, ExecutionMode.EXECUTE)
        
        if result['success'] and result['output']:
            try:
                packages = json.loads(result['output'])
                # Convert to simpler format
                results = []
                for pkg_path, pkg_info in packages.items():
                    pkg_name = pkg_path.split('.')[-1]
                    results.append({
                        'name': pkg_name,
                        'version': pkg_info.get('version', 'unknown'),
                        'description': pkg_info.get('description', 'No description')
                    })
                return True, results[:10], ""  # Limit to 10 results
            except json.JSONDecodeError:
                return False, [], "Failed to parse search results"
        else:
            return False, [], result.get('error', 'Search failed')
            
    def _command_exists(self, command: str) -> bool:
        """Check if command exists in PATH"""
        return subprocess.run(
            ['which', command],
            capture_output=True
        ).returncode == 0
        
    def _get_safe_env(self) -> Dict[str, str]:
        """Get minimal safe environment for command execution"""
        # Start with minimal environment
        safe_env = {
            'PATH': '/run/current-system/sw/bin:/nix/var/nix/profiles/default/bin',
            'HOME': os.environ.get('HOME', '/tmp'),
            'USER': os.environ.get('USER', 'nobody'),
            'LANG': 'en_US.UTF-8',
        }
        
        # Add NIX-specific variables if they exist
        nix_vars = ['NIX_PATH', 'NIX_PROFILES', 'NIX_SSL_CERT_FILE']
        for var in nix_vars:
            if var in os.environ:
                safe_env[var] = os.environ[var]
                
        return safe_env
        
    def _explain_command(self, command: Command) -> str:
        """Explain what a command will do"""
        
        explanations = {
            'nix profile install': "This will install the package into your user profile",
            'nix profile remove': "This will remove the package from your user profile",
            'nixos-rebuild switch': "This will rebuild and switch to the new system configuration",
            'nixos-rebuild switch --rollback': "This will switch back to the previous system generation",
            'nix search': "This will search for packages matching your query",
            'nix profile list': "This will show all packages in your profile"
        }
        
        cmd_prefix = f"{command.program} {' '.join(command.args[:2])}"
        for prefix, explanation in explanations.items():
            if cmd_prefix.startswith(prefix):
                return explanation
                
        return command.description