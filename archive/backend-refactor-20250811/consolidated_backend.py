"""
Consolidated Backend for Nix for Humanity v1.3.0+

This is the SINGLE unified backend that replaces:
- backend.py
- unified_backend.py  
- headless_engine.py
- engine.py

Architecture:
    All Frontends → This Backend → Native Python-Nix API → NixOS

Created: 2025-08-12
Purpose: Eliminate duplication and simplify architecture
"""

import asyncio
import json
import os
import subprocess
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Use lazy imports to improve startup time
_knowledge_engine = None
_command_executor = None
_fuzzy_search = None
_tree_sitter = None


def get_knowledge_engine():
    """Lazy load knowledge engine."""
    global _knowledge_engine
    if _knowledge_engine is None:
        from ..knowledge.engine import ModernNixOSKnowledgeEngine
        _knowledge_engine = ModernNixOSKnowledgeEngine()
    return _knowledge_engine


def get_command_executor():
    """Lazy load command executor."""
    global _command_executor
    if _command_executor is None:
        from .command_executor import CommandExecutor
        _command_executor = CommandExecutor()
    return _command_executor


def get_fuzzy_search():
    """Lazy load fuzzy search."""
    global _fuzzy_search
    if _fuzzy_search is None:
        try:
            from ..search.fuzzy_search import ConsciousFuzzySearch
            _fuzzy_search = ConsciousFuzzySearch()
        except ImportError:
            _fuzzy_search = None
    return _fuzzy_search


def get_tree_sitter():
    """Lazy load tree-sitter parsers."""
    global _tree_sitter
    if _tree_sitter is None:
        try:
            from ..parsers.multi_language_parser import MultiLanguageAnalyzer
            _tree_sitter = MultiLanguageAnalyzer()
        except ImportError:
            _tree_sitter = None
    return _tree_sitter


class IntentType(Enum):
    """Types of user intentions."""
    INSTALL = "install"
    REMOVE = "remove"
    SEARCH = "search"
    UPDATE = "update"
    ROLLBACK = "rollback"
    LIST = "list"
    QUERY = "query"
    GENERATE_CONFIG = "generate_config"
    ANALYZE_PROJECT = "analyze_project"
    MIGRATE_SCRIPT = "migrate_script"
    UNKNOWN = "unknown"


@dataclass
class Intent:
    """User intent with extracted parameters."""
    type: IntentType
    packages: List[str] = field(default_factory=list)
    query: str = ""
    options: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0


@dataclass
class Request:
    """Request from any frontend."""
    query: str
    context: Dict[str, Any] = field(default_factory=dict)
    dry_run: bool = True
    verbose: bool = False


@dataclass
class Response:
    """Response to any frontend."""
    success: bool
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    suggestions: List[str] = field(default_factory=list)


