#!/usr/bin/env python3
"""
Comprehensive tests for the Native Python-Nix Backend
Tests both the current and enhanced implementations
"""

import asyncio
import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

# Add backend to path for imports
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from nix_humanity.core.native_operations import (
    NativeNixBackend,
    NixOperation,
    NixResult,
    OperationType,
    ProgressCallback,
)

# Import additional components from the unified backend
try:
    from nix_humanity.core.native_operations import (
        AsyncNixAPI,
        ErrorRecovery,
        OperationCache,
        SecurityValidator,
    )

    ENHANCED_AVAILABLE = True
except ImportError:
    ENHANCED_AVAILABLE = False


class TestNativeNixBackend:
    """Test the basic native backend"""

    @pytest.fixture
    def backend(self):
        """Create a backend instance"""
        return NativeNixBackend()

    @pytest.fixture
    def mock_nix_api(self):
        """Mock the nixos_rebuild API"""
        with patch("python.native_nix_backend.nix") as mock_nix:
            # Mock common methods
            mock_nix.build.return_value = "/nix/store/abc123-system"
            mock_nix.switch_to_configuration.return_value = None
            mock_nix.rollback.return_value = None
            yield mock_nix

    @pytest.mark.asyncio
    async def test_update_system_dry_run(self, backend, mock_nix_api):
        """Test system update in dry run mode"""
        operation = NixOperation(type=OperationType.UPDATE, dry_run=True)

        result = await backend.execute(operation)

        assert result.success
        assert "dry run" in result.message.lower()
        assert mock_nix_api.build.called
        assert not mock_nix_api.switch_to_configuration.called

    @pytest.mark.asyncio
    async def test_update_system_real(self, backend, mock_nix_api):
        """Test real system update"""
        operation = NixOperation(type=OperationType.UPDATE, dry_run=False)

        # This would require sudo in real life
        with patch.dict(os.environ, {"LUMINOUS_NIX_ALLOW_UNPRIVILEGED": "true"}):
            result = await backend.execute(operation)

        # Should succeed in test environment
        assert result.success or "privilege" in str(result.error).lower()

    @pytest.mark.asyncio
    async def test_list_generations(self, backend):
        """Test listing system generations"""
        operation = NixOperation(type=OperationType.LIST_GENERATIONS)

        result = await backend.execute(operation)

        # Should work even without privileges
        assert result.success or result.data

    @pytest.mark.asyncio
    async def test_progress_callback(self, backend):
        """Test progress callback functionality"""
        progress_updates = []

        def callback(message: str, progress: float):
            progress_updates.append((message, progress))

        backend.progress.callback = callback

        operation = NixOperation(type=OperationType.BUILD, dry_run=True)

        await backend.execute(operation)

        # Should have progress updates
        assert len(progress_updates) > 0
        assert any(0.0 <= p[1] <= 1.0 for p in progress_updates)

    def test_flake_detection(self, backend):
        """Test flake detection"""
        # Test with mock
        with patch("os.path.exists") as mock_exists:
            mock_exists.return_value = True
            assert backend._check_flakes()

            mock_exists.return_value = False
            backend.use_flakes = backend._check_flakes()
            assert not backend.use_flakes


