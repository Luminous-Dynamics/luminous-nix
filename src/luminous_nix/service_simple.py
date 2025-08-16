"""
Simplified Service Layer for Luminous Nix.

A practical implementation that works with the existing codebase.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

import logging
from .core.backend import NixForHumanityBackend
from .api.schema import Request, Response

logger = logging.getLogger(__name__)


@dataclass
class ServiceOptions:
    """Options for service execution"""
    execute: bool = False  # Actually execute (not dry-run)
    verbose: bool = False  
    quiet: bool = False   
    json_output: bool = False  
    interface: str = "cli"  # Interface type (cli, tui, voice, api)
    user_id: Optional[str] = None  


class LuminousNixService:
    """
    Simplified unified service layer for all Luminous Nix interfaces.
    
    This provides a clean API for CLI, TUI, Voice to use without
    duplicating logic.
    """
    
    def __init__(self, options: Optional[ServiceOptions] = None):
        """Initialize the service."""
        self.options = options or ServiceOptions()
        self.backend = None  # Lazy load
        
    async def initialize(self):
        """Initialize the backend (lazy loading)"""
        if not self.backend:
            # Backend initializes in __init__, no separate initialize method
            self.backend = NixForHumanityBackend()
    
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
        # Initialize if needed
        await self.initialize()
        
        # Use provided execute flag or default from options
        if execute is None:
            execute = self.options.execute
        
        # Create request object for the backend
        request = Request(query=query, context={"dry_run": not execute})
        
        # Execute through backend
        try:
            response = await self.backend.process_request(request)
            return response
            
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return Response(
                success=False,
                text=str(e),
                commands=[],
                data={"error": str(e)}
            )
    
    # Simplified alias management (for now just in-memory)
    _aliases: Dict[str, str] = {}
    
    def create_alias(self, name: str) -> bool:
        """Create a command alias (simplified version)"""
        if name == 'ask-nix':
            logger.warning("Cannot create alias 'ask-nix'")
            return False
        
        self._aliases[name] = 'ask-nix'
        logger.info(f"Created alias '{name}' (in-memory only)")
        
        # Try to create symlink
        try:
            self._create_symlink(name)
        except Exception as e:
            logger.warning(f"Could not create symlink: {e}")
        
        return True
    
    def _create_symlink(self, name: str):
        """Create filesystem symlink for alias"""
        # Find ask-nix location
        project_root = Path(__file__).parent.parent.parent
        ask_nix = project_root / "bin" / "ask-nix"
        
        if not ask_nix.exists():
            logger.warning(f"ask-nix not found at {ask_nix}")
            return
        
        # Create symlink in ~/.local/bin
        local_bin = Path.home() / ".local" / "bin"
        local_bin.mkdir(parents=True, exist_ok=True)
        
        symlink = local_bin / name
        if symlink.exists():
            symlink.unlink()
        
        symlink.symlink_to(ask_nix)
        logger.info(f"Created symlink {symlink} -> {ask_nix}")
    
    def remove_alias(self, name: str) -> bool:
        """Remove a command alias"""
        if name in self._aliases:
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
        
        return False
    
    def list_aliases(self) -> List[str]:
        """Get list of configured aliases"""
        return list(self._aliases.keys())
    
    async def cleanup(self):
        """Clean up resources"""
        # Backend doesn't have cleanup method
        pass


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
    # API interface should default to JSON output
    if 'json_output' not in kwargs:
        kwargs['json_output'] = True
    options = ServiceOptions(interface="api", **kwargs)
    service = LuminousNixService(options)
    await service.initialize()
    return service