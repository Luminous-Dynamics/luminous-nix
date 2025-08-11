"""
Centralized Error Messages for Nix for Humanity.

Provides consistent, user-friendly error messages throughout the application.
All error messages are centralized here for easy maintenance and localization.

Usage Example:
    >>> from nix_for_humanity.errors.messages import ErrorMessages
    >>> error = ErrorMessages.PACKAGE_NOT_FOUND.format(package="firefox")
    >>> print(error)
    "Package 'firefox' not found. Try searching with: ask-nix search firefox"

Since: v1.0.0
"""

from typing import Any


class ErrorMessages:
    """
    Central repository of error messages.

    All error messages are defined as class attributes for easy access
    and consistency across the codebase.

    Since: v1.0.0
    """

    # ========================================================================
    # Package Management Errors
    # ========================================================================

    PACKAGE_NOT_FOUND = (
        "Package '{package}' not found. " "Try searching with: ask-nix search {package}"
    )

    PACKAGE_ALREADY_INSTALLED = (
        "Package '{package}' is already installed. "
        "Use 'ask-nix update {package}' to update it."
    )

    PACKAGE_INSTALL_FAILED = (
        "Failed to install package '{package}': {error}\n"
        "Try: ask-nix --debug install {package}"
    )

    PACKAGE_REMOVE_FAILED = (
        "Failed to remove package '{package}': {error}\n"
        "The package might be required by other packages."
    )

    # ========================================================================
    # Query and Intent Errors
    # ========================================================================

    QUERY_TOO_SHORT = (
        "Query too short. Please provide more details about what you want to do."
    )

    QUERY_TOO_LONG = (
        "Query exceeds maximum length of {max_length} characters. "
        "Please be more concise."
    )

    INTENT_NOT_RECOGNIZED = (
        "I couldn't understand '{query}'.\n"
        "Try commands like:\n"
        "  - install firefox\n"
        "  - search editor\n"
        "  - update system\n"
        "  - remove package vim"
    )

    AMBIGUOUS_INTENT = (
        "Your query '{query}' could mean multiple things:\n{suggestions}\n"
        "Please be more specific."
    )

    # ========================================================================
    # Configuration Errors
    # ========================================================================

    CONFIG_NOT_FOUND = (
        "Configuration file not found at: {path}\n"
        "Run 'ask-nix-config init' to create default configuration."
    )

    CONFIG_INVALID = (
        "Invalid configuration at {path}: {error}\n"
        "Check the configuration syntax or restore defaults."
    )

    CONFIG_PERMISSION_DENIED = (
        "Permission denied accessing configuration at {path}.\n"
        "Check file permissions or run with appropriate privileges."
    )

    # ========================================================================
    # Permission and Security Errors
    # ========================================================================

    PERMISSION_DENIED = (
        "Permission denied: {operation}\n"
        "This operation requires elevated privileges.\n"
        "Try: sudo {command}"
    )

    UNSAFE_COMMAND = (
        "Command blocked for safety: {command}\n"
        "This command could damage your system.\n"
        "Use --force to override (not recommended)."
    )

    # ========================================================================
    # Network and Connection Errors
    # ========================================================================

    NETWORK_TIMEOUT = (
        "Network timeout while {operation}.\n"
        "Check your internet connection and try again."
    )

    CACHE_SERVER_UNREACHABLE = (
        "Cannot reach NixOS cache server: {server}\n" "Trying alternative mirrors..."
    )

    DOWNLOAD_FAILED = (
        "Failed to download {resource}: {error}\n" "Will retry with alternative source."
    )

    # ========================================================================
    # File System Errors
    # ========================================================================

    FILE_NOT_FOUND = "File not found: {path}\n" "Check the path and try again."

    DIRECTORY_NOT_FOUND = (
        "Directory not found: {path}\n" "Create it with: mkdir -p {path}"
    )

    DISK_SPACE_LOW = (
        "Low disk space: only {available}MB available.\n"
        "Need at least {required}MB for this operation.\n"
        "Free up space with: ask-nix clean"
    )

    # ========================================================================
    # System and Environment Errors
    # ========================================================================

    NIX_NOT_INSTALLED = (
        "Nix is not installed on this system.\n"
        "Visit https://nixos.org/download.html for installation instructions."
    )

    NIXOS_REBUILD_TIMEOUT = (
        "nixos-rebuild is taking longer than expected.\n"
        "This is normal for large updates. The process continues in background.\n"
        "Check progress with: sudo journalctl -f"
    )

    PYTHON_VERSION_TOO_OLD = (
        "Python {current} is too old. Minimum required: {required}\n"
        "Update Python or use nix-shell with proper environment."
    )

    # ========================================================================
    # Cache Errors
    # ========================================================================

    CACHE_CORRUPTED = (
        "Cache appears to be corrupted.\n"
        "Clearing cache and rebuilding...\n"
        "This may take a moment."
    )

    CACHE_WRITE_FAILED = (
        "Failed to write to cache: {error}\n" "Cache is disabled for this session."
    )

    # ========================================================================
    # Learning System Errors
    # ========================================================================

    LEARNING_DATA_CORRUPTED = (
        "Learning data appears corrupted.\n"
        "Resetting to defaults. Your preferences will be relearned."
    )

    PATTERN_SAVE_FAILED = (
        "Failed to save learned patterns: {error}\n" "Learning is temporarily disabled."
    )

    # ========================================================================
    # Generic Errors
    # ========================================================================

    UNKNOWN_ERROR = (
        "An unexpected error occurred: {error}\n"
        "Please report this issue with the error details."
    )

    FEATURE_NOT_IMPLEMENTED = (
        "Feature '{feature}' is not yet implemented.\n"
        "Check for updates or contribute at: https://github.com/..."
    )

    TIMEOUT_ERROR = (
        "Operation timed out after {timeout} seconds.\n"
        "Try again or increase timeout with --timeout option."
    )


