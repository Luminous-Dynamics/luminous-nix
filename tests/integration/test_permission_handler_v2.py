#!/usr/bin/env python3
"""
Comprehensive integration tests for the simplified permission handler.

Tests both SERVICE and DEVELOPMENT modes with various scenarios.
"""

import asyncio
import os
import subprocess
import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import pytest

from luminous_nix.self_healing.permission_handler_v2 import (
    NixOSPermissionHandler,
    ExecutionMode,
    ExecutionResult,
    ServiceExecutor,
    DevelopmentExecutor,
)


class TestPermissionHandlerModeDetection(TestCase):
    """Test mode detection logic"""
    
    def setUp(self):
        # Clear environment variables
        os.environ.pop('LUMINOUS_DEV_MODE', None)
        os.environ.pop('LUMINOUS_NO_SERVICE', None)
    
    def tearDown(self):
        # Clean up environment
        os.environ.pop('LUMINOUS_DEV_MODE', None)
        os.environ.pop('LUMINOUS_NO_SERVICE', None)
    
    def test_default_mode_is_service(self):
        """Default mode should be SERVICE (production)"""
        handler = NixOSPermissionHandler()
        self.assertEqual(handler.mode, ExecutionMode.SERVICE)
        self.assertIsInstance(handler.executor, ServiceExecutor)
    
    def test_dev_mode_with_env_var(self):
        """Should use DEVELOPMENT mode when LUMINOUS_DEV_MODE is set"""
        os.environ['LUMINOUS_DEV_MODE'] = '1'
        handler = NixOSPermissionHandler()
        self.assertEqual(handler.mode, ExecutionMode.DEVELOPMENT)
        self.assertIsInstance(handler.executor, DevelopmentExecutor)
    
    def test_dev_mode_with_no_service(self):
        """Should use DEVELOPMENT mode when LUMINOUS_NO_SERVICE is set"""
        os.environ['LUMINOUS_NO_SERVICE'] = '1'
        handler = NixOSPermissionHandler()
        self.assertEqual(handler.mode, ExecutionMode.DEVELOPMENT)
        self.assertIsInstance(handler.executor, DevelopmentExecutor)
    
    def test_get_status(self):
        """Test status reporting"""
        handler = NixOSPermissionHandler()
        status = handler.get_status()
        
        self.assertIn('mode', status)
        self.assertIn('mode_description', status)
        self.assertIn('executor_type', status)
        self.assertIn('is_production', status)
        self.assertIn('capabilities', status)
        
        # In default mode
        self.assertEqual(status['mode'], 'service')
        self.assertTrue(status['is_production'])
        self.assertIsInstance(status['capabilities'], list)


class TestServiceExecutor(TestCase):
    """Test SERVICE mode executor"""
    
    @pytest.mark.asyncio
    async def test_service_executor_initialization(self):
        """Test ServiceExecutor initialization"""
        executor = ServiceExecutor()
        self.assertEqual(executor.socket_path, Path("/run/luminous-healing.sock"))
        self.assertIsNone(executor._client)
    
    @pytest.mark.asyncio
    async def test_service_executor_capabilities(self):
        """Test capability listing"""
        executor = ServiceExecutor()
        capabilities = executor.get_capabilities()
        
        self.assertIsInstance(capabilities, list)
        self.assertIn('restart_service', capabilities)
        self.assertIn('clean_nix_store', capabilities)
        self.assertIn('rollback_generation', capabilities)
        self.assertEqual(len(capabilities), 8)  # Should have exactly 8 capabilities
    
    @pytest.mark.asyncio
    async def test_service_executor_with_mock_client(self):
        """Test service executor with mocked client"""
        executor = ServiceExecutor()
        
        # Mock the privileged client
        mock_client = AsyncMock()
        mock_client.is_available.return_value = True
        mock_client.execute_privileged_action.return_value = {
            'success': True,
            'output': 'Service restarted',
            'duration_ms': 100
        }
        
        with patch('luminous_nix.self_healing.permission_handler_v2.PrivilegedHealingClient', return_value=mock_client):
            result = await executor.execute('restart_service', {'service': 'nginx'})
        
        self.assertTrue(result.success)
        self.assertEqual(result.output, 'Service restarted')
        self.assertEqual(result.duration_ms, 100)
        mock_client.execute_privileged_action.assert_called_once_with('restart_service', {'service': 'nginx'})
    
    @pytest.mark.asyncio
    async def test_service_executor_unavailable(self):
        """Test service executor when service is not running"""
        executor = ServiceExecutor()
        
        # Mock unavailable client
        mock_client = AsyncMock()
        mock_client.is_available.return_value = False
        
        with patch('luminous_nix.self_healing.permission_handler_v2.PrivilegedHealingClient', return_value=mock_client):
            with self.assertRaises(RuntimeError) as context:
                await executor.execute('restart_service', {'service': 'nginx'})
            
            self.assertIn("service not running", str(context.exception).lower())


