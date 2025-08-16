#!/usr/bin/env python3
"""
from typing import List, Optional
Nix for Humanity - Python Backend Integration
Bridges the new Python backend with existing NLP and knowledge systems
"""

import asyncio
import json
import logging
import sys
from collections.abc import Callable
from pathlib import Path

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

# Import existing components
try:
    from command_learning_system import CommandLearningSystem
    from nix_knowledge_engine import NixOSKnowledgeEngine
    from package_cache_manager import PackageCacheManager
except ImportError as e:
    print(f"Warning: Could not import existing modules: {e}")

    # Define placeholders
    class NixOSKnowledgeEngine:
        def extract_intent(self, query):
            return {"action": "unknown"}

        def get_solution(self, intent):
            return {"found": False}

    class CommandLearningSystem:
        def learn_from_execution(self, *args):
            pass

    class PackageCacheManager:
        def search_cached(self, query):
            return None


# Import our new backend
from .nixos_python_backend import (
    Action,
    NixOSPythonBackend,
)

logger = logging.getLogger(__name__)


class NixForHumanityBackend:
    """
    Unified backend for Nix for Humanity
    Integrates:
    - Python NixOS API (when available)
    - Knowledge engine for intent recognition
    - Learning system for adaptation
    - Cache system for performance
    - Progress callbacks for real-time feedback
    """

    def __init__(self, personality_style: str = "friendly"):
        # Initialize components
        self.nixos_backend = NixOSPythonBackend()
        self.knowledge_engine = NixOSKnowledgeEngine()
        self.learning_system = CommandLearningSystem()
        self.cache_manager = PackageCacheManager()
        self.personality_style = personality_style

        # Check capabilities
        self.has_python_api = self.nixos_backend.has_python_api

        logger.info("Nix for Humanity Backend initialized")
        logger.info(f"Python API available: {self.has_python_api}")

    def set_personality(self, style: str):
        """Change response personality"""
        self.personality_style = style

    async def process_natural_language(
        self,
        query: str,
        execute: bool = False,
        progress_callback: Callable | None = None,
    ) -> dict:
        """
        Process natural language query with full integration

        Args:
            query: Natural language input from user
            execute: Whether to execute commands (vs just explain)
            progress_callback: Function to call with progress updates

        Returns:
            Response dict with results and explanations
        """
        # Add progress callback if provided
        if progress_callback:
            self.nixos_backend.add_progress_callback(progress_callback)

        # Step 1: Extract intent
        intent = self.knowledge_engine.extract_intent(query)
        logger.info(f"Intent extracted: {intent}")

        # Step 2: Check cache for package searches
        if intent["action"] == "search_package" and "package" in intent:
            cached_results = self.cache_manager.search_cached(intent["package"])
            if cached_results:
                return self._format_search_response(cached_results, intent["package"])

        # Step 3: Get solution from knowledge base
        solution = self.knowledge_engine.get_solution(intent)

        # Step 4: Execute if requested
        if execute and solution["found"]:
            result = await self._execute_intent(intent, solution, progress_callback)

            # Step 5: Learn from execution
            self.learning_system.learn_from_execution(
                query=query,
                intent=intent,
                result=result,
                success=result.get("success", False),
            )

            return result
        # Just return explanation
        return self._format_explanation(intent, solution)

    async def _execute_intent(
        self, intent: dict, solution: dict, progress_callback: Callable | None = None
    ) -> dict:
        """Execute the actual NixOS command based on intent"""
        action = intent.get("action", "unknown")

        try:
            if action == "install_package":
                package = intent.get("package")
                if not package:
                    return {
                        "success": False,
                        "error": "No package specified",
                        "suggestion": "Please specify which package to install",
                    }

                # Use modern nix profile by default
                result = await self.nixos_backend.install_package(
                    package, method="profile"
                )

                return {
                    "success": result.success,
                    "action": "install",
                    "package": package,
                    "output": result.output,
                    "error": result.error,
                    "duration": result.duration,
                    "message": self._personalize_message(
                        f"{'Successfully installed' if result.success else 'Failed to install'} {package}",
                        result.success,
                    ),
                }

            if action == "search_package":
                query = intent.get("package", intent.get("query", ""))
                packages = await self.nixos_backend.search_packages(query)

                # Cache results
                if packages:
                    self.cache_manager.cache_search(query, packages)

                return self._format_search_response(packages, query)

            if action == "update_system":
                result = await self.nixos_backend.execute_action(
                    Action.SWITCH, upgrade=True
                )

                return {
                    "success": result.success,
                    "action": "update",
                    "output": result.output,
                    "error": result.error,
                    "duration": result.duration,
                    "generation": result.generation,
                    "message": self._personalize_message(
                        (
                            "System update completed"
                            if result.success
                            else "System update failed"
                        ),
                        result.success,
                    ),
                }

            if action == "rollback_system":
                result = await self.nixos_backend.execute_action(Action.ROLLBACK)

                return {
                    "success": result.success,
                    "action": "rollback",
                    "output": result.output,
                    "error": result.error,
                    "duration": result.duration,
                    "message": self._personalize_message(
                        "Rollback completed" if result.success else "Rollback failed",
                        result.success,
                    ),
                }

            if action == "test_configuration":
                result = await self.nixos_backend.execute_action(Action.TEST)

                return {
                    "success": result.success,
                    "action": "test",
                    "output": result.output,
                    "error": result.error,
                    "duration": result.duration,
                    "message": self._personalize_message(
                        (
                            "Configuration test passed"
                            if result.success
                            else "Configuration test failed"
                        ),
                        result.success,
                    ),
                }

            return {
                "success": False,
                "error": f"Unknown action: {action}",
                "suggestion": "Try asking about installing, searching, updating, or rolling back",
            }

        except Exception as e:
            logger.error(f"Execution error: {e}")
            return {
                "success": False,
                "error": str(e),
                "suggestion": "An unexpected error occurred. Please check your system configuration.",
            }

    def _format_search_response(self, packages: list[dict], query: str) -> dict:
        """Format package search results"""
        if not packages:
            return {
                "success": True,
                "action": "search",
                "query": query,
                "count": 0,
                "packages": [],
                "message": self._personalize_message(
                    f"No packages found matching '{query}'", False
                ),
            }

        # Limit to top 10 results
        top_packages = packages[:10]

        return {
            "success": True,
            "action": "search",
            "query": query,
            "count": len(packages),
            "packages": top_packages,
            "message": self._personalize_message(
                f"Found {len(packages)} packages matching '{query}'", True
            ),
        }

    def _format_explanation(self, intent: dict, solution: dict) -> dict:
        """Format explanation without execution"""
        if not solution["found"]:
            return {
                "success": False,
                "explanation": solution.get(
                    "suggestion", "I did not understand that request"
                ),
                "suggestion": "Try asking about installing, searching, updating, or rolling back",
            }

        # Build explanation based on intent
        action = intent.get("action", "unknown")

        if action == "install_package":
            package = intent.get("package", "the package")
            methods = solution.get("methods", [])

            explanation = f"To install {package}, you have several options:\n\n"
            for method in methods:
                explanation += f"**{method['name']}**: {method['description']}\n"
                explanation += f"```\n{method['example']}\n```\n\n"

            return {
                "success": True,
                "action": "explain",
                "explanation": explanation,
                "hint": "Add --execute flag to actually install",
            }

        return {
            "success": True,
            "action": "explain",
            "explanation": solution.get("solution", ""),
            "example": solution.get("example", ""),
            "hint": "Add --execute flag to run this command",
        }

    def _personalize_message(self, base_message: str, success: bool) -> str:
        """Add personality to messages based on style"""
        if self.personality_style == "minimal":
            return base_message

        if self.personality_style == "friendly":
            if success:
                return f"Great! {base_message} 😊"
            return f"Oh no! {base_message}. Let me help you troubleshoot."

        if self.personality_style == "encouraging":
            if success:
                return f"Awesome work! {base_message} 🌟 You're doing great!"
            return f"No worries! {base_message}. Every expert was once a beginner!"

        if self.personality_style == "technical":
            return f"[{success and 'SUCCESS' or 'FAILURE'}] {base_message}"

        return base_message

    async def get_system_status(self) -> dict:
        """Get comprehensive system status"""
        info = await self.nixos_backend.get_system_info()

        # Add backend status
        info["backend"] = {
            "has_python_api": self.has_python_api,
            "personality": self.personality_style,
            "learning_enabled": hasattr(self.learning_system, "is_enabled"),
            "cache_enabled": hasattr(self.cache_manager, "is_enabled"),
        }

        return info


