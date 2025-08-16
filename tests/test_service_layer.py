#!/usr/bin/env python3
"""
🧪 Comprehensive Test Suite for Luminous Nix Service Layer

Tests the unified service layer that powers CLI, TUI, Voice, and API interfaces.
Ensures consistent behavior across all interfaces.

Coverage Goals:
- ✅ Service initialization
- ✅ Command execution
- ✅ Dry run vs execute modes
- ✅ Error handling
- ✅ Alias management
- ✅ Interface-specific configurations
- ✅ Backend integration
- ✅ Async operations
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from luminous_nix.api.schema import Request, Response
from luminous_nix.service_simple import (
    LuminousNixService,
    ServiceOptions,
    create_api_service,
    create_cli_service,
    create_tui_service,
    create_voice_service,
)


# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TestServiceOptions:
    """Test ServiceOptions dataclass"""
    
    def test_default_options(self):
        """Test default ServiceOptions values"""
        options = ServiceOptions()
        
        assert options.execute == False  # Safe by default
        assert options.verbose == False
        assert options.quiet == False
        assert options.json_output == False
        assert options.interface == "cli"
        assert options.user_id is None
    
    def test_custom_options(self):
        """Test custom ServiceOptions"""
        options = ServiceOptions(
            execute=True,
            verbose=True,
            interface="tui",
            user_id="test-user"
        )
        
        assert options.execute == True
        assert options.verbose == True
        assert options.interface == "tui"
        assert options.user_id == "test-user"


class TestServiceInitialization:
    """Test service initialization"""
    
    @pytest.mark.asyncio
    async def test_basic_initialization(self):
        """Test basic service initialization"""
        service = LuminousNixService()
        
        assert service.options is not None
        assert service.backend is None  # Lazy loading
        
        # Initialize backend
        with patch('luminous_nix.service_simple.NixForHumanityBackend') as mock_backend:
            await service.initialize()
            mock_backend.assert_called_once()
            assert service.backend is not None
    
    @pytest.mark.asyncio
    async def test_initialization_with_options(self):
        """Test initialization with custom options"""
        options = ServiceOptions(execute=True, interface="tui")
        service = LuminousNixService(options)
        
        assert service.options.execute == True
        assert service.options.interface == "tui"
    
    @pytest.mark.asyncio
    async def test_lazy_initialization(self):
        """Test that backend is lazy-loaded only when needed"""
        service = LuminousNixService()
        
        # Backend not created yet
        assert service.backend is None
        
        # Mock backend
        with patch('luminous_nix.service_simple.NixForHumanityBackend') as mock_backend:
            # First call initializes
            await service.initialize()
            assert mock_backend.call_count == 1
            
            # Second call doesn't re-initialize
            await service.initialize()
            assert mock_backend.call_count == 1  # Still 1


class TestCommandExecution:
    """Test command execution through service layer"""
    
    @pytest.mark.asyncio
    async def test_basic_command_execution(self):
        """Test basic command execution"""
        service = LuminousNixService()
        
        # Mock backend
        mock_response = Response(
            success=True,
            text="Package firefox installed",
            commands=["nix-env -iA nixos.firefox"],
            data={"packages": ["firefox"]}
        )
        
        with patch('luminous_nix.service_simple.NixForHumanityBackend') as mock_backend_class:
            mock_backend = AsyncMock()
            mock_backend.process_request = AsyncMock(return_value=mock_response)
            mock_backend_class.return_value = mock_backend
            
            result = await service.execute_command("install firefox")
            
            assert result.success == True
            assert "firefox" in result.text
            assert len(result.commands) == 1
    
    @pytest.mark.asyncio
    async def test_dry_run_mode(self):
        """Test dry run mode (default)"""
        service = LuminousNixService()  # Default is dry run
        
        with patch('luminous_nix.service_simple.NixForHumanityBackend') as mock_backend_class:
            mock_backend = AsyncMock()
            mock_backend.process_request = AsyncMock()
            mock_backend_class.return_value = mock_backend
            
            await service.execute_command("install vim")
            
            # Check that dry_run=True was passed
            call_args = mock_backend.process_request.call_args
            request = call_args[0][0]
            assert request.context["dry_run"] == True
    
    @pytest.mark.asyncio
    async def test_execute_mode(self):
        """Test execute mode"""
        options = ServiceOptions(execute=True)
        service = LuminousNixService(options)
        
        with patch('luminous_nix.service_simple.NixForHumanityBackend') as mock_backend_class:
            mock_backend = AsyncMock()
            mock_backend.process_request = AsyncMock()
            mock_backend_class.return_value = mock_backend
            
            await service.execute_command("install emacs")
            
            # Check that dry_run=False was passed
            call_args = mock_backend.process_request.call_args
            request = call_args[0][0]
            assert request.context["dry_run"] == False
    
    @pytest.mark.asyncio
    async def test_execute_override(self):
        """Test execute parameter override"""
        service = LuminousNixService()  # Default is dry run
        
        with patch('luminous_nix.service_simple.NixForHumanityBackend') as mock_backend_class:
            mock_backend = AsyncMock()
            mock_backend.process_request = AsyncMock()
            mock_backend_class.return_value = mock_backend
            
            # Override to execute
            await service.execute_command("update system", execute=True)
            
            # Check that dry_run=False was passed
            call_args = mock_backend.process_request.call_args
            request = call_args[0][0]
            assert request.context["dry_run"] == False
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in command execution"""
        service = LuminousNixService()
        
        with patch('luminous_nix.service_simple.NixForHumanityBackend') as mock_backend_class:
            mock_backend = AsyncMock()
            mock_backend.process_request = AsyncMock(
                side_effect=Exception("Backend error")
            )
            mock_backend_class.return_value = mock_backend
            
            result = await service.execute_command("invalid command")
            
            assert result.success == False
            assert "Backend error" in result.text
            assert result.data["error"] == "Backend error"


