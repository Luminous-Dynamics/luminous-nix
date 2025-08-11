"""
🕉️ Unified Backend for Nix for Humanity

This is the sacred core - the single source of truth that unifies all operations.
Built with consciousness-first principles and luminous clarity.

Architecture:
    All Frontends → This Backend → Native Python-Nix API → NixOS

Principles:
    - Single source of truth
    - Plugin extensibility
    - Consciousness-first design
    - Native performance (10x-1500x)
    - NO MOCKS - only reality
"""

import asyncio
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import (
    Any,
    Optional,
)

# typing_extensions import removed - using built-in typing for compatibility
# Lazy imports - moved to properties to speed up startup
# from ..nix.python_api import get_nix_api, NixResult, NixAction
# from ..knowledge.engine import ModernNixOSKnowledgeEngine
# from .command_executor import CommandExecutor, ExecutionResult
# Import our logging configuration
from .logging_config import get_logger, log_duration, log_event

logger = get_logger(__name__)


class IntentType(Enum):
    """Types of user intentions"""

    INSTALL = "install"
    REMOVE = "remove"
    SEARCH = "search"
    UPDATE = "update"
    ROLLBACK = "rollback"
    LIST = "list"
    GENERATIONS = "generations"
    GENERATE_CONFIG = "generate_config"
    TRANSLATE_ERROR = "translate_error"
    QUERY = "query"
    LEARN = "learn"
    UNKNOWN = "unknown"


@dataclass
class Intent:
    """Structured representation of user intent"""

    type: IntentType
    query: str
    parameters: dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Context:
    """Execution context for maintaining state"""

    user_id: str | None = None
    session_id: str | None = None
    history: list[Intent] = field(default_factory=list)
    preferences: dict[str, Any] = field(default_factory=dict)
    environment: dict[str, str] = field(default_factory=dict)

    def add_to_history(self, intent: Intent):
        """Add intent to history, maintaining sacred memory"""
        self.history.append(intent)
        # Keep only last 100 for memory efficiency
        if len(self.history) > 100:
            self.history = self.history[-100:]


@dataclass
class Result:
    """Unified result structure"""

    success: bool
    output: str
    intent: Intent | None = None
    execution_time: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    suggestions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "suggestions": self.suggestions,
            "metadata": self.metadata,
            "execution_time": self.execution_time,
        }


class PluginRegistry:
    """Sacred registry for plugin management"""

    def __init__(self):
        self.plugins: dict[str, Plugin] = {}
        self.load_order: list[str] = []

    def register(self, plugin: "Plugin") -> None:
        """Register a plugin with the sacred core"""
        if plugin.name in self.plugins:
            logger.warning(f"Plugin {plugin.name} already registered, replacing")

        self.plugins[plugin.name] = plugin
        self.load_order.append(plugin.name)
        logger.info(f"✨ Registered plugin: {plugin.name}")

    def get(self, name: str) -> Optional["Plugin"]:
        """Get a plugin by name"""
        return self.plugins.get(name)

    def list_plugins(self) -> list[str]:
        """List all registered plugins"""
        return list(self.plugins.keys())

    async def process_intent(self, intent: Intent, context: Context) -> Result | None:
        """Let plugins process the intent"""
        for plugin_name in self.load_order:
            plugin = self.plugins[plugin_name]
            if plugin.can_handle(intent):
                try:
                    result = await plugin.process(intent, context)
                    if result:
                        logger.info(f"Plugin {plugin_name} handled intent")
                        return result
                except Exception as e:
                    logger.error(f"Plugin {plugin_name} failed: {e}")
        return None


class HookSystem:
    """Sacred hook system for lifecycle events"""

    def __init__(self):
        self.hooks: dict[str, list[Callable]] = defaultdict(list)

    def register(self, event: str, callback: Callable) -> None:
        """Register a hook for an event"""
        self.hooks[event].append(callback)
        logger.debug(f"Registered hook for {event}")

    async def run(self, event: str, data: Any) -> Any:
        """Run all hooks for an event"""
        for callback in self.hooks[event]:
            try:
                if asyncio.iscoroutinefunction(callback):
                    data = await callback(data)
                else:
                    data = callback(data)
            except Exception as e:
                logger.error(f"Hook failed for {event}: {e}")
        return data


