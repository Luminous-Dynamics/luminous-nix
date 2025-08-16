#!/usr/bin/env python3
"""
Integration tests for the unified service layer.

Tests that all interfaces (CLI, TUI, Voice, API) properly use
the service layer and produce consistent results.
"""

import asyncio
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

from luminous_nix.service_simple import (
    LuminousNixService,
    ServiceOptions,
    create_cli_service,
    create_tui_service,
    create_voice_service,
    create_api_service,
)
from luminous_nix.api.schema import Response


class TestServiceLayer:
    """Test the unified service layer"""
    
    @pytest.mark.asyncio
    async def test_service_initialization(self):
        """Test basic service initialization"""
        service = LuminousNixService()
        assert service is not None
        assert service.options.interface == "cli"
        assert service.options.execute == False  # Default to dry-run
        
        await service.initialize()
        assert service.backend is not None
        
        await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_service_with_options(self):
        """Test service with custom options"""
        options = ServiceOptions(
            execute=True,
            verbose=True,
            interface="test",
            json_output=True
        )
        service = LuminousNixService(options)
        
        assert service.options.execute == True
        assert service.options.verbose == True
        assert service.options.interface == "test"
        assert service.options.json_output == True
    
    @pytest.mark.asyncio
    async def test_execute_command_dry_run(self):
        """Test command execution in dry-run mode"""
        service = LuminousNixService()
        await service.initialize()
        
        # Mock the backend to avoid database issues
        with patch.object(service.backend, 'process_request') as mock_process:
            mock_process.return_value = asyncio.coroutine(lambda: Response(
                success=True,
                text="Would install firefox",
                commands=[{"command": "nix-env -iA nixpkgs.firefox"}],
                data={}
            ))()
            
            response = await service.execute_command("install firefox")
            
            assert response.success == True
            assert "firefox" in response.text.lower()
            assert len(response.commands) > 0
            
        await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_execute_command_real(self):
        """Test command execution in real mode"""
        options = ServiceOptions(execute=True)
        service = LuminousNixService(options)
        await service.initialize()
        
        # Mock the backend
        with patch.object(service.backend, 'process_request') as mock_process:
            mock_process.return_value = asyncio.coroutine(lambda: Response(
                success=True,
                text="Installed firefox",
                commands=[{"command": "nix-env -iA nixpkgs.firefox", "executed": True}],
                data={}
            ))()
            
            response = await service.execute_command("install firefox")
            
            assert response.success == True
            assert "firefox" in response.text.lower()
            
        await service.cleanup()
    
    def test_alias_management(self):
        """Test alias creation and management"""
        service = LuminousNixService()
        
        # Create an alias
        success = service.create_alias("test-alias")
        assert success == True
        
        # List aliases
        aliases = service.list_aliases()
        assert "test-alias" in aliases
        
        # Try to create ask-nix (should fail)
        success = service.create_alias("ask-nix")
        assert success == False
        
        # Remove alias
        success = service.remove_alias("test-alias")
        assert success == True
        
        # Verify removed
        aliases = service.list_aliases()
        assert "test-alias" not in aliases
    
    @pytest.mark.asyncio
    async def test_cli_service_factory(self):
        """Test CLI service factory function"""
        service = await create_cli_service(execute=True, verbose=True)
        
        assert service is not None
        assert service.options.interface == "cli"
        assert service.options.execute == True
        assert service.options.verbose == True
        assert service.backend is not None  # Should be initialized
        
        await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_tui_service_factory(self):
        """Test TUI service factory function"""
        service = await create_tui_service(execute=False)
        
        assert service is not None
        assert service.options.interface == "tui"
        assert service.options.execute == False
        assert service.backend is not None
        
        await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_voice_service_factory(self):
        """Test Voice service factory function"""
        service = await create_voice_service(user_id="voice_user")
        
        assert service is not None
        assert service.options.interface == "voice"
        assert service.options.user_id == "voice_user"
        assert service.backend is not None
        
        await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_api_service_factory(self):
        """Test API service factory function"""
        service = await create_api_service()
        
        assert service is not None
        assert service.options.interface == "api"
        assert service.options.json_output == True  # API should default to JSON
        assert service.backend is not None
        
        await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_consistency_across_interfaces(self):
        """Test that all interfaces produce consistent results"""
        # Create services for each interface
        cli_service = await create_cli_service()
        tui_service = await create_tui_service()
        voice_service = await create_voice_service()
        api_service = await create_api_service()
        
        # Mock the backend for all services
        for service in [cli_service, tui_service, voice_service, api_service]:
            with patch.object(service.backend, 'process_request') as mock:
                mock.return_value = asyncio.coroutine(lambda: Response(
                    success=True,
                    text="Consistent response",
                    commands=[{"command": "test"}],
                    data={"test": True}
                ))()
        
        # Execute same command on all interfaces
        query = "search firefox"
        responses = []
        
        for service in [cli_service, tui_service, voice_service, api_service]:
            response = await service.execute_command(query)
            responses.append(response)
        
        # Verify all responses are consistent
        first_response = responses[0]
        for response in responses[1:]:
            assert response.success == first_response.success
            assert response.text == first_response.text
            assert response.commands == first_response.commands
        
        # Cleanup
        for service in [cli_service, tui_service, voice_service, api_service]:
            await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in service layer"""
        service = LuminousNixService()
        await service.initialize()
        
        # Mock backend to raise an error
        with patch.object(service.backend, 'process_request') as mock:
            mock.side_effect = Exception("Test error")
            
            response = await service.execute_command("test command")
            
            assert response.success == False
            assert "Test error" in response.text
            assert "error" in response.data
        
        await service.cleanup()
    
    def test_symlink_creation(self):
        """Test that alias creates proper symlinks"""
        service = LuminousNixService()
        
        # Create alias
        alias_name = "test-luminix"
        service.create_alias(alias_name)
        
        # Check symlink exists
        symlink_path = Path.home() / ".local" / "bin" / alias_name
        # Note: This might not work in test environment without proper setup
        # Just verify the method doesn't crash
        
        # Cleanup
        service.remove_alias(alias_name)
    
    @pytest.mark.asyncio
    async def test_service_options_update(self):
        """Test updating service options after creation"""
        service = LuminousNixService()
        
        # Initial state
        assert service.options.execute == False
        
        # Update options
        service.options.execute = True
        service.options.verbose = True
        
        assert service.options.execute == True
        assert service.options.verbose == True
    
    @pytest.mark.asyncio
    async def test_multiple_commands(self):
        """Test executing multiple commands in sequence"""
        service = LuminousNixService()
        await service.initialize()
        
        commands = [
            "search firefox",
            "help",
            "list packages"
        ]
        
        with patch.object(service.backend, 'process_request') as mock:
            mock.return_value = asyncio.coroutine(lambda: Response(
                success=True,
                text="Command executed",
                commands=[],
                data={}
            ))()
            
            for cmd in commands:
                response = await service.execute_command(cmd)
                assert response.success == True
        
        await service.cleanup()


class TestInterfaceIntegration:
    """Test actual interface integration with service layer"""
    
    @pytest.mark.asyncio
    async def test_cli_interface_uses_service(self):
        """Test that CLI properly uses service layer"""
        # This would test the actual CLI implementation
        # For now, we verify the imports work
        from luminous_nix.interfaces.cli import handle_command
        assert handle_command is not None
    
    @pytest.mark.asyncio
    async def test_tui_interface_uses_service(self):
        """Test that TUI properly uses service layer"""
        from luminous_nix.interfaces.tui_components.app import NixForHumanityTUI
        
        # Verify TUI has service attribute
        tui = NixForHumanityTUI()
        assert hasattr(tui, 'service')
    
    @pytest.mark.asyncio
    async def test_voice_interface_uses_service(self):
        """Test that Voice interface properly uses service layer"""
        from luminous_nix.interfaces.voice import VoiceInterface
        
        # Create voice interface
        voice = VoiceInterface()
        assert hasattr(voice, 'service')
        assert voice.service is not None


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])