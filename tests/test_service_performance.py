#!/usr/bin/env python3
"""
⚡ Performance Tests for Service Layer

Ensures the service layer meets performance requirements:
- Command execution < 100ms (with caching)
- Initialization < 50ms
- Concurrent operations scale linearly
- Memory usage stays bounded
"""

import asyncio
import time
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from luminous_nix.api.schema import Response
from luminous_nix.service_simple import LuminousNixService, ServiceOptions


class TestPerformanceMetrics:
    """Test performance characteristics of service layer"""
    
    @pytest.mark.asyncio
    async def test_initialization_speed(self):
        """Test that service initialization is fast (<50ms)"""
        start = time.perf_counter()
        
        with patch('luminous_nix.service_simple.NixForHumanityBackend'):
            service = LuminousNixService()
            await service.initialize()
        
        elapsed = (time.perf_counter() - start) * 1000  # Convert to ms
        
        assert elapsed < 50, f"Initialization took {elapsed:.2f}ms (should be <50ms)"
    
    @pytest.mark.asyncio
    async def test_command_execution_speed(self):
        """Test that command execution is fast (<100ms with cache)"""
        service = LuminousNixService()
        
        # Mock fast response
        mock_response = Response(
            success=True,
            text="Command executed",
            commands=["nix-env -iA nixos.firefox"],
            data={}
        )
        
        with patch('luminous_nix.service_simple.NixForHumanityBackend') as mock_backend_class:
            mock_backend = AsyncMock()
            mock_backend.process_request = AsyncMock(return_value=mock_response)
            mock_backend_class.return_value = mock_backend
            
            # Warm up
            await service.execute_command("warmup")
            
            # Measure
            start = time.perf_counter()
            result = await service.execute_command("install firefox")
            elapsed = (time.perf_counter() - start) * 1000
            
            assert result.success == True
            assert elapsed < 100, f"Execution took {elapsed:.2f}ms (should be <100ms)"
    
    @pytest.mark.asyncio
    async def test_concurrent_performance(self):
        """Test that concurrent operations scale well"""
        service = LuminousNixService()
        
        mock_response = Response(
            success=True,
            text="OK",
            commands=[],
            data={}
        )
        
        async def delayed_response(request):
            await asyncio.sleep(0.01)  # 10ms delay
            return mock_response
        
        with patch('luminous_nix.service_simple.NixForHumanityBackend') as mock_backend_class:
            mock_backend = AsyncMock()
            mock_backend.process_request = delayed_response
            mock_backend_class.return_value = mock_backend
            
            # Sequential execution (baseline)
            start = time.perf_counter()
            for _ in range(5):
                await service.execute_command("test")
            sequential_time = time.perf_counter() - start
            
            # Concurrent execution
            start = time.perf_counter()
            tasks = [service.execute_command("test") for _ in range(5)]
            await asyncio.gather(*tasks)
            concurrent_time = time.perf_counter() - start
            
            # Concurrent should be much faster
            speedup = sequential_time / concurrent_time
            assert speedup > 3, f"Concurrent speedup only {speedup:.1f}x (should be >3x)"
    
    @pytest.mark.asyncio
    async def test_high_load_stability(self):
        """Test service stability under high load"""
        service = LuminousNixService()
        
        mock_response = Response(
            success=True,
            text="OK",
            commands=[],
            data={}
        )
        
        with patch('luminous_nix.service_simple.NixForHumanityBackend') as mock_backend_class:
            mock_backend = AsyncMock()
            mock_backend.process_request = AsyncMock(return_value=mock_response)
            mock_backend_class.return_value = mock_backend
            
            # Execute many commands concurrently
            tasks = [service.execute_command(f"command-{i}") for i in range(100)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # All should succeed
            failures = [r for r in results if isinstance(r, Exception)]
            assert len(failures) == 0, f"Had {len(failures)} failures under load"
            
            # All should be successful
            assert all(r.success for r in results)
    
    @pytest.mark.asyncio
    async def test_memory_efficiency(self):
        """Test that service doesn't leak memory"""
        import gc
        import tracemalloc
        
        tracemalloc.start()
        
        service = LuminousNixService()
        
        mock_response = Response(
            success=True,
            text="OK",
            commands=[],
            data={"large_data": "x" * 1000}  # Some data
        )
        
        with patch('luminous_nix.service_simple.NixForHumanityBackend') as mock_backend_class:
            mock_backend = AsyncMock()
            mock_backend.process_request = AsyncMock(return_value=mock_response)
            mock_backend_class.return_value = mock_backend
            
            # Take baseline
            gc.collect()
            snapshot1 = tracemalloc.take_snapshot()
            
            # Execute many commands
            for i in range(100):
                await service.execute_command(f"command-{i}")
            
            # Force cleanup
            await service.cleanup()
            gc.collect()
            
            # Check memory
            snapshot2 = tracemalloc.take_snapshot()
            top_stats = snapshot2.compare_to(snapshot1, 'lineno')
            
            # Calculate total memory growth
            total_growth = sum(stat.size_diff for stat in top_stats if stat.size_diff > 0)
            
            # Should be less than 10MB growth
            assert total_growth < 10 * 1024 * 1024, f"Memory grew by {total_growth / 1024 / 1024:.2f}MB"
            
            tracemalloc.stop()
    
    @pytest.mark.asyncio
    async def test_alias_performance(self):
        """Test that alias operations are fast"""
        service = LuminousNixService()
        
        with patch.object(service, '_create_symlink'):
            # Measure alias creation
            start = time.perf_counter()
            for i in range(100):
                service.create_alias(f"alias-{i}")
            elapsed = (time.perf_counter() - start) * 1000
            
            assert elapsed < 100, f"Creating 100 aliases took {elapsed:.2f}ms"
            
            # Measure listing
            start = time.perf_counter()
            aliases = service.list_aliases()
            elapsed = (time.perf_counter() - start) * 1000
            
            assert len(aliases) == 100
            assert elapsed < 10, f"Listing 100 aliases took {elapsed:.2f}ms"
    
    @pytest.mark.asyncio
    async def test_response_time_consistency(self):
        """Test that response times are consistent (low variance)"""
        service = LuminousNixService()
        
        mock_response = Response(
            success=True,
            text="OK",
            commands=[],
            data={}
        )
        
        with patch('luminous_nix.service_simple.NixForHumanityBackend') as mock_backend_class:
            mock_backend = AsyncMock()
            mock_backend.process_request = AsyncMock(return_value=mock_response)
            mock_backend_class.return_value = mock_backend
            
            times = []
            for _ in range(20):
                start = time.perf_counter()
                await service.execute_command("test")
                elapsed = (time.perf_counter() - start) * 1000
                times.append(elapsed)
            
            # Calculate statistics
            avg_time = sum(times) / len(times)
            variance = sum((t - avg_time) ** 2 for t in times) / len(times)
            std_dev = variance ** 0.5
            
            # Standard deviation should be low (consistent times)
            assert std_dev < 5, f"Response time std dev {std_dev:.2f}ms (should be <5ms)"
            assert max(times) - min(times) < 10, "Response time range too large"


class TestCachingPerformance:
    """Test caching impact on performance"""
    
    @pytest.mark.asyncio
    async def test_cache_hit_performance(self):
        """Test that cached responses are much faster"""
        from luminous_nix.utils.cache import get_default_cache_manager
        
        service = LuminousNixService()
        cache = get_default_cache_manager()
        
        # Pre-populate cache
        cache.set("test-key", {"result": "cached"}, ttl=60)
        
        mock_response = Response(
            success=True,
            text="From cache",
            commands=[],
            data={"result": "cached"}
        )
        
        with patch('luminous_nix.service_simple.NixForHumanityBackend') as mock_backend_class:
            mock_backend = AsyncMock()
            
            # Simulate cache-aware backend
            async def cached_response(request):
                # Check cache first
                cached = cache.get("test-key")
                if cached:
                    return Response(
                        success=True,
                        text="From cache",
                        commands=[],
                        data=cached
                    )
                # Simulate slow operation
                await asyncio.sleep(0.1)
                return mock_response
            
            mock_backend.process_request = cached_response
            mock_backend_class.return_value = mock_backend
            
            # Measure cached response
            start = time.perf_counter()
            result = await service.execute_command("test")
            cached_time = (time.perf_counter() - start) * 1000
            
            # Clear cache
            cache.clear()
            
            # Measure uncached response
            start = time.perf_counter()
            result = await service.execute_command("test")
            uncached_time = (time.perf_counter() - start) * 1000
            
            # Cached should be at least 10x faster
            speedup = uncached_time / cached_time
            assert speedup > 10, f"Cache speedup only {speedup:.1f}x (should be >10x)"


class TestScalability:
    """Test service scalability"""
    
    @pytest.mark.asyncio
    async def test_multiple_service_instances(self):
        """Test that multiple service instances work well together"""
        services = [LuminousNixService() for _ in range(10)]
        
        mock_response = Response(
            success=True,
            text="OK",
            commands=[],
            data={}
        )
        
        with patch('luminous_nix.service_simple.NixForHumanityBackend') as mock_backend_class:
            mock_backend = AsyncMock()
            mock_backend.process_request = AsyncMock(return_value=mock_response)
            mock_backend_class.return_value = mock_backend
            
            # Each service executes commands
            tasks = []
            for i, service in enumerate(services):
                for j in range(10):
                    tasks.append(service.execute_command(f"service-{i}-cmd-{j}"))
            
            start = time.perf_counter()
            results = await asyncio.gather(*tasks)
            elapsed = time.perf_counter() - start
            
            assert len(results) == 100
            assert all(r.success for r in results)
            assert elapsed < 1.0, f"100 commands across 10 services took {elapsed:.2f}s"
    
    @pytest.mark.asyncio  
    async def test_interface_switching_performance(self):
        """Test performance when switching between interfaces"""
        from luminous_nix.service_simple import (
            create_cli_service,
            create_tui_service,
            create_voice_service,
            create_api_service
        )
        
        mock_response = Response(
            success=True,
            text="OK",
            commands=[],
            data={}
        )
        
        with patch('luminous_nix.service_simple.NixForHumanityBackend') as mock_backend_class:
            mock_backend = AsyncMock()
            mock_backend.process_request = AsyncMock(return_value=mock_response)
            mock_backend_class.return_value = mock_backend
            
            # Create services for different interfaces
            start = time.perf_counter()
            
            cli = await create_cli_service()
            tui = await create_tui_service()
            voice = await create_voice_service()
            api = await create_api_service()
            
            # Execute commands on each
            await cli.execute_command("cli command")
            await tui.execute_command("tui command")
            await voice.execute_command("voice command")
            await api.execute_command("api command")
            
            elapsed = (time.perf_counter() - start) * 1000
            
            assert elapsed < 200, f"Interface switching took {elapsed:.2f}ms"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])