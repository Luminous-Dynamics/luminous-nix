"""
Unified pytest configuration for all tests.

This replaces scattered conftest.py files and provides
consistent fixtures and configuration for all test types.
"""

import os
import sys
from pathlib import Path
import pytest
from unittest.mock import Mock, MagicMock

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Disable slow imports during tests
os.environ["DISABLE_SLOW_IMPORTS"] = "1"
os.environ["TESTING"] = "1"


@pytest.fixture
def mock_backend():
    """Provide a mock backend for testing."""
    from luminous_nix.core.consolidated_backend import ConsolidatedBackend
    backend = ConsolidatedBackend()
    backend.cache = {}
    backend.stats = {
        "requests": 0,
        "success": 0, 
        "errors": 0,
        "avg_response_time": 0
    }
    return backend


@pytest.fixture
def mock_request():
    """Provide a mock request object."""
    from luminous_nix.core.consolidated_backend import Request
    return Request(
        query="test query",
        dry_run=True,
        verbose=False
    )


@pytest.fixture
def mock_subprocess(monkeypatch):
    """Mock subprocess calls for testing."""
    mock_run = Mock()
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "mock output"
    mock_run.return_value.stderr = ""
    monkeypatch.setattr("subprocess.run", mock_run)
    return mock_run


@pytest.fixture
def temp_dir(tmp_path):
    """Provide a temporary directory for tests."""
    return tmp_path


@pytest.fixture
def mock_knowledge_engine(monkeypatch):
    """Mock the knowledge engine."""
    mock_engine = Mock()
    mock_engine.answer_question.return_value = "Mock answer"
    
    def get_mock_engine():
        return mock_engine
    
    monkeypatch.setattr(
        "luminous_nix.core.consolidated_backend.get_knowledge_engine",
        get_mock_engine
    )
    return mock_engine


@pytest.fixture
def mock_fuzzy_search(monkeypatch):
    """Mock fuzzy search functionality."""
    mock_search = Mock()
    mock_search.search.return_value = [
        {"name": "firefox", "description": "Web browser"},
        {"name": "chromium", "description": "Web browser"}
    ]
    
    def get_mock_search():
        return mock_search
    
    monkeypatch.setattr(
        "luminous_nix.core.consolidated_backend.get_fuzzy_search",
        get_mock_search
    )
    return mock_search


# Performance benchmarking fixtures
@pytest.fixture
def benchmark_backend():
    """Backend configured for performance testing."""
    from luminous_nix.core.consolidated_backend import ConsolidatedBackend
    backend = ConsolidatedBackend()
    # Pre-warm caches
    backend.cache = {"warm": True}
    return backend


# Test markers
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "e2e: marks tests as end-to-end tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )