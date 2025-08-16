"""
Service Layer with Settings Management.

This adds comprehensive settings management to the service layer,
supporting user preferences, system configuration, and profiles.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from enum import Enum

from .service_with_learning import (
    LuminousNixServiceWithLearning, 
    LearningServiceOptions
)
from .api.schema import Response

logger = logging.getLogger(__name__)


class SettingType(Enum):
    """Types of settings."""
    BOOLEAN = "boolean"
    STRING = "string"
    INTEGER = "integer"
    LIST = "list"
    DICT = "dict"


@dataclass
class Setting:
    """Individual setting definition."""
    name: str
    value: Any
    type: SettingType
    description: str
    default: Any
    category: str = "general"
    requires_restart: bool = False
    validator: Optional[callable] = None


@dataclass
class UserProfile:
    """User profile with settings."""
    name: str
    settings: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = False
    created_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "settings": self.settings,
            "is_active": self.is_active,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "UserProfile":
        """Create from dictionary."""
        return cls(**data)


class SettingsManager:
    """Manages all settings for the service."""
    
    # Default settings definitions
    DEFAULT_SETTINGS = {
        # General settings
        "verbose": Setting(
            name="verbose",
            value=False,
            type=SettingType.BOOLEAN,
            description="Show detailed output",
            default=False,
            category="output"
        ),
        "color_output": Setting(
            name="color_output",
            value=True,
            type=SettingType.BOOLEAN,
            description="Use colored output in terminal",
            default=True,
            category="output"
        ),
        "json_output": Setting(
            name="json_output",
            value=False,
            type=SettingType.BOOLEAN,
            description="Output in JSON format",
            default=False,
            category="output"
        ),
        
        # Execution settings
        "dry_run": Setting(
            name="dry_run",
            value=True,
            type=SettingType.BOOLEAN,
            description="Preview commands without executing",
            default=True,
            category="execution"
        ),
        "confirm_execute": Setting(
            name="confirm_execute",
            value=True,
            type=SettingType.BOOLEAN,
            description="Ask for confirmation before executing",
            default=True,
            category="execution"
        ),
        "timeout": Setting(
            name="timeout",
            value=30,
            type=SettingType.INTEGER,
            description="Command timeout in seconds",
            default=30,
            category="execution",
            validator=lambda x: x > 0 and x < 300
        ),
        
        # Learning settings
        "enable_learning": Setting(
            name="enable_learning",
            value=True,
            type=SettingType.BOOLEAN,
            description="Enable personalized learning",
            default=True,
            category="learning"
        ),
        "privacy_mode": Setting(
            name="privacy_mode",
            value=False,
            type=SettingType.BOOLEAN,
            description="Disable all tracking for privacy",
            default=False,
            category="learning"
        ),
        
        # Interface settings
        "default_interface": Setting(
            name="default_interface",
            value="cli",
            type=SettingType.STRING,
            description="Default interface (cli, tui, voice)",
            default="cli",
            category="interface",
            validator=lambda x: x in ["cli", "tui", "voice", "api"]
        ),
        "theme": Setting(
            name="theme",
            value="auto",
            type=SettingType.STRING,
            description="Color theme (auto, light, dark)",
            default="auto",
            category="interface",
            validator=lambda x: x in ["auto", "light", "dark"]
        ),
        
        # Advanced settings
        "cache_enabled": Setting(
            name="cache_enabled",
            value=True,
            type=SettingType.BOOLEAN,
            description="Enable response caching",
            default=True,
            category="advanced"
        ),
        "log_level": Setting(
            name="log_level",
            value="INFO",
            type=SettingType.STRING,
            description="Logging level",
            default="INFO",
            category="advanced",
            validator=lambda x: x in ["DEBUG", "INFO", "WARNING", "ERROR"]
        ),
    }
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize settings manager."""
        self.config_path = config_path or Path.home() / ".config" / "luminous-nix"
        self.config_path.mkdir(parents=True, exist_ok=True)
        
        self.settings_file = self.config_path / "settings.json"
        self.profiles_file = self.config_path / "profiles.json"
        
        # Current settings (start with defaults)
        self.settings = {k: v.value for k, v in self.DEFAULT_SETTINGS.items()}
        
        # User profiles
        self.profiles: Dict[str, UserProfile] = {}
        self.active_profile: Optional[str] = None
        
        # Load saved settings
        self.load_settings()
        self.load_profiles()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value."""
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any) -> bool:
        """
        Set a setting value.
        
        Returns True if successful, False if validation failed.
        """
        # Check if setting exists
        if key not in self.DEFAULT_SETTINGS:
            logger.warning(f"Unknown setting: {key}")
            return False
        
        setting_def = self.DEFAULT_SETTINGS[key]
        
        # Validate if validator exists
        if setting_def.validator and not setting_def.validator(value):
            logger.error(f"Invalid value for {key}: {value}")
            return False
        
        # Type check
        expected_type = setting_def.type
        if not self._check_type(value, expected_type):
            logger.error(f"Wrong type for {key}: expected {expected_type.value}")
            return False
        
        # Set the value
        self.settings[key] = value
        logger.info(f"Set {key} = {value}")
        
        # Save immediately
        self.save_settings()
        
        return True
    
    def _check_type(self, value: Any, expected: SettingType) -> bool:
        """Check if value matches expected type."""
        type_map = {
            SettingType.BOOLEAN: bool,
            SettingType.STRING: str,
            SettingType.INTEGER: int,
            SettingType.LIST: list,
            SettingType.DICT: dict,
        }
        
        expected_python_type = type_map.get(expected)
        if expected_python_type:
            return isinstance(value, expected_python_type)
        return False
    
    def reset(self, key: Optional[str] = None):
        """Reset setting(s) to defaults."""
        if key:
            if key in self.DEFAULT_SETTINGS:
                self.settings[key] = self.DEFAULT_SETTINGS[key].default
                logger.info(f"Reset {key} to default")
        else:
            # Reset all
            self.settings = {k: v.default for k, v in self.DEFAULT_SETTINGS.items()}
            logger.info("Reset all settings to defaults")
        
        self.save_settings()
    
    def list_settings(self, category: Optional[str] = None) -> Dict[str, Any]:
        """List all settings or by category."""
        result = {}
        
        for key, setting_def in self.DEFAULT_SETTINGS.items():
            if category and setting_def.category != category:
                continue
            
            result[key] = {
                "value": self.settings.get(key, setting_def.default),
                "default": setting_def.default,
                "description": setting_def.description,
                "category": setting_def.category,
                "type": setting_def.type.value
            }
        
        return result
    
    def save_settings(self):
        """Save settings to file."""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            logger.debug(f"Saved settings to {self.settings_file}")
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
    
    def load_settings(self):
        """Load settings from file."""
        if not self.settings_file.exists():
            return
        
        try:
            with open(self.settings_file, 'r') as f:
                loaded = json.load(f)
                # Merge with defaults (in case new settings were added)
                for key, value in loaded.items():
                    if key in self.settings:
                        self.settings[key] = value
            logger.debug(f"Loaded settings from {self.settings_file}")
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
    
    # Profile management
    
    def create_profile(self, name: str) -> bool:
        """Create a new profile."""
        if name in self.profiles:
            logger.warning(f"Profile {name} already exists")
            return False
        
        profile = UserProfile(
            name=name,
            settings=self.settings.copy(),  # Copy current settings
            created_at=str(Path.ctime(Path.cwd()))
        )
        
        self.profiles[name] = profile
        self.save_profiles()
        logger.info(f"Created profile: {name}")
        return True
    
    def switch_profile(self, name: str) -> bool:
        """Switch to a different profile."""
        if name not in self.profiles:
            logger.error(f"Profile {name} not found")
            return False
        
        # Save current settings to current profile if exists
        if self.active_profile and self.active_profile in self.profiles:
            self.profiles[self.active_profile].settings = self.settings.copy()
            self.profiles[self.active_profile].is_active = False
        
        # Load new profile
        profile = self.profiles[name]
        self.settings = profile.settings.copy()
        profile.is_active = True
        self.active_profile = name
        
        self.save_settings()
        self.save_profiles()
        
        logger.info(f"Switched to profile: {name}")
        return True
    
    def delete_profile(self, name: str) -> bool:
        """Delete a profile."""
        if name not in self.profiles:
            return False
        
        if self.active_profile == name:
            self.active_profile = None
        
        del self.profiles[name]
        self.save_profiles()
        logger.info(f"Deleted profile: {name}")
        return True
    
    def list_profiles(self) -> List[Dict[str, Any]]:
        """List all profiles."""
        return [
            {
                "name": name,
                "is_active": profile.is_active,
                "created_at": profile.created_at
            }
            for name, profile in self.profiles.items()
        ]
    
    def save_profiles(self):
        """Save profiles to file."""
        try:
            profiles_data = {
                name: profile.to_dict() 
                for name, profile in self.profiles.items()
            }
            
            with open(self.profiles_file, 'w') as f:
                json.dump({
                    "profiles": profiles_data,
                    "active": self.active_profile
                }, f, indent=2)
            
            logger.debug(f"Saved profiles to {self.profiles_file}")
        except Exception as e:
            logger.error(f"Failed to save profiles: {e}")
    
    def load_profiles(self):
        """Load profiles from file."""
        if not self.profiles_file.exists():
            return
        
        try:
            with open(self.profiles_file, 'r') as f:
                data = json.load(f)
                
                # Load profiles
                for name, profile_data in data.get("profiles", {}).items():
                    self.profiles[name] = UserProfile.from_dict(profile_data)
                
                # Set active profile
                self.active_profile = data.get("active")
                
                # Load active profile settings if exists
                if self.active_profile and self.active_profile in self.profiles:
                    profile = self.profiles[self.active_profile]
                    self.settings = profile.settings.copy()
                    profile.is_active = True
            
            logger.debug(f"Loaded profiles from {self.profiles_file}")
        except Exception as e:
            logger.error(f"Failed to load profiles: {e}")


class LuminousNixServiceWithSettings(LuminousNixServiceWithLearning):
    """
    Service layer with integrated settings management.
    
    This adds comprehensive configuration management on top of
    the learning-enabled service.
    """
    
    def __init__(self, options: Optional[LearningServiceOptions] = None):
        """Initialize service with settings manager."""
        super().__init__(options)
        
        # Initialize settings manager
        config_path = getattr(options, 'config_path', None) if options else None
        self.settings_manager = SettingsManager(config_path)
        
        # Apply settings to options
        self._apply_settings_to_options()
    
    def _apply_settings_to_options(self):
        """Apply saved settings to service options."""
        if not self.settings_manager:
            return
        
        # Map settings to options
        setting_map = {
            "verbose": "verbose",
            "json_output": "json_output",
            "dry_run": lambda v: setattr(self.options, "execute", not v),
            "enable_learning": "enable_learning",
            "privacy_mode": "privacy_mode",
            "default_interface": "interface",
        }
        
        for setting_key, option_attr in setting_map.items():
            value = self.settings_manager.get(setting_key)
            if value is not None:
                if callable(option_attr):
                    option_attr(value)
                else:
                    setattr(self.options, option_attr, value)
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting value."""
        return self.settings_manager.get(key, default)
    
    def set_setting(self, key: str, value: Any) -> bool:
        """Set a setting value."""
        success = self.settings_manager.set(key, value)
        
        if success:
            # Re-apply settings to options
            self._apply_settings_to_options()
            
            # Some settings might need special handling
            if key == "log_level":
                logging.getLogger().setLevel(value)
        
        return success
    
    def reset_settings(self, key: Optional[str] = None):
        """Reset setting(s) to defaults."""
        self.settings_manager.reset(key)
        self._apply_settings_to_options()
    
    def list_settings(self, category: Optional[str] = None) -> Dict[str, Any]:
        """List all settings or by category."""
        return self.settings_manager.list_settings(category)
    
    # Profile management
    
    def create_profile(self, name: str) -> bool:
        """Create a settings profile."""
        return self.settings_manager.create_profile(name)
    
    def switch_profile(self, name: str) -> bool:
        """Switch to a different profile."""
        success = self.settings_manager.switch_profile(name)
        if success:
            self._apply_settings_to_options()
        return success
    
    def delete_profile(self, name: str) -> bool:
        """Delete a profile."""
        return self.settings_manager.delete_profile(name)
    
    def list_profiles(self) -> List[Dict[str, Any]]:
        """List all profiles."""
        return self.settings_manager.list_profiles()
    
    async def execute_settings_command(self, command: str, args: List[str]) -> Response:
        """
        Execute a settings-related command.
        
        Commands:
        - settings list [category]
        - settings get <key>
        - settings set <key> <value>
        - settings reset [key]
        - profile create <name>
        - profile switch <name>
        - profile delete <name>
        - profile list
        """
        try:
            if command == "settings":
                if len(args) == 0 or args[0] == "list":
                    category = args[1] if len(args) > 1 else None
                    settings = self.list_settings(category)
                    return Response(
                        success=True,
                        text=json.dumps(settings, indent=2),
                        commands=[],
                        data={"settings": settings}
                    )
                
                elif args[0] == "get" and len(args) > 1:
                    key = args[1]
                    value = self.get_setting(key)
                    return Response(
                        success=True,
                        text=f"{key} = {value}",
                        commands=[],
                        data={key: value}
                    )
                
                elif args[0] == "set" and len(args) > 2:
                    key = args[1]
                    value = " ".join(args[2:])
                    
                    # Try to parse value to appropriate type
                    if value.lower() in ["true", "false"]:
                        value = value.lower() == "true"
                    elif value.isdigit():
                        value = int(value)
                    
                    success = self.set_setting(key, value)
                    if success:
                        return Response(
                            success=True,
                            text=f"Set {key} = {value}",
                            commands=[],
                            data={"setting": key, "value": value}
                        )
                    else:
                        return Response(
                            success=False,
                            text=f"Failed to set {key}",
                            commands=[],
                            data={"error": "validation_failed"}
                        )
                
                elif args[0] == "reset":
                    key = args[1] if len(args) > 1 else None
                    self.reset_settings(key)
                    return Response(
                        success=True,
                        text=f"Reset {'all settings' if not key else key} to defaults",
                        commands=[],
                        data={"reset": key or "all"}
                    )
            
            elif command == "profile":
                if args[0] == "create" and len(args) > 1:
                    name = args[1]
                    success = self.create_profile(name)
                    return Response(
                        success=success,
                        text=f"{'Created' if success else 'Failed to create'} profile {name}",
                        commands=[],
                        data={"profile": name}
                    )
                
                elif args[0] == "switch" and len(args) > 1:
                    name = args[1]
                    success = self.switch_profile(name)
                    return Response(
                        success=success,
                        text=f"{'Switched to' if success else 'Failed to switch to'} profile {name}",
                        commands=[],
                        data={"profile": name}
                    )
                
                elif args[0] == "delete" and len(args) > 1:
                    name = args[1]
                    success = self.delete_profile(name)
                    return Response(
                        success=success,
                        text=f"{'Deleted' if success else 'Failed to delete'} profile {name}",
                        commands=[],
                        data={"profile": name}
                    )
                
                elif args[0] == "list":
                    profiles = self.list_profiles()
                    return Response(
                        success=True,
                        text=json.dumps(profiles, indent=2),
                        commands=[],
                        data={"profiles": profiles}
                    )
            
            # Unknown command
            return Response(
                success=False,
                text=f"Unknown settings command: {command} {' '.join(args)}",
                commands=[],
                data={"error": "unknown_command"}
            )
            
        except Exception as e:
            logger.error(f"Settings command error: {e}")
            return Response(
                success=False,
                text=str(e),
                commands=[],
                data={"error": str(e)}
            )


# Factory functions with full features

async def create_full_service(**kwargs) -> LuminousNixServiceWithSettings:
    """Create service with all features (learning + settings)."""
    service = LuminousNixServiceWithSettings()
    await service.initialize()
    return service