class TestAliasManagement:
    """Test alias management functionality"""
    
    def test_create_alias(self):
        """Test creating an alias"""
        service = LuminousNixService()
        
        # Mock symlink creation
        with patch.object(service, '_create_symlink'):
            result = service.create_alias("nix")
            
            assert result == True
            assert "nix" in service._aliases
            assert service._aliases["nix"] == "ask-nix"
    
    def test_cannot_override_ask_nix(self):
        """Test that 'ask-nix' cannot be overridden"""
        service = LuminousNixService()
        
        result = service.create_alias("ask-nix")
        
        assert result == False
        assert "ask-nix" not in service._aliases
    
    def test_remove_alias(self):
        """Test removing an alias"""
        service = LuminousNixService()
        
        # Create alias first
        with patch.object(service, '_create_symlink'):
            service.create_alias("ln")
        
        # Remove it
        with patch('pathlib.Path.unlink'):
            result = service.remove_alias("ln")
            
            assert result == True
            assert "ln" not in service._aliases
    
    def test_remove_nonexistent_alias(self):
        """Test removing an alias that doesn't exist"""
        service = LuminousNixService()
        
        result = service.remove_alias("nonexistent")
        
        assert result == False
    
    def test_list_aliases(self):
        """Test listing aliases"""
        service = LuminousNixService()
        
        # Create some aliases
        with patch.object(service, '_create_symlink'):
            service.create_alias("nix")
            service.create_alias("ln")
        
        aliases = service.list_aliases()
        
        assert len(aliases) == 2
        assert "nix" in aliases
        assert "ln" in aliases
    
    def test_create_symlink(self):
        """Test symlink creation"""
        service = LuminousNixService()
        
        with patch('pathlib.Path.exists') as mock_exists, \
             patch('pathlib.Path.mkdir') as mock_mkdir, \
             patch('pathlib.Path.symlink_to') as mock_symlink:
            
            mock_exists.side_effect = [True, False]  # ask-nix exists, symlink doesn't
            
            service._create_symlink("nix")
            
            mock_mkdir.assert_called_once()
            mock_symlink.assert_called_once()


