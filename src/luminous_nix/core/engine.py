"""
from typing import Dict, List, Optional
Main backend for Nix for Humanity

This is the unified backend that serves all frontend adapters (CLI, TUI, API, Voice).
It provides direct integration with nixos-rebuild-ng API for superior performance.
"""

import asyncio
import logging
import os
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

from luminous_nix.api.schema import Request, Response, Result
from luminous_nix.core.error_handler import ErrorContext, error_handler
from luminous_nix.core.intents import Intent, IntentRecognizer, IntentType

from .executor import SafeExecutor
from .knowledge import KnowledgeBase
from .package_discovery import PackageDiscovery

# Setup logging (moved up to be available for imports)
logger = logging.getLogger(__name__)

# Import the enhanced response system
try:
    from .responses import ResponseGenerator

    ENHANCED_RESPONSES_AVAILABLE = True
except ImportError:
    ENHANCED_RESPONSES_AVAILABLE = False
    logger.warning("Enhanced response system not available")

# Import XAI engine for intelligent explanations (optional feature)
try:
    # Add parent paths to find the XAI module
    import sys
    from pathlib import Path

    features_path = Path(__file__).parent.parent.parent / "features" / "v3.0" / "xai"
    if features_path.exists() and str(features_path) not in sys.path:
        sys.path.insert(0, str(features_path))

    from causal_xai_engine import CausalXAIEngine, ExplanationDepth

    XAI_AVAILABLE = True
except ImportError:
    XAI_AVAILABLE = False
    # XAI is an optional advanced feature - no warning needed
    logger.debug("XAI engine not available (optional feature)")

# Try to import native NixOS integration
try:
    from .nix_integration import NATIVE_API_AVAILABLE, NixOSIntegration

    NATIVE_INTEGRATION_AVAILABLE = True
except ImportError:
    NATIVE_INTEGRATION_AVAILABLE = False
    NATIVE_API_AVAILABLE = False

# Import our new native API implementation
try:
    from ..backend.native_nix_api import (
        HAS_NATIVE_API,
        NativeNixAPI,
        NixForHumanityNativeBackend,
    )

    NATIVE_API_IMPLEMENTATION = True
except ImportError:
    NATIVE_API_IMPLEMENTATION = False
    HAS_NATIVE_API = False


