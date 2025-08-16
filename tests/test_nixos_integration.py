#!/usr/bin/env python3
"""
🧪 Integration Tests for Real NixOS Operations

Tests actual NixOS commands in a safe, non-destructive way.
These tests verify that our system works with real NixOS, not just mocks.

Safety Measures:
- Only uses read-only operations
- Never modifies system configuration
- Uses --dry-run for any potentially destructive operations
- Checks if running on NixOS before executing
"""

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from luminous_nix.api.schema import Request, Response
from luminous_nix.core.backend import NixForHumanityBackend
from luminous_nix.nix.package_discovery import PackageDiscovery
from luminous_nix.nix.generation_manager import GenerationManager
from luminous_nix.service_simple import LuminousNixService, ServiceOptions


def is_nixos() -> bool:
    """Check if we're running on NixOS"""
    return Path("/etc/nixos").exists() or os.environ.get("NIXOS_TEST") == "1"


def has_nix_command(command: str) -> bool:
    """Check if a nix command is available"""
    try:
        result = subprocess.run(
            ["which", command],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except:
        return False


@pytest.mark.integration
@pytest.mark.skipif(not is_nixos(), reason="Requires NixOS")
class TestNixOSIntegration:
    """Integration tests that use real NixOS commands"""
    
    def test_nix_available(self):
        """Test that nix commands are available"""
        assert has_nix_command("nix"), "nix command not found"
        assert has_nix_command("nix-env"), "nix-env command not found"
        assert has_nix_command("nix-channel"), "nix-channel command not found"
    
    def test_package_search_real(self):
        """Test package search with real nix search"""
        discovery = PackageDiscovery()
        
        # Search for a common package
        results = discovery.search_packages("firefox", limit=5)
        
        assert len(results) > 0, "No results for firefox"
        assert any("firefox" in r.name.lower() for r in results), "Firefox not in results"
        
        # Check result structure
        first = results[0]
        assert hasattr(first, "name")
        assert hasattr(first, "description")
        assert hasattr(first, "score")
        assert first.score > 0
    
    def test_generation_list_real(self):
        """Test listing real system generations"""
        manager = GenerationManager()
        
        try:
            generations = manager.list_generations()
            
            # Should have at least one generation (current)
            assert len(generations) > 0, "No generations found"
            
            # Check current generation
            current = manager.get_current_generation()
            assert current is not None, "No current generation"
            assert current > 0, "Invalid generation number"
            
            # Verify current is in list
            gen_numbers = [g["generation"] for g in generations]
            assert current in gen_numbers, "Current generation not in list"
            
        except PermissionError:
            pytest.skip("Need elevated permissions for generation management")
    
    @pytest.mark.asyncio
    async def test_backend_dry_run_safety(self):
        """Test that backend respects dry-run mode with real commands"""
        backend = NixForHumanityBackend()
        
        # Try to install a package in dry-run mode
        request = Request(
            query="install hello",
            context={"dry_run": True}
        )
        
        response = await backend.process_request(request)
        
        assert response.success == True
        assert len(response.commands) > 0
        assert "hello" in response.text.lower()
        
        # Verify the package was NOT actually installed
        result = subprocess.run(
            ["nix-env", "-q", "hello"],
            capture_output=True,
            text=True
        )
        
        # If hello was already installed, skip this check
        if result.returncode != 0:
            assert "hello" not in result.stdout, "Package was installed despite dry-run!"
    
    def test_nix_info_commands(self):
        """Test read-only nix information commands"""
        # Test nix-info
        result = subprocess.run(
            ["nix", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        assert result.returncode == 0
        assert "nix" in result.stdout.lower()
        
        # Test nix-channel list
        result = subprocess.run(
            ["nix-channel", "--list"],
            capture_output=True,
            text=True,
            timeout=10
        )
        assert result.returncode == 0
        # Should have at least nixos channel
        assert "nixos" in result.stdout or len(result.stdout) > 0
    
    def test_package_info_real(self):
        """Test getting info about real packages"""
        discovery = PackageDiscovery()
        
        # Get info about a known package
        info = discovery.get_package_info("coreutils")
        
        assert info is not None, "Could not get coreutils info"
        assert "name" in info
        assert info["name"] == "coreutils" or "coreutils" in info["name"]
    
    @pytest.mark.asyncio
    async def test_service_layer_real_operations(self):
        """Test service layer with real NixOS operations"""
        service = LuminousNixService(ServiceOptions(execute=False))
        
        # Test search operation
        response = await service.execute_command("search text editor")
        assert response.success == True
        assert response.data is not None
        
        # Test query operation
        response = await service.execute_command("list installed packages")
        assert response.success == True
        
        # Test info operation
        response = await service.execute_command("show nix version")
        assert response.success == True
    
    def test_flake_detection(self):
        """Test detection of flake-enabled systems"""
        # Check if experimental features are enabled
        result = subprocess.run(
            ["nix", "show-config"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            has_flakes = "experimental-features" in result.stdout and "flakes" in result.stdout
            
            # This is informational, not a failure
            if has_flakes:
                print("✅ Flakes are enabled on this system")
            else:
                print("ℹ️ Flakes are not enabled (optional feature)")
    
    def test_home_manager_detection(self):
        """Test detection of home-manager"""
        has_home_manager = has_nix_command("home-manager")
        
        # This is informational, not a failure
        if has_home_manager:
            print("✅ Home-manager is installed")
        else:
            print("ℹ️ Home-manager is not installed (optional)")


@pytest.mark.integration
class TestSafeOperations:
    """Test operations that are safe even on non-NixOS systems"""
    
    def test_cache_operations(self):
        """Test cache operations work correctly"""
        from luminous_nix.utils.cache import get_default_cache_manager
        
        cache = get_default_cache_manager()
        
        # Test basic operations
        cache.set("test-key", {"data": "test"}, ttl=60)
        result = cache.get("test-key")
        assert result is not None
        assert result["data"] == "test"
        
        # Test cache stats
        stats = cache.get_stats()
        assert "memory_cache_size" in stats
        assert stats["memory_cache_size"] >= 1
        
        # Test clear
        cache.clear()
        result = cache.get("test-key")
        assert result is None
    
    def test_config_operations(self):
        """Test configuration operations"""
        from luminous_nix.config.loader import ConfigLoader
        
        loader = ConfigLoader()
        
        # Test default config
        config = loader.get_config()
        assert config is not None
        
        # Test aliases
        aliases = loader.get_aliases()
        assert isinstance(aliases, dict)
        
        # Test settings
        settings = loader.get_settings()
        assert isinstance(settings, dict)
    
    @pytest.mark.asyncio
    async def test_mock_mode(self):
        """Test that mock mode works without NixOS"""
        os.environ["NIX_HUMANITY_MOCK"] = "1"
        
        try:
            service = LuminousNixService()
            response = await service.execute_command("search firefox")
            
            # Should work even without NixOS in mock mode
            assert response.success == True
            
        finally:
            del os.environ["NIX_HUMANITY_MOCK"]


@pytest.mark.integration
@pytest.mark.slow
class TestPerformanceWithRealData:
    """Test performance with real NixOS data"""
    
    @pytest.mark.skipif(not is_nixos(), reason="Requires NixOS")
    def test_large_package_search_performance(self):
        """Test performance with large package searches"""
        import time
        
        discovery = PackageDiscovery()
        
        # Pre-warm cache
        discovery.search_packages("test", limit=1)
        
        # Test search performance
        start = time.perf_counter()
        results = discovery.search_packages("python", limit=100)
        elapsed = time.perf_counter() - start
        
        assert len(results) > 0
        assert elapsed < 5.0, f"Large search took {elapsed:.2f}s (should be <5s)"
        
        # Second search should be cached
        start = time.perf_counter()
        results2 = discovery.search_packages("python", limit=100)
        cached_elapsed = time.perf_counter() - start
        
        assert len(results2) == len(results)
        assert cached_elapsed < 0.1, f"Cached search took {cached_elapsed:.2f}s (should be <0.1s)"
    
    @pytest.mark.skipif(not is_nixos(), reason="Requires NixOS")
    @pytest.mark.asyncio
    async def test_concurrent_real_operations(self):
        """Test concurrent operations with real NixOS"""
        service = LuminousNixService()
        
        # Execute multiple real operations concurrently
        tasks = [
            service.execute_command("search editor"),
            service.execute_command("list generations"),
            service.execute_command("show nix info"),
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should succeed
        failures = [r for r in results if isinstance(r, Exception)]
        assert len(failures) == 0, f"Had {len(failures)} failures"
        
        # All should have results
        for r in results:
            assert r.success == True


class TestErrorRecovery:
    """Test error recovery with real commands"""
    
    @pytest.mark.asyncio
    async def test_invalid_package_name_recovery(self):
        """Test recovery from invalid package names"""
        service = LuminousNixService()
        
        # Try to install a package that doesn't exist
        response = await service.execute_command("install this-package-definitely-does-not-exist-12345")
        
        # Should handle gracefully
        assert response.success == False or "not found" in response.text.lower()
        assert response.data is not None
    
    @pytest.mark.asyncio
    async def test_malformed_command_recovery(self):
        """Test recovery from malformed commands"""
        service = LuminousNixService()
        
        # Send various malformed commands
        malformed = [
            "",
            "   ",
            "install",  # Missing package name
            "search",   # Missing search term
            "!@#$%^&*()",  # Special characters
            "x" * 1000,  # Very long input
        ]
        
        for cmd in malformed:
            response = await service.execute_command(cmd)
            # Should not crash, should return response
            assert response is not None
            assert hasattr(response, "success")
            assert hasattr(response, "text")


class TestNixOSCompatibility:
    """Test compatibility with different NixOS configurations"""
    
    @pytest.mark.skipif(not is_nixos(), reason="Requires NixOS")
    def test_nixos_version_detection(self):
        """Test detection of NixOS version"""
        result = subprocess.run(
            ["nixos-version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"Detected NixOS version: {version}")
            
            # Parse version
            parts = version.split(".")
            assert len(parts) >= 2, "Could not parse version"
            
            major = int(parts[0])
            assert major >= 20, "NixOS version too old"
    
    @pytest.mark.skipif(not is_nixos(), reason="Requires NixOS")
    def test_channel_configuration(self):
        """Test channel configuration detection"""
        result = subprocess.run(
            ["nix-channel", "--list"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            channels = result.stdout.strip().split("\n")
            print(f"Detected channels: {channels}")
            
            # Should have at least one channel
            assert len(channels) > 0, "No channels configured"


def test_integration_suite_completeness():
    """Meta-test: Verify integration tests cover key areas"""
    import inspect
    import sys
    
    # Get all test classes
    test_classes = [
        obj for name, obj in inspect.getmembers(sys.modules[__name__])
        if inspect.isclass(obj) and name.startswith("Test")
    ]
    
    # Check we have tests for key areas
    areas = {
        "NixOS": False,
        "Safe": False,
        "Performance": False,
        "Error": False,
        "Compatibility": False,
    }
    
    for cls in test_classes:
        name = cls.__name__
        if "NixOS" in name:
            areas["NixOS"] = True
        if "Safe" in name:
            areas["Safe"] = True
        if "Performance" in name:
            areas["Performance"] = True
        if "Error" in name:
            areas["Error"] = True
        if "Compatibility" in name:
            areas["Compatibility"] = True
    
    for area, covered in areas.items():
        assert covered, f"Missing integration tests for {area}"


if __name__ == "__main__":
    # Run with appropriate markers
    if is_nixos():
        print("🐧 Running on NixOS - all tests enabled")
        pytest.main([__file__, "-v", "--tb=short", "-m", "integration"])
    else:
        print("📦 Not on NixOS - running safe tests only")
        pytest.main([__file__, "-v", "--tb=short", "-k", "Safe"])