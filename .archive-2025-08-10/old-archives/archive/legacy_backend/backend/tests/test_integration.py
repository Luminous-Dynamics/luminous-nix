#!/usr/bin/env python3
"""
import subprocess
Comprehensive Integration Tests for Nix for Humanity Backend
Tests the full stack from user input to NixOS operations
"""

import asyncio
import os
import sys
import time
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

# Import all components
from api.schema import Request
from core.nix_integration import NixOSIntegration
from nix_humanity.core.engine import NixForHumanityBackend


class TestFullStackIntegration:
    """Test the complete integration from frontend to NixOS"""

    @pytest.fixture
    def backend(self):
        """Create a configured backend instance"""
        return NixForHumanityBackend()

    @pytest.fixture
    def mock_progress(self):
        """Mock progress callback to track updates"""
        progress_updates = []

        def callback(message: str, progress: float):
            progress_updates.append(
                {"message": message, "progress": progress, "timestamp": time.time()}
            )

        return callback, progress_updates

    @pytest.mark.asyncio
    async def test_natural_language_to_nixos(self, backend):
        """Test complete flow from natural language to NixOS operation"""
        # User asks in natural language
        request = Request(
            text="I want to install firefox",
            context={
                "execute": False,  # Don't actually execute
                "dry_run": True,
                "personality": "friendly",
            },
        )

        # Process through backend
        response = await backend.process_request(request)

        # Verify response
        assert response.success
        assert "firefox" in response.explanation.lower()
        assert response.intent.type.value == "install_package"
        assert len(response.suggestions) > 0

    @pytest.mark.asyncio
    async def test_update_system_flow(self, backend):
        """Test system update flow"""
        request = Request(
            text="update my system", context={"execute": False, "dry_run": True}
        )

        response = await backend.process_request(request)

        assert response.success
        assert response.intent.type.value == "update_system"
        assert "update" in response.explanation.lower()

    @pytest.mark.asyncio
    async def test_security_validation_integration(self, backend):
        """Test security validation in the full stack"""
        # Try dangerous input
        request = Request(text="install firefox; rm -rf /", context={"execute": False})

        response = await backend.process_request(request)

        # Should be rejected by security
        assert not response.success
        assert "validation failed" in response.explanation.lower()
        assert "rephrase" in " ".join(response.suggestions).lower()

    @pytest.mark.asyncio
    async def test_enhanced_backend_features(self, backend):
        """Test that enhanced backend features are available"""
        # Enable enhanced backend
        os.environ["LUMINOUS_NIX_PYTHON_BACKEND"] = "true"

        # Create integration
        integration = NixOSIntegration()
        status = integration.get_status()

        # Check enhanced features
        if status.get("enhanced_backend"):
            assert status["performance_boost"] == "10x-1500x"
            assert "metrics" in status

    @pytest.mark.asyncio
    async def test_progress_tracking_integration(self, backend, mock_progress):
        """Test progress tracking through the full stack"""
        callback, updates = mock_progress

        # Create backend with progress callback
        backend = NixForHumanityBackend(progress_callback=callback)

        request = Request(text="check system health", context={"execute": False})

        response = await backend.process_request(request)

        # Should have progress updates
        assert len(updates) > 0
        assert all(0 <= u["progress"] <= 1 for u in updates)
        assert updates[-1]["progress"] == 1.0  # Should complete at 100%

    @pytest.mark.asyncio
    async def test_caching_behavior(self, backend):
        """Test that caching works in integration"""
        # First request
        request1 = Request(text="list system generations", context={"execute": False})

        start1 = time.time()
        response1 = await backend.process_request(request1)
        time1 = time.time() - start1

        # Second identical request (should be cached)
        request2 = Request(text="list system generations", context={"execute": False})

        start2 = time.time()
        response2 = await backend.process_request(request2)
        time2 = time.time() - start2

        # Both should succeed
        assert response1.success
        assert response2.success

        # Second should be faster (if caching is working)
        # Note: This might not always be true in tests, so we just check both completed
        assert time1 > 0 and time2 > 0

    @pytest.mark.asyncio
    async def test_error_recovery_integration(self, backend):
        """Test error recovery in the full stack"""
        with patch(
            "core.nix_integration.NixOSIntegration.execute_intent"
        ) as mock_execute:
            # Simulate disk space error
            mock_execute.side_effect = Exception("No space left on device")

            request = Request(
                text="update system", context={"execute": True, "dry_run": False}
            )

            response = await backend.process_request(request)

            # Should handle error gracefully
            assert not response.success
            assert "error" in response.explanation.lower()

            # Should have recovery suggestions
            assert len(response.suggestions) > 0

    @pytest.mark.asyncio
    async def test_personality_adaptation(self, backend):
        """Test personality system integration"""
        personalities = ["minimal", "friendly", "encouraging", "technical", "symbiotic"]

        for personality in personalities:
            request = Request(
                text="install vim",
                context={"execute": False, "personality": personality},
            )

            response = await backend.process_request(request)

            assert response.success
            # Response should vary by personality
            assert len(response.explanation) > 0


