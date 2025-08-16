#!/usr/bin/env python3
"""
Integration tests for the simplified V2 self-healing system.
Tests the complete flow from detection to resolution.
"""

import asyncio
import pytest
import tempfile
import os
from unittest.mock import MagicMock, patch, AsyncMock
from pathlib import Path

from luminous_nix.self_healing import (
    create_self_healing_engine,
    quick_heal,
    SimplifiedHealingEngine,
    SimpleDetector,
    SimpleResolver,
    Issue,
    IssueType,
    Severity,
    execute_healing_action,
    get_permission_status,
)


class TestSelfHealingIntegration:
    """Integration tests for complete self-healing flow"""
    
    @pytest.fixture
    def mock_system_monitor(self):
        """Mock system monitor for testing"""
        monitor = MagicMock()
        monitor.get_health_metrics = AsyncMock(return_value={
            'cpu': {'percent': 50.0},
            'memory': {'percent': 60.0},
            'disk': {'percent': 70.0},
            'services': {
                'nginx': {'running': True},
                'postgresql': {'running': False}
            }
        })
        return monitor
    
    @pytest.fixture
    def healing_engine(self, mock_system_monitor):
        """Create test healing engine"""
        engine = SimplifiedHealingEngine()
        engine.dry_run = True  # Don't actually execute
        with patch('luminous_nix.environmental.get_system_monitor', return_value=mock_system_monitor):
            engine.detector.monitor = mock_system_monitor
        return engine
    
    @pytest.mark.asyncio
    async def test_no_issues_detected(self, healing_engine, mock_system_monitor):
        """Test when system is healthy"""
        # Set healthy metrics
        mock_system_monitor.get_health_metrics.return_value = {
            'cpu': {'percent': 30.0},
            'memory': {'percent': 40.0},
            'disk': {'percent': 50.0},
            'services': {'nginx': {'running': True}}
        }
        
        results = await healing_engine.detect_and_heal()
        
        assert len(results) == 0
        assert healing_engine.metrics['issues_detected'] == 0
        assert healing_engine.metrics['issues_resolved'] == 0
    
    @pytest.mark.asyncio
    async def test_high_cpu_detection(self, healing_engine, mock_system_monitor):
        """Test detection of high CPU usage"""
        # Set high CPU
        mock_system_monitor.get_health_metrics.return_value = {
            'cpu': {'percent': 85.0},
            'memory': {'percent': 40.0},
            'disk': {'percent': 50.0},
            'services': {}
        }
        
        results = await healing_engine.detect_and_heal()
        
        # Should detect but not fix (MEDIUM severity in dry run)
        assert healing_engine.metrics['issues_detected'] == 1
        assert len(results) == 0  # Medium priority not auto-fixed
    
    @pytest.mark.asyncio
    async def test_critical_disk_space(self, healing_engine, mock_system_monitor):
        """Test critical disk space triggers healing"""
        # Set critical disk usage
        mock_system_monitor.get_health_metrics.return_value = {
            'cpu': {'percent': 30.0},
            'memory': {'percent': 40.0},
            'disk': {'percent': 96.0},  # Critical!
            'services': {}
        }
        
        results = await healing_engine.detect_and_heal()
        
        assert healing_engine.metrics['issues_detected'] == 1
        assert len(results) == 1
        assert results[0].action_taken == '[DRY RUN] clean_nix_store'
        assert results[0].success
    
    @pytest.mark.asyncio
    async def test_service_restart(self, healing_engine, mock_system_monitor):
        """Test service restart healing"""
        # Service not running
        mock_system_monitor.get_health_metrics.return_value = {
            'cpu': {'percent': 30.0},
            'memory': {'percent': 40.0},
            'disk': {'percent': 50.0},
            'services': {
                'postgresql': {'running': False}
            }
        }
        
        results = await healing_engine.detect_and_heal()
        
        assert healing_engine.metrics['issues_detected'] == 1
        assert len(results) == 1
        assert results[0].action_taken == '[DRY RUN] restart_service'
        assert results[0].success
    
    @pytest.mark.asyncio
    async def test_multiple_issues(self, healing_engine, mock_system_monitor):
        """Test handling multiple issues"""
        # Multiple problems
        mock_system_monitor.get_health_metrics.return_value = {
            'cpu': {'percent': 92.0},  # High
            'memory': {'percent': 96.0},  # High
            'disk': {'percent': 95.0},  # Critical
            'services': {
                'nginx': {'running': False},
                'postgresql': {'running': False}
            }
        }
        
        results = await healing_engine.detect_and_heal()
        
        # Should handle all high/critical issues
        assert healing_engine.metrics['issues_detected'] == 5
        assert len(results) >= 4  # High/critical issues get fixed
        
        # Check action diversity
        actions = [r.action_taken for r in results]
        assert any('restart_service' in a for a in actions)
        assert any('clean_nix_store' in a for a in actions)
        assert any('clear_system_cache' in a for a in actions)