# CLI Interface for testing
async def main():
    """Test the integrated backend"""
    import argparse

    parser = argparse.ArgumentParser(description="Nix for Humanity Backend Test")
    parser.add_argument("query", nargs="?", help="Natural language query")
    parser.add_argument("--execute", action="store_true", help="Execute commands")
    parser.add_argument(
        "--personality",
        choices=["minimal", "friendly", "encouraging", "technical"],
        default="friendly",
        help="Response personality",
    )
    parser.add_argument("--status", action="store_true", help="Show system status")

    args = parser.parse_args()

    # Initialize backend
    backend = NixForHumanityBackend(personality_style=args.personality)

    # Progress callback
    def progress(msg, pct):
        if pct >= 0:
            print(f"\r[{'█' * int(pct/5):20}] {pct:3.0f}% {msg}", end="", flush=True)
        else:
            print(f"\n{msg}")

    if args.status:
        print("📊 System Status:")
        status = await backend.get_system_status()
        print(json.dumps(status, indent=2))

    elif args.query:
        print(f"🤔 Processing: {args.query}")
        result = await backend.process_natural_language(
            args.query, execute=args.execute, progress_callback=progress
        )

        print("\n\n📝 Result:")
        print(json.dumps(result, indent=2))

    else:
        # Interactive mode
        print("🗣️  Nix for Humanity - Interactive Mode")
        print("Type 'quit' to exit\n")

        while True:
            try:
                query = input("nix> ")
                if query.lower() in ["quit", "exit"]:
                    break

                execute = "--execute" in query
                query = query.replace("--execute", "").strip()

                result = await backend.process_natural_language(
                    query, execute=execute, progress_callback=progress
                )

                print("\n" + result.get("message", json.dumps(result, indent=2)))
                print()

            except KeyboardInterrupt:
                break

        print("\nGoodbye! 👋")


if __name__ == "__main__":
    asyncio.run(main())
