#!/usr/bin/env python3
"""
from typing import Dict, List, Optional
NixOS Python Backend - Direct integration with nixos-rebuild
Implements intelligent fallback between Python API and subprocess

This module provides:
1. Dynamic discovery of nixos-rebuild Python modules
2. Direct Python API integration when available
3. Graceful fallback to subprocess commands
4. Real-time progress callbacks
5. Comprehensive error handling
"""

import asyncio
import json
import logging
import re
import subprocess
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Action(Enum):
    """NixOS rebuild actions"""

    SWITCH = "switch"
    BOOT = "boot"
    TEST = "test"
    BUILD = "build"
    DRY_BUILD = "dry-build"
    DRY_RUN = "dry-run"
    DRY_ACTIVATE = "dry-activate"
    BUILD_VM = "build-vm"
    BUILD_VM_WITH_BOOTLOADER = "build-vm-with-bootloader"
    ROLLBACK = "rollback"
    LIST_GENERATIONS = "list-generations"


@dataclass
class BuildResult:
    """Result of a NixOS build operation"""

    success: bool
    action: Action
    output: str
    error: str | None = None
    duration: float | None = None
    store_paths: list[str] = None
    generation: int | None = None


class NixOSPythonBackend:
    """
    Unified NixOS backend with intelligent Python API / subprocess fallback

    Provides:
    - Automatic detection of nixos-rebuild Python modules
    - Direct API calls when available (NixOS 25.11+)
    - Graceful fallback to subprocess for older versions
    - Progress callbacks and real-time feedback
    - Comprehensive error handling
    """

    def __init__(self, use_sudo: bool = True):
        self.use_sudo = use_sudo
        self.has_python_api = False
        self.nixos_rebuild_module = None
        self.progress_callbacks: list[Callable] = []

        # Try to import nixos-rebuild Python API
        self._discover_python_api()

    def _discover_python_api(self) -> bool:
        """Discover and import nixos-rebuild Python modules if available"""
        try:
            # Method 1: Try to find nixos-rebuild in PATH and extract module path
            nixos_rebuild_path = subprocess.check_output(
                ["which", "nixos-rebuild"], text=True
            ).strip()

            if nixos_rebuild_path:
                # Resolve symlinks to find actual nix store path
                real_path = Path(nixos_rebuild_path).resolve()
                nix_store_path = str(real_path.parent.parent)

                # Look for Python modules in typical locations
                possible_paths = [
                    f"{nix_store_path}/lib/python3.11/site-packages",
                    f"{nix_store_path}/lib/python3.12/site-packages",
                    f"{nix_store_path}/lib/python3.13/site-packages",
                ]

                for py_path in possible_paths:
                    if Path(py_path).exists():
                        sys.path.insert(0, py_path)
                        try:
                            # Try to import the module
                            import nixos_rebuild

                            self.nixos_rebuild_module = nixos_rebuild
                            self.has_python_api = True
                            logger.info(
                                f"✅ Found nixos-rebuild Python API at {py_path}"
                            )
                            return True
                        except ImportError:
                            sys.path.remove(py_path)

        except (subprocess.CalledProcessError, FileNotFoundError):
            # TODO: Add proper error handling
            pass  # Silent for now, should log error

        # Method 2: Search nix store directly
        try:
            result = subprocess.run(
                ["find", "/nix/store", "-name", "nixos_rebuild", "-type", "d"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            for line in result.stdout.splitlines():
                if "site-packages" in line:
                    parent_path = str(Path(line).parent)
                    sys.path.insert(0, parent_path)
                    try:
                        import nixos_rebuild

                        self.nixos_rebuild_module = nixos_rebuild
                        self.has_python_api = True
                        logger.info(
                            f"✅ Found nixos-rebuild Python API at {parent_path}"
                        )
                        return True
                    except ImportError:
                        sys.path.remove(parent_path)

        except (subprocess.TimeoutExpired, Exception):
            # TODO: Add proper error handling
            pass  # Silent for now, should log error

        logger.info("ℹ️  No nixos-rebuild Python API found, using subprocess fallback")
        return False

    def add_progress_callback(self, callback: Callable[[str, float], None]):
        """Add a progress callback function"""
        self.progress_callbacks.append(callback)

    def _notify_progress(self, message: str, percentage: float = -1):
        """Notify all progress callbacks"""
        for callback in self.progress_callbacks:
            try:
                callback(message, percentage)
            except Exception as e:
                logger.error(f"Progress callback error: {e}")

    async def execute_action(self, action: Action, **kwargs) -> BuildResult:
        """
        Execute a NixOS action with automatic API/subprocess selection

        Args:
            action: The Action to perform
            **kwargs: Additional arguments for the action

        Returns:
            BuildResult with operation status and details
        """
        start_time = time.time()

        if self.has_python_api:
            result = await self._execute_via_api(action, **kwargs)
        else:
            result = await self._execute_via_subprocess(action, **kwargs)

        result.duration = time.time() - start_time
        return result

    async def _execute_via_api(self, action: Action, **kwargs) -> BuildResult:
        """Execute using direct Python API (NixOS 25.11+)"""
        try:
            # Import required components
            from nixos_rebuild import models, nix

            self._notify_progress(f"Starting {action.value} via Python API", 0)

            # Map our Action enum to nixos-rebuild's Action
            api_action = getattr(models.Action, action.name)

            # Get profile
            profile = models.Profile.from_arg(kwargs.get("profile_name", "system"))

            # Build configuration
            if action in [Action.SWITCH, Action.BOOT, Action.TEST, Action.BUILD]:
                self._notify_progress("Building NixOS configuration", 20)

                # Build the system
                build_attr = models.BuildAttr(
                    attr="config.system.build.toplevel",
                    file=kwargs.get("file", "/etc/nixos/configuration.nix"),
                )

                # Use progress callback during build
                def build_progress(line: str):
                    # Parse nix build output for progress
                    if "building" in line:
                        self._notify_progress(line, 40)
                    elif "copying" in line:
                        self._notify_progress(line, 60)

                path = await nix.build(
                    build_attr.attr, build_attr, progress_callback=build_progress
                )

                self._notify_progress("Build complete, activating", 80)

            # Execute action
            if action == Action.SWITCH:
                await nix.switch_to_configuration(path, api_action, profile)
                self._notify_progress("System switched successfully", 100)

            elif action == Action.ROLLBACK:
                await nix.rollback(profile)
                self._notify_progress("Rollback complete", 100)

            elif action == Action.LIST_GENERATIONS:
                generations = await nix.list_generations(profile)
                return BuildResult(
                    success=True,
                    action=action,
                    output=json.dumps(generations, indent=2),
                )

            # Get current generation number
            gen_info = await nix.get_current_generation(profile)

            return BuildResult(
                success=True,
                action=action,
                output=f"Successfully executed {action.value}",
                generation=gen_info.get("number"),
            )

        except Exception as e:
            logger.error(f"Python API error: {e}")
            return BuildResult(success=False, action=action, output="", error=str(e))

    async def _execute_via_subprocess(self, action: Action, **kwargs) -> BuildResult:
        """Execute using subprocess (fallback for older NixOS)"""
        try:
            # Build command
            cmd = []
            if self.use_sudo:
                cmd.extend(["sudo"])

            cmd.extend(["nixos-rebuild", action.value])

            # Add optional arguments
            if kwargs.get("flake"):
                cmd.extend(["--flake", kwargs["flake"]])
            if kwargs.get("profile_name"):
                cmd.extend(["--profile-name", kwargs["profile_name"]])
            if kwargs.get("upgrade"):
                cmd.append("--upgrade")
            if kwargs.get("show_trace"):
                cmd.append("--show-trace")

            self._notify_progress(f"Executing: {' '.join(cmd)}", 10)

            # Run with real-time output
            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            output_lines = []
            store_paths = []

            # Read output in real-time
            while True:
                line = await process.stdout.readline()
                if not line:
                    break

                line_str = line.decode("utf-8").strip()
                output_lines.append(line_str)

                # Parse progress from output
                if "building" in line_str.lower():
                    self._notify_progress(line_str, 30)
                elif "copying" in line_str.lower():
                    self._notify_progress(line_str, 50)
                elif "activating" in line_str.lower():
                    self._notify_progress(line_str, 80)

                # Extract store paths
                if "/nix/store/" in line_str:
                    match = re.search(r"/nix/store/[\w-]+", line_str)
                    if match:
                        store_paths.append(match.group(0))

            # Wait for completion
            await process.wait()

            if process.returncode == 0:
                self._notify_progress(f"{action.value} completed successfully", 100)
                return BuildResult(
                    success=True,
                    action=action,
                    output="\n".join(output_lines),
                    store_paths=store_paths,
                )
            stderr = await process.stderr.read()
            return BuildResult(
                success=False,
                action=action,
                output="\n".join(output_lines),
                error=stderr.decode("utf-8"),
            )

        except Exception as e:
            logger.error(f"Subprocess error: {e}")
            return BuildResult(success=False, action=action, output="", error=str(e))

    async def install_package(
        self, package: str, method: str = "profile"
    ) -> BuildResult:
        """
        Install a package using various methods

        Args:
            package: Package name to install
            method: Installation method (profile, env, shell)
        """
        self._notify_progress(f"Installing {package} via {method}", 0)

        try:
            if method == "profile":
                # Modern nix profile install
                cmd = ["nix", "profile", "install", f"nixpkgs#{package}"]

            elif method == "env":
                # Legacy nix-env
                cmd = ["nix-env", "-iA", f"nixpkgs.{package}"]

            elif method == "shell":
                # Temporary shell
                cmd = ["nix-shell", "-p", package, "--run", 'echo "Package available"']

            else:
                return BuildResult(
                    success=False,
                    action=Action.BUILD,
                    output="",
                    error=f"Unknown installation method: {method}",
                )

            # Execute command
            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                self._notify_progress(f"{package} installed successfully", 100)
                return BuildResult(
                    success=True, action=Action.BUILD, output=stdout.decode("utf-8")
                )
            return BuildResult(
                success=False,
                action=Action.BUILD,
                output=stdout.decode("utf-8"),
                error=stderr.decode("utf-8"),
            )

        except Exception as e:
            return BuildResult(
                success=False, action=Action.BUILD, output="", error=str(e)
            )

    async def search_packages(self, query: str) -> list[dict[str, str]]:
        """Search for packages in nixpkgs"""
        try:
            cmd = ["nix", "search", "nixpkgs", query, "--json"]

            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, _ = await process.communicate()

            if process.returncode == 0:
                results = json.loads(stdout.decode("utf-8"))
                packages = []

                for pkg_path, info in results.items():
                    # Extract package name from path
                    pkg_name = pkg_path.split(".")[-1]
                    packages.append(
                        {
                            "name": pkg_name,
                            "version": info.get("version", "unknown"),
                            "description": info.get("description", ""),
                            "path": pkg_path,
                        }
                    )

                return packages

        except Exception as e:
            logger.error(f"Search error: {e}")
            return []

    async def get_system_info(self) -> dict[str, Any]:
        """Get current NixOS system information"""
        info = {}

        try:
            # Get NixOS version
            version_output = subprocess.check_output(
                ["nixos-version"], text=True
            ).strip()
            info["nixos_version"] = version_output

            # Get current generation
            gen_output = subprocess.check_output(
                ["nixos-rebuild", "list-generations"], text=True
            )

            # Parse current generation
            for line in gen_output.splitlines():
                if "(current)" in line:
                    match = re.match(r"(\d+)", line)
                    if match:
                        info["current_generation"] = int(match.group(1))

            # Check if Python API is available
            info["has_python_api"] = self.has_python_api

            # Get channel info
            channels = subprocess.check_output(["nix-channel", "--list"], text=True)
            info["channels"] = channels.strip()

        except Exception as e:
            logger.error(f"Error getting system info: {e}")

        return info


# Migration helper for gradual transition
class HybridNixOSBackend:
    """
    Hybrid backend that intelligently chooses between Python API and subprocess
    Provides seamless migration path
    """

    def __init__(self):
        self.backend = NixOSPythonBackend()

    async def execute(self, command: str, progress_callback=None) -> dict[str, Any]:
        """
        Execute a natural language command
        Maps to appropriate backend method
        """
        if progress_callback:
            self.backend.add_progress_callback(progress_callback)

        # Parse command intent
        command_lower = command.lower()

        if "install" in command_lower:
            # Extract package name
            package = self._extract_package_name(command)
            if package:
                result = await self.backend.install_package(package)
                return self._format_result(result)

        elif "update" in command_lower or "upgrade" in command_lower:
            result = await self.backend.execute_action(Action.SWITCH, upgrade=True)
            return self._format_result(result)

        elif "rollback" in command_lower:
            result = await self.backend.execute_action(Action.ROLLBACK)
            return self._format_result(result)

        elif "search" in command_lower:
            query = self._extract_search_query(command)
            packages = await self.backend.search_packages(query)
            return {"success": True, "packages": packages, "count": len(packages)}

        elif "test" in command_lower:
            result = await self.backend.execute_action(Action.TEST)
            return self._format_result(result)

        else:
            return {
                "success": False,
                "error": f"Unable to understand command: {command}",
            }

    def _extract_package_name(self, command: str) -> str | None:
        """Extract package name from install command"""
        # Simple extraction - can be enhanced with NLP
        words = command.split()
        if "install" in words:
            idx = words.index("install")
            if idx + 1 < len(words):
                return words[idx + 1]
        return None

    def _extract_search_query(self, command: str) -> str:
        """Extract search query from command"""
        # Remove common words
        stop_words = {"search", "for", "find", "look", "packages"}
        words = [w for w in command.split() if w.lower() not in stop_words]
        return " ".join(words)

    def _format_result(self, result: BuildResult) -> dict[str, Any]:
        """Format BuildResult for JSON response"""
        return {
            "success": result.success,
            "action": result.action.value,
            "output": result.output,
            "error": result.error,
            "duration": result.duration,
            "generation": result.generation,
        }


# Example usage and testing
async def main():
    """Test the backend functionality"""
    backend = NixOSPythonBackend()

    # Add progress callback
    def progress(msg, pct):
        if pct >= 0:
            print(f"[{pct:3.0f}%] {msg}")
        else:
            print(f"[...] {msg}")

    backend.add_progress_callback(progress)

    # Get system info
    print("🔍 System Information:")
    info = await backend.get_system_info()
    for key, value in info.items():
        print(f"  {key}: {value}")

    print("\n" + "=" * 50 + "\n")

    # Test search
    print("🔎 Searching for 'firefox':")
    packages = await backend.search_packages("firefox")
    for pkg in packages[:3]:
        print(f"  - {pkg['name']} ({pkg['version']}): {pkg['description'][:60]}...")

    print("\n" + "=" * 50 + "\n")

    # Test hybrid backend
    print("🌐 Testing Hybrid Backend:")
    hybrid = HybridNixOSBackend()

    commands = ["search firefox", "install htop", "update my system", "rollback"]

    for cmd in commands:
        print(f"\n📝 Command: {cmd}")
        result = await hybrid.execute(cmd, progress)
        print(f"✅ Success: {result.get('success')}")
        if result.get("error"):
            print(f"❌ Error: {result['error']}")


if __name__ == "__main__":
    asyncio.run(main())
