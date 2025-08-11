"""Simple knowledge engine for NixOS operations"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class NixOSKnowledgeEngine:
    """Basic NixOS knowledge and command mapping"""

    def __init__(self):
        self.commands = {
            "install": {
                "command": "nix-env -iA nixos.{package}",
                "description": "Install a package",
                "example": "nix-env -iA nixos.firefox",
            },
            "remove": {
                "command": "nix-env -e {package}",
                "description": "Remove a package",
                "example": "nix-env -e firefox",
            },
            "search": {
                "command": "nix search nixpkgs {query}",
                "description": "Search for packages",
                "example": "nix search nixpkgs firefox",
            },
            "update": {
                "command": "sudo nixos-rebuild switch",
                "description": "Update the system",
                "example": "sudo nixos-rebuild switch",
            },
            "rollback": {
                "command": "sudo nixos-rebuild switch --rollback",
                "description": "Rollback to previous generation",
                "example": "sudo nixos-rebuild switch --rollback",
            },
            "list": {
                "command": "nix-env -q",
                "description": "List installed packages",
                "example": "nix-env -q",
            },
            "generations": {
                "command": "nix-env --list-generations",
                "description": "List system generations",
                "example": "nix-env --list-generations",
            },
        }

    def get_command(self, intent: str, **kwargs) -> str | None:
        """Get the command for a given intent"""
        if intent in self.commands:
            cmd = self.commands[intent]["command"]
            # Format with any provided arguments
            return cmd.format(**kwargs)
        return None

    def get_help(self, intent: str | None = None) -> str:
        """Get help for commands"""
        if intent and intent in self.commands:
            cmd_info = self.commands[intent]
            return f"{cmd_info['description']}\nExample: {cmd_info['example']}"

        # Return all commands
        help_text = "Available commands:\n"
        for name, info in self.commands.items():
            help_text += f"  {name}: {info['description']}\n"
        return help_text

    def parse_query(self, query: str) -> dict[str, Any]:
        """Parse a natural language query into intent and parameters"""
        query_lower = query.lower()

        # Check for list/show commands first (before install check)
        if any(
            word in query_lower
            for word in [
                "list",
                "show",
                "display",
                "what's installed",
                "what is installed",
            ]
        ):
            # Special case for "list installed" or similar
            if "installed" in query_lower or "package" in query_lower:
                return {"intent": "list"}
            # Check for generations
            if "generation" in query_lower:
                return {"intent": "generations"}
            return {"intent": "list"}

        # Search commands
        if any(word in query_lower for word in ["search", "find", "look for"]):
            # Remove the search verb and get the query
            for word in ["search for", "find", "look for", "search"]:
                if word in query_lower:
                    query_part = query_lower.replace(word, "").strip()
                    return {"intent": "search", "query": query_part}
            return {"intent": "search", "query": query_lower}

        # Install commands (check after list to avoid confusion)
        if any(word in query_lower for word in ["install", "add", "get"]):
            # Extract package name
            words = query.split()
            package = None
            for i, word in enumerate(words):
                if word.lower() in ["install", "add", "get"] and i + 1 < len(words):
                    package = words[i + 1]
                    break
            return {"intent": "install", "package": package}

        # Remove/uninstall commands
        if any(word in query_lower for word in ["remove", "uninstall", "delete"]):
            words = query.split()
            package = None
            for i, word in enumerate(words):
                if word.lower() in ["remove", "uninstall", "delete"] and i + 1 < len(
                    words
                ):
                    package = words[i + 1]
                    break
            return {"intent": "remove", "package": package}

        # Update/upgrade commands
        if any(word in query_lower for word in ["update", "upgrade", "refresh"]):
            return {"intent": "update"}

        # Rollback commands
        if any(
            word in query_lower for word in ["rollback", "revert", "undo", "go back"]
        ):
            return {"intent": "rollback"}

        # Generation commands
        if "generation" in query_lower:
            return {"intent": "generations"}

        return {"intent": "unknown", "query": query}


class ModernNixOSKnowledgeEngine(NixOSKnowledgeEngine):
    """Extended knowledge engine with modern features"""

    def __init__(self):
        super().__init__()

        # Add flake commands
        self.commands.update(
            {
                "flake-init": {
                    "command": "nix flake init",
                    "description": "Initialize a new flake",
                    "example": "nix flake init",
                },
                "flake-update": {
                    "command": "nix flake update",
                    "description": "Update flake inputs",
                    "example": "nix flake update",
                },
                "develop": {
                    "command": "nix develop",
                    "description": "Enter development shell",
                    "example": "nix develop",
                },
                "build": {
                    "command": "nix build",
                    "description": "Build a derivation",
                    "example": "nix build .#package",
                },
            }
        )

        # Add home-manager commands
        self.commands.update(
            {
                "home-switch": {
                    "command": "home-manager switch",
                    "description": "Apply home configuration",
                    "example": "home-manager switch",
                },
                "home-generations": {
                    "command": "home-manager generations",
                    "description": "List home-manager generations",
                    "example": "home-manager generations",
                },
            }
        )

    def extract_intent(self, query: str) -> dict[str, Any]:
        """Extract intent from a natural language query

        This is an alias for parse_query() to maintain compatibility
        with older code that expects extract_intent() method.
        """
        return self.parse_query(query)

    def get_advanced_help(self) -> str:
        """Get help for advanced features"""
        return """Advanced NixOS Features:
        
Flakes:
  - nix flake init: Start a new flake project
  - nix flake update: Update dependencies
  - nix develop: Enter development environment
  
Home Manager:
  - home-manager switch: Apply user configuration
  - home-manager generations: View history
  
Configuration:
  - Edit /etc/nixos/configuration.nix
  - sudo nixos-rebuild test: Test changes
  - sudo nixos-rebuild switch: Apply changes
"""
