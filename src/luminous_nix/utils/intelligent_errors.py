"""
Intelligent Error Handling System for Nix for Humanity

Transforms cryptic errors into educational opportunities.
"""

import logging
import re
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ErrorContext:
    """Context for understanding and explaining errors"""

    error_type: str
    original_message: str
    user_query: str | None = None
    operation: str | None = None
    package: str | None = None


class IntelligentErrorHandler:
    """
    Transforms technical errors into helpful, educational messages

    This system:
    - Detects common error patterns
    - Provides clear explanations
    - Suggests concrete solutions
    - Shows correct examples
    - Educates users about NixOS
    """

    def __init__(self):
        # Common error patterns and their explanations
        self.error_patterns = self._build_error_patterns()

    def _build_error_patterns(
        self,
    ) -> list[tuple[re.Pattern, str, list[str], str | None]]:
        """
        Build database of error patterns

        Returns: List of (pattern, explanation, suggestions, example)
        """
        return [
            # Package not found errors
            (
                re.compile(r"attribute ['\"]?(\w+)['\"]? .*not found", re.IGNORECASE),
                "Package '{package}' not found in nixpkgs",
                [
                    "Check if the package name is spelled correctly",
                    "Search for similar packages: ask-nix 'search {package}'",
                    "The package might have a different name in NixOS",
                    "Try searching by description instead of name",
                ],
                "ask-nix 'search text editor'",
            ),
            # Permission denied errors
            (
                re.compile(
                    r"permission denied|access denied|operation not permitted",
                    re.IGNORECASE,
                ),
                "Permission denied - this operation requires elevated privileges",
                [
                    "System-wide changes need sudo or root access",
                    "Use 'sudo' for system operations",
                    "Check if you're trying to modify system files",
                    "For user packages, use home-manager instead",
                ],
                "sudo nixos-rebuild switch",
            ),
            # Syntax errors in configuration
            (
                re.compile(r"syntax error|unexpected|expecting", re.IGNORECASE),
                "Configuration syntax error detected",
                [
                    "Check for missing semicolons (;) at line ends",
                    "Ensure all brackets { } are properly matched",
                    "Verify quotes are properly closed",
                    "NixOS uses specific syntax - check the format",
                ],
                "{ pkgs, ... }: {\n  environment.systemPackages = [ pkgs.firefox ];\n}",
            ),
            # Network/download errors
            (
                re.compile(
                    r"unable to download|connection.*failed|network.*error|timeout",
                    re.IGNORECASE,
                ),
                "Network connection issue while downloading packages",
                [
                    "Check your internet connection",
                    "The NixOS cache server might be slow - try again",
                    "Use a different cache: --option substituters https://cache.nixos.org",
                    "Some packages are large and take time to download",
                ],
                None,
            ),
            # Disk space errors
            (
                re.compile(r"no space left|disk full|out of space", re.IGNORECASE),
                "Insufficient disk space",
                [
                    "Free up disk space in /nix/store",
                    "Run garbage collection: nix-collect-garbage -d",
                    "Remove old generations: sudo nix-collect-garbage -d",
                    "Check disk usage: df -h /",
                ],
                "nix-collect-garbage -d",
            ),
            # Build failures
            (
                re.compile(
                    r"build.*failed|compilation.*error|make.*error", re.IGNORECASE
                ),
                "Package build failed",
                [
                    "This package needs to be built from source",
                    "Check if a binary cache is available",
                    "Some packages require additional build dependencies",
                    "Try installing a different version or alternative",
                ],
                None,
            ),
            # Collision errors
            (
                re.compile(r"collision between|conflicting packages", re.IGNORECASE),
                "Package conflict detected - multiple packages provide the same file",
                [
                    "Two packages are trying to install the same file",
                    "Remove one of the conflicting packages",
                    "Use priority to resolve: lib.hiPrio or lib.lowPrio",
                    "Check which packages conflict: nix-store -q --referrers",
                ],
                "(lib.hiPrio pkgs.package1)",
            ),
            # File not found
            (
                re.compile(
                    r"no such file or directory|file not found|cannot find",
                    re.IGNORECASE,
                ),
                "File or directory not found",
                [
                    "Check if the path exists",
                    "Paths in NixOS might be different than expected",
                    "Use 'which' to find command locations",
                    "Some files are in /nix/store with hash prefixes",
                ],
                "which firefox",
            ),
            # Module errors
            (
                re.compile(
                    r"module.*not found|undefined variable.*module", re.IGNORECASE
                ),
                "NixOS module not found or not imported",
                [
                    "Ensure the module is imported in configuration.nix",
                    "Check if the module name is correct",
                    "Some modules need to be explicitly enabled",
                    "Module might be in nixos-unstable but not stable",
                ],
                "imports = [ ./hardware-configuration.nix ];",
            ),
            # Evaluation errors
            (
                re.compile(
                    r"evaluation.*error|infinite recursion|assertion.*failed",
                    re.IGNORECASE,
                ),
                "Configuration evaluation error",
                [
                    "There's a logical error in your configuration",
                    "Check for circular dependencies",
                    "An assertion in the config failed",
                    "Try commenting out recent changes to isolate the issue",
                ],
                None,
            ),
        ]

    def explain_error(
        self, error: str, context: ErrorContext | None = None
    ) -> dict[str, any]:
        """
        Transform an error into helpful explanation

        Args:
            error: The error message
            context: Optional context about the operation

        Returns:
            Dictionary with explanation, suggestions, and examples
        """
        error_lower = error.lower()

        # Try to match against known patterns
        for pattern, explanation, suggestions, example in self.error_patterns:
            match = pattern.search(error)
            if match:
                # Customize explanation with context
                if context and context.package:
                    explanation = explanation.format(package=context.package)
                    suggestions = [
                        s.format(package=context.package) for s in suggestions
                    ]

                return {
                    "explanation": explanation,
                    "suggestions": suggestions,
                    "example": example,
                    "error_type": self._categorize_error(explanation),
                    "learn_more": self._get_learning_resources(explanation),
                }

        # Fallback for unknown errors
        return self._handle_unknown_error(error, context)

    def _categorize_error(self, explanation: str) -> str:
        """Categorize the error type"""
        explanation_lower = explanation.lower()

        if "package" in explanation_lower or "not found" in explanation_lower:
            return "package_error"
        if "permission" in explanation_lower:
            return "permission_error"
        if "syntax" in explanation_lower or "configuration" in explanation_lower:
            return "syntax_error"
        if "network" in explanation_lower or "download" in explanation_lower:
            return "network_error"
        if "disk" in explanation_lower or "space" in explanation_lower:
            return "storage_error"
        if "build" in explanation_lower:
            return "build_error"
        return "general_error"

    def _get_learning_resources(self, explanation: str) -> list[str]:
        """Get relevant learning resources based on error type"""
        resources = []
        explanation_lower = explanation.lower()

        if "package" in explanation_lower:
            resources.append("NixOS Package Search: https://search.nixos.org")
            resources.append("Learn about nixpkgs: https://nixos.org/manual/nixpkgs")
        elif "configuration" in explanation_lower or "syntax" in explanation_lower:
            resources.append("NixOS Manual: https://nixos.org/manual/nixos")
            resources.append(
                "Nix Language: https://nixos.org/manual/nix/stable/language"
            )
        elif "module" in explanation_lower:
            resources.append(
                "NixOS Modules: https://nixos.org/manual/nixos/stable/#sec-writing-modules"
            )

        return resources

    def _handle_unknown_error(
        self, error: str, context: ErrorContext | None
    ) -> dict[str, any]:
        """Handle errors we don't recognize"""

        # Try to extract useful info from the error
        suggestions = [
            "This appears to be an uncommon error",
            "Try searching for this error message online",
            "Check the NixOS forums or GitHub issues",
            "Use --debug flag for more details",
        ]

        # Add context-specific suggestions
        if context:
            if context.operation == "install":
                suggestions.append(
                    "Try searching for the package first: ask-nix 'search <package>'"
                )
            elif context.operation == "build":
                suggestions.append("Check if all dependencies are available")
            elif context.operation == "config":
                suggestions.append(
                    "Validate your configuration: nixos-rebuild dry-build"
                )

        return {
            "explanation": "An unexpected error occurred",
            "suggestions": suggestions,
            "example": None,
            "error_type": "unknown_error",
            "learn_more": [
                "NixOS Discourse: https://discourse.nixos.org",
                "NixOS Wiki: https://nixos.wiki",
            ],
        }

    def format_error_message(self, error_info: dict[str, any]) -> str:
        """
        Format error information into a beautiful, helpful message

        Args:
            error_info: Dictionary from explain_error

        Returns:
            Formatted error message
        """
        lines = []

        # Header
        lines.append("❌ " + error_info["explanation"])
        lines.append("")

        # Suggestions
        if error_info["suggestions"]:
            lines.append("💡 How to fix this:")
            for i, suggestion in enumerate(error_info["suggestions"], 1):
                lines.append(f"   {i}. {suggestion}")
            lines.append("")

        # Example
        if error_info.get("example"):
            lines.append("📝 Example:")
            lines.append("   " + error_info["example"])
            lines.append("")

        # Learning resources
        if error_info.get("learn_more"):
            lines.append("📚 Learn more:")
            for resource in error_info["learn_more"]:
                lines.append(f"   • {resource}")

        return "\n".join(lines)


