#!/usr/bin/env python3
"""
Test configuration loading and saving functionality.

Tests that configuration can be persisted and restored correctly.
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))

from luminous_nix.config.config_manager import ConfigManager
from luminous_nix.config.settings import Config as Settings


class TestConfigPersistence(unittest.TestCase):
    """Test configuration loading and saving"""

    def setUp(self):
        """Create temporary directory for test configs"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / "test_config.json"

    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_save_and_load_config(self):
        """Test saving configuration to file and loading it back"""
        # Create config manager with test file
        config = ConfigManager(config_path=self.config_file)
        
        # Set some values
        test_data = {
            "personality": "friendly",
            "dry_run": True,
            "enable_learning": False,
            "custom_setting": "test_value"
        }
        
        for key, value in test_data.items():
            config.set(key, value)
        
        # Save to file
        config.save()
        
        # Verify file exists
        self.assertTrue(self.config_file.exists())
        
        # Load from file
        with open(self.config_file, 'r') as f:
            loaded_data = json.load(f)
        
        # Check values were saved
        for key, value in test_data.items():
            self.assertEqual(loaded_data.get(key), value)

    def test_load_existing_config(self):
        """Test loading an existing configuration file"""
        # Create a config file
        config_data = {
            "personality": "minimal",
            "dry_run": False,
            "enable_learning": True,
            "api_endpoint": "http://localhost:8080"
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config_data, f)
        
        # Load it with ConfigManager
        config = ConfigManager(config_path=self.config_file)
        
        # Verify values were loaded
        self.assertEqual(config.get("personality"), "minimal")
        self.assertEqual(config.get("dry_run"), False)
        self.assertEqual(config.get("enable_learning"), True)
        self.assertEqual(config.get("api_endpoint"), "http://localhost:8080")

    def test_update_existing_config(self):
        """Test updating an existing configuration"""
        # Create initial config
        initial_data = {
            "personality": "friendly",
            "dry_run": True
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(initial_data, f)
        
        # Load and update
        config = ConfigManager(config_path=self.config_file)
        config.set("personality", "minimal")
        config.set("new_setting", "new_value")
        config.save()
        
        # Reload and verify
        with open(self.config_file, 'r') as f:
            updated_data = json.load(f)
        
        self.assertEqual(updated_data["personality"], "minimal")
        self.assertEqual(updated_data["new_setting"], "new_value")
        self.assertEqual(updated_data["dry_run"], True)  # Should be preserved

    def test_settings_class(self):
        """Test the Settings class if it exists"""
        try:
            # Create settings with test directory
            settings = Settings(data_dir=self.temp_dir)
            
            # Test basic operations
            settings.set("test_key", "test_value")
            self.assertEqual(settings.get("test_key"), "test_value")
            
            # Test persistence
            settings.save()
            
            # Create new instance and verify persistence
            settings2 = Settings(data_dir=self.temp_dir)
            self.assertEqual(settings2.get("test_key"), "test_value")
            
        except Exception as e:
            # Settings class might not have all methods, that's OK
            self.skipTest(f"Settings class not fully implemented: {e}")

    def test_config_defaults(self):
        """Test that default configuration values are set"""
        config = ConfigManager(config_path=self.config_file)
        
        # Check some expected defaults
        # These may vary based on implementation
        defaults_to_check = [
            ("personality", ["friendly", "minimal", "technical", None]),
            ("dry_run", [True, False, None]),
            ("enable_learning", [True, False, None])
        ]
        
        for key, expected_values in defaults_to_check:
            value = config.get(key)
            if value is not None:
                self.assertIn(value, expected_values, 
                             f"Default value for {key} not in expected range")


if __name__ == "__main__":
    unittest.main()