class TestDetectorIntegration:
    """Test the detection subsystem"""
    
    @pytest.fixture
    def detector(self):
        """Create test detector"""
        detector = SimpleDetector()
        return detector
    
    @pytest.mark.asyncio
    async def test_threshold_configuration(self, detector):
        """Test threshold configuration"""
        # Default thresholds
        assert detector.thresholds['cpu_percent'] == 80.0
        assert detector.thresholds['memory_percent'] == 85.0
        assert detector.thresholds['disk_percent'] == 90.0
        
        # Update thresholds
        detector.thresholds['cpu_percent'] = 60.0
        assert detector.thresholds['cpu_percent'] == 60.0
    
    @pytest.mark.asyncio
    async def test_severity_assignment(self, detector):
        """Test correct severity assignment"""
        # Create mock data structures
        from dataclasses import dataclass
        
        @dataclass
        class MockCPU:
            percent: float
            
        @dataclass
        class MockMemory:
            percent_used: float
            
        @dataclass
        class MockDisk:
            percent_used: float
        
        with patch.object(detector.monitor, 'update_category', new_callable=AsyncMock) as mock_update, \
             patch.object(detector.monitor, 'get_state') as mock_state:
            # Test CPU severity levels (Medium)
            mock_state.return_value = {
                'cpu': MockCPU(percent=85.0),
                'memory': MockMemory(percent_used=0),
                'disk': [MockDisk(percent_used=0)],
                'services': []
            }
            issues = await detector.detect_issues()
            assert len(issues) == 1
            assert issues[0].severity == Severity.MEDIUM
            
            # Test critical CPU (High)
            mock_state.return_value = {
                'cpu': MockCPU(percent=95.0),
                'memory': MockMemory(percent_used=0),
                'disk': [MockDisk(percent_used=0)],
                'services': []
            }
            issues = await detector.detect_issues()
            assert issues[0].severity == Severity.HIGH


class TestResolverIntegration:
    """Test the resolution subsystem"""
    
    @pytest.fixture
    def resolver(self):
        """Create test resolver"""
        return SimpleResolver()
    
    def test_service_issue_resolution(self, resolver):
        """Test service issue resolution"""
        issue = Issue(
            type=IssueType.SERVICE,
            severity=Severity.HIGH,
            description="nginx not running",
            component="nginx",
            metric_value=0,
            threshold=1
        )
        
        action = resolver.get_action(issue)
        
        assert action['action'] == 'restart_service'
        assert action['parameters']['service'] == 'nginx'
    
    def test_resource_issue_resolution(self, resolver):
        """Test resource issue resolution"""
        # CPU issue
        cpu_issue = Issue(
            type=IssueType.RESOURCE,
            severity=Severity.HIGH,
            description="High CPU",
            component="cpu",
            metric_value=90,
            threshold=80
        )
        action = resolver.get_action(cpu_issue)
        assert action['action'] == 'set_cpu_governor'
        
        # Memory issue
        mem_issue = Issue(
            type=IssueType.RESOURCE,
            severity=Severity.HIGH,
            description="High memory",
            component="memory",
            metric_value=90,
            threshold=85
        )
        action = resolver.get_action(mem_issue)
        assert action['action'] == 'clear_system_cache'
        
        # Disk issue
        disk_issue = Issue(
            type=IssueType.RESOURCE,
            severity=Severity.CRITICAL,
            description="Low disk",
            component="disk",
            metric_value=95,
            threshold=90
        )
        action = resolver.get_action(disk_issue)
        assert action['action'] == 'clean_nix_store'
    
    def test_system_issue_resolution(self, resolver):
        """Test system issue resolution"""
        issue = Issue(
            type=IssueType.SYSTEM,
            severity=Severity.CRITICAL,
            description="System corruption",
            component="system",
            metric_value=0,
            threshold=0
        )
        
        action = resolver.get_action(issue)
        assert action['action'] == 'rollback_generation'


class TestPermissionIntegration:
    """Test permission system integration"""
    
    def test_permission_status(self):
        """Test permission status check"""
        status = get_permission_status()
        
        assert 'mode' in status
        assert 'is_production' in status
        assert 'capabilities' in status
        assert status['mode'] in ['service', 'dev']
    
    @pytest.mark.asyncio
    async def test_healing_action_execution(self):
        """Test healing action execution"""
        # Force dev mode for testing
        os.environ['LUMINOUS_DEV_MODE'] = '1'
        
        try:
            # Test a safe action
            result = await execute_healing_action('clear_system_cache', {})
            
            # Check mode - can be enum or string
            from luminous_nix.self_healing import ExecutionMode
            assert result.mode in [ExecutionMode.SERVICE, ExecutionMode.DEVELOPMENT, 'SERVICE', 'DEVELOPMENT']
            # In dev mode, it might fail due to permissions
            if not result.success:
                assert result.error is not None
                assert result.suggestion is not None
        finally:
            # Clean up
            if 'LUMINOUS_DEV_MODE' in os.environ:
                del os.environ['LUMINOUS_DEV_MODE']