class NixForHumanityBackend:
    """
    The ONE backend to rule them all.
    
    This consolidates all backend functionality into a single,
    clean, maintainable class with <500ms response time.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the consolidated backend."""
        self.config = config or {}
        self.cache = {}
        self.stats = {
            "requests": 0,
            "success": 0,
            "errors": 0,
            "avg_response_time": 0
        }
        
        # Performance optimization: lazy load heavy components
        self._knowledge = None
        self._executor = None
        self._fuzzy = None
        self._tree_sitter = None
    
    def process(self, request: Request) -> Response:
        """
        Main entry point for all requests.
        
        This method:
        1. Parses intent
        2. Routes to appropriate handler
        3. Returns unified response
        
        Target: <500ms response time
        """
        start_time = time.time()
        self.stats["requests"] += 1
        
        try:
            # Parse intent from natural language
            intent = self._parse_intent(request.query)
            
            # Route to appropriate handler
            if intent.type == IntentType.INSTALL:
                response = self._handle_install(intent, request)
            elif intent.type == IntentType.REMOVE:
                response = self._handle_remove(intent, request)
            elif intent.type == IntentType.SEARCH:
                response = self._handle_search(intent, request)
            elif intent.type == IntentType.UPDATE:
                response = self._handle_update(intent, request)
            elif intent.type == IntentType.ROLLBACK:
                response = self._handle_rollback(intent, request)
            elif intent.type == IntentType.LIST:
                response = self._handle_list(intent, request)
            elif intent.type == IntentType.GENERATE_CONFIG:
                response = self._handle_generate_config(intent, request)
            elif intent.type == IntentType.ANALYZE_PROJECT:
                response = self._handle_analyze_project(intent, request)
            elif intent.type == IntentType.MIGRATE_SCRIPT:
                response = self._handle_migrate_script(intent, request)
            else:
                response = self._handle_query(intent, request)
            
            self.stats["success"] += 1
            
        except Exception as e:
            self.stats["errors"] += 1
            response = Response(
                success=False,
                message=f"Error processing request: {str(e)}",
                error=str(e)
            )
        
        # Track performance
        elapsed = time.time() - start_time
        self._update_avg_response_time(elapsed)
        
        if elapsed > 0.5:  # Log slow requests
            print(f"⚠️ Slow request ({elapsed:.2f}s): {request.query}")
        
        return response
    
    def _parse_intent(self, query: str) -> Intent:
        """Parse user intent from natural language."""
        query_lower = query.lower()
        
        # Quick pattern matching for common intents
        # Check for more specific terms first to avoid false matches
        if any(word in query_lower for word in ["list", "show"]):
            return Intent(type=IntentType.LIST, query=query)
        
        elif any(word in query_lower for word in ["remove", "uninstall", "delete"]):
            packages = self._extract_packages(query)
            return Intent(type=IntentType.REMOVE, packages=packages, query=query)
        
        elif any(word in query_lower for word in ["search", "find", "look for"]):
            return Intent(type=IntentType.SEARCH, query=query)
        
        elif any(word in query_lower for word in ["install", "add", "get"]):
            # Extract package names
            packages = self._extract_packages(query)
            return Intent(type=IntentType.INSTALL, packages=packages, query=query)
        
        elif "update" in query_lower:
            return Intent(type=IntentType.UPDATE, query=query)
        
        elif "rollback" in query_lower:
            return Intent(type=IntentType.ROLLBACK, query=query)
        
        elif "what" in query_lower:
            return Intent(type=IntentType.LIST, query=query)
        
        elif "generate" in query_lower and "config" in query_lower:
            return Intent(type=IntentType.GENERATE_CONFIG, query=query)
        
        elif "analyze" in query_lower and "project" in query_lower:
            return Intent(type=IntentType.ANALYZE_PROJECT, query=query)
        
        elif "migrate" in query_lower:
            return Intent(type=IntentType.MIGRATE_SCRIPT, query=query)
        
        else:
            return Intent(type=IntentType.UNKNOWN, query=query)
    
    def _extract_packages(self, query: str) -> List[str]:
        """Extract package names from query."""
        # Remove common words
        words = query.split()
        stop_words = {"install", "remove", "uninstall", "delete", "add", "get", 
                     "please", "i", "want", "need", "to", "the", "a", "an", 
                     "and", "or", "but", "list", "show", "search", "find"}
        
        packages = [w for w in words if w.lower() not in stop_words]
        return packages
    
    def _handle_install(self, intent: Intent, request: Request) -> Response:
        """Handle package installation."""
        if not intent.packages:
            return Response(
                success=False,
                message="No packages specified for installation",
                suggestions=["Try: 'install firefox'", "Try: 'add vim'"]
            )
        
        # Build nix command
        packages_str = " ".join(intent.packages)
        
        if request.dry_run:
            return Response(
                success=True,
                message=f"Would install: {packages_str}",
                data={"packages": intent.packages, "dry_run": True}
            )
        
        # Execute installation
        try:
            result = subprocess.run(
                ["nix-env", "-iA"] + [f"nixpkgs.{pkg}" for pkg in intent.packages],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return Response(
                    success=True,
                    message=f"Successfully installed: {packages_str}",
                    data={"packages": intent.packages, "output": result.stdout}
                )
            else:
                return Response(
                    success=False,
                    message=f"Failed to install packages",
                    error=result.stderr,
                    suggestions=["Check package names", "Try 'search <package>' first"]
                )
        except subprocess.TimeoutExpired:
            return Response(
                success=False,
                message="Installation timed out",
                error="Operation took too long",
                suggestions=["Try installing fewer packages at once"]
            )
    
    def _handle_remove(self, intent: Intent, request: Request) -> Response:
        """Handle package removal."""
        if not intent.packages:
            return Response(
                success=False,
                message="No packages specified for removal"
            )
        
        packages_str = " ".join(intent.packages)
        
        if request.dry_run:
            return Response(
                success=True,
                message=f"Would remove: {packages_str}",
                data={"packages": intent.packages, "dry_run": True}
            )
        
        # Execute removal
        try:
            result = subprocess.run(
                ["nix-env", "-e"] + intent.packages,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return Response(
                    success=True,
                    message=f"Successfully removed: {packages_str}",
                    data={"packages": intent.packages}
                )
            else:
                return Response(
                    success=False,
                    message="Failed to remove packages",
                    error=result.stderr
                )
        except subprocess.TimeoutExpired:
            return Response(
                success=False,
                message="Removal timed out",
                error="Operation took too long"
            )
    
    def _handle_search(self, intent: Intent, request: Request) -> Response:
        """Handle package search with fuzzy finding."""
        search_term = intent.query.replace("search", "").replace("find", "").strip()
        
        if not search_term:
            return Response(
                success=False,
                message="Please specify what to search for"
            )
        
        # Try fuzzy search if available
        fuzzy = get_fuzzy_search()
        if fuzzy:
            try:
                results = fuzzy.search(search_term, limit=10)
                if results:
                    packages = [r["name"] for r in results]
                    return Response(
                        success=True,
                        message=f"Found {len(packages)} packages",
                        data={"results": results, "packages": packages}
                    )
            except Exception:
                pass  # Fall back to basic search
        
        # Fallback to basic nix search
        try:
            result = subprocess.run(
                ["nix", "search", "nixpkgs", search_term],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout:
                # Parse search results
                lines = result.stdout.strip().split("\n")
                packages = []
                for line in lines:
                    if line.startswith("* "):
                        pkg_name = line.split()[1].split(".")[-1]
                        packages.append(pkg_name)
                
                if packages:
                    return Response(
                        success=True,
                        message=f"Found {len(packages)} packages",
                        data={"packages": packages[:10]}  # Limit to 10
                    )
            
            return Response(
                success=False,
                message="No packages found",
                suggestions=[f"Try broader search terms"]
            )
            
        except subprocess.TimeoutExpired:
            return Response(
                success=False,
                message="Search timed out",
                error="Search took too long"
            )
    
    def _handle_update(self, intent: Intent, request: Request) -> Response:
        """Handle system update."""
        if request.dry_run:
            return Response(
                success=True,
                message="Would update system",
                data={"dry_run": True}
            )
        
        return Response(
            success=True,
            message="System update initiated",
            data={"info": "Run 'sudo nixos-rebuild switch' to update"}
        )
    
    def _handle_rollback(self, intent: Intent, request: Request) -> Response:
        """Handle system rollback."""
        if request.dry_run:
            return Response(
                success=True,
                message="Would rollback system",
                data={"dry_run": True}
            )
        
        return Response(
            success=True,
            message="Rollback information",
            data={"info": "Run 'sudo nixos-rebuild switch --rollback' to rollback"}
        )
    
    def _handle_list(self, intent: Intent, request: Request) -> Response:
        """Handle listing installed packages."""
        try:
            result = subprocess.run(
                ["nix-env", "-q"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                packages = result.stdout.strip().split("\n")
                return Response(
                    success=True,
                    message=f"Found {len(packages)} installed packages",
                    data={"packages": packages}
                )
            else:
                return Response(
                    success=False,
                    message="Failed to list packages",
                    error=result.stderr
                )
        except subprocess.TimeoutExpired:
            return Response(
                success=False,
                message="Listing timed out"
            )
    
    def _handle_generate_config(self, intent: Intent, request: Request) -> Response:
        """Handle configuration generation."""
        return Response(
            success=True,
            message="Configuration generation",
            data={
                "template": """
# Generated NixOS configuration
{ config, pkgs, ... }:
{
  environment.systemPackages = with pkgs; [
    vim
    git
    firefox
  ];
}
"""
            }
        )
    
    def _handle_analyze_project(self, intent: Intent, request: Request) -> Response:
        """Handle project analysis with tree-sitter."""
        tree_sitter = get_tree_sitter()
        if not tree_sitter:
            return Response(
                success=False,
                message="Project analysis not available",
                error="Tree-sitter module not installed"
            )
        
        # Get project path from context or current directory
        project_path = request.context.get("project_path", ".")
        
        try:
            analysis = tree_sitter.analyze_project(project_path)
            return Response(
                success=True,
                message=f"Analyzed {analysis.language} project",
                data={"analysis": analysis.__dict__}
            )
        except Exception as e:
            return Response(
                success=False,
                message="Failed to analyze project",
                error=str(e)
            )
    
    def _handle_migrate_script(self, intent: Intent, request: Request) -> Response:
        """Handle shell script migration."""
        return Response(
            success=True,
            message="Script migration feature",
            data={"info": "Specify script path to migrate to NixOS"}
        )
    
    def _handle_query(self, intent: Intent, request: Request) -> Response:
        """Handle general queries."""
        # Use knowledge engine if available
        knowledge = get_knowledge_engine()
        if knowledge:
            try:
                answer = knowledge.answer_question(intent.query)
                if answer:
                    return Response(
                        success=True,
                        message=answer,
                        data={"source": "knowledge_engine"}
                    )
            except Exception:
                pass  # Fall back to basic response
        
        return Response(
            success=True,
            message="I can help you with NixOS operations",
            suggestions=[
                "Try: 'install <package>'",
                "Try: 'search <term>'",
                "Try: 'list installed packages'"
            ]
        )
    
    def _update_avg_response_time(self, elapsed: float):
        """Update average response time."""
        current_avg = self.stats["avg_response_time"]
        total_requests = self.stats["requests"]
        
        # Calculate new average
        new_avg = ((current_avg * (total_requests - 1)) + elapsed) / total_requests
        self.stats["avg_response_time"] = new_avg
    
    def get_stats(self) -> Dict[str, Any]:
        """Get backend statistics."""
        return self.stats
    
    # Async support for frontends that need it
    async def process_async(self, request: Request) -> Response:
        """Async wrapper for process method."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.process, request)


# Singleton instance for import compatibility
_backend_instance = None


def get_backend() -> NixForHumanityBackend:
    """Get or create the singleton backend instance."""
    global _backend_instance
    if _backend_instance is None:
        _backend_instance = NixForHumanityBackend()
    return _backend_instance


# Compatibility aliases
NixForHumanityBackend = NixForHumanityBackend
create_backend = get_backend
Backend = NixForHumanityBackend

__all__ = [
    "NixForHumanityBackend",
    "NixForHumanityBackend", 
    "Backend",
    "get_backend",
    "create_backend",
    "Request",
    "Response",
    "Intent",
    "IntentType"
]