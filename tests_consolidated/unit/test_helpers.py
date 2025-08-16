"""
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
