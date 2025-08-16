#!/usr/bin/env python3
"""
Simple working CLI for Nix for Humanity

This demonstrates the complete integration:
- Natural language parsing
- Native Python-Nix API
- Command execution
- NO MOCKS
"""

import argparse
import logging
import sys

# Add src to path
sys.path.insert(0, "src")

from luminous_nix.core.command_executor import CommandExecutor
from luminous_nix.knowledge.engine import ModernNixOSKnowledgeEngine
from luminous_nix.nlp.personas import PersonaManager

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class SimpleNixCLI:
    """Simple CLI for natural language NixOS operations"""

    def __init__(self, dry_run: bool = True):
        self.knowledge = ModernNixOSKnowledgeEngine()
        self.executor = CommandExecutor(dry_run=dry_run)
        self.personas = PersonaManager()
        self.dry_run = dry_run

    def process_query(self, query: str) -> None:
        """Process a natural language query"""
        print(f"\n🔍 Processing: '{query}'")
        print("-" * 50)

        # Parse the query
        intent_data = self.knowledge.extract_intent(query)
        intent = intent_data.get("intent", "unknown")

        if intent == "unknown":
            print(f"❓ I don't understand '{query}'")
            print("\nTry something like:")
            print("  • install firefox")
            print("  • search python")
            print("  • update system")
            print("  • list packages")
            return

        print(f"📋 Intent: {intent}")

        # Extract parameters
        params = {k: v for k, v in intent_data.items() if k != "intent"}
        if params:
            print(f"📦 Parameters: {params}")

        # Execute the command
        print(f"\n{'🧪 DRY RUN' if self.dry_run else '⚡ EXECUTING'}:")
        result = self.executor.execute(intent, **params)

        if result.success:
            print(f"✅ {result.output}")
            if result.metadata:
                print(f"📊 Metadata: {result.metadata}")
        else:
            print(f"❌ Failed: {result.error}")

        if self.dry_run and result.command:
            print(f"\n💡 Actual command: {result.command}")
            print("   Run with --execute to perform this action")

    def interactive_mode(self) -> None:
        """Run in interactive mode"""
        print("\n🌟 Nix for Humanity - Interactive Mode")
        print("=" * 50)
        print("Type natural language commands or 'quit' to exit")
        print("Examples: 'install firefox', 'search editor', 'update system'")
        print()

        while True:
            try:
                query = input("nix> ").strip()

                if query.lower() in ["quit", "exit", "q"]:
                    print("👋 Goodbye!")
                    break

                if query:
                    self.process_query(query)
                    print()

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Nix for Humanity - Natural Language NixOS Interface"
    )

    parser.add_argument(
        "query", nargs="*", help="Natural language query (e.g., 'install firefox')"
    )

    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually execute commands (default is dry-run)",
    )

    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Run in interactive mode"
    )

    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        # Suppress info messages for cleaner output
        logging.getLogger().setLevel(logging.WARNING)

    # Create CLI instance
    cli = SimpleNixCLI(dry_run=not args.execute)

    if args.interactive:
        cli.interactive_mode()
    elif args.query:
        query = " ".join(args.query)
        cli.process_query(query)
    else:
        # No query provided, show help
        parser.print_help()
        print("\n💡 Examples:")
        print("  python ask-nix-simple.py install firefox")
        print("  python ask-nix-simple.py search python editor")
        print("  python ask-nix-simple.py update system")
        print("  python ask-nix-simple.py --interactive")
        print("  python ask-nix-simple.py --execute install hello")


if __name__ == "__main__":
    main()