class TestQuickHeal:
    """Test the quick heal convenience function"""
    
    @pytest.mark.asyncio
    async def test_quick_heal_function(self):
        """Test quick heal runs a single cycle"""
        with patch('luminous_nix.environmental.get_system_monitor') as mock_monitor:
            mock_monitor.return_value.get_health_metrics = AsyncMock(return_value={
                'cpu': {'percent': 30.0},
                'memory': {'percent': 40.0},
                'disk': {'percent': 50.0},
                'services': {}
            })
            
            results = await quick_heal()
            
            assert isinstance(results, list)
            # With healthy system, should return empty
            assert len(results) == 0


class TestEngineLifecycle:
    """Test engine lifecycle management"""
    
    @pytest.mark.asyncio
    async def test_engine_creation(self):
        """Test engine creation"""
        engine = create_self_healing_engine()
        
        assert isinstance(engine, SimplifiedHealingEngine)
        assert engine.healing_enabled
        assert not engine.dry_run
        assert engine.metrics['issues_detected'] == 0
    
    @pytest.mark.asyncio
    async def test_engine_metrics(self):
        """Test metrics tracking"""
        engine = create_self_healing_engine()
        engine.dry_run = True
        
        # Create mock data structures
        from dataclasses import dataclass
        
        @dataclass
        class MockCPU:
            percent: float
            
        @dataclass
        class MockMemory:
            percent_used: float
            
        @dataclass
        class MockDisk:
            percent_used: float
            
        with patch.object(engine.detector.monitor, 'update_category', new_callable=AsyncMock) as mock_update, \
             patch.object(engine.detector.monitor, 'get_state') as mock:
            mock.return_value = {
                'cpu': MockCPU(percent=95.0),
                'memory': MockMemory(percent_used=40.0),
                'disk': [MockDisk(percent_used=50.0)],
                'services': []
            }
            
            await engine.detect_and_heal()
            
            metrics = engine.get_metrics()
            assert metrics['issues_detected'] > 0
            assert 'success_rate' in metrics
            assert metrics['last_check'] is not None
    
    @pytest.mark.asyncio
    async def test_continuous_monitoring(self):
        """Test continuous monitoring (quick test)"""
        engine = create_self_healing_engine()
        engine.dry_run = True
        
        # Create mock data structures
        from dataclasses import dataclass
        
        @dataclass
        class MockCPU:
            percent: float
            
        @dataclass
        class MockMemory:
            percent_used: float
            
        @dataclass
        class MockDisk:
            percent_used: float
            
        with patch.object(engine.detector.monitor, 'update_category', new_callable=AsyncMock) as mock_update, \
             patch.object(engine.detector.monitor, 'get_state') as mock:
            mock.return_value = {
                'cpu': MockCPU(percent=30.0),
                'memory': MockMemory(percent_used=40.0),
                'disk': [MockDisk(percent_used=50.0)],
                'services': []
            }
            
            # Start monitoring
            task = asyncio.create_task(engine.start_monitoring(interval=0.1))
            
            # Let it run briefly
            await asyncio.sleep(0.3)
            
            # Cancel
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            
            # Should have run at least once
            assert engine.metrics['last_check'] is not None


@pytest.mark.integration
class TestCompleteFlow:
    """Test complete integration flow"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_healing(self):
        """Test complete flow from detection to resolution"""
        # This test simulates a complete healing cycle
        engine = create_self_healing_engine()
        engine.dry_run = True  # Don't actually modify system
        
        # Mock unhealthy system
        with patch('luminous_nix.environmental.get_system_monitor') as mock_monitor:
            mock_instance = MagicMock()
            mock_instance.get_health_metrics = AsyncMock(return_value={
                'cpu': {'percent': 30.0},
                'memory': {'percent': 96.0},  # High!
                'disk': {'percent': 95.0},  # Critical!
                'services': {
                    'nginx': {'running': False}  # Service down!
                }
            })
            mock_monitor.return_value = mock_instance
            engine.detector.monitor = mock_instance
            
            # Run healing
            results = await engine.detect_and_heal()
            
            # Verify detection
            assert engine.metrics['issues_detected'] == 3
            
            # Verify healing attempts
            assert len(results) == 3
            
            # Verify correct actions taken
            actions = [r.action_taken for r in results]
            assert any('clear_system_cache' in a for a in actions)  # Memory
            assert any('clean_nix_store' in a for a in actions)  # Disk
            assert any('restart_service' in a for a in actions)  # Service
            
            # All should succeed in dry run
            assert all(r.success for r in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])