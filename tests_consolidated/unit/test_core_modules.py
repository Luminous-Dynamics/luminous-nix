"""
Comprehensive tests for core modules to improve coverage.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import json

from luminous_nix.core.consolidated_backend import (
    ConsolidatedBackend, Request, Response, IntentType
)
from luminous_nix.core import (
    CommandExecutor,
    NixForHumanityCore,
    Query,
)


class TestCoreModules:
    """Test core module functionality."""
    
    def test_command_executor_init(self):
        """Test command executor initialization."""
        from luminous_nix.core.command_executor import CommandExecutor
        executor = CommandExecutor()
        assert executor is not None
        assert hasattr(executor, 'execute')
    
    def test_command_executor_execute_simple(self):
        """Test simple command execution."""
        from luminous_nix.core.command_executor import CommandExecutor
        executor = CommandExecutor()
        
        # Test with mock command
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "Success"
            
            result = executor.execute(["echo", "test"])
            assert result is not None
    
    def test_backend_cache_operations(self):
        """Test backend caching."""
        backend = ConsolidatedBackend()
        
        # Test cache storage
        backend.cache["test_key"] = "test_value"
        assert backend.cache["test_key"] == "test_value"
        
        # Test cache retrieval
        value = backend.cache.get("test_key")
        assert value == "test_value"
    
    def test_backend_stats_tracking(self):
        """Test statistics tracking."""
        backend = ConsolidatedBackend()
        
        # Initial stats
        assert backend.stats["requests"] == 0
        assert backend.stats["success"] == 0
        assert backend.stats["errors"] == 0
        
        # Process successful request
        request = Request(query="test", dry_run=True)
        response = backend.process(request)
        
        assert backend.stats["requests"] == 1
        if response.success:
            assert backend.stats["success"] == 1
    
    def test_request_validation(self):
        """Test request validation."""
        # Valid request
        request = Request(query="install firefox")
        assert request.query == "install firefox"
        assert request.dry_run is False
        
        # Request with options
        request = Request(
            query="search editor",
            dry_run=True,
            options={"limit": 10}
        )
        assert request.options["limit"] == 10
    
    def test_response_structure(self):
        """Test response structure."""
        response = Response(
            success=True,
            message="Test successful",
            data={"key": "value"},
            suggestions=["Try this", "Or that"]
        )
        
        assert response.success is True
        assert response.message == "Test successful"
        assert response.data["key"] == "value"
        assert len(response.suggestions) == 2
    
    def test_intent_types(self):
        """Test all intent types are handled."""
        backend = ConsolidatedBackend()
        
        test_queries = {
            "install firefox": IntentType.INSTALL,
            "remove vim": IntentType.REMOVE,
            "search editor": IntentType.SEARCH,
            "update system": IntentType.UPDATE,
            "rollback changes": IntentType.ROLLBACK,
            "list installed": IntentType.LIST,
            "generate config for web server": IntentType.GENERATE_CONFIG,
            "analyze project dependencies": IntentType.ANALYZE_PROJECT,
            "migrate script to nix": IntentType.MIGRATE_SCRIPT,
        }
        
        for query, expected_type in test_queries.items():
            intent = backend._parse_intent(query)
            assert intent.type == expected_type, f"Failed for: {query}"
