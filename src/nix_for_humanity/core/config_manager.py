"""Configuration management for Nix for Humanity"""

import json
from pathlib import Path

class ConfigManager:
    """Manages user configuration and preferences"""
    
    def __init__(self):
        self.config_file = Path.home() / ".config/nix-humanity/config.json"
        self.config = self.load_config()
    
    def load_config(self) -> dict:
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                return json.loads(self.config_file.read_text())
            except:
                pass
        return self.get_default_config()
    
    def get_default_config(self) -> dict:
        """Get default configuration"""
        return {
            "personality": "friendly",
            "show_progress": True,
            "auto_update": False,
            "learning_enabled": True
        }
    
    def save_config(self):
        """Save configuration to file"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self.config_file.write_text(json.dumps(self.config, indent=2))
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value):
        """Set configuration value"""
        self.config[key] = value
        self.save_config()
