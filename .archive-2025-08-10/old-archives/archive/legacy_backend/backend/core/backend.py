"""
from typing import List, Dict, Optional
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

# Setup logging

logger = logging.getLogger(__name__)


from ..api.schema import Request, Response, Result
from .error_handler import ErrorContext, error_handler
from .intents import Intent, IntentRecognizer, IntentType
from .knowledge import KnowledgeBase
from .response_adapter import create_simple_response

# Setup logging first
logger = logging.getLogger(__name__)

# Import the enhanced response system
try:
    from .responses import ResponseGenerator

    ENHANCED_RESPONSES_AVAILABLE = True
except ImportError:
    ENHANCED_RESPONSES_AVAILABLE = False
    logger.warning("Enhanced response system not available")

# Import research-based components
try:
    from ..consciousness_metrics.sacred_metrics import SacredMetricsCollector
    from ..knowledge_graph.skg import SymbioticKnowledgeGraph
    from ..perception.activity_monitor import ActivityMonitor
    from ..sacred_development.consciousness_first import ConsciousnessGuard
    from ..trust_modeling.trust_engine import TrustEngine

    SKG_AVAILABLE = True
except ImportError as e:
    SKG_AVAILABLE = False
    # Try to import mocks as fallback
    try:
        from ..mocks import (
            MockActivityMonitor as ActivityMonitor,
        )
        from ..mocks import (
            MockConsciousnessGuard as ConsciousnessGuard,
        )
        from ..mocks import (
            MockSacredMetricsCollector as SacredMetricsCollector,
        )
        from ..mocks import (
            MockSymbioticKnowledgeGraph as SymbioticKnowledgeGraph,
        )
        from ..mocks import (
            MockTrustEngine as TrustEngine,
        )

        SKG_AVAILABLE = True
        logger.info("Using mock research components for testing")
    except ImportError:
        logger.warning(f"Research-based components not available: {e}")

# Try to import native NixOS integration
try:
    from .nix_integration import NATIVE_API_AVAILABLE, NixOSIntegration

    NATIVE_INTEGRATION_AVAILABLE = True
except ImportError:
    NATIVE_INTEGRATION_AVAILABLE = False
    NATIVE_API_AVAILABLE = False


class NixForHumanityBackend:
    """Unified backend for all Nix for Humanity operations"""

    def __init__(self, progress_callback: Callable | None = None):
        """
        Initialize the backend

        Args:
            progress_callback: Optional callback for progress updates
        """
        from .executor import SafeExecutor  # Import here to avoid circular import

        self.intent_recognizer = IntentRecognizer()
        self.executor = SafeExecutor(progress_callback)
        self.knowledge = KnowledgeBase()
        self.progress_callback = progress_callback
        self._init_nixos_api()

        # Initialize enhanced response system if available
        if ENHANCED_RESPONSES_AVAILABLE:
            self.response_generator = ResponseGenerator()
            self.use_enhanced_responses = (
                os.getenv("LUMINOUS_NIX_ENHANCED_RESPONSES", "true").lower() == "true"
            )
        else:
            self.response_generator = None
            self.use_enhanced_responses = False

        # Initialize research-based components if available
        if SKG_AVAILABLE:
            self._init_research_components()
        else:
            self.skg = None
            self.trust_engine = None
            self.metrics_collector = None
            self.activity_monitor = None
            self.consciousness_guard = None

    def _init_nixos_api(self):
        """Initialize direct nixos-rebuild-ng API"""
        self.nix_integration = None
        logger.info("🚀 Initializing native backend with 10x-1500x performance")

        try:
            # Find nixos-rebuild-ng path dynamically
            nixos_rebuild_path = self._find_nixos_rebuild_path()
            if nixos_rebuild_path and str(nixos_rebuild_path) not in sys.path:
                sys.path.insert(0, str(nixos_rebuild_path))

            # Try to import the modules
            from nixos_rebuild import models, nix

            self.nix_api = nix
            self.nix_models = models
            self._has_python_api = True

            if self.progress_callback:
                self.progress_callback("Python NixOS API initialized", 0.1)

        except ImportError as e:
            # Fallback to subprocess mode
            self._has_python_api = False
            if os.getenv("DEBUG"):
                print(f"Python API not available: {e}")

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

    def _init_research_components(self):
        """Initialize research-based symbiotic intelligence components"""
        try:
            # Initialize Symbiotic Knowledge Graph
            skg_path = os.getenv("LUMINOUS_NIX_SKG_PATH", "./nix_humanity_skg.db")
            self.skg = SymbioticKnowledgeGraph(skg_path)
            logger.info("✅ Symbiotic Knowledge Graph initialized")

            # Initialize Trust Engine with SKG
            self.trust_engine = TrustEngine(self.skg)
            logger.info("✅ Trust Engine initialized with Theory of Mind")

            # Initialize Sacred Metrics Collector
            self.metrics_collector = SacredMetricsCollector(self.skg)
            logger.info("✅ Consciousness-First Metrics initialized")

            # Initialize Activity Monitor (privacy-first)
            if os.getenv("LUMINOUS_NIX_ACTIVITY_TRACKING", "false").lower() == "true":
                self.activity_monitor = ActivityMonitor(self.skg)
                logger.info("✅ Activity Monitor initialized (privacy mode)")
            else:
                self.activity_monitor = None
                logger.info("ℹ️ Activity Monitor disabled by default")

            # Initialize Consciousness Guard
            self.consciousness_guard = ConsciousnessGuard()
            logger.info("✅ Consciousness Guard active")

        except Exception as e:
            logger.error(f"Failed to initialize research components: {e}")
            self.skg = None
            self.trust_engine = None
            self.metrics_collector = None
            self.activity_monitor = None
            self.consciousness_guard = None

    async def process_request(self, request: Request) -> Response:
        """
        Main entry point for all requests

        Args:
            request: The incoming request

        Returns:
            Response with results
        """
        try:
            # CONSCIOUSNESS GUARD: Set intention for this request
            if self.consciousness_guard:
                with self.consciousness_guard.sacred_context(
                    intention="Process user request with awareness and care"
                ):
                    return await self._process_with_awareness(request)
            else:
                return await self._process_traditional(request)

        except Exception as e:
            # Use comprehensive error handler
            context = ErrorContext(
                operation="process_request",
                user_input=getattr(request, "text", getattr(request, "query", "")),
                metadata={"request_context": request.context},
            )

            nix_error = error_handler.handle_error(e, context)

            # Handle errors gracefully with rich information
            return create_simple_response(
                intent=Intent(
                    type=IntentType.UNKNOWN,
                    entities={},
                    confidence=0.0,
                    raw_text=context.user_input,
                ),
                success=False,
                text=nix_error.user_message,
                error=nix_error.user_message,
                suggestions=nix_error.suggestions,
                data={"error_code": nix_error.error_code},
            )

    async def _process_with_awareness(self, request: Request) -> Response:
        """Process request with full research-based awareness"""
        # Track in SKG if available
        interaction_id = None
        if self.skg:
            interaction_id = self.skg.episodic.record_interaction(
                user_input=getattr(request, "text", getattr(request, "query", "")),
                timestamp=asyncio.get_event_loop().time(),
            )

        try:
            # SECURITY: Validate and sanitize all user input first
            from ..security.input_validator import InputValidator

            # Get the text from request safely
            request_text = getattr(request, "text", None) or getattr(
                request, "query", ""
            )

            # Validate input
            validation_result = InputValidator.validate_input(request_text, "nlp")
            if not validation_result["valid"]:
                return create_simple_response(
                    intent=Intent(
                        type=IntentType.UNKNOWN,
                        entities={},
                        confidence=0.0,
                        raw_text=request_text,
                    ),
                    success=False,
                    text=f"I couldn't process that request safely: {validation_result['reason']}",
                    error=f"Input validation failed: {validation_result['reason']}",
                    suggestions=validation_result.get(
                        "suggestions", ["Please rephrase your request"]
                    ),
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
                response = create_simple_response(
                    intent=intent,
                    success=result.success if result else True,
                    text=self._explain(intent, plan, result),
                    commands=self._extract_commands(plan),
                    data={
                        "plan": plan,
                        "result": result.__dict__ if result else None,
                        "suggestions": self._get_suggestions(intent, result),
                    },
                )

            # 5. Learn from interaction (async, don't wait)
            asyncio.create_task(self._learn(request, response))

            # 6. Track with research components
            if interaction_id and self.skg:
                # Record AI response in SKG
                self.skg.episodic.record_ai_response(
                    interaction_id, response.text, response.success
                )

                # Update trust model
                if self.trust_engine:
                    trust_update = self.trust_engine.process_interaction(
                        interaction_id, request_text, response.text
                    )
                    if trust_update.get("vulnerability_action"):
                        # Add vulnerability disclosure to response
                        response.data["trust_building"] = trust_update[
                            "vulnerability_action"
                        ]

                # Collect consciousness metrics
                if self.metrics_collector:
                    metrics = self.metrics_collector.collect_current_metrics(
                        {
                            "session_start": request.context.get("session_start"),
                            "interruptions": request.context.get(
                                "interruption_count", 0
                            ),
                            "breaks_taken": request.context.get("breaks_taken", 0),
                            "focus_duration": request.context.get("focus_duration", 0),
                        }
                    )
                    response.data["consciousness_metrics"] = {
                        "wellbeing_score": metrics.wellbeing_score,
                        "attention_state": metrics.attention_state.value,
                        "flow_state": metrics.flow_state,
                    }

            if self.progress_callback:
                self.progress_callback("Complete!", 1.0)

            return response

        except Exception as e:
            # Record error in SKG if available
            if interaction_id and self.skg:
                self.skg.episodic.record_ai_response(
                    interaction_id, f"Error: {str(e)}", False
                )
            raise  # Re-raise to be caught by outer handler

    async def _process_traditional(self, request: Request) -> Response:
        """Traditional processing without research components"""
        try:
            # SECURITY: Validate and sanitize all user input first
            from ..security.input_validator import InputValidator

            # Get the text from request safely
            request_text = getattr(request, "text", None) or getattr(
                request, "query", ""
            )

            # Validate input
            validation_result = InputValidator.validate_input(request_text, "nlp")
            if not validation_result["valid"]:
                return create_simple_response(
                    intent=Intent(
                        type=IntentType.UNKNOWN,
                        entities={},
                        confidence=0.0,
                        raw_text=request_text,
                    ),
                    success=False,
                    text=f"I couldn't process that request safely: {validation_result['reason']}",
                    error=f"Input validation failed: {validation_result['reason']}",
                    suggestions=validation_result.get(
                        "suggestions", ["Please rephrase your request"]
                    ),
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
                response = create_simple_response(
                    intent=intent,
                    success=result.success if result else True,
                    text=self._explain(intent, plan, result),
                    commands=self._extract_commands(plan),
                    data={
                        "plan": plan,
                        "result": result.__dict__ if result else None,
                        "suggestions": self._get_suggestions(intent, result),
                    },
                )

            # 5. Learn from interaction (async, don't wait)
            asyncio.create_task(self._learn(request, response))

            if self.progress_callback:
                self.progress_callback("Complete!", 1.0)

            return response

        except Exception:
            raise  # Re-raise to be caught by outer handler

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
        """Generate human-friendly explanation"""
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
        """Get relevant suggestions based on context"""
        suggestions = []

        if intent.type == IntentType.INSTALL_PACKAGE and result and result.success:
            package = intent.entities.get("package")
            suggestions.append(f"You can now run {package} from your terminal")
            suggestions.append(
                f"To make this permanent, add {package} to your configuration.nix"
            )

        elif intent.type == IntentType.UPDATE_SYSTEM:
            suggestions.append("Check what changed with: nixos-rebuild dry-build")
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
        """Learn from the interaction using SKG and research components"""
        try:
            # Get request text safely
            request_text = getattr(request, "text", getattr(request, "query", ""))

            if self.skg:
                # Update ontological layer with new knowledge
                if response.intent and response.intent.type != IntentType.UNKNOWN:
                    self.skg.ontological.add_concept(
                        name=response.intent.type.value,
                        type="intent",
                        properties={
                            "entities": response.intent.entities,
                            "confidence": response.intent.confidence,
                        },
                    )

                    # Link intent to successful commands
                    if response.success and response.commands:
                        for cmd in response.commands:
                            self.skg.ontological.link_concepts(
                                response.intent.type.value,
                                cmd.get("command", ""),
                                "executes",
                            )

                # Update phenomenological layer with user experience
                if hasattr(request.context, "user_feedback"):
                    self.skg.phenomenological.record_experience(
                        {
                            "type": "user_feedback",
                            "content": request.context.user_feedback,
                            "success": response.success,
                            "intent": (
                                response.intent.type.value if response.intent else None
                            ),
                        }
                    )

                # Update metacognitive layer with reflection
                if response.success:
                    self.skg.metacognitive.record_meta_learning(
                        {
                            "pattern": "successful_interaction",
                            "context": {
                                "intent": (
                                    response.intent.type.value
                                    if response.intent
                                    else None
                                ),
                                "approach": (
                                    "traditional"
                                    if not self.consciousness_guard
                                    else "awareness-based"
                                ),
                            },
                            "insight": "Pattern reinforced",
                        }
                    )

            # Log if in debug mode
            if os.getenv("DEBUG"):
                print(
                    f"Learning from: {request_text} -> {response.intent.type.value if response.intent else 'unknown'}"
                )

        except Exception as e:
            logger.error(f"Learning error: {e}")
            # Don't fail the main flow for learning errors

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