class TestDevelopmentExecutor(TestCase):
    """Test DEVELOPMENT mode executor"""
    
    def test_development_executor_initialization(self):
        """Test DevelopmentExecutor initialization"""
        with patch('luminous_nix.self_healing.permission_handler_v2.DevelopmentExecutor._check_sudo', return_value=True):
            executor = DevelopmentExecutor()
            self.assertTrue(executor.has_sudo)
    
    def test_check_sudo_available(self):
        """Test sudo availability check when sudo works"""
        executor = DevelopmentExecutor()
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            self.assertTrue(executor._check_sudo())
            mock_run.assert_called_once()
    
    def test_check_sudo_unavailable(self):
        """Test sudo availability check when sudo fails"""
        executor = DevelopmentExecutor()
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1
            self.assertFalse(executor._check_sudo())
    
    @pytest.mark.asyncio
    async def test_unknown_action(self):
        """Test handling of unknown actions"""
        executor = DevelopmentExecutor()
        result = await executor.execute('unknown_action', {})
        
        self.assertFalse(result.success)
        self.assertIn("Unknown action", result.error)
    
    @pytest.mark.asyncio
    async def test_restart_service_with_sudo(self):
        """Test service restart with sudo available"""
        executor = DevelopmentExecutor()
        executor.has_sudo = True
        executor.is_root = False
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "Service restarted"
            mock_run.return_value.stderr = ""
            
            result = await executor._restart_service({'service': 'nginx'})
            
            self.assertTrue(result.success)
            self.assertEqual(result.output, "Service restarted")
            mock_run.assert_called_once_with(
                ['sudo', 'systemctl', 'restart', 'nginx'],
                capture_output=True,
                text=True,
                timeout=30
            )
    
    @pytest.mark.asyncio
    async def test_restart_service_without_privileges(self):
        """Test service restart without sudo or root"""
        executor = DevelopmentExecutor()
        executor.has_sudo = False
        executor.is_root = False
        
        result = await executor._restart_service({'service': 'nginx'})
        
        self.assertFalse(result.success)
        self.assertEqual(result.error, "Insufficient privileges")
        self.assertIn("sudo systemctl restart nginx", result.suggestion)
    
    @pytest.mark.asyncio
    async def test_clean_nix_store(self):
        """Test nix store cleanup"""
        executor = DevelopmentExecutor()
        executor.has_sudo = True
        executor.is_root = False
        
        with patch('subprocess.run') as mock_run:
            # First call for nix-collect-garbage
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "100 MB freed"
            
            result = await executor._clean_nix_store({'older_than_days': 7})
            
            self.assertTrue(result.success)
            self.assertIn("freed", result.output)
    
    @pytest.mark.asyncio
    async def test_set_cpu_governor(self):
        """Test CPU governor setting"""
        executor = DevelopmentExecutor()
        executor.has_sudo = True
        executor.is_root = False
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = ""
            mock_run.return_value.stderr = ""
            
            result = await executor._set_cpu_governor({'governor': 'performance'})
            
            self.assertTrue(result.success)
            self.assertIn("performance", result.output)
            mock_run.assert_called_once_with(
                ['sudo', 'cpupower', 'frequency-set', '-g', 'performance'],
                capture_output=True,
                text=True,
                timeout=10
            )


