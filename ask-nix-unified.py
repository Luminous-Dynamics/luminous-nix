#!/usr/bin/env python3
"""
🕉️ Unified CLI for Nix for Humanity

This demonstrates the sacred unified backend architecture with
consciousness-first principles and luminous clarity.

It shows:
1. Using the unified backend
2. Plugin system in action
3. Hook system for extensibility
4. Native Python-Nix performance
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from nix_for_humanity.core.unified_backend import (
    Context,
    Intent,
    IntentType,
    NixForHumanityBackend,
    Plugin,
    Result,
)
from nix_for_humanity.plugins.config_generator import (
    ConfigGeneratorPlugin,
    SmartSearchPlugin,
)

# Configure logging with sacred symbols
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ConsciousnessPlugin(Plugin):
    """
    🌟 Example plugin showing consciousness-first design

    This plugin adds sacred pauses and mindful transitions
    to NixOS operations.
    """

    @property
    def name(self) -> str:
        return "consciousness"

    def can_handle(self, intent: Intent) -> bool:
        """This plugin enhances all operations"""
        return True  # Applies consciousness to everything

    async def process(self, intent: Intent, context: Context) -> Result | None:
        """Add consciousness to the operation"""
        # Don't actually execute - just enhance with awareness

        # For install operations, add sacred pause
        if intent.type == IntentType.INSTALL:
            package = intent.parameters.get("package", "unknown")
            print(f"\n🧘 Taking a sacred pause before installing {package}...")
            await asyncio.sleep(1)  # Sacred pause
            print("✨ Setting intention: This package will serve consciousness")

        # For search, add mindful guidance
        elif intent.type == IntentType.SEARCH:
            print("\n🔍 Searching with awareness and curiosity...")

        # We don't handle the actual execution, just enhance it
        return None


class MetricsPlugin(Plugin):
    """
    📊 Example plugin for tracking usage patterns

    This shows how plugins can observe without interfering.
    """

    @property
    def name(self) -> str:
        return "metrics"

    def can_handle(self, intent: Intent) -> bool:
        """Observe all operations"""
        return False  # Never handles, only observes via hooks

    async def process(self, intent: Intent, context: Context) -> Result | None:
        """We don't process, we observe via hooks"""
        return None

    def record_intent(self, intent: Intent) -> Intent:
        """Hook to record intents"""
        logger.info(f"📊 Metrics: Recording {intent.type.value} operation")
        # Would write to database in real implementation
        return intent

    def record_result(self, result: Result) -> Result:
        """Hook to record results"""
        if result.success:
            logger.info(
                f"📊 Metrics: Operation succeeded in {result.execution_time:.3f}s"
            )
        else:
            logger.info(f"📊 Metrics: Operation failed: {result.error}")
        return result


