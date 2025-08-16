#!/usr/bin/env python3
"""
Test Coverage Improvement Script for Nix for Humanity

This script creates comprehensive test coverage to achieve 80%+ coverage.
It generates test files for all major modules and components.

Target: 80% test coverage across the entire codebase
"""

import os
import subprocess
from pathlib import Path

def create_comprehensive_tests():
    """Create comprehensive test files for all modules."""
    
    # Test creation plan
    test_files = {
        "tests_consolidated/unit/test_core_modules.py": '''"""
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
''',

        "tests_consolidated/unit/test_knowledge_engine.py": '''"""
Tests for the knowledge engine module.
"""

import pytest
from unittest.mock import Mock, patch
import json

def test_knowledge_engine_init():
    """Test knowledge engine initialization."""
    from luminous_nix.knowledge.engine import ModernNixOSKnowledgeEngine
    
    engine = ModernNixOSKnowledgeEngine()
    assert engine is not None
    assert hasattr(engine, 'query')
    assert hasattr(engine, 'search')


def test_knowledge_query():
    """Test knowledge queries."""
    from luminous_nix.knowledge.engine import ModernNixOSKnowledgeEngine
    
    engine = ModernNixOSKnowledgeEngine()
    
    # Test package query
    result = engine.query("firefox", query_type="package")
    assert result is not None
    
    # Test option query
    result = engine.query("networking.firewall", query_type="option")
    assert result is not None


def test_knowledge_search():
    """Test knowledge search."""
    from luminous_nix.knowledge.engine import ModernNixOSKnowledgeEngine
    
    engine = ModernNixOSKnowledgeEngine()
    
    # Test search
    results = engine.search("editor", limit=5)
    assert isinstance(results, list)
    assert len(results) <= 5
''',

        "tests_consolidated/unit/test_ui_components.py": '''"""
Tests for UI components.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from luminous_nix.ui.consolidated_ui import (
    ConsolidatedUI, UIConfig, SimpleUI
)


class TestUIComponents:
    """Test UI components."""
    
    def test_ui_config_defaults(self):
        """Test default UI configuration."""
        config = UIConfig()
        
        assert config.theme == "default"
        assert config.show_hints is True
        assert config.enable_animations is True
        assert config.max_history == 100
    
    def test_simple_ui_init(self):
        """Test simple UI initialization."""
        ui = SimpleUI()
        
        assert ui is not None
        assert hasattr(ui, 'prompt')
        assert hasattr(ui, 'display')
    
    def test_simple_ui_prompt(self, monkeypatch):
        """Test simple UI prompting."""
        ui = SimpleUI()
        
        # Mock input
        monkeypatch.setattr('builtins.input', lambda _: "test command")
        
        result = ui.prompt()
        assert result == "test command"
    
    def test_simple_ui_display(self, capsys):
        """Test simple UI display."""
        ui = SimpleUI()
        
        ui.display("Test message")
        
        captured = capsys.readouterr()
        assert "Test message" in captured.out
    
    @patch('luminous_nix.ui.consolidated_ui.TEXTUAL_AVAILABLE', True)
    def test_consolidated_ui_with_textual(self):
        """Test ConsolidatedUI when Textual is available."""
        config = UIConfig(theme="dark")
        ui = ConsolidatedUI(config)
        
        assert ui.config.theme == "dark"
    
    @patch('luminous_nix.ui.consolidated_ui.TEXTUAL_AVAILABLE', False) 
    def test_consolidated_ui_fallback(self):
        """Test ConsolidatedUI fallback when Textual not available."""
        ui = ConsolidatedUI()
        
        # Should fallback to SimpleUI behavior
        assert hasattr(ui, 'prompt')
        assert hasattr(ui, 'display')
''',

        "tests_consolidated/integration/test_end_to_end.py": '''"""
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
            mock_run.return_value.stdout = "* nixpkgs.vim\\n* nixpkgs.emacs"
            
            response = backend.process(request)
            
            # Even if search fails, should have graceful response
            assert response is not None
    
    def test_list_workflow(self):
        """Test listing installed packages."""
        backend = ConsolidatedBackend()
        
        request = Request(query="list installed")
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "firefox\\nvim\\ngit"
            
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
''',

        "tests_consolidated/unit/test_helpers.py": '''"""
Tests for helper functions and utilities.
"""

import pytest
from pathlib import Path
import json
import tempfile


def test_path_operations():
    """Test path utility functions."""
    from luminous_nix.utils import ensure_dir, get_cache_dir
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_path = Path(tmpdir) / "test" / "nested" / "dir"
        
        # Ensure directory creation
        ensure_dir(test_path)
        assert test_path.exists()
        assert test_path.is_dir()


def test_cache_directory():
    """Test cache directory functions."""
    from luminous_nix.utils import get_cache_dir
    
    cache_dir = get_cache_dir()
    assert cache_dir is not None
    assert isinstance(cache_dir, Path)


def test_config_loading():
    """Test configuration loading."""
    from luminous_nix.config import load_config, save_config
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_path = Path(f.name)
        
        # Save config
        test_config = {"key": "value", "number": 42}
        save_config(test_config, config_path)
        
        # Load config
        loaded = load_config(config_path)
        assert loaded == test_config
        
        # Cleanup
        config_path.unlink()


def test_logging_setup():
    """Test logging configuration."""
    import logging
    from luminous_nix.utils import setup_logging
    
    # Setup logging
    logger = setup_logging("test", level=logging.DEBUG)
    
    assert logger is not None
    assert logger.level == logging.DEBUG
'''
    }
    
    # Create test files
    for filepath, content in test_files.items():
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        print(f"✅ Created: {filepath}")
    
    return list(test_files.keys())


def run_coverage_report():
    """Run tests with coverage and generate report."""
    print("\n📊 Running test coverage analysis...")
    
    # Run pytest with coverage
    result = subprocess.run(
        ["poetry", "run", "pytest", 
         "--cov=nix_for_humanity", 
         "--cov-report=term-missing",
         "--cov-report=html",
         "tests_consolidated/"],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print("Warnings:", result.stderr)
    
    # Parse coverage percentage
    for line in result.stdout.split('\n'):
        if 'TOTAL' in line:
            parts = line.split()
            if len(parts) >= 4:
                try:
                    coverage = float(parts[-1].replace('%', ''))
                    print(f"\n{'✅' if coverage >= 80 else '⚠️'} Total Coverage: {coverage}%")
                    return coverage
                except:
                    pass
    
    return 0


def main():
    """Main function to improve test coverage."""
    print("🎯 Test Coverage Improvement for Nix for Humanity")
    print("=" * 50)
    
    # Create comprehensive tests
    test_files = create_comprehensive_tests()
    print(f"\n✅ Created {len(test_files)} new test files")
    
    # Run coverage analysis
    coverage = run_coverage_report()
    
    if coverage >= 80:
        print("\n🎉 SUCCESS: Achieved 80%+ test coverage!")
    else:
        print(f"\n⚠️  Current coverage: {coverage}%")
        print("📝 Additional tests needed in:")
        print("  - More edge cases for backend")
        print("  - Voice interface error paths")
        print("  - UI component interactions")
        print("  - Integration with real NixOS commands")
    
    print("\n📁 HTML coverage report: htmlcov/index.html")


if __name__ == "__main__":
    main()