class NixForHumanityBackend:
    """Unified backend for all Nix for Humanity operations"""

    def __init__(self, progress_callback: Callable | None = None):
        """
        Initialize the backend

        Args:
            progress_callback: Optional callback for progress updates
        """
        self.intent_recognizer = IntentRecognizer()
        self.executor = SafeExecutor(progress_callback)
        self.knowledge = KnowledgeBase()
        self.package_discovery = PackageDiscovery()
        self.progress_callback = progress_callback
        self.dry_run = True  # Default to dry run for safety
        self._init_nixos_api()

        # Initialize XAI engine for intelligent explanations
        self.xai_engine = None
        if XAI_AVAILABLE:
            try:
                self.xai_engine = CausalXAIEngine()
                logger.info("✅ XAI engine initialized for intelligent explanations")
            except Exception as e:
                logger.warning(f"Failed to initialize XAI engine: {e}")

        # Initialize enhanced response system if available
        if ENHANCED_RESPONSES_AVAILABLE:
            self.response_generator = ResponseGenerator()
            self.use_enhanced_responses = (
                os.getenv("LUMINOUS_NIX_ENHANCED_RESPONSES", "true").lower() == "true"
            )
        else:
            self.response_generator = None
            self.use_enhanced_responses = False

    def _init_nixos_api(self):
        """Initialize direct nixos-rebuild-ng API"""
        self.nix_integration = None
        self.native_api = None
        self._has_python_api = False  # Initialize the attribute
        logger.info("🚀 Initializing native backend with 10x-1500x performance")

        # Try our new native API implementation first
        if NATIVE_API_IMPLEMENTATION:
            try:
                self.native_api = NativeNixAPI(use_native=True)
                self.native_backend = NixForHumanityNativeBackend()
                self._has_python_api = True
                logger.info(
                    "✅ Using Native Python-Nix API with 10x-1500x performance!"
                )

                # Show performance stats
                stats = self.native_api.get_performance_stats()
                logger.info(f"📊 API Type: {stats['api_type']}")
                for metric, value in stats["performance_gains"].items():
                    logger.debug(f"  {metric}: {value}")

            except Exception as e:
                logger.warning(f"Native API initialization failed: {e}")
                self._has_python_api = False

        # Fallback to original approach
        if not self._has_python_api:
            try:
                # Find nixos-rebuild-ng path dynamically
                nixos_rebuild_path = self._find_nixos_rebuild_path()
                if nixos_rebuild_path and str(nixos_rebuild_path) not in sys.path:
                    sys.path.insert(0, str(nixos_rebuild_path))

                # Try to import the modules - proper environment required
                try:
                    from nixos_rebuild import models, nix

                    self.nix_api = nix
                    self.nix_models = models
                    self._has_python_api = True
                    logger.info("✅ Using real nixos-rebuild-ng API")
                except (ImportError, SyntaxError) as e:
                    # Document the environment blocker - NO MOCKS
                    self._has_python_api = False
                    self.nix_api = None
                    self.nix_models = None
                    logger.warning(f"⚠️ nixos-rebuild-ng not available: {e}")
                    logger.warning(
                        "📝 This requires Python 3.13+ or proper nix-shell environment"
                    )
                    logger.warning(
                        "🔧 Fix: Use 'nix develop' or update Python to 3.13+"
                    )

                if self.progress_callback:
                    self.progress_callback("Python NixOS API initialized", 0.1)

            except ImportError as e:
                # Fallback to subprocess mode
                self._has_python_api = False
                if os.getenv("DEBUG"):
                    print(f"Python API not available: {e}")

    def search_packages(self, query: str, limit: int = 10) -> list[Any]:
        """Search for packages using smart discovery.

        Uses native API for 1500x performance improvement when available!

        Args:
            query: Natural language search query
            limit: Maximum number of results

        Returns:
            List of package matches
        """
        # Use native API if available (1500x faster!)
        if self.native_api:
            try:
                results = self.native_api.search_packages(query)
                return results[:limit] if results else []
            except Exception as e:
                logger.warning(f"Native search failed, falling back: {e}")

        # Fallback to original package discovery
        return self.package_discovery.search_packages(query, limit)

    def get_current_context(self) -> dict[str, Any]:
        """Get current context information for TUI display.

        Returns:
            Dict containing current state, settings, and context
        """
        return {
            "personality": self.get_current_personality(),
            "native_api_enabled": self._has_python_api,
            "current_directory": str(Path.cwd()),
            "nixos_version": (
                self._get_nixos_version()
                if hasattr(self, "_get_nixos_version")
                else "Unknown"
            ),
            "generation": (
                self._get_current_generation()
                if hasattr(self, "_get_current_generation")
                else "Unknown"
            ),
        }

    def get_settings(self) -> dict[str, Any]:
        """Get current settings for TUI configuration panel.

        Returns:
            Dict of current settings
        """
        return {
            "personality": self.get_current_personality(),
            "execute_commands": False,  # Safety first
            "show_explanations": True,
            "native_api": self._has_python_api,
            "voice_enabled": False,  # For future
            "theme": "dark",  # TUI theme
        }

    def execute_command(self, command: str, dry_run: bool = True) -> dict[str, Any]:
        """Execute a Nix command with safety checks.

        Args:
            command: The command to execute
            dry_run: If True, only show what would be done

        Returns:
            Dict with success, output, and error information
        """
        # For simple command execution, bypass the full intent system
        import subprocess

        try:
            if dry_run:
                # Just return what would be done
                return {
                    "success": True,
                    "output": f"Would execute: {command}",
                    "error": None,
                    "command": command,
                    "dry_run": dry_run,
                }
            # Actually execute (be careful!)
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=30
            )

            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None,
                "command": command,
                "dry_run": dry_run,
            }

        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": str(e),
                "command": command,
                "dry_run": dry_run,
            }

    def get_suggestions(self, partial: str, context: str | None = None) -> list[str]:
        """Get autocomplete suggestions for partial input.

        Args:
            partial: Partial text to complete
            context: Optional context (like current command type)

        Returns:
            List of suggestions
        """
        suggestions = []

        # Package name suggestions
        if context == "package" or "install" in partial.lower():
            packages = self.search_packages(partial, limit=5)
            suggestions.extend([p.name for p in packages])

        # Command suggestions
        command_starters = [
            "install",
            "remove",
            "search",
            "update",
            "rollback",
            "list generations",
            "show installed",
            "help",
        ]
        for cmd in command_starters:
            if cmd.startswith(partial.lower()):
                suggestions.append(cmd)

        return suggestions[:10]  # Limit suggestions

    def get_current_personality(self) -> str:
        """Get the current personality setting."""
        # Default personality
        return "balanced"

    def _get_nixos_version(self) -> str:
        """Get NixOS version (if not already defined)."""
        if hasattr(super(), "_get_nixos_version"):
            return super()._get_nixos_version()

        try:
            import subprocess

            result = subprocess.run(["nixos-version"], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception as e:
            logger.debug(f"Failed to get NixOS version: {e}")

        return "Unknown"

    def _get_current_generation(self) -> str:
        """Get current system generation."""
        try:
            import subprocess

            result = subprocess.run(
                ["nix-env", "--list-generations", "-p", "/nix/var/nix/profiles/system"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                for line in lines:
                    if "(current)" in line:
                        return line.split()[0]
        except Exception as e:
            logger.debug(f"Failed to get current generation: {e}")

        return "Unknown"

    def _find_nixos_rebuild_path(self) -> Path | None:
        """Find the nixos-rebuild-ng module path"""
        try:
            # Method 1: Check known paths
            known_paths = [
                Path(
                    "/nix/store/nmg1ksa23fpsl631x3n8lnp9467vqiqi-nixos-rebuild-ng-0.0.0/lib/python3.13/site-packages"
                ),
                Path("/run/current-system/sw/lib/python3.13/site-packages"),
            ]

            for path in known_paths:
                if path.exists() and (path / "nixos_rebuild").exists():
                    return path

            # Method 2: Find via which command
            import subprocess

            result = subprocess.run(
                ["which", "nixos-rebuild"], capture_output=True, text=True
            )

            if result.returncode == 0:
                rebuild_path = Path(result.stdout.strip()).resolve()
                # Go up to find site-packages
                for parent in rebuild_path.parents:
                    site_packages = parent / "lib" / "python3.13" / "site-packages"
                    if (
                        site_packages.exists()
                        and (site_packages / "nixos_rebuild").exists()
                    ):
                        return site_packages

        except Exception as e:
            if os.getenv("DEBUG"):
                print(f"Error finding nixos-rebuild path: {e}")

        return None

    async def process_request(self, request: Request) -> Response:
        """
        Main entry point for all requests

        Args:
            request: The incoming request

        Returns:
            Response with results
        """
        try:
            # SECURITY: Validate and sanitize all user input first
            from luminous_nix.security.input_validator import InputValidator

            # Get the text from request safely
            request_text = getattr(request, "text", None) or getattr(
                request, "query", ""
            )

            # Validate input
            validation_result = InputValidator.validate_input(request_text, "nlp")
            if not validation_result["valid"]:
                return Response(
                    intent=Intent(
                        type=IntentType.UNKNOWN,
                        entities={},
                        confidence=0.0,
                        raw_input=request_text,
                    ),
                    plan=[],
                    result=Result(
                        success=False,
                        output="",
                        error=f"Input validation failed: {validation_result['reason']}",
                    ),
                    explanation=f"I couldn't process that request safely: {validation_result['reason']}",
                    suggestions=validation_result.get(
                        "suggestions", ["Please rephrase your request"]
                    ),
                    success=False,
                    commands=[],
                )

            # Use sanitized input for further processing
            sanitized_text = validation_result.get("sanitized_input", request_text)

            # Check if we should use native integration
            if NATIVE_INTEGRATION_AVAILABLE and self._should_use_native_api(request):
                return await self._process_native(request)

            # Otherwise, use traditional flow
            # 1. Recognize intent
            if self.progress_callback:
                self.progress_callback("Analyzing request...", 0.2)

            intent = await self.intent_recognizer.recognize(
                sanitized_text, request.context
            )

            # 2. Validate and plan
            if self.progress_callback:
                self.progress_callback("Planning actions...", 0.4)

            plan = await self._plan_actions(intent, request)

            # 3. Execute if requested
            result = None
            if request.context.get("execute", False) and not request.context.get(
                "dry_run", False
            ):
                if self.progress_callback:
                    self.progress_callback("Executing...", 0.6)

                result = await self.executor.execute(plan, intent)

            # 4. Generate response
            if self.progress_callback:
                self.progress_callback("Generating response...", 0.8)

            # Use enhanced response system if available and enabled
            if self.use_enhanced_responses and self.response_generator:
                response = self._generate_enhanced_response(intent, plan, result)
            else:
                # Fall back to traditional response
                response = Response(
                    intent=intent,
                    plan=plan,
                    result=result,
                    explanation=self._explain(intent, plan, result),
                    suggestions=self._get_suggestions(intent, result),
                    success=result.success if result else True,
                    commands=self._extract_commands(plan),
                )

            # 5. Learn from interaction (async, don't wait)
            asyncio.create_task(self._learn(request, response))

            if self.progress_callback:
                self.progress_callback("Complete!", 1.0)

            return response

        except Exception as e:
            # Use comprehensive error handler
            context = ErrorContext(
                operation="process_request",
                user_input=getattr(request, "text", getattr(request, "query", "")),
                metadata={"request_context": request.context},
            )

            nix_error = error_handler.handle_error(e, context)

            # Try to get XAI-powered error explanation
            error_explanation = nix_error.user_message
            error_suggestions = nix_error.suggestions

            if self.xai_engine:
                try:
                    xai_error_result = self.xai_engine.explain_error(
                        str(e),
                        {
                            "operation": context.operation,
                            "user_input": context.user_input,
                        },
                    )

                    if xai_error_result.get("understood"):
                        error_explanation = (
                            f"{xai_error_result.get('why', error_explanation)}"
                        )

                        # Add confidence indicator
                        confidence = xai_error_result.get("confidence", 0)
                        if confidence > 0:
                            conf_str = (
                                "High"
                                if confidence > 0.8
                                else "Medium" if confidence > 0.5 else "Low"
                            )
                            error_explanation += f" (Confidence: {conf_str})"

                        # Use XAI's suggestions if available
                        xai_fixes = xai_error_result.get("how_to_fix", [])
                        if xai_fixes:
                            error_suggestions = xai_fixes[:3]  # Top 3 suggestions

                except Exception as xai_e:
                    logger.debug(f"XAI error explanation failed: {xai_e}")

            # Handle errors gracefully with rich information
            return Response(
                intent=Intent(
                    type=IntentType.UNKNOWN,
                    entities={},
                    confidence=0.0,
                    raw_input=context.user_input,
                ),
                plan=[],
                result=Result(success=False, output="", error=error_explanation),
                explanation=error_explanation,
                suggestions=error_suggestions,
                success=False,
                commands=[],
                data={"error_code": nix_error.error_code},
            )

    async def _plan_actions(self, intent: Intent, request: Request) -> list:
        """Plan the actions to take based on intent"""
        plan = []

        if intent.type == IntentType.INSTALL_PACKAGE:
            package = intent.entities.get("package")
            if package:
                # Check if we have Python API
                if self._has_python_api:
                    plan.append(f"Use Python API to install {package}")
                else:
                    plan.append(f"Use nix profile install nixpkgs#{package}")

                plan.append(f"Verify {package} installation")

        elif intent.type == IntentType.UPDATE_SYSTEM:
            if self._has_python_api:
                plan.append("Use Python API for system update")
            else:
                plan.append("Update channels: sudo nix-channel --update")
                plan.append("Rebuild system: sudo nixos-rebuild switch")

        elif intent.type == IntentType.SEARCH_PACKAGE:
            query = intent.entities.get("query", "")
            plan.append(f"Search for packages matching '{query}'")

        elif intent.type == IntentType.ROLLBACK:
            plan.append("List available generations")
            plan.append("Rollback to previous generation")

        elif intent.type == IntentType.CONFIGURE:
            config = intent.entities.get("config", "")
            plan.append(f"Help configure {config}")

        elif intent.type == IntentType.EXPLAIN:
            topic = intent.entities.get("topic", "")
            plan.append(f"Explain {topic}")

        elif intent.type == IntentType.HELP:
            plan.append("Show available commands and examples")

        elif intent.type == IntentType.REMOVE_PACKAGE:
            package = intent.entities.get("package")
            if package:
                if self._has_python_api:
                    plan.append(f"Use Python API to remove {package}")
                else:
                    plan.append(f"Use nix profile remove nixpkgs#{package}")
                plan.append(f"Verify {package} removal")

        elif intent.type == IntentType.GARBAGE_COLLECT:
            plan.append("Check how much space can be freed")
            plan.append("Run garbage collection to clean old packages")

        elif intent.type == IntentType.LIST_GENERATIONS:
            plan.append("List all system generations")

        elif intent.type == IntentType.SWITCH_GENERATION:
            generation = intent.entities.get("generation")
            if generation:
                plan.append(f"Switch to generation {generation}")
                plan.append("Activate the configuration")

        elif intent.type == IntentType.REBUILD:
            rebuild_type = intent.entities.get("rebuild_type", "switch")
            plan.append(f"Run nixos-rebuild {rebuild_type}")

        elif intent.type == IntentType.EDIT_CONFIG:
            plan.append("Show how to edit configuration.nix")

        elif intent.type == IntentType.SHOW_CONFIG:
            plan.append("Display configuration.nix contents")

        elif intent.type == IntentType.CHECK_STATUS:
            plan.append("Check system status and health")

        elif intent.type == IntentType.LIST_INSTALLED:
            plan.append("List installed packages")

        # Network management intents
        elif intent.type == IntentType.SHOW_NETWORK:
            plan.append("Check network configuration and status")
            plan.append("Display network interfaces and routing")

        elif intent.type == IntentType.SHOW_IP:
            plan.append("Display IP addresses for all interfaces")
            plan.append("Show external IP if available")

        elif intent.type == IntentType.CONNECT_WIFI:
            ssid = intent.entities.get("ssid")
            if ssid:
                plan.append(f"Connect to WiFi network '{ssid}'")
            else:
                plan.append("Connect to WiFi network (SSID needed)")

        elif intent.type == IntentType.LIST_WIFI:
            plan.append("Scan for available WiFi networks")

        elif intent.type == IntentType.TEST_CONNECTION:
            plan.append("Test DNS resolution")
            plan.append("Test internet connectivity")
            plan.append("Test web access")

        # Service management intents
        elif intent.type == IntentType.START_SERVICE:
            service = intent.entities.get("service")
            if service:
                plan.append(f"Start service '{service}'")
                plan.append("Verify service is active")

        elif intent.type == IntentType.STOP_SERVICE:
            service = intent.entities.get("service")
            if service:
                plan.append(f"Stop service '{service}'")

        elif intent.type == IntentType.RESTART_SERVICE:
            service = intent.entities.get("service")
            if service:
                plan.append(f"Restart service '{service}'")
                plan.append("Verify service is active")

        elif intent.type == IntentType.SERVICE_STATUS:
            service = intent.entities.get("service")
            if service:
                plan.append(f"Check status of service '{service}'")

        elif intent.type == IntentType.LIST_SERVICES:
            plan.append("List all system services")

        elif intent.type == IntentType.ENABLE_SERVICE:
            service = intent.entities.get("service")
            if service:
                plan.append(f"Enable service '{service}' to start at boot")

        elif intent.type == IntentType.DISABLE_SERVICE:
            service = intent.entities.get("service")
            if service:
                plan.append(f"Disable service '{service}' from starting at boot")

        elif intent.type == IntentType.SERVICE_LOGS:
            service = intent.entities.get("service")
            if service:
                plan.append(f"Show recent logs for service '{service}'")

        # User management intents
        elif intent.type == IntentType.CREATE_USER:
            username = intent.entities.get("username")
            if username:
                plan.append(f"Create new user '{username}'")
                plan.append("Create home directory")
                plan.append(f"Suggest setting password for '{username}'")

        elif intent.type == IntentType.LIST_USERS:
            plan.append("List all system users")
            plan.append("Show sudo status for each user")

        elif intent.type == IntentType.ADD_USER_TO_GROUP:
            username = intent.entities.get("username")
            group = intent.entities.get("group")
            if username and group:
                plan.append(f"Add user '{username}' to group '{group}'")

        elif intent.type == IntentType.CHANGE_PASSWORD:
            username = intent.entities.get("username")
            if username:
                plan.append(f"Provide instructions to change password for '{username}'")

        elif intent.type == IntentType.GRANT_SUDO:
            username = intent.entities.get("username")
            if username:
                plan.append(f"Add '{username}' to wheel group for sudo access")

        # Storage management intents
        elif intent.type == IntentType.DISK_USAGE:
            plan.append("Show disk usage summary")
            plan.append("Display Nix store size")

        elif intent.type == IntentType.ANALYZE_DISK:
            plan.append("Analyze disk usage by directory")
            plan.append("Check Nix store and generations")

        elif intent.type == IntentType.MOUNT_DEVICE:
            device = intent.entities.get("device")
            mount_point = intent.entities.get("mount_point")
            if device:
                plan.append(f"Mount device '{device}'")
                if mount_point:
                    plan.append(f"Use mount point '{mount_point}'")

        elif intent.type == IntentType.UNMOUNT_DEVICE:
            device = intent.entities.get("device")
            if device:
                plan.append(f"Unmount device '{device}'")

        elif intent.type == IntentType.FIND_LARGE_FILES:
            count = intent.entities.get("count", 10)
            plan.append(f"Find {count} largest files")
            plan.append("Check /tmp directory")

        return plan

    def _explain(self, intent: Intent, plan: list, result: Result | None) -> str:
        """Generate human-friendly explanation, using XAI if available"""

        # Try to use XAI engine for intelligent explanations
        if self.xai_engine:
            try:
                # Convert intent to format XAI expects
                intent_data = {
                    "type": (
                        intent.type.value
                        if hasattr(intent.type, "value")
                        else str(intent.type)
                    ),
                    "confidence": getattr(intent, "confidence", 0.8),
                    "entities": getattr(intent, "entities", {}),
                }

                # Get context for explanation
                context = {
                    "plan": plan,
                    "result_success": result.success if result else None,
                    "has_error": bool(result and not result.success),
                }

                # Generate XAI explanation
                xai_result = self.xai_engine.explain_intent(
                    intent=intent_data, context=context, depth=ExplanationDepth.STANDARD
                )

                if xai_result and xai_result.get("success"):
                    explanation = xai_result.get("explanation", "")
                    if explanation:
                        # Add confidence indicator if available
                        confidence = xai_result.get("confidence", 0)
                        if confidence > 0:
                            confidence_str = (
                                "High"
                                if confidence > 0.8
                                else "Medium" if confidence > 0.5 else "Low"
                            )
                            explanation = (
                                f"{explanation} (Confidence: {confidence_str})"
                            )
                        return explanation
            except Exception as e:
                logger.debug(f"XAI explanation failed, using fallback: {e}")

        # Fallback to simple explanations
        explanations = {
            IntentType.INSTALL_PACKAGE: "I'll help you install {package}",
            IntentType.UPDATE_SYSTEM: "I'll update your NixOS system",
            IntentType.SEARCH_PACKAGE: "I'll search for packages matching your query",
            IntentType.ROLLBACK: "I'll help you rollback to a previous system state",
            IntentType.CONFIGURE: "I'll help you configure {config}",
            IntentType.EXPLAIN: "Let me explain {topic}",
            IntentType.HELP: "Here are the available commands:",
            IntentType.REMOVE_PACKAGE: "I'll help you remove {package}",
            IntentType.GARBAGE_COLLECT: "I'll help you free up disk space",
            IntentType.LIST_GENERATIONS: "I'll show you the available system generations",
            IntentType.SWITCH_GENERATION: "I'll switch to generation {generation}",
            IntentType.REBUILD: "I'll rebuild your NixOS configuration",
            IntentType.EDIT_CONFIG: "I'll show you how to edit your configuration",
            IntentType.SHOW_CONFIG: "I'll display your current configuration",
            IntentType.CHECK_STATUS: "I'll check your system status",
            IntentType.LIST_INSTALLED: "I'll show you what packages are installed",
            # Network intents
            IntentType.SHOW_NETWORK: "I'll show you your network configuration",
            IntentType.SHOW_IP: "I'll display your IP addresses",
            IntentType.CONNECT_WIFI: "I'll help you connect to WiFi network {ssid}",
            IntentType.LIST_WIFI: "I'll scan for available WiFi networks",
            IntentType.TEST_CONNECTION: "I'll test your internet connectivity",
            # Service intents
            IntentType.START_SERVICE: "I'll start the {service} service",
            IntentType.STOP_SERVICE: "I'll stop the {service} service",
            IntentType.RESTART_SERVICE: "I'll restart the {service} service",
            IntentType.SERVICE_STATUS: "I'll check the status of {service}",
            IntentType.LIST_SERVICES: "I'll list all system services",
            IntentType.ENABLE_SERVICE: "I'll enable {service} to start at boot",
            IntentType.DISABLE_SERVICE: "I'll disable {service} from starting at boot",
            IntentType.SERVICE_LOGS: "I'll show recent logs for {service}",
            # User management intents
            IntentType.CREATE_USER: "I'll create a new user account for {username}",
            IntentType.LIST_USERS: "I'll show you all the users on this system",
            IntentType.ADD_USER_TO_GROUP: "I'll add {username} to the {group} group",
            IntentType.CHANGE_PASSWORD: "I'll help you change the password for {username}",
            IntentType.GRANT_SUDO: "I'll grant sudo privileges to {username}",
            # Storage management intents
            IntentType.DISK_USAGE: "I'll show you the disk usage information",
            IntentType.ANALYZE_DISK: "I'll analyze what's using disk space",
            IntentType.MOUNT_DEVICE: "I'll mount the device {device}",
            IntentType.UNMOUNT_DEVICE: "I'll safely unmount {device}",
            IntentType.FIND_LARGE_FILES: "I'll find the largest files on your system",
            IntentType.UNKNOWN: "I'm not sure what you're asking for",
        }

        base = explanations.get(intent.type, "I'll help with that")

        # Substitute entities
        for key, value in intent.entities.items():
            base = base.replace(f"{{{key}}}", str(value))

        # Add result information
        if result:
            if result.success:
                base += ". The operation completed successfully!"
            else:
                base += f". However, there was an error: {result.error}"

        return base

    def _get_suggestions(self, intent: Intent, result: Result | None) -> list:
        """Get relevant suggestions based on context, using XAI if available"""
        suggestions = []

        # Try to use XAI engine for intelligent suggestions
        if self.xai_engine:
            try:
                # Prepare context for XAI
                action_map = {
                    IntentType.INSTALL_PACKAGE: "install_package",
                    IntentType.UPDATE_SYSTEM: "update_system",
                    IntentType.SEARCH_PACKAGE: "search_package",
                    IntentType.REMOVE_PACKAGE: "remove_package",
                    IntentType.ROLLBACK: "rollback",
                }

                action = action_map.get(intent.type, "unknown")
                package = intent.entities.get("package", "")

                # Get XAI explanation for this action
                xai_explanation = self.xai_engine.explain_intent(
                    {"action": action, "package": package},
                    {"result_success": result.success if result else True},
                    depth=ExplanationDepth.STANDARD if XAI_AVAILABLE else None,
                )

                # Extract alternatives as suggestions
                if (
                    hasattr(xai_explanation, "alternatives")
                    and xai_explanation.alternatives
                ):
                    suggestions.extend(xai_explanation.alternatives[:2])

                # Add benefits as positive suggestions if successful
                if result and result.success and hasattr(xai_explanation, "benefits"):
                    for benefit in xai_explanation.benefits[:1]:
                        suggestions.append(f"✨ {benefit}")

                # Add causal insights
                if (
                    hasattr(xai_explanation, "causal_factors")
                    and xai_explanation.causal_factors
                ):
                    top_factor = max(
                        xai_explanation.causal_factors.items(), key=lambda x: x[1]
                    )
                    if top_factor[1] > 0.5:  # Only show high-confidence factors
                        suggestions.append(
                            f"💡 Main reason: {top_factor[0].replace('_', ' ').title()}"
                        )

            except Exception as e:
                logger.debug(f"XAI suggestions failed, using fallback: {e}")

        # Fallback or enhance with traditional suggestions
        if intent.type == IntentType.INSTALL_PACKAGE and result and result.success:
            package = intent.entities.get("package")
            if not any("run" in s.lower() for s in suggestions):
                suggestions.append(f"You can now run {package} from your terminal")
            if not any("permanent" in s.lower() for s in suggestions):
                suggestions.append(
                    f"To make this permanent, add {package} to your configuration.nix"
                )

        elif intent.type == IntentType.UPDATE_SYSTEM:
            if not any("dry" in s.lower() for s in suggestions):
                suggestions.append("Check what changed with: nixos-rebuild dry-build")
            if not any("generation" in s.lower() for s in suggestions):
                suggestions.append(
                    "View system generations with: sudo nix-env --list-generations -p /nix/var/nix/profiles/system"
                )

        elif intent.type == IntentType.UNKNOWN:
            suggestions.append(
                "Try asking about installing packages, updating your system, or configuring services"
            )
            suggestions.append("For example: 'install firefox' or 'update my system'")

        return suggestions

    def _extract_commands(self, plan: list) -> list:
        """Extract actual commands from the plan"""
        commands = []

        for action in plan:
            if "nix profile install" in action:
                commands.append(
                    {
                        "command": action.split("Use ")[-1],
                        "description": "Install package",
                    }
                )
            elif "nix-channel --update" in action:
                commands.append(
                    {
                        "command": "sudo nix-channel --update",
                        "description": "Update channels",
                    }
                )
            elif "nixos-rebuild switch" in action:
                commands.append(
                    {
                        "command": "sudo nixos-rebuild switch",
                        "description": "Rebuild system",
                    }
                )

        return commands

    async def _learn(self, request: Request, response: Response):
        """Learn from the interaction using XAI if available"""

        # Try to use XAI learning if available
        if self.xai_engine and hasattr(self.xai_engine, "learn_from_outcome"):
            try:
                # Prepare intent data
                intent_data = {
                    "action": (
                        response.intent.type.value
                        if hasattr(response.intent.type, "value")
                        else str(response.intent.type)
                    ),
                    "package": response.intent.entities.get("package", ""),
                    "confidence": getattr(response.intent, "confidence", 0.8),
                }

                # Prepare outcome data
                outcome_data = {
                    "success": response.success,
                    "had_error": bool(response.result and response.result.error),
                    "commands_executed": (
                        len(response.commands) if response.commands else 0
                    ),
                }

                # Let XAI learn from this interaction
                self.xai_engine.learn_from_outcome(
                    intent=intent_data,
                    outcome=outcome_data,
                    user_feedback=None,  # Could add user feedback here later
                )

                if os.getenv("DEBUG"):
                    print(
                        f"XAI learned from: {request.query} -> {response.intent.type} (success={response.success})"
                    )

            except Exception as e:
                logger.debug(f"XAI learning failed: {e}")

        # Fallback to simple logging
        elif os.getenv("DEBUG"):
            print(f"Learning from: {request.query} -> {response.data.get('intent')}")

    def _should_use_native_api(self, request: Request) -> bool:
        """Determine if we should use native NixOS integration"""
        # Check feature flag
        if not os.getenv("LUMINOUS_NIX_PYTHON_BACKEND"):
            return False

        # Check if this is a NixOS operation
        nixos_operations = ["update", "rollback", "install", "remove", "build", "test"]
        query_lower = (
            request.text.lower() if hasattr(request, "text") else request.query.lower()
        )

        return any(op in query_lower for op in nixos_operations)

    async def _process_native(self, request: Request) -> Response:
        """Process request using native NixOS integration"""
        if self.progress_callback:
            self.progress_callback("Initializing native NixOS integration...", 0.1)

        # Import integration
        integration = NixOSIntegration(self.progress_callback)

        # Recognize intent first
        if self.progress_callback:
            self.progress_callback("Analyzing request...", 0.2)

        intent = await self.intent_recognizer.recognize(
            request.text if hasattr(request, "text") else request.query, request.context
        )

        # Map intent to native operation
        intent_map = {
            IntentType.UPDATE_SYSTEM: "update_system",
            IntentType.ROLLBACK: "rollback_system",
            IntentType.INSTALL_PACKAGE: "install_package",
            IntentType.REMOVE_PACKAGE: "remove_package",
            IntentType.SEARCH_PACKAGE: "search_package",
        }

        native_intent = intent_map.get(intent.type)

        if not native_intent:
            # Fall back to traditional processing
            return await self.process_request(request)

        # Execute via native integration
        if self.progress_callback:
            self.progress_callback("Executing via native API...", 0.4)

        try:
            # Prepare parameters
            params = {"dry_run": request.context.get("dry_run", False)}

            # Add package info if present
            if intent.entities.get("package"):
                params["package"] = intent.entities["package"]

            # Execute
            result = await integration.execute_intent(native_intent, params)

            # Convert to Response
            if self.progress_callback:
                self.progress_callback("Generating response...", 0.8)

            response = Response(
                intent=intent,
                plan=[f"Execute {native_intent} via native Python API"],
                result=(
                    Result(
                        success=result["success"],
                        output=result.get("message", ""),
                        error=result.get("error"),
                    )
                    if result["success"] or result.get("error")
                    else None
                ),
                explanation=result.get("message", ""),
                suggestions=self._extract_suggestions(result),
                success=result["success"],
                commands=[],
            )

            # Add educational context if present
            if result.get("education"):
                response.data = {"education": result["education"]}

            if self.progress_callback:
                self.progress_callback("Complete!", 1.0)

            return response

        except Exception as e:
            context = ErrorContext(
                operation="native_processing",
                user_input=getattr(request, "text", getattr(request, "query", "")),
                metadata={"native_intent": native_intent},
            )

            nix_error = error_handler.handle_error(e, context)
            logger.error(f"Native processing failed: {nix_error.error_code} - {e}")

            # Fall back to traditional processing
            return await self.process_request(request)

    def _extract_suggestions(self, result: dict[str, Any]) -> list[str]:
        """Extract suggestions from native result"""
        suggestions = []

        if result.get("suggestion"):
            suggestions.append(result["suggestion"])

        if result.get("education", {}).get("next_steps"):
            suggestions.append(result["education"]["next_steps"])

        return suggestions

    def process(self, request: Request) -> Response:
        """
        Synchronous process method for CLI compatibility

        Args:
            request: The request to process

        Returns:
            Response object with results
        """
        # Run async method in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Use the simpler sync version for now
            return self._process_sync(request)
        finally:
            loop.close()

    def _process_sync(self, request: Request) -> Response:
        """Synchronous processing implementation"""
        try:
            # Extract intent from query
            intent = self.intent_recognizer.recognize(request.query)

            # Get knowledge-based response
            knowledge_response = self.knowledge.get_solution(
                intent.type.value, request.query
            )

            # Handle both Context objects and dicts
            if hasattr(request.context, "personality"):
                personality = request.context.personality
                execute = request.context.execute
                collect_feedback = True  # Default
            else:
                personality = request.context.get("personality", "friendly")
                execute = request.context.get("execute", False)
                collect_feedback = request.context.get("collect_feedback", True)

            # Build response text
            response_text = self._build_response_text(
                intent=intent, knowledge=knowledge_response, personality=personality
            )

            # Prepare commands
            commands = []
            if knowledge_response and "commands" in knowledge_response:
                for cmd in knowledge_response["commands"]:
                    commands.append(
                        {
                            "command": cmd.get("command", ""),
                            "description": cmd.get("description", ""),
                            "would_execute": not execute,
                        }
                    )

            return Response(
                success=True,
                text=response_text,
                commands=commands,
                data={
                    "intent": intent.type.value,
                    "package": (
                        intent.entities.get("package")
                        if hasattr(intent, "entities")
                        else None
                    ),
                    "collect_feedback": collect_feedback,
                },
            )

        except Exception as e:
            # Handle both Context objects and dicts for error context
            if hasattr(request.context, "personality"):
                personality = request.context.personality
            else:
                personality = request.context.get("personality", "friendly")

            context = ErrorContext(
                operation="process_sync",
                user_input=request.query,
                metadata={"personality": personality},
            )

            nix_error = error_handler.handle_error(e, context)

            return Response(
                success=False,
                text=nix_error.user_message,
                error=nix_error.message,
                data={
                    "error_code": nix_error.error_code,
                    "suggestions": nix_error.suggestions,
                },
            )

    def _generate_enhanced_response(
        self, intent: Intent, plan: list, result: Result | None
    ) -> Response:
        """Generate enhanced two-path educational response"""

        # Use the enhanced response generator
        context = {
            "intent": intent.type.value,
            "package": intent.entities.get("package"),
            "service": intent.entities.get("service"),
            "query": intent.raw_input,
            "has_home_manager": os.path.exists(
                os.path.expanduser("~/.config/home-manager/home.nix")
            ),
            "result": result,
        }

        # Generate the enhanced response
        enhanced = self.response_generator.generate(intent.type.value, context)

        # Convert to our Response format
        return Response(
            intent=intent,
            plan=plan,
            result=result,
            explanation=enhanced.format_for_cli(),
            suggestions=enhanced.related_topics,
            success=result.success if result else True,
            commands=self._extract_commands_from_paths(enhanced.paths),
            data={
                "education": (
                    enhanced.education.__dict__ if enhanced.education else None
                ),
                "paths": [path.__dict__ for path in enhanced.paths],
                "warnings": [warning.__dict__ for warning in enhanced.warnings],
            },
        )

    def _extract_commands_from_paths(self, paths) -> list:
        """Extract executable commands from solution paths"""
        commands = []
        for path in paths:
            if path.path_type.value in ["imperative", "temporary"]:
                for cmd in path.commands:
                    if not cmd.startswith("#") and cmd.strip():
                        commands.append(
                            {
                                "command": cmd,
                                "description": f"{path.title}: {cmd[:50]}...",
                                "requires_sudo": path.requires_sudo,
                            }
                        )
        return commands[:3]  # Limit to 3 most relevant commands

    def _build_response_text(
        self, intent: Intent, knowledge: dict[str, Any], personality: str
    ) -> str:
        """Build response text based on intent and personality"""
        if not knowledge:
            return "I'm not sure how to help with that. Try asking about installing packages, updating your system, or configuring services."

        # Build base response based on intent type
        if intent.type.value == "install_package" and knowledge.get("methods"):
            package = knowledge.get("package", "that package")
            base_response = (
                f"I'll help you install {package}! Here are your options:\n\n"
            )

            for i, method in enumerate(knowledge["methods"][:3], 1):
                base_response += (
                    f"{i}. **{method['name']}** - {method['description']}\n"
                )
                base_response += f"   ```\n   {method['example']}\n   ```\n\n"

            if knowledge.get("explanation"):
                base_response += f"\n💡 {knowledge['explanation']}"
        else:
            # Use pre-formatted response or build from solution
            base_response = knowledge.get("response", "")
            if not base_response and knowledge.get("solution"):
                base_response = knowledge["solution"]
                if knowledge.get("example"):
                    base_response += f"\n\nExample:\n```\n{knowledge['example']}\n```"
                if knowledge.get("explanation"):
                    base_response += f"\n\n💡 {knowledge['explanation']}"

        # Apply personality
        if personality == "minimal":
            return base_response
        if personality == "friendly":
            return f"Hi there! {base_response}\n\nLet me know if you need any clarification! 😊"
        if personality == "encouraging":
            return f"Great question! {base_response}\n\nYou're doing awesome learning NixOS! Keep it up! 🌟"
        if personality == "technical":
            return f"{base_response}\n\nNote: This follows NixOS's declarative configuration paradigm."
        if personality == "symbiotic":
            return f"{base_response}\n\n🤝 I'm still learning! Was this helpful? Your feedback helps me improve."
        return base_response


# Convenience function for creating the backend
def create_backend(
    progress_callback: Callable | None = None,
) -> NixForHumanityBackend:
    """Create a configured backend instance"""
    return NixForHumanityBackend(progress_callback)


# Alias for backward compatibility
get_backend = create_backend