class SacredCLI:
    """
    The unified CLI demonstrating the sacred architecture
    """

    def __init__(self):
        """Initialize with sacred intention"""
        self.backend = NixForHumanityBackend(
            config={"dry_run": True}  # Safe by default
        )
        self.setup_plugins()
        self.setup_hooks()

    def setup_plugins(self):
        """Register plugins with the sacred core"""
        # Consciousness plugin for mindful operations
        consciousness = ConsciousnessPlugin()
        self.backend.register_plugin(consciousness)

        # Metrics plugin for learning
        self.metrics = MetricsPlugin()
        self.backend.register_plugin(self.metrics)

        # Config generation plugin - KILLER FEATURE!
        config_gen = ConfigGeneratorPlugin()
        self.backend.register_plugin(config_gen)

        # Smart search plugin - Find by description
        smart_search = SmartSearchPlugin()
        self.backend.register_plugin(smart_search)

        logger.info("🔌 Plugins registered with sacred core")

    def setup_hooks(self):
        """Setup lifecycle hooks"""
        # Pre-execution hook
        self.backend.register_hook("pre_execute", self.before_execute)

        # Post-execution hook
        self.backend.register_hook("post_execute", self.after_execute)

        # Intent understanding hook
        self.backend.register_hook("intent_understood", self.metrics.record_intent)

        # Result hook
        self.backend.register_hook("post_execute", self.metrics.record_result)

        logger.info("🪝 Hooks registered for lifecycle events")

    def before_execute(self, intent: Intent) -> Intent:
        """Sacred preparation before execution"""
        print(f"\n🌅 Preparing to execute: {intent.query}")
        return intent

    def after_execute(self, result: Result) -> Result:
        """Sacred completion after execution"""
        if result.success:
            print("✅ Operation completed successfully")
        else:
            print(f"❌ Operation encountered challenges: {result.error}")
            if result.suggestions:
                print("💡 Suggestions:")
                for suggestion in result.suggestions:
                    print(f"   • {suggestion}")
        return result

    async def run(self, query: str, execute: bool = False):
        """
        Execute a query through the unified backend

        Args:
            query: Natural language query
            execute: If True, actually execute (not just dry-run)
        """
        print(f"\n{'='*60}")
        print("🕉️  Sacred Unified CLI - Consciousness-First Computing")
        print(f"{'='*60}")

        # Initialize the backend
        await self.backend.initialize()

        # Create or retrieve context
        context = Context(
            user_id="sacred_user", preferences={"style": "consciousness-first"}
        )

        # Update config for execution mode
        if execute:
            self.backend.config["dry_run"] = False
            print("⚡ LIVE EXECUTION MODE")
        else:
            print("🛡️  DRY RUN MODE (safe)")

        # Execute through unified backend
        result = await self.backend.execute(query, context)

        # Display result
        print("\n📋 Result:")
        print(f"{'─'*40}")
        if result.output:
            print(result.output)

        # Cleanup
        await self.backend.cleanup()

        return result

    async def interactive(self):
        """Interactive REPL mode with sacred flow"""
        print(f"\n{'='*60}")
        print("🕉️  Sacred Interactive Mode")
        print(f"{'='*60}")
        print("Enter natural language commands. Type 'exit' to leave.")
        print("Type '--execute' before a command to run it for real.")

        await self.backend.initialize()

        context = Context(user_id="sacred_user")

        while True:
            try:
                query = input("\n🌟 > ").strip()

                if query.lower() in ["exit", "quit", "bye"]:
                    print("🙏 May your path be luminous")
                    break

                if not query:
                    continue

                # Check for execution flag
                execute = False
                if query.startswith("--execute"):
                    execute = True
                    query = query[10:].strip()
                    self.backend.config["dry_run"] = False
                else:
                    self.backend.config["dry_run"] = True

                # Execute the query
                result = await self.backend.execute(query, context)

                # Display output
                if result.output:
                    print(f"\n{result.output}")

            except KeyboardInterrupt:
                print("\n🙏 May consciousness guide your path")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

        await self.backend.cleanup()


async def demonstrate_streaming():
    """Demonstrate streaming capabilities"""
    print(f"\n{'='*60}")
    print("🌊 Streaming Demo - Real-time Progress")
    print(f"{'='*60}")

    backend = NixForHumanityBackend()
    await backend.initialize()

    print("\n📡 Streaming system update progress:")
    async for update in backend.stream_execute("update system"):
        if update["type"] == "progress":
            bar = "█" * int(update["percent"] / 5)
            print(f"  [{bar:<20}] {update['percent']:.0f}% - {update['message']}")
        elif update["type"] == "complete":
            print(f"  ✅ {update['message']}")

    await backend.cleanup()


async def main():
    """Main entry point with sacred intention"""

    # Setup CLI
    cli = SacredCLI()

    # Parse arguments
    if len(sys.argv) < 2:
        print("Usage: python ask-nix-unified.py <query>")
        print("       python ask-nix-unified.py --interactive")
        print("       python ask-nix-unified.py --stream")
        print("       python ask-nix-unified.py --execute <query>")
        return

    # Handle different modes
    if sys.argv[1] == "--interactive":
        await cli.interactive()
    elif sys.argv[1] == "--stream":
        await demonstrate_streaming()
    elif sys.argv[1] == "--execute" and len(sys.argv) > 2:
        query = " ".join(sys.argv[2:])
        await cli.run(query, execute=True)
    else:
        query = " ".join(sys.argv[1:])
        await cli.run(query, execute=False)


if __name__ == "__main__":
    # Run with sacred intention
    asyncio.run(main())
