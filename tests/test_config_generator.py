#!/usr/bin/env python3
"""
Tests for Configuration Generator Plugin

Tests the NixOS configuration generation from natural language.
"""

import sys
from pathlib import Path

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from luminous_nix.api.schema import Context
from luminous_nix.core.intents import Intent, IntentType
from luminous_nix.plugins.config_generator import ConfigGeneratorPlugin

class TestConfigGeneratorPlugin:
    """Test configuration generation"""

    @pytest.fixture
    def plugin(self):
        """Create config generator plugin"""
        return ConfigGeneratorPlugin()

    def test_service_detection(self, plugin):
        """Test that services are correctly detected"""
        config = plugin.generate_config("web server with nginx and postgresql")

        # Check that both services are included
        assert "services.nginx.enable = true" in config
        assert "services.postgresql.enable = true" in config

        # Check that services aren't duplicated
        assert config.count("services.nginx.enable = true") == 1
        assert config.count("services.postgresql.enable = true") == 1

    def test_package_detection(self, plugin):
        """Test that packages are correctly detected"""
        config = plugin.generate_config("development environment with python and rust")

        # Check that development packages are included
        assert "python3" in config
        assert "rustc" in config
        assert "cargo" in config
        assert "environment.systemPackages" in config

    def test_no_duplicates(self, plugin):
        """Test that duplicates are not generated"""
        # Test with repeated mentions
        config = plugin.generate_config(
            "postgresql database with postgresql and postgres"
        )

        # Should only have one postgresql enable line
        assert config.count("services.postgresql.enable = true") == 1

        # Test with overlapping package categories
        config = plugin.generate_config("python development with python3")
        assert config.count("python3") == 1

    def test_desktop_configuration(self, plugin):
        """Test desktop environment configuration"""
        config = plugin.generate_config("desktop with firefox and vscode")

        # Check desktop settings
        assert "services.xserver.enable = true" in config
        assert "firefox" in config
        assert "vscode" in config

    def test_server_configuration(self, plugin):
        """Test server configuration"""
        config = plugin.generate_config("web server with nginx")

        # Check server settings
        assert "networking.firewall.enable = true" in config
        assert "services.openssh.enable = true" in config
        assert "services.nginx.enable = true" in config

    def test_development_configuration(self, plugin):
        """Test development environment configuration"""
        config = plugin.generate_config("development environment with docker")

        # Check development settings
        assert "programs.git.enable = true" in config
        assert "virtualisation.docker.enable = true" in config

    def test_config_structure(self, plugin):
        """Test that generated config has correct Nix structure"""
        config = plugin.generate_config("simple web server")

        # Check Nix configuration structure
        assert config.startswith("{ config, pkgs, ... }:")
        assert config.endswith("}")
        assert "{" in config
        assert "}" in config

        # Check proper indentation (Nix is sensitive to this)
        lines = config.split("\n")
        assert any(line.startswith("  ") for line in lines)

    def test_empty_description(self, plugin):
        """Test handling of empty or minimal descriptions"""
        config = plugin.generate_config("nothing specific")

        # Should still generate valid structure
        assert "{ config, pkgs, ... }:" in config
        assert "{" in config
        assert "}" in config

    @pytest.mark.asyncio
    async def test_plugin_can_handle(self, plugin):
        """Test plugin's can_handle method"""
        # Should handle config generation intents
        intent = Intent(type=IntentType.GENERATE_CONFIG, query="web server config")
        assert plugin.can_handle(intent)

        # Should handle natural language with config keywords
        intent = Intent(type=IntentType.UNKNOWN, query="setup web server with nginx")
        assert plugin.can_handle(intent)

        # Should not handle unrelated intents
        intent = Intent(type=IntentType.INSTALL, query="install firefox")
        assert not plugin.can_handle(intent)

    @pytest.mark.asyncio
    async def test_plugin_process(self, plugin):
        """Test plugin's process method"""
        intent = Intent(type=IntentType.GENERATE_CONFIG, query="web server with nginx")
        context = Context()

        result = await plugin.process(intent, context)

        assert result is not None
        assert result.success
        assert "services.nginx.enable = true" in result.output
        assert result.metadata["type"] == "nix_config"

class TestSmartSearchPlugin:
    """Test smart search functionality"""

    def test_smart_search_import(self):
        """Test that SmartSearchPlugin can be imported"""
        from luminous_nix.plugins.config_generator import SmartSearchPlugin

        assert SmartSearchPlugin is not None

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