class TestInterfaceSpecificServices:
    """Test interface-specific service creation"""
    
    @pytest.mark.asyncio
    async def test_cli_service(self):
        """Test CLI service creation"""
        with patch('luminous_nix.service_simple.NixForHumanityBackend'):
            service = await create_cli_service(verbose=True)
            
            assert service.options.interface == "cli"
            assert service.options.verbose == True
            assert service.backend is not None
    
    @pytest.mark.asyncio
    async def test_tui_service(self):
        """Test TUI service creation"""
        with patch('luminous_nix.service_simple.NixForHumanityBackend'):
            service = await create_tui_service(execute=True)
            
            assert service.options.interface == "tui"
            assert service.options.execute == True
            assert service.backend is not None
    
    @pytest.mark.asyncio
    async def test_voice_service(self):
        """Test Voice service creation"""
        with patch('luminous_nix.service_simple.NixForHumanityBackend'):
            service = await create_voice_service(quiet=True)
            
            assert service.options.interface == "voice"
            assert service.options.quiet == True
            assert service.backend is not None
    
    @pytest.mark.asyncio
    async def test_api_service(self):
        """Test API service creation"""
        with patch('luminous_nix.service_simple.NixForHumanityBackend'):
            service = await create_api_service()
            
            assert service.options.interface == "api"
            assert service.options.json_output == True  # Default for API
            assert service.backend is not None
    
    @pytest.mark.asyncio
    async def test_api_service_custom_json(self):
        """Test API service with custom JSON setting"""
        with patch('luminous_nix.service_simple.NixForHumanityBackend'):
            service = await create_api_service(json_output=False)
            
            assert service.options.interface == "api"
            assert service.options.json_output == False  # Overridden


class TestServiceIntegration:
    """Integration tests for service layer"""
    
    @pytest.mark.asyncio
    async def test_full_command_flow(self):
        """Test full command execution flow"""
        options = ServiceOptions(execute=True, verbose=True)
        service = LuminousNixService(options)
        
        # Mock the entire flow
        mock_response = Response(
            success=True,
            text="Successfully searched for editors",
            commands=["nix search editor"],
            data={
                "packages": [
                    {"name": "vim", "description": "Vi improved"},
                    {"name": "emacs", "description": "Extensible editor"},
                    {"name": "neovim", "description": "Vim fork"}
                ]
            }
        )
        
        with patch('luminous_nix.service_simple.NixForHumanityBackend') as mock_backend_class:
            mock_backend = AsyncMock()
            mock_backend.process_request = AsyncMock(return_value=mock_response)
            mock_backend_class.return_value = mock_backend
            
            result = await service.execute_command("search for text editors")
            
            assert result.success == True
            assert "editors" in result.text
            assert len(result.data["packages"]) == 3
            
            # Verify request was built correctly
            call_args = mock_backend.process_request.call_args
            request = call_args[0][0]
            assert request.query == "search for text editors"
            assert request.context["dry_run"] == False
    
    @pytest.mark.asyncio
    async def test_cleanup(self):
        """Test service cleanup"""
        service = LuminousNixService()
        
        # Should not raise any errors
        await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_concurrent_commands(self):
        """Test concurrent command execution"""
        service = LuminousNixService()
        
        mock_response = Response(
            success=True,
            text="Command executed",
            commands=[],
            data={}
        )
        
        with patch('luminous_nix.service_simple.NixForHumanityBackend') as mock_backend_class:
            mock_backend = AsyncMock()
            mock_backend.process_request = AsyncMock(return_value=mock_response)
            mock_backend_class.return_value = mock_backend
            
            # Execute multiple commands concurrently
            tasks = [
                service.execute_command("install firefox"),
                service.execute_command("search editor"),
                service.execute_command("update system")
            ]
            
            results = await asyncio.gather(*tasks)
            
            assert len(results) == 3
            assert all(r.success for r in results)
            assert mock_backend.process_request.call_count == 3


