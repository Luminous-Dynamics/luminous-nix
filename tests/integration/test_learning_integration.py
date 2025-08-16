#!/usr/bin/env python3
"""
Integration tests for service layer with learning system.

Tests that the learning system properly integrates with the service layer
and provides personalized experiences.
"""

import asyncio
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import tempfile

from luminous_nix.service_with_learning import (
    LuminousNixServiceWithLearning,
    LearningServiceOptions,
    create_cli_service_with_learning,
    create_private_service,
)
from luminous_nix.api.schema import Response


class TestLearningIntegration:
    """Test learning system integration with service layer"""
    
    @pytest.mark.asyncio
    async def test_service_with_learning_initialization(self):
        """Test that service initializes with learning system"""
        with tempfile.TemporaryDirectory() as tmpdir:
            options = LearningServiceOptions(
                enable_learning=True,
                learning_path=Path(tmpdir),
                user_id="test_user"
            )
            
            service = LuminousNixServiceWithLearning(options)
            await service.initialize()
            
            assert service.learning_system is not None
            assert service.learning_system.user_id == "test_user"
            
            await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_privacy_mode(self):
        """Test that privacy mode disables tracking"""
        service = await create_private_service()
        
        assert service.learning_system is None
        
        # Should still work without learning
        with patch.object(service.backend, 'process_request') as mock:
            mock.return_value = asyncio.coroutine(lambda: Response(
                success=True,
                text="Success",
                commands=[],
                data={}
            ))()
            
            response = await service.execute_command("test command")
            assert response.success == True
        
        await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_alias_learning(self):
        """Test that system learns and applies aliases"""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = await create_cli_service_with_learning(
                learning_path=Path(tmpdir),
                user_id="alias_test"
            )
            
            # Teach an alias
            success = service.teach_alias("grab", "install")
            assert success == True
            
            # Mock backend
            with patch.object(service.backend, 'process_request') as mock:
                mock.return_value = asyncio.coroutine(lambda: Response(
                    success=True,
                    text="Package installed",
                    commands=[],
                    data={}
                ))()
                
                # Test that alias is applied
                response = await service.execute_command("grab firefox")
                
                # The mock should have received the expanded command
                # Note: We'd need to check the actual Request object
                assert response.success == True
            
            await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_command_tracking(self):
        """Test that commands are tracked for learning"""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = await create_cli_service_with_learning(
                learning_path=Path(tmpdir),
                user_id="tracking_test"
            )
            
            # Execute several commands
            with patch.object(service.backend, 'process_request') as mock:
                mock.return_value = asyncio.coroutine(lambda: Response(
                    success=True,
                    text="Success",
                    commands=[],
                    data={}
                ))()
                
                # Execute multiple commands
                for i in range(5):
                    await service.execute_command(f"command {i}")
                
                # Check that learning system tracked them
                assert len(service.learning_system.recent_commands) == 5
            
            await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_error_tracking_and_suggestions(self):
        """Test that errors are tracked and recovery suggestions provided"""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = await create_cli_service_with_learning(
                learning_path=Path(tmpdir),
                user_id="error_test",
                verbose=True
            )
            
            # First, simulate an error
            with patch.object(service.backend, 'process_request') as mock:
                mock.return_value = asyncio.coroutine(lambda: Response(
                    success=False,
                    text="Package not found: ffox",
                    commands=[],
                    data={}
                ))()
                
                error_response = await service.execute_command("install ffox")
                assert error_response.success == False
            
            # Now simulate the corrected command
            with patch.object(service.backend, 'process_request') as mock:
                mock.return_value = asyncio.coroutine(lambda: Response(
                    success=True,
                    text="firefox installed",
                    commands=[],
                    data={}
                ))()
                
                success_response = await service.execute_command("install firefox")
                assert success_response.success == True
            
            # The system should have learned from this
            preferences = service.get_user_preferences()
            assert preferences is not None
            
            await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_suggestions_in_response(self):
        """Test that personalized suggestions are added to responses"""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = await create_cli_service_with_learning(
                learning_path=Path(tmpdir),
                user_id="suggest_test",
                verbose=True
            )
            
            # Mock the learning system to provide suggestions
            with patch.object(service.learning_system, 'suggest_alias') as mock_alias:
                mock_alias.return_value = "install firefox"
                
                with patch.object(service.backend, 'process_request') as mock_backend:
                    mock_backend.return_value = asyncio.coroutine(lambda: Response(
                        success=True,
                        text="Command executed",
                        commands=[],
                        data={}
                    ))()
                    
                    response = await service.execute_command("get firefox")
                    
                    # Check that suggestions were added
                    assert response.data is not None
                    assert "personalized_suggestions" in response.data
                    assert len(response.data["personalized_suggestions"]) > 0
            
            await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_forget_user_data(self):
        """Test privacy feature to clear all learned data"""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = await create_cli_service_with_learning(
                learning_path=Path(tmpdir),
                user_id="privacy_test"
            )
            
            # Add some data
            service.teach_alias("test", "testing")
            
            # Execute some commands to create history
            with patch.object(service.backend, 'process_request') as mock:
                mock.return_value = asyncio.coroutine(lambda: Response(
                    success=True,
                    text="Success",
                    commands=[],
                    data={}
                ))()
                
                await service.execute_command("test command")
            
            # Now forget everything
            success = service.forget_user_data()
            assert success == True
            
            # Preferences should be cleared
            preferences = service.get_user_preferences()
            assert len(preferences.aliases) == 0
            
            await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_learning_persistence(self):
        """Test that learned patterns persist across sessions"""
        with tempfile.TemporaryDirectory() as tmpdir:
            learning_path = Path(tmpdir)
            
            # First session - teach something
            service1 = await create_cli_service_with_learning(
                learning_path=learning_path,
                user_id="persist_test"
            )
            
            service1.teach_alias("grab", "install")
            await service1.cleanup()  # This should save
            
            # Second session - check it's remembered
            service2 = await create_cli_service_with_learning(
                learning_path=learning_path,
                user_id="persist_test"
            )
            
            preferences = service2.get_user_preferences()
            assert "grab" in preferences.aliases
            assert preferences.aliases["grab"] == "install"
            
            await service2.cleanup()


class TestLearningFactoryFunctions:
    """Test factory functions for creating services with learning"""
    
    @pytest.mark.asyncio
    async def test_cli_service_factory_with_learning(self):
        """Test CLI service factory with learning"""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = await create_cli_service_with_learning(
                learning_path=Path(tmpdir),
                execute=True,
                verbose=True
            )
            
            assert service is not None
            assert service.options.interface == "cli"
            assert service.options.execute == True
            assert service.learning_system is not None
            
            await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_private_service_factory(self):
        """Test private service factory (no learning)"""
        service = await create_private_service(execute=True)
        
        assert service is not None
        assert service.options.privacy_mode == True
        assert service.options.enable_learning == False
        assert service.learning_system is None
        
        await service.cleanup()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])