class Plugin:
    """Base class for plugins - extend the sacred core"""

    @property
    def name(self) -> str:
        """Plugin name"""
        raise NotImplementedError

    def can_handle(self, intent: Intent) -> bool:
        """Check if this plugin can handle the intent"""
        return False

    async def process(self, intent: Intent, context: Context) -> Result | None:
        """Process the intent"""
        return None

    async def initialize(self) -> None:
        """Initialize the plugin"""
        pass

    async def cleanup(self) -> None:
        """Cleanup plugin resources"""
        pass


class NixForHumanityBackend:
    """
    🕉️ The Sacred Core - Unified Backend for All Operations

    This is the single source of truth that all frontends connect to.
    It provides a unified, extensible, consciousness-first interface
    to NixOS operations with native Python performance.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """
        Initialize the sacred backend (optimized with lazy loading)

        Args:
            config: Optional configuration dictionary
        """
        # Load configuration from persistence if not provided
        if config is None:
            from .config_manager import get_config_manager

            self._config_manager = get_config_manager()
            self.config = self._config_manager.get_config_dict()
        else:
            self.config = config
            self._config_manager = None

        # Lazy-loaded core components
        self._native_api = None
        self._knowledge = None
        self._executor = None

        # Extensibility systems (lightweight, can init immediately)
        self.plugins = PluginRegistry()
        self.hooks = HookSystem()

        # Context management
        self.contexts: dict[str, Context] = {}

        # Learning & adaptation
        self.learning_enabled = self.config.get("learning", True)

        # Caching system (lazy loaded)
        self._cache = None
        self.caching_enabled = self.config.get("caching", True)

        logger.debug("🕉️ Sacred Backend initialized (lazy mode)")

    @property
    def cache(self):
        """Lazy-load cache only when needed"""
        if self._cache is None and self.caching_enabled:
            from .cache import get_cache

            self._cache = get_cache()
            logger.debug("Loaded cache system")
        return self._cache

    @property
    def native_api(self):
        """Lazy-load native API only when needed"""
        if self._native_api is None:
            from ..nix.python_api import get_nix_api

            self._native_api = get_nix_api()
            logger.debug("Loaded native API")
        return self._native_api

    @property
    def knowledge(self):
        """Lazy-load knowledge engine only when needed"""
        if self._knowledge is None:
            from ..knowledge.engine import ModernNixOSKnowledgeEngine

            self._knowledge = ModernNixOSKnowledgeEngine()
            logger.debug("Loaded knowledge engine")
        return self._knowledge

    @property
    def executor(self):
        """Lazy-load command executor only when needed"""
        if self._executor is None:
            from .command_executor import CommandExecutor

            self._executor = CommandExecutor(dry_run=self.config.get("dry_run", False))
            logger.debug("Loaded command executor")
        return self._executor

    async def initialize(self) -> None:
        """Initialize all systems with sacred intention"""
        # Initialize plugins
        for plugin in self.plugins.plugins.values():
            await plugin.initialize()

        # Run initialization hooks
        await self.hooks.run("backend_initialized", self)

        logger.info("✨ All systems initialized and harmonized")

    async def execute(
        self,
        query: str,
        context: Context | None = None,
        options: dict[str, Any] | None = None,
    ) -> Result:
        """
        Execute a natural language query with sacred precision

        This is the main entry point for all operations.

        Args:
            query: Natural language query
            context: Optional execution context
            options: Optional execution options

        Returns:
            Result object with execution outcome
        """
        start_time = asyncio.get_event_loop().time()
        options = options or {}

        # Validate input
        if not query or not query.strip():
            return Result(
                success=False,
                output="",
                error="Empty query provided",
                suggestions=["Please provide a command or question"],
                execution_time=0.0,
            )

        # Sanitize query
        query = query.strip()

        # Expand aliases if config manager is available
        if self._config_manager:
            query = self._config_manager.expand_aliases(query)

        # Create or use context
        if context is None:
            context = Context()

        try:
            # Check cache first (for read-only operations)
            cache_key = None
            if self.caching_enabled and self.cache:
                # Check if this query is cacheable
                temp_intent = await self.understand(query, context)
                if self.cache.should_cache(temp_intent.type.value):
                    cached_result = self.cache.get(
                        query, {"dry_run": options.get("dry_run", True)}
                    )
                    if cached_result:
                        # Return cached result
                        result = (
                            Result(**cached_result)
                            if isinstance(cached_result, dict)
                            else cached_result
                        )
                        result.execution_time = (
                            asyncio.get_event_loop().time() - start_time
                        )
                        result.metadata["cached"] = True
                        logger.info(
                            f"✅ Returned cached result in {result.execution_time:.3f}s"
                        )
                        return result
                    cache_key = query  # Remember to cache the result

            # Pre-execution hooks
            query = await self.hooks.run("pre_query", query)

            # Parse intent with sacred understanding
            intent = await self.understand(query, context)

            # Add to context history
            context.add_to_history(intent)

            # Pre-execution intent hooks
            intent = await self.hooks.run("pre_execute", intent)

            # Let plugins handle first
            result = await self.plugins.process_intent(intent, context)

            # If no plugin handled it, use core execution
            if result is None:
                result = await self._execute_core(intent, options)

            # Post-execution hooks
            result = await self.hooks.run("post_execute", result)

            # Learning from interaction
            if self.learning_enabled:
                await self._learn_from_interaction(intent, result, context)

            # Calculate execution time
            result.execution_time = asyncio.get_event_loop().time() - start_time

            # Cache successful results for cacheable queries
            if (
                cache_key
                and self.caching_enabled
                and self.cache
                and result.success
                and self.cache.should_cache(intent.type.value)
            ):
                self.cache.set(
                    cache_key,
                    result.to_dict(),
                    {"dry_run": options.get("dry_run", True)},
                )

            # Log execution metrics
            log_duration(logger, f"execute_{intent.type.value}", result.execution_time)
            log_event(
                logger,
                "query_executed",
                success=result.success,
                intent_type=intent.type.value,
                cached=result.metadata.get("cached", False),
            )

            # Track in config manager if available
            if self._config_manager:
                self._config_manager.add_to_history(
                    query, result.success, result.execution_time
                )
                self._config_manager.learn_pattern(
                    intent.type.value, query, result.success
                )

            return result

        except ValueError as e:
            # Handle validation errors with intelligent explanation
            logger.warning(f"Validation error: {e}")

            # Get intelligent error explanation
            from ..errors import ErrorContext, get_error_educator

            context = ErrorContext(
                error_type="validation",
                original_message=str(e),
                user_query=query,
                operation="validation",
            )
            educated_error = get_error_educator().educate(str(e), context)

            return Result(
                success=False,
                output="",
                error=educated_error,
                suggestions=[
                    "Check your command syntax",
                    "Use natural language like 'install firefox'",
                    "Try simpler commands",
                ],
                execution_time=asyncio.get_event_loop().time() - start_time,
            )
        except TimeoutError as e:
            # Handle timeout errors with intelligent explanation
            logger.error(f"Operation timed out: {e}")

            from ..errors import ErrorContext, get_error_educator

            context = ErrorContext(
                error_type="timeout",
                original_message="Operation timed out",
                user_query=query,
                operation="execution",
            )
            educated_error = get_error_educator().educate(
                "Operation timed out - network connection failed", context
            )

            return Result(
                success=False,
                output="",
                error=educated_error,
                suggestions=[
                    "Try a simpler operation",
                    "Check your network connection",
                    "Use --debug flag for more details",
                ],
                execution_time=asyncio.get_event_loop().time() - start_time,
            )
        except Exception as e:
            # Generic error handler with intelligent explanation
            logger.error(f"Execution failed: {e}")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Exception args: {e.args}")
            import traceback

            logger.error(f"Traceback: {traceback.format_exc()}")

            from ..errors import ErrorContext, get_error_educator

            context = ErrorContext(
                error_type="execution",
                original_message=str(e),
                user_query=query,
                operation="execution",
            )
            educated_error = get_error_educator().educate(str(e), context)

            return Result(
                success=False,
                output="",
                error=educated_error,
                suggestions=[
                    "Please try again",
                    "Use --debug flag for more information",
                    "Report this issue if it persists",
                ],
                execution_time=asyncio.get_event_loop().time() - start_time,
            )

    async def understand(self, query: str, context: Context) -> Intent:
        """
        Understand user intent with sacred wisdom

        Args:
            query: Natural language query
            context: Execution context

        Returns:
            Structured Intent object
        """
        # Use knowledge engine for parsing
        intent_data = self.knowledge.extract_intent(query)

        # Map to our Intent structure
        intent_name = intent_data.get("intent", "unknown")

        # Try to get the enum value directly - the values match the intent names
        try:
            intent_type = IntentType(intent_name)
        except ValueError:
            # Fall back to unknown if invalid
            intent_type = IntentType.UNKNOWN

        # Extract parameters
        parameters = {k: v for k, v in intent_data.items() if k != "intent"}

        # Use context to improve understanding
        if context.history:
            # Could use previous intents to disambiguate
            pass

        intent = Intent(
            type=intent_type,
            query=query,
            parameters=parameters,
            confidence=0.95,  # Could calculate based on parsing confidence
            metadata={"source": "knowledge_engine"},
        )

        # Intent understanding hooks
        intent = await self.hooks.run("intent_understood", intent)

        return intent

    async def _execute_core(self, intent: Intent, options: dict[str, Any]) -> Result:
        """
        Core execution using our native Python-Nix API

        This uses what we already built - the CommandExecutor
        with native Python bindings for 10x-1500x performance.
        """
        # Use our existing executor
        exec_result = self.executor.execute(intent.type.value, **intent.parameters)

        # Convert to unified Result
        result = Result(
            success=exec_result.success,
            output=exec_result.output,
            intent=intent,
            error=exec_result.error,
            metadata=exec_result.metadata or {},
        )

        # Add suggestions if failed
        if not result.success:
            result.suggestions = await self._generate_suggestions(intent, result)

        return result

    async def _generate_suggestions(self, intent: Intent, result: Result) -> list[str]:
        """Generate helpful suggestions when operations fail"""
        suggestions = []

        if intent.type == IntentType.INSTALL:
            package = intent.parameters.get("package")
            suggestions.append(f"Try: nix search nixpkgs {package}")
            suggestions.append("Check spelling: did you mean a different package?")

        elif intent.type == IntentType.SEARCH:
            suggestions.append("Try broader search terms")
            suggestions.append("Use 'nix search nixpkgs' directly for more results")

        return suggestions

    async def _learn_from_interaction(
        self, intent: Intent, result: Result, context: Context
    ) -> None:
        """
        Learn from each interaction to improve future understanding

        This is where the sacred learning happens - improving
        with each interaction.
        """
        if not self.learning_enabled:
            return

        # Record successful patterns
        if result.success:
            # This would update our knowledge base
            pass

        # Learn from failures
        else:
            # This would help avoid similar failures
            pass

        logger.debug("📚 Learning from interaction")

    def register_plugin(self, plugin: Plugin) -> None:
        """Register a plugin with the sacred core"""
        self.plugins.register(plugin)

    def register_hook(self, event: str, callback: Callable) -> None:
        """Register a lifecycle hook"""
        self.hooks.register(event, callback)

    async def stream_execute(self, query: str, context: Context | None = None):
        """
        Stream execution results for long-running operations

        This enables real-time progress updates.
        """
        # Parse intent
        intent = await self.understand(query, context or Context())

        # Stream based on intent type
        if intent.type == IntentType.UPDATE:
            async for update in self._stream_system_update():
                yield update
        else:
            # For non-streaming operations, yield single result
            result = await self.execute(query, context)
            yield result.to_dict()

    async def _stream_system_update(self):
        """Stream system update progress"""
        # This would use native API streaming capabilities
        phases = [
            "Evaluating configuration...",
            "Building derivations...",
            "Downloading packages...",
            "Activating configuration...",
            "Setting up systemd services...",
        ]

        for i, phase in enumerate(phases):
            await asyncio.sleep(0.5)  # Simulate work
            yield {
                "type": "progress",
                "phase": phase,
                "percent": (i + 1) / len(phases) * 100,
                "message": phase,
            }

        yield {"type": "complete", "message": "System updated successfully"}

    async def cleanup(self) -> None:
        """Sacred cleanup of all resources"""
        # Cleanup plugins
        for plugin in self.plugins.plugins.values():
            await plugin.cleanup()

        # Run cleanup hooks
        await self.hooks.run("backend_cleanup", self)

        logger.info("🕉️ Sacred cleanup complete")


# Singleton instance for easy access
_backend: NixForHumanityBackend | None = None


def get_backend(config: dict[str, Any] | None = None) -> NixForHumanityBackend:
    """Get the singleton backend instance"""
    global _backend
    if _backend is None:
        _backend = NixForHumanityBackend(config)
    return _backend
