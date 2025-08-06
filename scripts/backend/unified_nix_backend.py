#!/usr/bin/env python3
"""
🎯 Unified Nix Backend - The Brain That Powers All Frontends
Single source of truth for all Nix operations
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum

# Add parent directories to path
script_dir = Path(__file__).parent.parent
sys.path.insert(0, str(script_dir))

# Import our components
from backend.nix_python_backend import NixPythonBackend, OperationType, OperationResult
from nix_knowledge_engine import NixOSKnowledgeEngine
from plugin_manager import PluginManager, get_plugin_manager
from feedback_collector import FeedbackCollector
from command_learning_system import CommandLearningSystem
from package_cache_manager import PackageCacheManager


class IntentType(Enum):
    """Types of user intents"""
    # System operations (use Python backend)
    REBUILD_SYSTEM = "rebuild_system"
    UPDATE_SYSTEM = "update_system"
    ROLLBACK_SYSTEM = "rollback_system"
    LIST_GENERATIONS = "list_generations"
    
    # Package operations
    INSTALL_PACKAGE = "install_package"
    SEARCH_PACKAGE = "search_package"
    REMOVE_PACKAGE = "remove_package"
    
    # Information queries (use knowledge engine)
    EXPLAIN_CONCEPT = "explain_concept"
    SHOW_EXAMPLE = "show_example"
    GET_HELP = "get_help"
    
    # Unknown
    UNKNOWN = "unknown"


@dataclass
class Intent:
    """Structured intent from user input"""
    type: IntentType
    query: str
    entities: Dict[str, Any]
    confidence: float


@dataclass
class BackendResponse:
    """Unified response format for all operations"""
    success: bool
    text: str
    intent: Intent
    commands: List[Dict[str, str]] = None
    operation_result: Optional[OperationResult] = None
    suggestions: List[str] = None
    metadata: Dict[str, Any] = None


class UnifiedNixBackend:
    """
    The single backend that powers all frontends
    This is the brain - all intelligence lives here
    """
    
    def __init__(self, progress_callback: Optional[Callable] = None):
        # Core components
        self.python_backend = NixPythonBackend(progress_callback)
        self.knowledge = NixOSKnowledgeEngine()
        self.plugin_manager = get_plugin_manager()
        
        # Supporting systems
        self.feedback = FeedbackCollector()
        self.learner = CommandLearningSystem()
        self.cache = PackageCacheManager()
        
        # Configuration
        self.collect_feedback = True
        self.use_cache = True
        
    def process_intent(self, 
                      intent: Intent, 
                      context: Dict[str, Any]) -> BackendResponse:
        """
        Main entry point - process any intent from any frontend
        
        This is where the magic happens!
        """
        
        # Check plugins first
        plugin_response = self._check_plugins(intent, context)
        if plugin_response:
            return plugin_response
        
        # Route to appropriate handler
        if intent.type in [IntentType.REBUILD_SYSTEM, IntentType.UPDATE_SYSTEM]:
            return self._handle_system_operation(intent, context)
        
        elif intent.type == IntentType.ROLLBACK_SYSTEM:
            return self._handle_rollback(intent, context)
        
        elif intent.type == IntentType.LIST_GENERATIONS:
            return self._handle_list_generations(intent, context)
        
        elif intent.type == IntentType.INSTALL_PACKAGE:
            return self._handle_install_package(intent, context)
        
        elif intent.type == IntentType.SEARCH_PACKAGE:
            return self._handle_search_package(intent, context)
        
        elif intent.type in [IntentType.EXPLAIN_CONCEPT, IntentType.SHOW_EXAMPLE, 
                            IntentType.GET_HELP]:
            return self._handle_knowledge_query(intent, context)
        
        else:
            return self._handle_unknown(intent, context)
    
    def extract_intent(self, query: str) -> Intent:
        """Extract structured intent from natural language"""
        query_lower = query.lower()
        
        # System operations
        if any(word in query_lower for word in ['rebuild', 'update', 'upgrade']):
            if 'system' in query_lower or 'nixos' in query_lower:
                return Intent(
        type=IntentType.UPDATE,
        entities={},
        confidence=0.9,
        raw_input=query
    )
        
        elif any(word in query_lower for word in ['rollback', 'previous', 'undo']):
            return Intent(
        type=IntentType.ROLLBACK_SYSTEM,
        entities={},
        confidence=0.8,
        raw_input=query
    )
        
        elif 'generation' in query_lower and any(word in query_lower for word in ['list', 'show']):
            return Intent(
        type=IntentType.LIST_GENERATIONS,
        entities={},
        confidence=0.9,
        raw_input=query
    )
        
        # Package operations
        elif any(word in query_lower for word in ['install', 'get', 'add']):
            # Try to extract package name
            package = self._extract_package_name(query)
            return Intent(
        type=IntentType.INSTALL,
        entities={'package': package},
        confidence=0.85 if package else 0.5,
        raw_input=query
    )
        
        elif any(word in query_lower for word in ['search', 'find', 'look for']):
            search_term = self._extract_search_term(query)
            return Intent(
        type=IntentType.SEARCH,
        entities={'search_term': search_term},
        confidence=0.8,
        raw_input=query
    )
        
        # Knowledge queries
        elif any(word in query_lower for word in ['what', 'how', 'why', 'explain']):
            return Intent(
        type=IntentType.EXPLAIN_CONCEPT,
        entities={},
        confidence=0.7,
        raw_input=query
    )
        
        # Fallback to knowledge engine's intent extraction
        legacy_intent = self.knowledge.extract_intent(query)
        return self._convert_legacy_intent(legacy_intent, query)
    
    def _handle_system_operation(self, 
                               intent: Intent, 
                               context: Dict[str, Any]) -> BackendResponse:
        """Handle system rebuild/update operations"""
        
        # Determine operation type
        operation = OperationType.SWITCH
        if context.get('dry_run'):
            operation = OperationType.DRY_BUILD
        elif context.get('test_only'):
            operation = OperationType.TEST
        
        # Use Python backend for speed!
        result = self.python_backend.rebuild_system(operation)
        
        if result.success:
            text = self._format_success_message(result, context)
            commands = [{
                'description': f'Rebuild system ({operation.value})',
                'command': f'nixos-rebuild {operation.value}',
                'executed': True
            }]
        else:
            text = self._format_error_message(result, context)
            commands = []
        
        # Learn from this
        if self.learner:
            self.learner.record_command(
                intent=intent.type.value,
                query=intent.query,
                command=f'nixos-rebuild {operation.value}'
            )
        
        return BackendResponse(
            success=result.success,
            text=text,
            intent=intent,
            commands=commands,
            operation_result=result,
            suggestions=self._get_suggestions(result)
        )
    
    def _handle_rollback(self, 
                        intent: Intent, 
                        context: Dict[str, Any]) -> BackendResponse:
        """Handle system rollback"""
        
        generation = intent.entities.get('generation')
        result = self.python_backend.rollback(generation)
        
        if result.success:
            text = f"✅ {result.message}"
            if generation:
                text += f"\n\nYour system is now at generation {generation}."
            else:
                text += "\n\nYour system has been rolled back to the previous generation."
        else:
            text = f"❌ {result.message}"
        
        return BackendResponse(
            success=result.success,
            text=text,
            intent=intent,
            operation_result=result
        )
    
    def _handle_list_generations(self, 
                                intent: Intent, 
                                context: Dict[str, Any]) -> BackendResponse:
        """List system generations"""
        
        result = self.python_backend.list_generations()
        
        if result.success:
            generations = result.details['generations']
            text = "📋 System Generations:\n\n"
            
            for gen in generations[-10:]:  # Show last 10
                marker = " ← current" if gen['current'] else ""
                text += f"  {gen['number']:3d} - {gen['date']}{marker}\n"
            
            if len(generations) > 10:
                text += f"\n(Showing last 10 of {len(generations)} generations)"
        else:
            text = f"❌ {result.message}"
        
        return BackendResponse(
            success=result.success,
            text=text,
            intent=intent,
            operation_result=result
        )
    
    def _handle_install_package(self, 
                              intent: Intent, 
                              context: Dict[str, Any]) -> BackendResponse:
        """Handle package installation"""
        
        package = intent.entities.get('package')
        if not package:
            return BackendResponse(
                success=False,
                text="❓ I couldn't identify which package you want to install. Please specify the package name.",
                intent=intent
            )
        
        # Check cache first
        if self.use_cache:
            cached = self.cache.get_cached_search(package)
            if cached and cached['exact_match']:
                package = cached['packages'][0]['attribute']
        
        # Use Python backend to install
        result = self.python_backend.install_package(package)
        
        if result.success:
            text = f"✅ {result.message}\n\nThe package is now available in your user profile."
            commands = [{
                'description': f'Install {package}',
                'command': f'nix profile install nixpkgs#{package}',
                'executed': True
            }]
        else:
            # Provide helpful alternatives
            text = self._format_package_error(package, result, context)
            commands = []
        
        return BackendResponse(
            success=result.success,
            text=text,
            intent=intent,
            commands=commands,
            operation_result=result
        )
    
    def _handle_search_package(self, 
                             intent: Intent, 
                             context: Dict[str, Any]) -> BackendResponse:
        """Handle package search"""
        
        search_term = intent.entities.get('search_term', intent.query)
        
        # Use cache for speed
        if self.use_cache:
            cached = self.cache.get_cached_search(search_term)
            if cached:
                packages = cached['packages'][:5]
            else:
                packages = self.python_backend.search_packages(search_term)
                if packages:
                    self.cache.cache_search_results(search_term, packages, False)
        else:
            packages = self.python_backend.search_packages(search_term)
        
        if packages:
            text = f"🔍 Found {len(packages)} packages matching '{search_term}':\n\n"
            for pkg in packages[:5]:
                text += f"• **{pkg['name']}** ({pkg['version']})\n"
                text += f"  {pkg['description'][:60]}...\n\n"
        else:
            text = f"❌ No packages found matching '{search_term}'"
        
        return BackendResponse(
            success=bool(packages),
            text=text,
            intent=intent,
            metadata={'packages': packages}
        )
    
    def _handle_knowledge_query(self, 
                              intent: Intent, 
                              context: Dict[str, Any]) -> BackendResponse:
        """Handle knowledge/help queries using knowledge engine"""
        
        # Convert to legacy format for knowledge engine
        legacy_intent = {
            'action': intent.type.value,
            'query': intent.query
        }
        
        solution = self.knowledge.get_solution(legacy_intent)
        
        if solution.get('found'):
            text = self.knowledge.format_response(legacy_intent, solution)
            
            # Extract commands if present
            commands = []
            if solution.get('methods'):
                for method in solution['methods']:
                    commands.append({
                        'description': method['name'],
                        'command': method['command'],
                        'example': method.get('example', '')
                    })
        else:
            text = solution.get('suggestion', "I don't have information about that yet.")
        
        return BackendResponse(
            success=solution.get('found', False),
            text=text,
            intent=intent,
            commands=commands
        )
    
    def _handle_unknown(self, 
                       intent: Intent, 
                       context: Dict[str, Any]) -> BackendResponse:
        """Handle unknown intents"""
        
        suggestions = [
            "install <package> - Install a package",
            "update system - Update NixOS",
            "rollback - Go to previous generation",
            "search <term> - Search for packages",
            "help - Get general help"
        ]
        
        text = (f"I'm not sure what you want to do. Here are some things I can help with:\n\n"
                + "\n".join(f"• {s}" for s in suggestions))
        
        return BackendResponse(
            success=False,
            text=text,
            intent=intent,
            suggestions=suggestions
        )
    
    def _check_plugins(self, 
                      intent: Intent, 
                      context: Dict[str, Any]) -> Optional[BackendResponse]:
        """Check if any plugin can handle this intent"""
        
        for plugin in self.plugin_manager.get_active_plugins():
            if plugin.can_handle(intent.query):
                try:
                    result = plugin.handle(intent.query, context)
                    return BackendResponse(
                        success=True,
                        text=result.get('response', ''),
                        intent=intent,
                        commands=result.get('commands', []),
                        metadata={'plugin': plugin.name}
                    )
                except Exception as e:
                    print(f"Plugin {plugin.name} error: {e}")
        
        return None
    
    def _extract_package_name(self, query: str) -> Optional[str]:
        """Extract package name from query"""
        query_lower = query.lower()
        
        # Remove common words
        stopwords = ['install', 'get', 'add', 'please', 'can', 'you', 'i', 
                    'want', 'need', 'the', 'a', 'an', 'package', 'program']
        
        words = query_lower.split()
        for word in words:
            if word not in stopwords and len(word) > 2:
                return word
        
        return None
    
    def _extract_search_term(self, query: str) -> str:
        """Extract search term from query"""
        query_lower = query.lower()
        
        # Try to find what comes after search/find/look for
        for phrase in ['search for', 'find', 'look for']:
            if phrase in query_lower:
                parts = query_lower.split(phrase)
                if len(parts) > 1:
                    return parts[1].strip()
        
        # Fallback to removing common words
        stopwords = ['search', 'find', 'look', 'for', 'please', 'can', 'you']
        words = query_lower.split()
        terms = [w for w in words if w not in stopwords]
        
        return ' '.join(terms) if terms else query
    
    def _convert_legacy_intent(self, legacy_intent: Dict, query: str) -> Intent:
        """Convert legacy knowledge engine intent to new format"""
        
        action_map = {
            'install_package': IntentType.INSTALL_PACKAGE,
            'search_package': IntentType.SEARCH_PACKAGE,
            'update_system': IntentType.UPDATE_SYSTEM,
            'rollback_system': IntentType.ROLLBACK_SYSTEM,
            'unknown': IntentType.UNKNOWN
        }
        
        intent_type = action_map.get(legacy_intent.get('action'), IntentType.UNKNOWN)
        
        return Intent(
        type=intent_type,
        entities={
                'package': legacy_intent.get('package',
        confidence=1.0,
        raw_input=query
    ),
                'original_action': legacy_intent.get('action')
            },
            confidence=0.6  # Lower confidence for legacy conversion
        )
    
    def _format_success_message(self, 
                              result: OperationResult, 
                              context: Dict[str, Any]) -> str:
        """Format success message based on personality"""
        
        personality = context.get('personality', 'friendly')
        
        if personality == 'minimal':
            return f"✓ {result.message}"
        
        elif personality == 'friendly':
            return (f"✅ {result.message}\n\n"
                   f"Completed in {result.duration:.1f} seconds. "
                   "Your system has been successfully updated!")
        
        elif personality == 'encouraging':
            return (f"🎉 {result.message}\n\n"
                   f"Great job keeping your system updated! "
                   f"Completed in just {result.duration:.1f} seconds.")
        
        elif personality == 'technical':
            details = result.details or {}
            return (f"✅ {result.message}\n\n"
                   f"Duration: {result.duration:.3f}s\n"
                   f"API Used: {details.get('api_used', False)}\n"
                   f"Profile: {details.get('profile', 'system')}")
        
        else:
            return f"✅ {result.message}"
    
    def _format_error_message(self, 
                            result: OperationResult, 
                            context: Dict[str, Any]) -> str:
        """Format error message helpfully"""
        
        base_msg = f"❌ {result.message}"
        
        # Add helpful suggestions based on error
        if result.error:
            if 'permission' in result.error.lower():
                base_msg += "\n\n💡 Try running with sudo"
            elif 'network' in result.error.lower():
                base_msg += "\n\n💡 Check your internet connection"
            elif 'disk space' in result.error.lower():
                base_msg += "\n\n💡 Free up some disk space with: nix-collect-garbage -d"
        
        return base_msg
    
    def _format_package_error(self, 
                            package: str, 
                            result: OperationResult, 
                            context: Dict[str, Any]) -> str:
        """Format package installation error with alternatives"""
        
        text = f"❌ {result.message}\n\n"
        
        # Try to search for similar packages
        similar = self.python_backend.search_packages(package)
        if similar:
            text += "💡 Did you mean one of these?\n\n"
            for pkg in similar[:3]:
                text += f"• {pkg['name']} - {pkg['description'][:50]}...\n"
        
        # Add installation methods
        text += f"\n📚 For system-wide installation, add to /etc/nixos/configuration.nix:\n"
        text += f"```\nenvironment.systemPackages = with pkgs; [ {package} ];\n```"
        
        return text
    
    def _get_suggestions(self, result: OperationResult) -> List[str]:
        """Get relevant suggestions based on operation result"""
        
        suggestions = []
        
        if result.success and result.operation == OperationType.SWITCH:
            suggestions.extend([
                "list generations - See all system generations",
                "rollback - Go back if something broke"
            ])
        elif not result.success:
            suggestions.extend([
                "Check the logs for more details",
                "Try with --dry-run first",
                "Ask for help with the specific error"
            ])
        
        return suggestions


def test_unified_backend():
    """Test the unified backend"""
    print("🎯 Unified Nix Backend Test")
    print("=" * 60)
    
    backend = UnifiedNixBackend()
    
    # Test queries
    test_queries = [
        "install firefox",
        "update my system",
        "what's a generation?",
        "search for text editors",
        "rollback to previous",
        "list generations"
    ]
    
    for query in test_queries:
        print(f"\n❓ Query: {query}")
        print("-" * 40)
        
        # Extract intent
        intent = backend.extract_intent(query)
        print(f"🎯 Intent: {intent.type.value} (confidence: {intent.confidence:.2f})")
        
        # Process with context
        context = {
            'personality': 'friendly',
            'frontend': 'cli',
            'collect_feedback': False
        }
        
        response = backend.process_intent(intent, context)
        print(f"✅ Success: {response.success}")
        print(f"💬 Response: {response.text[:150]}...")
        
        if response.commands:
            print(f"📦 Commands: {len(response.commands)}")


if __name__ == "__main__":
    test_unified_backend()