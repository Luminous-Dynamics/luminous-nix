"""
Command Result Cache

Caches the results of NixOS command executions to avoid redundant operations.
"""

import hashlib
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from dataclasses import dataclass

from .cache_manager import CacheManager
from ..core.types import ExecutionResult, Command


@dataclass 
class CachedCommand:
    """Cached command result with metadata"""
    command: Command
    result: ExecutionResult
    system_generation: int
    timestamp: datetime
    invalidation_triggers: List[str]


class CommandResultCache:
    """
    Cache for NixOS command execution results.
    
    Features:
    - Safe command result caching
    - System generation awareness
    - Intelligent invalidation
    - Command fingerprinting
    """
    
    def __init__(self, cache_manager: CacheManager):
        """Initialize command cache"""
        self.cache_manager = cache_manager
        
        # Commands safe to cache
        self.cacheable_commands = {
            'nix-env -q',           # List installed
            'nix search',           # Search results
            'nix-channel --list',   # Channel list
            'nixos-option',         # Option queries
            'nix eval',             # Pure evaluations
            'nix show-derivation',  # Derivation info
        }
        
        # Commands that invalidate cache
        self.invalidating_commands = {
            'nix-env -i': ['nix-env -q'],              # Install invalidates list
            'nix-env -e': ['nix-env -q'],              # Uninstall invalidates list
            'nixos-rebuild': ['*'],                     # Rebuild invalidates all
            'nix-channel --update': ['nix search'],     # Channel update invalidates search
            'nix-collect-garbage': ['nix-store'],       # GC invalidates store queries
        }
        
        self.current_generation = self._get_system_generation()
    
    def get(self, command: Command) -> Optional[ExecutionResult]:
        """Get cached command result if valid"""
        if not self._is_cacheable(command):
            return None
            
        cache_key = self._generate_cache_key(command)
        cached = self.cache_manager.get(cache_key, cache_type='command')
        
        if not cached:
            return None
            
        # Validate cached result
        if not self._is_valid(cached):
            self.cache_manager.invalidate(cache_key)
            return None
            
        return cached.result
    
    def set(self, command: Command, result: ExecutionResult) -> None:
        """Cache command result if appropriate"""
        if not self._is_cacheable(command) or not result.success:
            return
            
        cache_key = self._generate_cache_key(command)
        cached_command = CachedCommand(
            command=command,
            result=result,
            system_generation=self.current_generation,
            timestamp=datetime.now(),
            invalidation_triggers=self._get_invalidation_triggers(command)
        )
        
        # Determine TTL based on command type
        ttl = self._determine_ttl(command)
        
        self.cache_manager.set(
            cache_key,
            cached_command,
            ttl=ttl,
            metadata={
                'command_type': self._classify_command(command),
                'generation': self.current_generation
            }
        )
    
    def invalidate_by_command(self, command: Command) -> int:
        """Invalidate cache entries affected by a command"""
        count = 0
        
        # Check if this command invalidates others
        command_str = self._command_to_string(command)
        for pattern, affected in self.invalidating_commands.items():
            if command_str.startswith(pattern):
                for affected_pattern in affected:
                    if affected_pattern == '*':
                        count += self.cache_manager.invalidate('command:')
                    else:
                        count += self.cache_manager.invalidate(f'command:{affected_pattern}')
                        
        # Update generation if it's a rebuild
        if 'nixos-rebuild' in command_str:
            self.current_generation = self._get_system_generation()
            
        return count
    
    # Private helper methods
    
    def _is_cacheable(self, command: Command) -> bool:
        """Check if command result can be cached"""
        command_str = self._command_to_string(command)
        
        # Check against whitelist
        return any(
            command_str.startswith(safe_cmd) 
            for safe_cmd in self.cacheable_commands
        )
    
    def _generate_cache_key(self, command: Command) -> str:
        """Generate cache key for command"""
        # Include all command details
        key_parts = [
            'command',
            command.get('command', ''),
            json.dumps(command.get('args', []), sort_keys=True),
            str(command.get('requires_sudo', False))
        ]
        
        key_string = ':'.join(key_parts)
        return f"command:{hashlib.sha256(key_string.encode()).hexdigest()[:16]}"
    
    def _command_to_string(self, command: Command) -> str:
        """Convert command to string representation"""
        parts = [command.get('command', '')]
        parts.extend(command.get('args', []))
        return ' '.join(parts)
    
    def _is_valid(self, cached: CachedCommand) -> bool:
        """Check if cached command is still valid"""
        # Check system generation
        if cached.system_generation != self.current_generation:
            return False
            
        # Check age (already handled by TTL, but double-check)
        age = (datetime.now() - cached.timestamp).total_seconds()
        if age > 3600:  # 1 hour max
            return False
            
        return True
    
    def _determine_ttl(self, command: Command) -> int:
        """Determine TTL for command result"""
        command_str = self._command_to_string(command)
        
        # Very short TTL for system state queries
        if 'nixos-option' in command_str:
            return 60  # 1 minute
            
        # Medium TTL for package lists
        if 'nix-env -q' in command_str:
            return 300  # 5 minutes
            
        # Longer TTL for search results
        if 'nix search' in command_str:
            return 1800  # 30 minutes
            
        # Default
        return self.cache_manager.config.command_ttl
    
    def _classify_command(self, command: Command) -> str:
        """Classify command for statistics"""
        command_str = self._command_to_string(command)
        
        if 'search' in command_str:
            return 'search'
        elif 'nix-env -q' in command_str:
            return 'list'
        elif 'nixos-option' in command_str:
            return 'query'
        elif 'eval' in command_str:
            return 'eval'
        else:
            return 'other'
    
    def _get_invalidation_triggers(self, command: Command) -> List[str]:
        """Get list of commands that would invalidate this cache entry"""
        triggers = []
        command_str = self._command_to_string(command)
        
        # Find what invalidates this command
        for inv_cmd, affected in self.invalidating_commands.items():
            for affected_pattern in affected:
                if affected_pattern == '*' or command_str.startswith(affected_pattern):
                    triggers.append(inv_cmd)
                    
        return triggers
    
    def _get_system_generation(self) -> int:
        """Get current NixOS system generation"""
        # This would actually query the system
        # For now, return a mock value
        return 42