class ErrorFormatter:
    """
    Utilities for formatting error messages.

    Provides consistent formatting and styling for error messages.

    Since: v1.0.0
    """

    @staticmethod
    def format_suggestions(suggestions: list) -> str:
        """
        Format a list of suggestions.

        Args:
            suggestions: List of suggestion strings

        Returns:
            Formatted suggestions as bullet points

        Since: v1.0.0
        """
        if not suggestions:
            return ""
        return "\n".join(f"  • {s}" for s in suggestions)

    @staticmethod
    def format_error_with_context(
        message: str, context: dict[str, Any], include_traceback: bool = False
    ) -> str:
        """
        Format error message with additional context.

        Args:
            message: Base error message
            context: Additional context dictionary
            include_traceback: Whether to include traceback

        Returns:
            Formatted error message with context

        Since: v1.0.0
        """
        formatted = message

        if context:
            formatted += "\n\nContext:"
            for key, value in context.items():
                formatted += f"\n  {key}: {value}"

        if include_traceback:
            import traceback

            formatted += "\n\nTraceback:\n"
            formatted += traceback.format_exc()

        return formatted


class UserFriendlyErrors:
    """
    Translates technical errors into user-friendly messages.

    Provides helpful suggestions and next steps for common errors.

    Since: v1.0.0
    """

    ERROR_TRANSLATIONS = {
        "ENOENT": "File or directory not found",
        "EACCES": "Permission denied",
        "ENOSPC": "No space left on device",
        "ETIMEDOUT": "Connection timed out",
        "ECONNREFUSED": "Connection refused",
        "EHOSTUNREACH": "Host unreachable",
        "ENOTFOUND": "Domain name not found",
    }

    @classmethod
    def translate(cls, technical_error: str) -> str:
        """
        Translate technical error to user-friendly message.

        Args:
            technical_error: Technical error message or code

        Returns:
            User-friendly error message

        Since: v1.0.0
        """
        for code, translation in cls.ERROR_TRANSLATIONS.items():
            if code in technical_error:
                return translation

        # Extract key information from technical errors
        if "attribute" in technical_error and "not found" in technical_error:
            # Extract package name from Nix attribute errors
            import re

            match = re.search(r"attribute '([^']+)'", technical_error)
            if match:
                package = match.group(1)
                return ErrorMessages.PACKAGE_NOT_FOUND.format(package=package)

        return technical_error  # Return as-is if no translation found