class ErrorEducator:
    """
    Educational component that teaches through errors
    """

    def __init__(self):
        self.handler = IntelligentErrorHandler()
        self.error_history = []

    def educate(self, error: str, context: ErrorContext | None = None) -> str:
        """
        Turn an error into a learning opportunity

        Args:
            error: The error message
            context: Optional context

        Returns:
            Educational error message
        """
        # Get explanation
        error_info = self.handler.explain_error(error, context)

        # Track for learning
        self.error_history.append(
            {
                "error": error,
                "type": error_info["error_type"],
                "helped": True,  # Track if this helped the user
            }
        )

        # Add educational context based on history
        if self._is_repeated_error_type(error_info["error_type"]):
            error_info["suggestions"].insert(
                0, "💭 You've seen this type of error before. Remember the pattern!"
            )

        # Format beautifully
        return self.handler.format_error_message(error_info)

    def _is_repeated_error_type(self, error_type: str) -> bool:
        """Check if user has seen this error type before"""
        count = sum(1 for e in self.error_history if e["type"] == error_type)
        return count > 1

    def get_common_mistakes(self) -> list[str]:
        """Get list of common mistakes to help user avoid them"""
        # Analyze error history for patterns
        error_counts = {}
        for error in self.error_history:
            error_type = error["type"]
            error_counts[error_type] = error_counts.get(error_type, 0) + 1

        # Return tips for most common errors
        tips = []
        for error_type, count in sorted(
            error_counts.items(), key=lambda x: x[1], reverse=True
        ):
            if count > 2:
                if error_type == "package_error":
                    tips.append(
                        "Tip: Package names in NixOS often differ from other distros"
                    )
                elif error_type == "syntax_error":
                    tips.append("Tip: NixOS configs need semicolons after each line")
                elif error_type == "permission_error":
                    tips.append("Tip: System changes need 'sudo nixos-rebuild'")

        return tips


# Global instance
_educator = None


def get_error_educator() -> ErrorEducator:
    """Get the global error educator instance"""
    global _educator
    if _educator is None:
        _educator = ErrorEducator()
    return _educator
