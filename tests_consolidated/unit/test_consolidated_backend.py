"""
Unit tests for the consolidated backend.

These tests verify the core functionality of the unified backend
without external dependencies.
"""

import pytest
import time
from unittest.mock import Mock, patch

from luminous_nix.core.consolidated_backend import (
    ConsolidatedBackend,
    Request,
    Response,
    Intent,
    IntentType,
    get_backend
)


class TestConsolidatedBackend:
    """Test the consolidated backend functionality."""
    
    def test_initialization(self):
        """Test backend initializes correctly."""
        backend = ConsolidatedBackend()
        assert backend.config == {}
        assert backend.cache == {}
        assert backend.stats["requests"] == 0
        assert backend.stats["success"] == 0
        assert backend.stats["errors"] == 0
    
    def test_singleton_pattern(self):
        """Test get_backend returns singleton."""
        backend1 = get_backend()
        backend2 = get_backend()
        assert backend1 is backend2
    
    def test_parse_intent_install(self):
        """Test parsing install intent."""
        backend = ConsolidatedBackend()
        
        queries = [
            "install firefox",
            "add vim and git",
            "please install neovim",
            "i want to install emacs"
        ]
        
        for query in queries:
            intent = backend._parse_intent(query)
            assert intent.type == IntentType.INSTALL
            assert len(intent.packages) > 0
    
    def test_parse_intent_remove(self):
        """Test parsing remove intent."""
        backend = ConsolidatedBackend()
        
        queries = [
            "remove firefox",
            "uninstall vim",
            "delete emacs"
        ]
        
        for query in queries:
            intent = backend._parse_intent(query)
            assert intent.type == IntentType.REMOVE
            assert len(intent.packages) > 0
    
    def test_parse_intent_search(self):
        """Test parsing search intent."""
        backend = ConsolidatedBackend()
        
        queries = [
            "search firefox",
            "find web browser",
            "look for editor"
        ]
        
        for query in queries:
            intent = backend._parse_intent(query)
            assert intent.type == IntentType.SEARCH
    
    def test_extract_packages(self):
        """Test package extraction from queries."""
        backend = ConsolidatedBackend()
        
        test_cases = [
            ("install firefox", ["firefox"]),
            ("install vim and git", ["vim", "git"]),
            ("please install neovim emacs", ["neovim", "emacs"]),
            ("i need firefox", ["firefox"])
        ]
        
        for query, expected in test_cases:
            packages = backend._extract_packages(query)
            assert packages == expected
    
    def test_handle_install_dry_run(self, mock_backend):
        """Test install handling in dry run mode."""
        request = Request(
            query="install firefox",
            dry_run=True
        )
        
        response = mock_backend.process(request)
        
        assert response.success
        assert "Would install" in response.message
        assert response.data["dry_run"] is True
    
    @patch("subprocess.run")
    def test_handle_install_real(self, mock_run):
        """Test real installation."""
        backend = ConsolidatedBackend()
        
        # Mock successful installation
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "installing firefox..."
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        request = Request(
            query="install firefox",
            dry_run=False
        )
        
        response = backend.process(request)
        
        assert response.success
        assert "Successfully installed" in response.message
        mock_run.assert_called_once()
    
    @patch("subprocess.run")
    def test_handle_install_failure(self, mock_run):
        """Test installation failure."""
        backend = ConsolidatedBackend()
        
        # Mock failed installation
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Package not found"
        mock_run.return_value = mock_result
        
        request = Request(
            query="install nonexistent",
            dry_run=False
        )
        
        response = backend.process(request)
        
        assert not response.success
        assert response.error == "Package not found"
    
    def test_handle_search_with_fuzzy(self, mock_fuzzy_search):
        """Test search with fuzzy search available."""
        backend = ConsolidatedBackend()
        
        request = Request(query="search browser")
        response = backend.process(request)
        
        assert response.success
        assert "Found" in response.message
        assert "firefox" in response.data["packages"]
    
    @patch("subprocess.run")
    def test_handle_search_fallback(self, mock_run):
        """Test search fallback when fuzzy not available."""
        backend = ConsolidatedBackend()
        
        # Mock nix search output
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "* nixpkgs.firefox\n* nixpkgs.chromium"
        mock_run.return_value = mock_result
        
        request = Request(query="search browser")
        
        # Disable fuzzy search
        with patch("luminous_nix.core.consolidated_backend.get_fuzzy_search", return_value=None):
            response = backend.process(request)
        
        assert response.success
        assert "packages" in response.data
    
    def test_handle_list(self, mock_subprocess):
        """Test listing installed packages."""
        backend = ConsolidatedBackend()
        
        mock_subprocess.return_value.stdout = "firefox\nvim\ngit"
        
        request = Request(query="list installed")
        response = backend.process(request)
        
        assert response.success
        assert "Found" in response.message
        assert len(response.data["packages"]) == 3
    
    def test_performance_tracking(self):
        """Test performance metrics are tracked."""
        backend = ConsolidatedBackend()
        
        request = Request(query="test", dry_run=True)
        
        # Process multiple requests
        for _ in range(5):
            backend.process(request)
        
        assert backend.stats["requests"] == 5
        assert backend.stats["avg_response_time"] > 0
    
    def test_slow_request_warning(self, capsys):
        """Test warning for slow requests."""
        backend = ConsolidatedBackend()
        
        # Mock slow processing
        with patch.object(backend, "_parse_intent") as mock_parse:
            mock_parse.side_effect = lambda x: (time.sleep(0.6), Intent(type=IntentType.UNKNOWN))[1]
            
            request = Request(query="slow request")
            backend.process(request)
            
            captured = capsys.readouterr()
            assert "Slow request" in captured.out
    
    def test_error_handling(self):
        """Test error handling in process method."""
        backend = ConsolidatedBackend()
        
        # Force an error
        with patch.object(backend, "_parse_intent", side_effect=Exception("Test error")):
            request = Request(query="error test")
            response = backend.process(request)
            
            assert not response.success
            assert "Error processing request" in response.message
            assert backend.stats["errors"] == 1
    
    @pytest.mark.asyncio
    async def test_async_process(self):
        """Test async processing wrapper."""
        backend = ConsolidatedBackend()
        request = Request(query="test async", dry_run=True)
        
        response = await backend.process_async(request)
        
        assert response.success
    
    def test_generate_config(self):
        """Test configuration generation."""
        backend = ConsolidatedBackend()
        
        request = Request(query="generate config")
        response = backend.process(request)
        
        assert response.success
        assert "template" in response.data
        assert "environment.systemPackages" in response.data["template"]
    
    def test_unknown_intent(self):
        """Test handling of unknown intents."""
        backend = ConsolidatedBackend()
        
        request = Request(query="something random")
        response = backend.process(request)
        
        assert response.success
        assert len(response.suggestions) > 0


class TestBackendPerformance:
    """Performance tests for the backend."""
    
    def test_startup_time(self):
        """Test backend startup is under 500ms."""
        start = time.time()
        backend = ConsolidatedBackend()
        elapsed = time.time() - start
        
        assert elapsed < 0.5, f"Startup took {elapsed:.3f}s"
    
    def test_request_processing_time(self, benchmark_backend):
        """Test request processing is under 500ms."""
        request = Request(query="install firefox", dry_run=True)
        
        start = time.time()
        response = benchmark_backend.process(request)
        elapsed = time.time() - start
        
        assert elapsed < 0.5, f"Processing took {elapsed:.3f}s"
        assert response.success
    
    def test_lazy_loading(self):
        """Test lazy loading of heavy components."""
        backend = ConsolidatedBackend()
        
        # Components should not be loaded initially
        assert backend._knowledge is None
        assert backend._executor is None
        assert backend._fuzzy is None
        assert backend._tree_sitter is None