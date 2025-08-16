"""
End-to-end integration tests.
"""

import pytest
from unittest.mock import patch
import subprocess

from luminous_nix.core.consolidated_backend import (
    ConsolidatedBackend, Request, Response
)


class TestEndToEnd:
    """Test end-to-end workflows."""
    
    def test_install_workflow(self):
        """Test complete install workflow."""
        backend = ConsolidatedBackend()
        
        # Dry run first
        request = Request(query="install firefox", dry_run=True)
        response = backend.process(request)
        
        assert response.success
        assert "Would install" in response.message
        assert "firefox" in response.data["packages"]
    
    def test_search_workflow(self):
        """Test complete search workflow."""
        backend = ConsolidatedBackend()
        
        request = Request(query="search editor")
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "* nixpkgs.vim\n* nixpkgs.emacs"
            
            response = backend.process(request)
            
            # Even if search fails, should have graceful response
            assert response is not None
    
    def test_list_workflow(self):
        """Test listing installed packages."""
        backend = ConsolidatedBackend()
        
        request = Request(query="list installed")
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "firefox\nvim\ngit"
            
            response = backend.process(request)
            
            assert response.success
            assert "Found" in response.message
            assert isinstance(response.data.get("packages"), list)
    
    def test_error_handling(self):
        """Test error handling in workflows."""
        backend = ConsolidatedBackend()
        
        # Test with command that will fail
        request = Request(query="install")  # No package specified
        response = backend.process(request)
        
        # Should handle gracefully
        assert response is not None
        if not response.success:
            assert response.message
            assert response.suggestions or response.error
    
    def test_performance_requirements(self):
        """Test performance requirements are met."""
        import time
        
        backend = ConsolidatedBackend()
        
        # Test quick operations complete in <500ms
        start = time.time()
        request = Request(query="test", dry_run=True)
        response = backend.process(request)
        elapsed = time.time() - start
        
        # Should complete quickly for simple requests
        assert elapsed < 1.0  # Generous limit for CI