class TestPermissionHandlerIntegration(TestCase):
    """Integration tests for the complete permission handler"""
    
    @pytest.mark.asyncio
    async def test_development_mode_full_flow(self):
        """Test complete flow in development mode"""
        os.environ['LUMINOUS_DEV_MODE'] = '1'
        
        handler = NixOSPermissionHandler()
        self.assertEqual(handler.mode, ExecutionMode.DEVELOPMENT)
        
        # Mock subprocess for clean test
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "Success"
            
            # Mock sudo check
            with patch.object(handler.executor, 'has_sudo', True):
                result = await handler.execute('restart_service', {'service': 'test'})
            
            self.assertTrue(result.success)
            self.assertEqual(result.mode, ExecutionMode.DEVELOPMENT)
    
    @pytest.mark.asyncio
    async def test_service_mode_full_flow(self):
        """Test complete flow in service mode"""
        # Clear dev mode
        os.environ.pop('LUMINOUS_DEV_MODE', None)
        
        handler = NixOSPermissionHandler()
        self.assertEqual(handler.mode, ExecutionMode.SERVICE)
        
        # Mock the privileged client
        mock_client = AsyncMock()
        mock_client.is_available.return_value = True
        mock_client.execute_privileged_action.return_value = {
            'success': True,
            'output': 'Action completed',
            'duration_ms': 50
        }
        
        with patch('luminous_nix.self_healing.permission_handler_v2.PrivilegedHealingClient', return_value=mock_client):
            result = await handler.execute('clean_nix_store', {'older_than_days': 7})
        
        self.assertTrue(result.success)
        self.assertEqual(result.mode, ExecutionMode.SERVICE)
        self.assertEqual(result.output, 'Action completed')
    
    @pytest.mark.asyncio
    async def test_error_handling_with_suggestions(self):
        """Test error handling and suggestions"""
        handler = NixOSPermissionHandler()
        
        # Test service not running error
        mock_client = AsyncMock()
        mock_client.is_available.return_value = False
        
        with patch('luminous_nix.self_healing.permission_handler_v2.PrivilegedHealingClient', return_value=mock_client):
            result = await handler.execute('restart_service', {'service': 'test'})
        
        self.assertFalse(result.success)
        self.assertIsNotNone(result.suggestion)
        self.assertIn("services.luminous-healing.enable", result.suggestion)
    
    def test_error_suggestions(self):
        """Test various error suggestions"""
        handler = NixOSPermissionHandler()
        
        # Test permission denied suggestion
        suggestion = handler._get_error_suggestion("Permission denied")
        self.assertIn("LUMINOUS_DEV_MODE", suggestion)
        
        # Test socket not found suggestion
        suggestion = handler._get_error_suggestion("Socket not found")
        self.assertIn("systemctl status", suggestion)
        
        # Test generic error suggestion
        suggestion = handler._get_error_suggestion("Unknown error")
        self.assertIn("journalctl", suggestion)


class TestExecutionResult(TestCase):
    """Test ExecutionResult dataclass"""
    
    def test_execution_result_creation(self):
        """Test creating ExecutionResult"""
        result = ExecutionResult(
            success=True,
            output="Test output",
            error=None,
            mode=ExecutionMode.SERVICE,
            suggestion=None,
            duration_ms=100
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.output, "Test output")
        self.assertIsNone(result.error)
        self.assertEqual(result.mode, ExecutionMode.SERVICE)
        self.assertEqual(result.duration_ms, 100)
    
    def test_execution_result_defaults(self):
        """Test ExecutionResult with defaults"""
        result = ExecutionResult(success=False)
        
        self.assertFalse(result.success)
        self.assertIsNone(result.output)
        self.assertIsNone(result.error)
        self.assertIsNone(result.mode)
        self.assertIsNone(result.suggestion)
        self.assertEqual(result.duration_ms, 0)