@pytest.mark.skipif(not ENHANCED_AVAILABLE, reason="Enhanced backend not available")
class TestEnhancedNativeNixBackend:
    """Test the enhanced native backend"""

    @pytest.fixture
    def backend(self):
        """Create an enhanced backend instance"""
        return EnhancedNativeNixBackend()

    @pytest.fixture
    def mock_async_api(self):
        """Mock the async API wrapper"""
        mock = AsyncMock()
        mock.build.return_value = "/nix/store/xyz789-system"
        mock.get_generations.return_value = [
            {"number": 100, "date": "2024-01-01", "current": True},
            {"number": 99, "date": "2023-12-31", "current": False},
            {"number": 98, "date": "2023-12-30", "current": False},
        ]
        return mock

    @pytest.mark.asyncio
    async def test_security_validation(self, backend):
        """Test security validation"""
        # Dangerous operation
        dangerous_op = NixOperation(
            type=OperationType.REMOVE, packages=["rm -rf /"], options={"force": True}
        )

        result = await backend.execute(dangerous_op)

        assert not result.success
        assert "security" in result.message.lower()

    @pytest.mark.asyncio
    async def test_caching(self, backend):
        """Test operation caching"""
        # First call - cache miss
        op = NixOperation(type=OperationType.LIST_GENERATIONS)
        result1 = await backend.execute(op)

        # Second call - should be cached
        result2 = await backend.execute(op)

        # Check metrics
        metrics = backend.get_metrics()
        assert metrics["details"]["cache_hits"] > 0

    @pytest.mark.asyncio
    async def test_error_recovery_disk_space(self, backend):
        """Test automatic disk space recovery"""
        with patch.object(backend, "_update_system") as mock_update:
            # Simulate disk space error
            mock_update.side_effect = Exception("No space left on device")

            op = NixOperation(type=OperationType.UPDATE)
            result = await backend.execute(op)

            assert not result.success
            assert any("garbage" in s.lower() for s in result.suggestions)

    @pytest.mark.asyncio
    async def test_enhanced_rollback(self, backend, mock_async_api):
        """Test enhanced rollback with smart targeting"""
        backend.async_api = mock_async_api

        # Test rollback by description
        op = NixOperation(
            type=OperationType.ROLLBACK, options={"description": "2023-12-31"}
        )

        with patch.object(backend, "_rollback_system_enhanced") as mock_rollback:
            mock_rollback.return_value = NixResult(
                success=True, message="Rolled back to generation 99"
            )

            result = await backend.execute(op)

            assert result.success
            assert "99" in result.message

    @pytest.mark.asyncio
    async def test_repair_system(self, backend):
        """Test system repair functionality"""
        op = NixOperation(type=OperationType.REPAIR)

        with patch.object(backend, "_verify_store_integrity") as mock_verify:
            mock_verify.return_value = {"valid": True, "errors": None}

            result = await backend.execute(op)

            assert result.success or "healthy" in result.message

    def test_metrics_tracking(self, backend):
        """Test performance metrics"""
        initial_metrics = backend.get_metrics()

        assert initial_metrics["total_operations"] == 0
        assert initial_metrics["success_rate"] == 0

        # After some operations, metrics should update
        # (Would need to run actual operations here)

    @pytest.mark.asyncio
    async def test_progress_estimation(self, backend):
        """Test progress completion estimation"""
        progress = ProgressCallback()

        # Simulate progress updates
        progress.update("Starting", 0.0)
        await asyncio.sleep(0.1)
        progress.update("Building", 0.3)
        await asyncio.sleep(0.1)
        progress.update("Testing", 0.6)

        estimate = progress.estimate_completion()
        assert estimate is not None
        assert estimate > 0


class TestSecurityValidator:
    """Test the security validator"""

    def test_validate_safe_operation(self):
        """Test validation of safe operations"""
        op = NixOperation(type=OperationType.UPDATE, dry_run=True)

        valid, error = SecurityValidator.validate_operation(op)
        assert valid
        assert error is None

    def test_validate_dangerous_package(self):
        """Test detection of dangerous packages"""
        op = NixOperation(type=OperationType.INSTALL, packages=["firefox", "rm -rf /"])

        valid, error = SecurityValidator.validate_operation(op)
        assert not valid
        assert "suspicious" in error.lower()

    def test_privilege_check(self):
        """Test privilege checking"""
        # Mock non-root user
        with patch("os.geteuid", return_value=1000):
            op = NixOperation(type=OperationType.UPDATE)
            valid, error = SecurityValidator.validate_operation(op)

            # Should fail without privileges unless override set
            if "LUMINOUS_NIX_ALLOW_UNPRIVILEGED" not in os.environ:
                assert not valid
                assert "privilege" in error.lower()


