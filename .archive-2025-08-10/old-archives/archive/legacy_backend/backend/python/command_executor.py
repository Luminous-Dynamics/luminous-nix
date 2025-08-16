#!/usr/bin/env python3
"""
from typing import List
NixOS Command Executor - Actually runs commands safely
Phase 0: Make basic commands work!
Enhanced with comprehensive security validation
"""

import json
import logging
import os
import subprocess
import sys
from enum import Enum

# Add the src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

try:
    from src.luminous_nix.security.enhanced_validator import (
        EnhancedInputValidator,
        ValidationContext,
    )
except ImportError:
    # Fallback if module structure is different
    EnhancedInputValidator = None
    ValidationContext = None


class ExecutionMode(Enum):
    DRY_RUN = "dry-run"
    INTERACTIVE = "interactive"
    EXECUTE = "execute"


class CommandExecutor:
    """Execute NixOS commands safely with user consent"""

    def __init__(
        self,
        mode: ExecutionMode = ExecutionMode.INTERACTIVE,
        security_level: str = "balanced",
    ):
        self.mode = mode
        self.logger = logging.getLogger(__name__)
        self.security_level = security_level

        # Initialize enhanced security validator if available
        self.validator = EnhancedInputValidator() if EnhancedInputValidator else None

        # Commands that are safe to run without sudo
        self.safe_commands = {
            "search": ["nix", "search"],
            "info": ["nix-env", "-qa", "--description"],
            "list": ["nix-env", "-q"],
            "shell": ["nix-shell", "-p"],
        }

        # Commands that need careful handling
        self.privileged_commands = {
            "install": ["nix-env", "-iA"],
            "remove": ["nix-env", "-e"],
            "update": ["nix-channel", "--update"],
            "rebuild": ["nixos-rebuild", "switch"],
        }

    def execute_command(
        self, action: str, package: str = None, user_context: dict = None
    ) -> dict:
        """Execute a NixOS command based on the action with enhanced security validation"""

        # Enhanced security validation if available
        if self.validator and ValidationContext:
            # Build context for validation
            context = ValidationContext(
                user_id=(
                    user_context.get("user_id", "anonymous")
                    if user_context
                    else "anonymous"
                ),
                ip_address=(
                    user_context.get("ip_address", "127.0.0.1")
                    if user_context
                    else "127.0.0.1"
                ),
                session_id=user_context.get("session_id", "") if user_context else "",
                trust_level=(
                    user_context.get("trust_level", 0.5) if user_context else 0.5
                ),
                command_history=(
                    user_context.get("command_history", []) if user_context else []
                ),
            )

            # Validate the inputs
            validation_input = (
                {"action": action, "package": package}
                if package
                else {"action": action}
            )

            try:
                sanitized = self.validator.validate_enhanced(
                    validation_input, context, command_type=action
                )

                if not sanitized.safe:
                    return {
                        "success": False,
                        "error": "Security validation failed",
                        "reason": sanitized.reason,
                        "threat_type": sanitized.threat_type,
                        "output": "",
                    }

                # Use sanitized values
                if isinstance(sanitized.value, dict):
                    action = sanitized.value.get("action", action)
                    package = sanitized.value.get("package", package)

            except Exception as e:
                self.logger.warning(f"Enhanced validation failed, falling back: {e}")
                # Continue with basic validation

        # Original action routing
        if action == "install_package" and package:
            return self._install_package(package)
        if action == "search_package":
            return self._search_package(package)
        if action == "update_system":
            return self._update_system()
        if action == "rollback_system":
            return self._rollback_system()
        return {
            "success": False,
            "error": f"Unknown action: {action}",
            "output": "",
        }

    def _install_package(self, package: str) -> dict:
        """Install a package with proper checks and enhanced validation"""

        # Additional package name validation
        if self.validator:
            try:
                context = ValidationContext(
                    user_id="system",
                    ip_address="127.0.0.1",
                    session_id="install",
                    trust_level=0.8,
                    command_history=[],
                )

                sanitized = self.validator.validate_enhanced(
                    package, context, command_type="install_package"
                )

                if not sanitized.safe:
                    return {
                        "success": False,
                        "error": f"Invalid package name: {sanitized.reason}",
                        "suggestion": "Use only alphanumeric characters, hyphens, and underscores",
                    }

                # Use sanitized package name
                package = (
                    sanitized.value
                    if isinstance(sanitized.value, str)
                    else str(sanitized.value)
                )

            except Exception as e:
                self.logger.warning(f"Package validation error: {e}")

        # First, check if package exists
        search_result = self._run_command(["nix", "search", f"nixpkgs#{package}"])

        if not search_result["success"] or not search_result["output"]:
            return {
                "success": False,
                "error": f"Package {package} not found in nixpkgs",
                "suggestion": "Try searching with a different name",
            }

        # Build the install command
        if self.mode == ExecutionMode.DRY_RUN:
            cmd = ["nix-env", "-iA", f"nixos.{package}", "--dry-run"]
        else:
            cmd = ["nix-env", "-iA", f"nixos.{package}"]

        # In interactive mode, ask for confirmation
        if self.mode == ExecutionMode.INTERACTIVE:
            print(f"\n🔧 About to run: {' '.join(cmd)}")
            response = input("Proceed? (y/N): ")
            if response.lower() != "y":
                return {
                    "success": False,
                    "cancelled": True,
                    "output": "Installation cancelled by user",
                }

        # Execute the command
        result = self._run_command(cmd)

        if result["success"]:
            result["output"] = f"✅ Successfully installed {package}!"

            # Check if it needs to be added to PATH
            if package in ["nodejs", "python3", "rust"]:
                result[
                    "note"
                ] = "You may need to restart your shell or run 'source ~/.bashrc'"

        return result

    def _search_package(self, query: str) -> dict:
        """Search for packages"""
        cmd = ["nix", "search", "nixpkgs", query or ""]
        return self._run_command(cmd)

    def _update_system(self) -> dict:
        """Update the system"""

        if self.mode == ExecutionMode.INTERACTIVE:
            print("\n🔧 System update requires two steps:")
            print("1. Update channels: sudo nix-channel --update")
            print("2. Rebuild system: sudo nixos-rebuild switch")
            response = input("Proceed? (y/N): ")
            if response.lower() != "y":
                return {
                    "success": False,
                    "cancelled": True,
                    "output": "Update cancelled by user",
                }

        # Update channels
        channel_result = self._run_command(
            ["sudo", "nix-channel", "--update"], needs_sudo=True
        )
        if not channel_result["success"]:
            return channel_result

        # Rebuild
        if self.mode == ExecutionMode.DRY_RUN:
            rebuild_cmd = ["sudo", "nixos-rebuild", "dry-build"]
        else:
            rebuild_cmd = ["sudo", "nixos-rebuild", "switch"]

        rebuild_result = self._run_command(rebuild_cmd, needs_sudo=True)

        if rebuild_result["success"]:
            rebuild_result["output"] = "✅ System successfully updated!"

        return rebuild_result

    def _rollback_system(self) -> dict:
        """Rollback to previous generation"""

        if self.mode == ExecutionMode.INTERACTIVE:
            # Show current generations
            gen_result = self._run_command(
                [
                    "sudo",
                    "nix-env",
                    "--list-generations",
                    "--profile",
                    "/nix/var/nix/profiles/system",
                ]
            )

            print("\n📋 Current generations:")
            print(gen_result["output"])

            response = input("\nRollback to previous generation? (y/N): ")
            if response.lower() != "y":
                return {
                    "success": False,
                    "cancelled": True,
                    "output": "Rollback cancelled by user",
                }

        cmd = ["sudo", "nixos-rebuild", "switch", "--rollback"]
        return self._run_command(cmd, needs_sudo=True)

    def _run_command(self, cmd: list[str], needs_sudo: bool = False) -> dict:
        """Run a command and capture output"""

        try:
            # Log what we're doing
            self.logger.info(f"Executing: {' '.join(cmd)}")

            # Handle sudo commands
            if needs_sudo and "sudo" not in cmd:
                cmd = ["sudo"] + cmd

            # Execute
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=300  # 5 minute timeout
            )

            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None,
                "command": " ".join(cmd),
                "returncode": result.returncode,
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timed out after 5 minutes",
                "command": " ".join(cmd),
            }
        except FileNotFoundError:
            return {
                "success": False,
                "error": f"Command not found: {cmd[0]}",
                "command": " ".join(cmd),
            }
        except Exception as e:
            return {"success": False, "error": str(e), "command": " ".join(cmd)}

    def validate_environment(self) -> dict:
        """Check if we're in a proper NixOS environment"""

        checks = {
            "nixos": os.path.exists("/etc/nixos/configuration.nix"),
            "nix_env": self._run_command(["which", "nix-env"])["success"],
            "nix_channel": self._run_command(["which", "nix-channel"])["success"],
            "nixos_rebuild": self._run_command(["which", "nixos-rebuild"])["success"],
        }

        return {"valid": all(checks.values()), "checks": checks}


def main():
    """Test the executor"""
    executor = CommandExecutor(mode=ExecutionMode.DRY_RUN)

    # Validate environment
    env_check = executor.validate_environment()
    print(f"Environment valid: {env_check['valid']}")
    print(f"Checks: {json.dumps(env_check['checks'], indent=2)}")

    # Test install
    print("\n--- Testing install ---")
    result = executor.execute_command("install_package", "htop")
    print(f"Success: {result['success']}")
    print(f"Output: {result.get('output', '')}")
    print(f"Error: {result.get('error', '')}")


if __name__ == "__main__":
    main()