class TestErrorScenarios:
    """Test various error scenarios"""
    
    @pytest.mark.asyncio
    async def test_backend_initialization_error(self):
        """Test handling of backend initialization errors"""
        service = LuminousNixService()
        
        with patch('luminous_nix.service_simple.NixForHumanityBackend') as mock_backend_class:
            mock_backend_class.side_effect = Exception("Backend init failed")
            
            # Should handle the error gracefully
            result = await service.execute_command("test command")
            
            assert result.success == False
            assert "Backend init failed" in result.text
    
    @pytest.mark.asyncio
    async def test_request_timeout(self):
        """Test handling of request timeouts"""
        service = LuminousNixService()
        
        async def slow_request(request):
            await asyncio.sleep(10)  # Simulate slow request
            return Response(success=True, text="Done", commands=[], data={})
        
        with patch('luminous_nix.service_simple.NixForHumanityBackend') as mock_backend_class:
            mock_backend = AsyncMock()
            mock_backend.process_request = slow_request
            mock_backend_class.return_value = mock_backend
            
            # Use timeout
            with pytest.raises(asyncio.TimeoutError):
                await asyncio.wait_for(
                    service.execute_command("slow command"),
                    timeout=0.1
                )
    
    def test_symlink_creation_error(self):
        """Test handling of symlink creation errors"""
        service = LuminousNixService()
        
        with patch('pathlib.Path.exists') as mock_exists, \
             patch('pathlib.Path.symlink_to') as mock_symlink:
            
            mock_exists.return_value = True
            mock_symlink.side_effect = PermissionError("No permission")
            
            # Should handle error gracefully
            result = service.create_alias("nix")
            
            assert result == True  # Alias created in memory
            assert "nix" in service._aliases


class TestServiceState:
    """Test service state management"""
    
    def test_service_state_isolation(self):
        """Test that service instances have isolated state"""
        service1 = LuminousNixService()
        service2 = LuminousNixService()
        
        # Create alias in service1
        with patch.object(service1, '_create_symlink'):
            service1.create_alias("nix")
        
        # Service2 should not have the alias
        assert "nix" in service1._aliases
        assert "nix" not in service2._aliases
    
    @pytest.mark.asyncio
    async def test_options_immutability(self):
        """Test that options can be modified per-request"""
        service = LuminousNixService()
        
        with patch('luminous_nix.service_simple.NixForHumanityBackend') as mock_backend_class:
            mock_backend = AsyncMock()
            mock_backend.process_request = AsyncMock(
                return_value=Response(success=True, text="OK", commands=[], data={})
            )
            mock_backend_class.return_value = mock_backend
            
            # Execute with different modes
            await service.execute_command("test1", execute=False)
            await service.execute_command("test2", execute=True)
            
            # Check both calls
            calls = mock_backend.process_request.call_args_list
            assert calls[0][0][0].context["dry_run"] == True
            assert calls[1][0][0].context["dry_run"] == False


@pytest.mark.asyncio
async def test_real_world_scenario():
    """Test a real-world usage scenario"""
    # Create service for TUI
    service = await create_tui_service(execute=False)
    
    with patch('luminous_nix.service_simple.NixForHumanityBackend') as mock_backend_class:
        mock_backend = AsyncMock()
        
        # Mock different responses
        responses = [
            Response(
                success=True,
                text="Found 3 editors",
                commands=["nix search editor"],
                data={"packages": ["vim", "emacs", "neovim"]}
            ),
            Response(
                success=True,
                text="Would install neovim",
                commands=["nix-env -iA nixos.neovim"],
                data={"package": "neovim"}
            ),
            Response(
                success=False,
                text="Invalid command",
                commands=[],
                data={"error": "Could not parse command"}
            )
        ]
        
        mock_backend.process_request = AsyncMock(side_effect=responses)
        mock_backend_class.return_value = mock_backend
        
        # Simulate user session
        result1 = await service.execute_command("search editors")
        assert result1.success == True
        assert len(result1.data["packages"]) == 3
        
        result2 = await service.execute_command("install neovim")
        assert result2.success == True
        assert "neovim" in result2.text
        
        result3 = await service.execute_command("invalid gibberish")
        assert result3.success == False
        assert "Invalid" in result3.text
        
        # Cleanup
        await service.cleanup()


def test_service_layer_completeness():
    """Meta-test: Verify service layer provides all needed functionality"""
    service = LuminousNixService()
    
    # Check all required methods exist
    required_methods = [
        'initialize',
        'execute_command',
        'create_alias',
        'remove_alias',
        'list_aliases',
        'cleanup'
    ]
    
    for method in required_methods:
        assert hasattr(service, method), f"Missing required method: {method}"
    
    # Check convenience functions exist
    convenience_functions = [
        'create_cli_service',
        'create_tui_service',
        'create_voice_service',
        'create_api_service'
    ]
    
    import luminous_nix.service_simple as service_module
    for func in convenience_functions:
        assert hasattr(service_module, func), f"Missing convenience function: {func}"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])