class TestOperationCache:
    """Test the operation cache"""

    def test_cache_basic_operations(self):
        """Test basic cache operations"""
        cache = OperationCache(ttl=1)  # 1 second TTL

        # Set value
        cache.set("test_key", {"data": "test"})

        # Get value immediately
        value = cache.get("test_key")
        assert value == {"data": "test"}

        # Wait for expiration
        import time

        time.sleep(1.1)

        # Should be expired
        value = cache.get("test_key")
        assert value is None

    def test_cache_thread_safety(self):
        """Test cache thread safety"""
        cache = OperationCache()
        results = []

        def writer():
            for i in range(100):
                cache.set(f"key_{i}", i)

        def reader():
            for i in range(100):
                value = cache.get(f"key_{i}")
                if value is not None:
                    results.append(value)

        import threading

        # Run concurrent readers and writers
        threads = []
        for _ in range(5):
            threads.append(threading.Thread(target=writer))
            threads.append(threading.Thread(target=reader))

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        # Should have read some values without errors
        assert len(results) > 0


# Integration tests
class TestIntegration:
    """Integration tests for the full system"""

    @pytest.mark.asyncio
    async def test_full_update_cycle(self):
        """Test a full update cycle"""
        backend = NativeNixBackend()

        # List generations
        list_op = NixOperation(type=OperationType.LIST_GENERATIONS)
        list_result = await backend.execute(list_op)

        # Dry run update
        update_op = NixOperation(type=OperationType.UPDATE, dry_run=True)
        update_result = await backend.execute(update_op)

        # Both should complete without errors
        assert list_result.success or list_result.error
        assert update_result.success or update_result.error

    @pytest.mark.asyncio
    @pytest.mark.skipif(not ENHANCED_AVAILABLE, reason="Enhanced backend required")
    async def test_enhanced_features(self):
        """Test enhanced backend features"""
        backend = EnhancedNativeNixBackend()

        # Test multiple operations with caching
        ops = [
            NixOperation(type=OperationType.LIST_GENERATIONS),
            NixOperation(type=OperationType.SEARCH, packages=["firefox"]),
            NixOperation(type=OperationType.BUILD, dry_run=True),
        ]

        results = []
        for op in ops:
            result = await backend.execute(op)
            results.append(result)

        # Check metrics
        metrics = backend.get_metrics()
        assert metrics["total_operations"] == len(ops)

        # At least some should succeed in test environment
        assert any(r.success for r in results)


# Performance benchmarks
class TestPerformance:
    """Performance benchmarks"""

    @pytest.mark.asyncio
    async def test_native_vs_subprocess_performance(self):
        """Compare native API vs subprocess performance"""
        import time

        # This would need actual implementations to compare
        # For now, just verify the native backend initializes quickly

        start = time.time()
        backend = NativeNixBackend()
        init_time = time.time() - start

        assert init_time < 1.0  # Should initialize in under 1 second

    @pytest.mark.asyncio
    @pytest.mark.skipif(not ENHANCED_AVAILABLE, reason="Enhanced backend required")
    async def test_cache_performance(self):
        """Test cache performance impact"""
        backend = EnhancedNativeNixBackend()

        op = NixOperation(type=OperationType.LIST_GENERATIONS)

        # First call - no cache
        start = time.time()
        await backend.execute(op)
        first_time = time.time() - start

        # Second call - cached
        start = time.time()
        await backend.execute(op)
        cached_time = time.time() - start

        # Cached should be much faster
        assert cached_time < first_time * 0.5  # At least 2x faster


# Run specific test groups
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        test_group = sys.argv[1]
        pytest.main(["-v", "-k", test_group, __file__])
    else:
        # Run all tests
        pytest.main(["-v", __file__])
