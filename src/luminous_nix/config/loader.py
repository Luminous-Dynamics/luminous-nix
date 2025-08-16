"""
from typing import Dict, Optional
Configuration Loading and Parsing

Handles loading configuration from multiple sources and formats.
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import toml
import yaml

from .schema import ConfigSchema


class ConfigLoader:
    """Loads and parses configuration from various sources"""

    # Configuration search paths in priority order
    CONFIG_PATHS = [
        # Project-specific
        "./.nix-humanity/config.yaml",
        "./.nix-humanity.yaml",
        "./nix-humanity.yaml",
        # User-specific
        "~/.config/nix-for-humanity/config.yaml",
        "~/.config/nix-for-humanity/config.json",
        "~/.config/nix-for-humanity/config.toml",
        "~/.nix-for-humanity/config.yaml",  # Legacy location
        # System-wide
        "/etc/nix-for-humanity/config.yaml",
        "/etc/nix-for-humanity/config.json",
    ]

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def load_config(self, config_path: str | None = None) -> ConfigSchema:
        """Load configuration from file or search default locations"""
        if config_path:
            # Load specific config file
            data = self._load_file(config_path)
            if data:
                return self._parse_config(data, config_path)
            # If file doesn't exist, return default config
            self.logger.info(f"Config file {config_path} not found, using defaults")
            return self.create_default_config()

        # Search default locations
        config_data = {}
        loaded_files = []

        # First load system config
        for path in self.CONFIG_PATHS[-2:]:  # System paths
            expanded = os.path.expanduser(path)
            if os.path.exists(expanded):
                data = self._load_file(expanded)
                if data:
                    config_data = self._merge_configs(config_data, data)
                    loaded_files.append(expanded)

        # Then load user config (overrides system)
        for path in self.CONFIG_PATHS[3:-2]:  # User paths
            expanded = os.path.expanduser(path)
            if os.path.exists(expanded):
                data = self._load_file(expanded)
                if data:
                    config_data = self._merge_configs(config_data, data)
                    loaded_files.append(expanded)
                    break  # Only load first user config found

        # Finally load project config (overrides all)
        for path in self.CONFIG_PATHS[:3]:  # Project paths
            expanded = os.path.expanduser(path)
            if os.path.exists(expanded):
                data = self._load_file(expanded)
                if data:
                    config_data = self._merge_configs(config_data, data)
                    loaded_files.append(expanded)
                    break  # Only load first project config found

        # Apply environment variable overrides
        config_data = self._apply_env_overrides(config_data)

        # Create config object
        if config_data:
            config = self._parse_config(config_data, loaded_files)
            self.logger.info(f"Loaded configuration from: {loaded_files}")
            return config
        self.logger.info("No configuration files found, using defaults")
        return ConfigSchema()

    def _load_file(self, path: str) -> dict[str, Any] | None:
        """Load a configuration file based on its extension"""
        try:
            path_obj = Path(path)

            if path_obj.suffix in [".yaml", ".yml"]:
                with open(path) as f:
                    return yaml.safe_load(f)

            elif path_obj.suffix == ".json":
                with open(path) as f:
                    return json.load(f)

            elif path_obj.suffix == ".toml":
                with open(path) as f:
                    return toml.load(f)

            else:
                # Try to detect format
                with open(path) as f:
                    content = f.read()

                # Try JSON first
                try:
                    return json.loads(content)
                except json.JSONDecodeError as e:
                    self.logger.debug(f"Not JSON format: {e}")

                # Try YAML
                try:
                    return yaml.safe_load(content)
                except yaml.YAMLError as e:
                    self.logger.debug(f"Not YAML format: {e}")

                # Try TOML
                try:
                    return toml.loads(content)
                except toml.TomlDecodeError as e:
                    self.logger.debug(f"Not TOML format: {e}")

                self.logger.warning(f"Unable to parse config file: {path}")
                return None

        except Exception as e:
            self.logger.error(f"Error loading config file {path}: {e}")
            return None

    def _merge_configs(
        self, base: dict[str, Any], override: dict[str, Any]
    ) -> dict[str, Any]:
        """Deep merge two configuration dictionaries"""
        result = base.copy()

        for key, value in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                # Recursively merge dictionaries
                result[key] = self._merge_configs(result[key], value)
            else:
                # Override value
                result[key] = value

        return result

    def _apply_env_overrides(self, config: dict[str, Any]) -> dict[str, Any]:
        """Apply environment variable overrides to configuration"""
        env_mappings = {
            # Core settings
            "LUMINOUS_NIX_BACKEND": ("core", "backend"),
            "LUMINOUS_NIX_LOG_LEVEL": ("core", "log_level"),
            "LUMINOUS_NIX_DATA_DIR": ("core", "data_directory"),
            "LUMINOUS_NIX_CACHE_DIR": ("core", "cache_directory"),
            # UI settings
            "LUMINOUS_NIX_PERSONALITY": ("ui", "default_personality"),
            "LUMINOUS_NIX_NO_COLOR": (
                "ui",
                "use_colors",
                lambda v: v.lower() != "true",
            ),
            "LUMINOUS_NIX_THEME": ("ui", "theme"),
            # Performance settings
            "LUMINOUS_NIX_FAST_MODE": (
                "performance",
                "fast_mode",
                lambda v: v.lower() == "true",
            ),
            "LUMINOUS_NIX_TIMEOUT": ("performance", "timeout", int),
            "LUMINOUS_NIX_MEMORY_LIMIT": ("performance", "memory_limit"),
            # Privacy settings
            "LUMINOUS_NIX_LOCAL_ONLY": (
                "privacy",
                "local_only",
                lambda v: v.lower() == "true",
            ),
            "LUMINOUS_NIX_DATA_COLLECTION": ("privacy", "data_collection"),
            # Learning settings
            "LUMINOUS_NIX_LEARNING_ENABLED": (
                "learning",
                "enabled",
                lambda v: v.lower() == "true",
            ),
            # Voice settings
            "LUMINOUS_NIX_VOICE_ENABLED": (
                "voice",
                "enabled",
                lambda v: v.lower() == "true",
            ),
            "LUMINOUS_NIX_WAKE_WORD": ("voice", "wake_word"),
            # Accessibility settings
            "LUMINOUS_NIX_SCREEN_READER": (
                "accessibility",
                "screen_reader",
                lambda v: v.lower() == "true",
            ),
            "LUMINOUS_NIX_HIGH_CONTRAST": (
                "accessibility",
                "high_contrast",
                lambda v: v.lower() == "true",
            ),
            "LUMINOUS_NIX_ACCESSIBLE": (
                "accessibility",
                "screen_reader",
                lambda v: v.lower() == "true",
            ),
            # Development settings
            "LUMINOUS_NIX_DEBUG": (
                "development",
                "debug_mode",
                lambda v: v.lower() == "true",
            ),
            "LUMINOUS_NIX_MOCK": (
                "development",
                "mock_execution",
                lambda v: v.lower() == "true",
            ),
        }

        for env_var, mapping in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                if len(mapping) == 2:
                    section, key = mapping
                    transform = None
                else:
                    section, key, transform = mapping

                # Apply transformation if provided
                if transform:
                    value = transform(value)

                # Create section if it doesn't exist
                if section not in config:
                    config[section] = {}

                # Set value
                config[section][key] = value
                self.logger.debug(
                    f"Applied env override: {env_var} -> {section}.{key} = {value}"
                )

        return config

    def _parse_config(self, data: dict[str, Any], source: Any) -> ConfigSchema:
        """Parse configuration data into ConfigSchema"""
        try:
            config = ConfigSchema.from_dict(data)

            # Add metadata
            config.last_modified = datetime.now().isoformat()
            if isinstance(source, list):
                config.profile_name = f"merged from {len(source)} files"
            else:
                config.profile_name = f"loaded from {source}"

            # Validate
            errors = config.validate()
            if errors:
                self.logger.warning(f"Configuration validation errors: {errors}")

            return config

        except Exception as e:
            self.logger.error(f"Error parsing configuration: {e}")
            # Return default config on error
            return ConfigSchema()

    def save_config(
        self, config: ConfigSchema, path: str, format: str = "yaml"
    ) -> bool:
        """Save configuration to file"""
        try:
            # Ensure directory exists
            Path(path).parent.mkdir(parents=True, exist_ok=True)

            # Convert to dict
            data = config.to_dict()

            # Save based on format
            if format == "yaml":
                with open(path, "w") as f:
                    yaml.dump(data, f, default_flow_style=False, sort_keys=False)

            elif format == "json":
                with open(path, "w") as f:
                    json.dump(data, f, indent=2)

            elif format == "toml":
                with open(path, "w") as f:
                    toml.dump(data, f)

            else:
                raise ValueError(f"Unknown format: {format}")

            self.logger.info(f"Saved configuration to {path}")
            return True

        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
            return False

    def migrate_legacy_config(self) -> bool:
        """Migrate configuration from legacy locations"""
        legacy_paths = [
            "~/.nix-for-humanity/config.yaml",
            "~/.nix-humanity/config.yaml",
        ]

        new_path = "~/.config/nix-for-humanity/config.yaml"
        new_path_expanded = os.path.expanduser(new_path)

        # Don't migrate if new config already exists
        if os.path.exists(new_path_expanded):
            return False

        for legacy_path in legacy_paths:
            expanded = os.path.expanduser(legacy_path)
            if os.path.exists(expanded):
                try:
                    # Load legacy config
                    data = self._load_file(expanded)
                    if data:
                        # Create new config directory
                        Path(new_path_expanded).parent.mkdir(
                            parents=True, exist_ok=True
                        )

                        # Save to new location
                        with open(new_path_expanded, "w") as f:
                            yaml.dump(data, f, default_flow_style=False)

                        self.logger.info(
                            f"Migrated configuration from {expanded} to {new_path_expanded}"
                        )

                        # Rename old file
                        os.rename(expanded, f"{expanded}.migrated")

                        return True

                except Exception as e:
                    self.logger.error(f"Error migrating configuration: {e}")

        return False

    def create_default_config(self, path: str | None = None) -> str:
        """Create a default configuration file"""
        if not path:
            path = os.path.expanduser("~/.config/nix-for-humanity/config.yaml")

        # Ensure directory exists
        Path(path).parent.mkdir(parents=True, exist_ok=True)

        # Create default config
        config = ConfigSchema()

        # Save it
        self.save_config(config, path)

        return path
