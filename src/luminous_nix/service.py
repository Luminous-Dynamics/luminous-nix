"""
Unified Service Layer for Luminous Nix.

This is the single source of truth that all interfaces (CLI, TUI, Voice, API)
use for executing commands. It handles settings, learning, aliases, and other
cross-cutting concerns.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json

from .core.backend import NixForHumanityBackend
from .api.schema import Context, Response
from .config.config_manager import ConfigManager
from .utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ServiceOptions:
    """Options for service execution"""
    execute: bool = False  # Actually execute (not dry-run)
    verbose: bool = False  # Verbose output
    quiet: bool = False   # Minimal output
    json_output: bool = False  # JSON format output
    interface: str = "cli"  # Interface type (cli, tui, voice, api)
    user_id: Optional[str] = None  # User identifier for personalization


class LuminousNixService:
    """
    Unified service layer for all Luminous Nix interfaces.
    
    This ensures consistency across CLI, TUI, Voice, and API interfaces
    while maintaining high performance through direct Python calls.
    """
    
    def __init__(self, options: Optional[ServiceOptions] = None):
        """
        Initialize the service.
        
        Args:
            options: Service configuration options
        """
        self.options = options or ServiceOptions()
        self.config_manager = ConfigManager()
        self.config = self.config_manager.config
        self.backend = None  # Lazy load
        self._aliases = self._load_aliases()
        
    def _load_aliases(self) -> Dict[str, str]:
        """Load command aliases from config"""
        aliases = {}
        if 'aliases' in self.config:
            alias_list = self.config['aliases'].get('list', [])
            for alias in alias_list:
                aliases[alias] = 'ask-nix'
        return aliases
    
    async def initialize(self):
        """Initialize the backend (lazy loading)"""
        if not self.backend:
            self.backend = NixForHumanityBackend()
            await self.backend.initialize()
    
    async def execute_command(
        self, 
        query: str, 
        execute: Optional[bool] = None,
        **kwargs
    ) -> Response:
        """
        Execute a natural language command.
        
        Args:
            query: Natural language query
            execute: Override default execute mode
            **kwargs: Additional options
            
        Returns:
            Response object with results
        """
        # Initialize backend if needed
        await self.initialize()
        
        # Use provided execute flag or default from options
        if execute is None:
            execute = self.options.execute
        
        # Set dry_run mode (opposite of execute)
        self.backend.dry_run = not execute
        
        # Resolve any aliases in the command
        query = self._resolve_aliases(query)
        
        # Track command for learning (if enabled)
        if self.options.user_id:
            self._track_command(query)
        
        # Create context
        context = Context()
        
        # Execute through backend
        try:
            response = await self.backend.execute(query, context)
            
            # Track response for learning
            if self.options.user_id:
                self._track_response(response)
            
            # Format output based on options
            if self.options.json_output:
                response = self._format_json_response(response)
            
            return response
            
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return Response(
                success=False,
                text=str(e),
                commands=[],
                data={"error": str(e)}
            )
    
    def _resolve_aliases(self, query: str) -> str:
        """Resolve command aliases"""
        # For now, aliases are handled at the shell level
        # This could be extended to handle internal aliases
        return query
    
    def _track_command(self, query: str):
        """Track command for learning system"""
        # TODO: Implement learning system integration
        try:
            from .learning.pragmatic_learning import PragmaticLearningSystem
            learning = PragmaticLearningSystem(self.options.user_id)
            learning.track_command(query)
        except ImportError:
            pass  # Learning system not available
    
    def _track_response(self, response: Response):
        """Track response for learning system"""
        # TODO: Implement learning system integration
        try:
            from .learning.pragmatic_learning import PragmaticLearningSystem
            learning = PragmaticLearningSystem(self.options.user_id)
            learning.observe_command(
                command="",  # Would need to store this
                success=response.success,
                error=response.error
            )
        except ImportError:
            pass  # Learning system not available
    
    def _format_json_response(self, response: Response) -> Response:
        """Format response for JSON output"""
        # Response is already structured, just ensure it's JSON-serializable
        return response
    
    # Alias Management
    
    def create_alias(self, name: str) -> bool:
        """
        Create a command alias.
        
        Args:
            name: Alias name (e.g., 'luminix', 'lnix')
            
        Returns:
            Success status
        """
        if name == 'ask-nix':
            logger.warning("Cannot create alias 'ask-nix' - it's the main command")
            return False
        
        # Add to config
        if 'aliases' not in self.config:
            self.config['aliases'] = {'list': []}
        
        alias_list = self.config['aliases']['list']
        if name not in alias_list:
            alias_list.append(name)
            save_config(self.config)
            self._aliases[name] = 'ask-nix'
            
            # Create symlink
            self._create_symlink(name)
            
            logger.info(f"Created alias '{name}'")
            return True
        
        logger.info(f"Alias '{name}' already exists")
        return True
    
    def _create_symlink(self, name: str):
        """Create filesystem symlink for alias"""
        try:
            # Find ask-nix location
            project_root = Path(__file__).parent.parent.parent
            ask_nix = project_root / "bin" / "ask-nix"
            
            # Create symlink in ~/.local/bin
            local_bin = Path.home() / ".local" / "bin"
            local_bin.mkdir(parents=True, exist_ok=True)
            
            symlink = local_bin / name
            if symlink.exists():
                symlink.unlink()
            
            symlink.symlink_to(ask_nix)
            logger.info(f"Created symlink {symlink} -> {ask_nix}")
            
        except Exception as e:
            logger.error(f"Failed to create symlink: {e}")
    
    def remove_alias(self, name: str) -> bool:
        """Remove a command alias"""
        if name not in self._aliases:
            logger.warning(f"Alias '{name}' does not exist")
            return False
        
        # Remove from config
        alias_list = self.config.get('aliases', {}).get('list', [])
        if name in alias_list:
            alias_list.remove(name)
            save_config(self.config)
            del self._aliases[name]
        
        # Remove symlink
        try:
            symlink = Path.home() / ".local" / "bin" / name
            if symlink.exists():
                symlink.unlink()
        except Exception as e:
            logger.error(f"Failed to remove symlink: {e}")
        
        logger.info(f"Removed alias '{name}'")
        return True
    
    def list_aliases(self) -> List[str]:
        """Get list of configured aliases"""
        return list(self._aliases.keys())
    
    # Settings Management
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a configuration setting"""
        return self.config.get(key, default)
    
    def set_setting(self, key: str, value: Any):
        """Set a configuration setting"""
        self.config[key] = value
        save_config(self.config)
    
    # Cleanup
    
    async def cleanup(self):
        """Clean up resources"""
        if self.backend:
            await self.backend.cleanup()


# Convenience functions for different interfaces

async def create_cli_service(**kwargs) -> LuminousNixService:
    """Create service configured for CLI use"""
    options = ServiceOptions(interface="cli", **kwargs)
    service = LuminousNixService(options)
    await service.initialize()
    return service


async def create_tui_service(**kwargs) -> LuminousNixService:
    """Create service configured for TUI use"""
    options = ServiceOptions(interface="tui", **kwargs)
    service = LuminousNixService(options)
    await service.initialize()
    return service


async def create_voice_service(**kwargs) -> LuminousNixService:
    """Create service configured for Voice use"""
    options = ServiceOptions(interface="voice", **kwargs)
    service = LuminousNixService(options)
    await service.initialize()
    return service


async def create_api_service(**kwargs) -> LuminousNixService:
    """Create service configured for API use"""
    options = ServiceOptions(interface="api", json_output=True, **kwargs)
    service = LuminousNixService(options)
    await service.initialize()
    return service