class TestSpecificActions(TestCase):
    """Test specific healing actions"""
    
    @pytest.mark.asyncio
    async def test_clear_cache_action(self):
        """Test cache clearing action"""
        executor = DevelopmentExecutor()
        executor.has_sudo = True
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "Cache cleared"
            
            result = await executor._clear_cache({})
            
            self.assertTrue(result.success)
            # Should call sync and echo commands
            self.assertEqual(mock_run.call_count, 2)
    
    @pytest.mark.asyncio
    async def test_rollback_generation(self):
        """Test NixOS generation rollback"""
        executor = DevelopmentExecutor()
        executor.has_sudo = True
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "Rolled back"
            
            result = await executor._rollback_generation({})
            
            self.assertTrue(result.success)
            self.assertIn("rolled back", result.output.lower())
    
    @pytest.mark.asyncio
    async def test_kill_process(self):
        """Test process killing"""
        executor = DevelopmentExecutor()
        executor.has_sudo = False  # Should work without sudo
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            
            result = await executor._kill_process({'pid': 12345, 'signal': 15})
            
            self.assertTrue(result.success)
            mock_run.assert_called_once_with(
                ['kill', '-15', '12345'],
                capture_output=True,
                text=True,
                timeout=5
            )


class TestEdgeCases(TestCase):
    """Test edge cases and error conditions"""
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test command timeout handling"""
        executor = DevelopmentExecutor()
        executor.has_sudo = True
        
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired('cmd', 30)
            
            result = await executor._restart_service({'service': 'slow-service'})
            
            self.assertFalse(result.success)
            self.assertIn("timeout", result.error.lower())
    
    @pytest.mark.asyncio
    async def test_missing_parameters(self):
        """Test handling of missing parameters"""
        executor = DevelopmentExecutor()
        
        # Test missing service parameter
        result = await executor._restart_service({})
        self.assertFalse(result.success)
        self.assertIn("No service specified", result.error)
        
        # Test missing PID parameter
        result = await executor._kill_process({})
        self.assertFalse(result.success)
        self.assertIn("No PID specified", result.error)
    
    @pytest.mark.asyncio
    async def test_exception_handling(self):
        """Test general exception handling"""
        handler = NixOSPermissionHandler()
        
        # Force an exception
        with patch.object(handler.executor, 'execute', side_effect=Exception("Test error")):
            result = await handler.execute('test_action', {})
        
        self.assertFalse(result.success)
        self.assertEqual(result.error, "Test error")
        self.assertIsNotNone(result.suggestion)


class TestPermissionEscalation(TestCase):
    """Test permission escalation scenarios"""
    
    @pytest.mark.asyncio
    async def test_root_user_no_sudo_needed(self):
        """Test that root user doesn't need sudo"""
        executor = DevelopmentExecutor()
        executor.is_root = True
        executor.has_sudo = False  # Shouldn't matter
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            
            result = await executor._restart_service({'service': 'test'})
            
            self.assertTrue(result.success)
            # Should NOT have sudo in command
            called_cmd = mock_run.call_args[0][0]
            self.assertNotIn('sudo', called_cmd)
            self.assertEqual(called_cmd[0], 'systemctl')
    
    @pytest.mark.asyncio
    async def test_regular_user_needs_sudo(self):
        """Test that regular user needs sudo"""
        executor = DevelopmentExecutor()
        executor.is_root = False
        executor.has_sudo = True
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            
            result = await executor._restart_service({'service': 'test'})
            
            self.assertTrue(result.success)
            # Should have sudo in command
            called_cmd = mock_run.call_args[0][0]
            self.assertEqual(called_cmd[0], 'sudo')


if __name__ == "__main__":
    # Run async tests with pytest
    import sys
    sys.exit(pytest.main([__file__, '-v']))