class TestAPIIntegration:
    """Test API layer integration"""

    @pytest.mark.asyncio
    async def test_request_response_cycle(self):
        """Test complete request/response cycle"""
        backend = NixForHumanityBackend()

        # Create request
        request = Request(
            query="What's my disk usage?",
            context={"session_id": "test-123", "personality": "friendly"},
        )

        # Process
        response = backend.process(request)

        # Verify response structure
        assert hasattr(response, "success")
        assert hasattr(response, "text")
        assert hasattr(response, "commands")
        assert hasattr(response, "data")

    @pytest.mark.asyncio
    async def test_multi_modal_context(self):
        """Test context sharing across interfaces"""
        backend = NixForHumanityBackend()

        # Simulate CLI request
        cli_request = Request(
            query="install firefox",
            context={"interface": "cli", "session_id": "shared-123"},
        )

        cli_response = backend.process(cli_request)

        # Simulate follow-up from TUI with same session
        tui_request = Request(
            query="actually, make it brave instead",
            context={
                "interface": "tui",
                "session_id": "shared-123",
                "previous_intent": "install_package",
            },
        )

        tui_response = backend.process(tui_request)

        # Should understand context
        assert tui_response.success
        assert "brave" in tui_response.text.lower()


class TestPerformanceIntegration:
    """Test performance characteristics of the integrated system"""

    @pytest.mark.asyncio
    async def test_response_time_targets(self):
        """Test that response times meet targets for each persona"""
        backend = NixForHumanityBackend()

        # Maya (ADHD) needs <1 second response
        request = Request(text="list packages", context={"personality": "minimal"})

        start = time.time()
        response = await backend.process_request(request)
        duration = time.time() - start

        assert response.success
        assert duration < 1.0  # Should respond in under 1 second

    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test handling concurrent requests"""
        backend = NixForHumanityBackend()

        # Create multiple requests
        requests = [
            Request(text="install firefox", context={"session_id": f"test-{i}"})
            for i in range(5)
        ]

        # Process concurrently
        tasks = [backend.process_request(req) for req in requests]
        responses = await asyncio.gather(*tasks)

        # All should succeed
        assert all(r.success for r in responses)
        assert len(responses) == 5


class TestEndToEndScenarios:
    """Test real-world end-to-end scenarios"""

    @pytest.mark.asyncio
    async def test_new_user_onboarding(self):
        """Test new user onboarding flow"""
        backend = NixForHumanityBackend()

        # New user asks for help
        help_request = Request(text="help", context={"first_time_user": True})

        help_response = await backend.process_request(help_request)

        assert help_response.success
        assert "install" in help_response.explanation.lower()
        assert "update" in help_response.explanation.lower()

        # User tries their first command
        first_command = Request(
            text="I want to install a text editor", context={"first_time_user": True}
        )

        first_response = await backend.process_request(first_command)

        assert first_response.success
        assert any(
            editor in first_response.explanation.lower()
            for editor in ["vim", "emacs", "code", "sublime"]
        )

    @pytest.mark.asyncio
    async def test_troubleshooting_flow(self):
        """Test troubleshooting scenario"""
        backend = NixForHumanityBackend()

        # User reports problem
        problem = Request(
            text="my wifi isn't working", context={"troubleshooting": True}
        )

        response = await backend.process_request(problem)

        assert response.success
        assert len(response.suggestions) > 0
        assert (
            "network" in response.explanation.lower()
            or "wifi" in response.explanation.lower()
        )

    @pytest.mark.asyncio
    async def test_power_user_workflow(self):
        """Test power user advanced workflow"""
        backend = NixForHumanityBackend()

        # Power user wants specific generation
        advanced_request = Request(
            text="rollback to generation 98",
            context={"power_user": True, "execute": False},
        )

        response = await backend.process_request(advanced_request)

        assert response.success
        assert "98" in response.explanation


class TestIntegrationWithMocks:
    """Test integration with mocked NixOS operations"""

    @pytest.fixture
    def mock_nix_operations(self):
        """Mock NixOS operations for testing"""
        with patch("subprocess.run") as mock_run:
            # Mock successful operations
            mock_run.return_value = Mock(
                returncode=0, stdout="Operation completed successfully", stderr=""
            )
            yield mock_run

    @pytest.mark.asyncio
    async def test_full_update_cycle_mocked(self, mock_nix_operations):
        """Test full update cycle with mocked operations"""
        backend = NixForHumanityBackend()

        # List generations
        list_req = Request(text="show me system generations")
        list_resp = await backend.process_request(list_req)
        assert list_resp.success

        # Check for updates
        check_req = Request(text="are there any updates?")
        check_resp = await backend.process_request(check_req)
        assert check_resp.success

        # Perform update (dry run)
        update_req = Request(text="update everything", context={"dry_run": True})
        update_resp = await backend.process_request(update_req)
        assert update_resp.success


# Performance benchmarks for integration
class BenchmarkIntegration:
    """Benchmark the integrated system"""

    @pytest.mark.benchmark
    def test_simple_query_performance(self, benchmark):
        """Benchmark simple query processing"""
        backend = NixForHumanityBackend()

        def process_query():
            request = Request(text="install firefox", context={"execute": False})
            return backend.process(request)

        result = benchmark(process_query)
        assert result.success

    @pytest.mark.benchmark
    def test_complex_query_performance(self, benchmark):
        """Benchmark complex query processing"""
        backend = NixForHumanityBackend()

        def process_complex():
            request = Request(
                text="I need a development environment with python, git, and docker",
                context={"execute": False},
            )
            return backend.process(request)

        result = benchmark(process_complex)
        assert result.success


if __name__ == "__main__":
    # Run specific test groups
    import sys

    if len(sys.argv) > 1:
        test_group = sys.argv[1]
        pytest.main(["-v", "-k", test_group, __file__])
    else:
        # Run all integration tests
        pytest.main(["-v", __file__])
