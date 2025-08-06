"""
NixOS-specific error patterns and solutions

This module contains comprehensive error patterns commonly encountered
in NixOS, along with context-aware solutions and educational information.
"""

import re
from typing import List, Dict
import logging

from .error_analyzer import (
    ErrorPattern, ErrorSolution, ErrorCategory, 
    ErrorSeverity, ErrorAnalyzer
)

logger = logging.getLogger(__name__)


class NixOSErrorPatterns:
    """
    Registry of NixOS-specific error patterns with solutions
    """
    
    @staticmethod
    def register_all_patterns(analyzer: ErrorAnalyzer):
        """Register all NixOS error patterns with the analyzer"""
        patterns = NixOSErrorPatterns._get_all_patterns()
        for pattern in patterns:
            analyzer.register_pattern(pattern)
        logger.info(f"Registered {len(patterns)} NixOS error patterns")
    
    @staticmethod
    def _get_all_patterns() -> List[ErrorPattern]:
        """Get all defined error patterns"""
        return [
            # Package not found errors
            ErrorPattern(
                id="package_not_found",
                category=ErrorCategory.NOT_FOUND,
                severity=ErrorSeverity.ERROR,
                patterns=[
                    re.compile(r"attribute '(.+)' missing", re.IGNORECASE),
                    re.compile(r"error: undefined variable '(.+)'", re.IGNORECASE),
                    re.compile(r"Package '(.+)' not found", re.IGNORECASE)
                ],
                keywords=["attribute", "missing", "undefined variable", "not found"],
                description="The requested package doesn't exist or name is incorrect",
                common_causes=[
                    "Package name is misspelled",
                    "Package exists but with different attribute name",
                    "Package is in a different channel or overlay",
                    "Package was removed or renamed in recent NixOS versions"
                ]
            ),
            
            # Permission denied errors
            ErrorPattern(
                id="permission_denied",
                category=ErrorCategory.PERMISSION,
                severity=ErrorSeverity.ERROR,
                patterns=[
                    re.compile(r"Permission denied", re.IGNORECASE),
                    re.compile(r"error: opening file .+: Permission denied"),
                    re.compile(r"cannot open .+ for writing: Permission denied"),
                    re.compile(r"error: cannot write to .+, permission denied")
                ],
                keywords=["permission denied", "access denied", "cannot write"],
                description="Operation requires elevated privileges",
                common_causes=[
                    "Trying to modify system files without sudo",
                    "Attempting to install system-wide without proper permissions",
                    "File ownership prevents modification",
                    "SELinux or AppArmor restrictions"
                ]
            ),
            
            # Disk space errors
            ErrorPattern(
                id="disk_space_full",
                category=ErrorCategory.SYSTEM,
                severity=ErrorSeverity.CRITICAL,
                patterns=[
                    re.compile(r"No space left on device"),
                    re.compile(r"error: writing to file: No space left on device"),
                    re.compile(r"cannot write to .+: No space left on device"),
                    re.compile(r"Build of .+ failed.*No space left")
                ],
                keywords=["no space", "disk full", "space left on device"],
                description="Insufficient disk space for operation",
                common_causes=[
                    "Nix store has accumulated too many old generations",
                    "/tmp or /var/tmp is full",
                    "Home directory quota exceeded",
                    "Large builds require more temporary space"
                ]
            ),
            
            # Network errors
            ErrorPattern(
                id="network_error",
                category=ErrorCategory.NETWORK,
                severity=ErrorSeverity.ERROR,
                patterns=[
                    re.compile(r"unable to download .+: HTTP error 404"),
                    re.compile(r"curl: .+ Connection refused"),
                    re.compile(r"error: unable to download .+: Couldn't resolve host"),
                    re.compile(r"SSL certificate problem"),
                    re.compile(r"Network is unreachable")
                ],
                keywords=["unable to download", "connection refused", "network unreachable", "SSL"],
                description="Network connectivity or remote resource issue",
                common_causes=[
                    "No internet connection",
                    "Firewall blocking connections",
                    "Proxy configuration needed",
                    "Remote server is down",
                    "SSL/TLS certificate issues"
                ]
            ),
            
            # Build errors
            ErrorPattern(
                id="build_failure",
                category=ErrorCategory.DEPENDENCY,
                severity=ErrorSeverity.ERROR,
                patterns=[
                    re.compile(r"error: build of .+ failed"),
                    re.compile(r"builder for .+ failed with exit code \d+"),
                    re.compile(r"error: while evaluating"),
                    re.compile(r"make: \*\*\* .+ Error \d+")
                ],
                keywords=["build failed", "exit code", "compilation error"],
                description="Package build process failed",
                common_causes=[
                    "Missing build dependencies",
                    "Incompatible compiler version",
                    "Source code errors",
                    "Insufficient resources (RAM/CPU)",
                    "Conflicting environment variables"
                ]
            ),
            
            # Configuration syntax errors
            ErrorPattern(
                id="config_syntax_error",
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.ERROR,
                patterns=[
                    re.compile(r"error: syntax error, unexpected"),
                    re.compile(r"error: .+ at .+:\d+:\d+"),
                    re.compile(r"parse error on value"),
                    re.compile(r"unexpected end of file")
                ],
                keywords=["syntax error", "parse error", "unexpected"],
                description="Nix configuration file has syntax errors",
                common_causes=[
                    "Missing semicolon or bracket",
                    "Unmatched quotes or parentheses",
                    "Invalid Nix expression syntax",
                    "Typo in attribute name",
                    "Incorrect indentation in multi-line strings"
                ]
            ),
            
            # Infinite recursion
            ErrorPattern(
                id="infinite_recursion",
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.ERROR,
                patterns=[
                    re.compile(r"infinite recursion encountered"),
                    re.compile(r"error: infinite recursion encountered"),
                    re.compile(r"while evaluating .+ infinite recursion")
                ],
                keywords=["infinite recursion"],
                description="Circular dependency in configuration",
                common_causes=[
                    "Self-referential package override",
                    "Circular imports in configuration modules",
                    "Recursive attribute definition",
                    "Overlay that references itself"
                ]
            ),
            
            # Hash mismatch
            ErrorPattern(
                id="hash_mismatch",
                category=ErrorCategory.DEPENDENCY,
                severity=ErrorSeverity.ERROR,
                patterns=[
                    re.compile(r"hash mismatch in fixed-output derivation"),
                    re.compile(r"specified: .+\s+got: .+"),
                    re.compile(r"error: hash .+ does not match")
                ],
                keywords=["hash mismatch", "sha256 mismatch"],
                description="Downloaded file doesn't match expected hash",
                common_causes=[
                    "Upstream source file was updated",
                    "Network corruption during download",
                    "Wrong hash specified in derivation",
                    "Different file downloaded due to redirect"
                ]
            ),
            
            # Out of memory
            ErrorPattern(
                id="out_of_memory",
                category=ErrorCategory.SYSTEM,
                severity=ErrorSeverity.CRITICAL,
                patterns=[
                    re.compile(r"error: out of memory"),
                    re.compile(r"Cannot allocate memory"),
                    re.compile(r"g\+\+: fatal error: Killed signal terminated"),
                    re.compile(r"virtual memory exhausted")
                ],
                keywords=["out of memory", "cannot allocate", "memory exhausted"],
                description="System ran out of available memory",
                common_causes=[
                    "Build requires more RAM than available",
                    "Too many parallel build jobs",
                    "Memory leak in build process",
                    "Large evaluation of Nix expressions"
                ]
            ),
            
            # Channel errors
            ErrorPattern(
                id="channel_error",
                category=ErrorCategory.CONFIGURATION,
                severity=ErrorSeverity.WARNING,
                patterns=[
                    re.compile(r"error: file .+ was not found in the Nix search path"),
                    re.compile(r"cannot find flake .+ in the flake registry"),
                    re.compile(r"warning: Nix search path .+ does not exist")
                ],
                keywords=["search path", "not found in", "channel"],
                description="Nix channel or search path issue",
                common_causes=[
                    "Channel not added or updated",
                    "NIX_PATH not configured correctly",
                    "Flake registry not updated",
                    "Using old channel name"
                ]
            )
        ]
    
    @staticmethod
    def get_pattern_solutions(pattern_id: str) -> List[ErrorSolution]:
        """Get specific solutions for a pattern"""
        solutions_map = {
            "package_not_found": [
                ErrorSolution(
                    id="search_correct_name",
                    title="Search for the correct package name",
                    steps=[
                        "Search available packages with fuzzy matching",
                        "Check if package exists with different name",
                        "Look for package in different channels"
                    ],
                    commands=[
                        "nix search nixpkgs#firefox",  # Example
                        "nix search nixpkgs --regex 'fire.*fox'",
                        "nix search unstable#firefox"
                    ],
                    explanation="Package names in Nix often differ from common names",
                    confidence=0.9
                ),
                ErrorSolution(
                    id="check_nixpkgs_github",
                    title="Check package availability on GitHub",
                    steps=[
                        "Visit NixOS package search website",
                        "Search GitHub nixpkgs repository",
                        "Check if package was recently added/removed"
                    ],
                    commands=[],
                    explanation="Some packages may be too new or removed",
                    confidence=0.7,
                    learn_more_url="https://search.nixos.org/"
                )
            ],
            
            "disk_space_full": [
                ErrorSolution(
                    id="garbage_collection",
                    title="Free disk space with garbage collection",
                    steps=[
                        "Check current disk usage",
                        "Remove old system generations",
                        "Run Nix garbage collection",
                        "Verify freed space"
                    ],
                    commands=[
                        "df -h /",
                        "sudo nix-env --delete-generations +5",
                        "sudo nix-collect-garbage -d",
                        "df -h /"
                    ],
                    explanation="Nix keeps old generations which can use significant space",
                    confidence=0.95,
                    warnings=["This will remove ability to rollback to deleted generations"]
                ),
                ErrorSolution(
                    id="optimize_store",
                    title="Optimize Nix store to save space",
                    steps=[
                        "Optimize store by hard-linking identical files",
                        "This can save significant space"
                    ],
                    commands=[
                        "sudo nix-store --optimise"
                    ],
                    explanation="Nix store may contain duplicate files that can be hard-linked",
                    confidence=0.8
                )
            ],
            
            "permission_denied": [
                ErrorSolution(
                    id="use_sudo",
                    title="Run with administrator privileges",
                    steps=[
                        "Retry the command with sudo",
                        "Enter your password when prompted"
                    ],
                    commands=[
                        "sudo nixos-rebuild switch"
                    ],
                    explanation="System-wide changes require administrator privileges",
                    confidence=0.9,
                    prerequisites=["User must be in sudo/wheel group"]
                ),
                ErrorSolution(
                    id="use_home_manager",
                    title="Use Home Manager for user packages",
                    steps=[
                        "Install packages in user profile instead",
                        "No sudo required for user packages"
                    ],
                    commands=[
                        "nix-env -iA nixos.firefox",
                        "# Or with Home Manager:",
                        "home-manager switch"
                    ],
                    explanation="User-specific installations don't need sudo",
                    confidence=0.8
                )
            ],
            
            "infinite_recursion": [
                ErrorSolution(
                    id="debug_recursion",
                    title="Debug the recursive reference",
                    steps=[
                        "Check recent configuration changes",
                        "Look for self-referential definitions",
                        "Comment out suspicious sections",
                        "Test configuration incrementally"
                    ],
                    commands=[
                        "nixos-rebuild dry-build",
                        "nix-instantiate '<nixpkgs/nixos>' -A system --show-trace"
                    ],
                    explanation="Infinite recursion usually comes from circular references",
                    confidence=0.8,
                    warnings=["May require careful analysis of configuration"]
                )
            ]
        }
        
        return solutions_map.get(pattern_id, [])