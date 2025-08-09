#!/usr/bin/env python3
"""
from typing import List, Optional
Natural Language Executor - Bridges NLP with NixOS Python Backend
Integrates the hybrid NLP system with direct nixos-rebuild-ng API
"""

import asyncio
import sys
import os
from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import dataclass
import logging

# Add scripts directory for knowledge engine
script_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../scripts'))
sys.path.insert(0, script_dir)

# Import our modules
from nix_knowledge_engine import NixOSKnowledgeEngine
from nixos_backend import NixOSBackend, NixOSOperationHandler, OperationType

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ExecutionRequest:
    """Request for natural language execution"""
    query: str
    personality: str = 'friendly'
    dry_run: bool = True
    verbose: bool = False


@dataclass 
class ExecutionResponse:
    """Response from execution"""
    success: bool
    message: str
    details: Optional[Dict] = None
    suggestions: Optional[List[str]] = None
    personality_response: Optional[str] = None


class NaturalLanguageExecutor:
    """
    Bridges natural language understanding with NixOS Python backend.
    
    This class combines:
    1. NLP understanding from the knowledge engine
    2. Direct NixOS operations via Python API
    3. Personality-aware responses
    4. Real execution (not just information)
    """
    
    def __init__(self):
        self.knowledge = NixOSKnowledgeEngine()
        self.backend = NixOSOperationHandler()
        self.personality = 'friendly'
        
    async def execute_query(self, request: ExecutionRequest) -> ExecutionResponse:
        """
        Execute a natural language query with real NixOS operations.
        
        This is the main entry point that:
        1. Validates and sanitizes user input for security
        2. Understands the intent
        3. Maps to NixOS operations  
        4. Executes via Python API
        5. Returns friendly response
        """
        # SECURITY: Validate and sanitize all user input first
        if not isinstance(request.query, str):
            return ExecutionResponse(
                success=False,
                message="Invalid input type",
                suggestions=["Please provide text input"]
            )
        
        # SECURITY: Length and safety checks
        if len(request.query) > 1000:
            return ExecutionResponse(
                success=False,
                message="Input too long",
                suggestions=["Please keep queries under 1000 characters"]
            )
        
        # SECURITY: Check for dangerous patterns before processing
        dangerous_patterns = [
            r'[;&|`$]',           # Shell metacharacters
            r'\$\{.*\}',          # Variable expansion
            r'\$\(.*\)',          # Command substitution
            r'`.*`',              # Backticks
            r'\.\.\/',            # Path traversal
            r'<[^>]+>',           # HTML/Script tags
        ]
        
        import re
        for pattern in dangerous_patterns:
            if re.search(pattern, request.query):
                return ExecutionResponse(
                    success=False,
                    message="Unsafe characters detected in input",
                    suggestions=["Please rephrase your request without special characters"]
                )
        
        logger.info(f"Executing query: {request.query}")
        
        # Step 1: Extract intent
        intent_data = self.knowledge.extract_intent(request.query)
        action = intent_data.get('action', 'unknown')
        
        # Step 2: Route to appropriate handler
        if action == 'install_package':
            return await self._handle_install(intent_data, request)
        elif action == 'update_system':
            return await self._handle_update(request)
        elif action == 'rollback_system':
            return await self._handle_rollback(request)
        elif action == 'search_package':
            return await self._handle_search(intent_data, request)
        else:
            # Get knowledge-based response
            solution = self.knowledge.get_solution(intent_data)
            response = self.knowledge.format_response(intent_data, solution)
            
            return ExecutionResponse(
                success=True,
                message=response,
                personality_response=self._add_personality(response, request.personality)
            )
    
    async def _handle_install(self, intent: Dict, request: ExecutionRequest) -> ExecutionResponse:
        """Handle package installation with real execution"""
        package = intent.get('package')
        
        if not package:
            return ExecutionResponse(
                success=False,
                message="I couldn't identify which package you want to install",
                suggestions=["Try: 'install firefox'", "Or: 'I need a text editor'"]
            )
        
        # Get installation methods from knowledge base
        solution = self.knowledge.get_solution(intent)
        
        if request.dry_run:
            # Dry run - just show what would happen
            message = f"Would install {package} using your preferred method"
            if solution.get('found'):
                methods = solution.get('methods', [])
                if methods:
                    message += f"\n\nAvailable methods:\n"
                    for method in methods[:2]:  # Show top 2 methods
                        message += f"- {method['name']}: {method['command']}\n"
            
            return ExecutionResponse(
                success=True,
                message=message,
                details={'package': package, 'dry_run': True},
                personality_response=self._add_personality(message, request.personality)
            )
        else:
            # Real installation via backend
            logger.info(f"Attempting real installation of {package}")
            
            try:
                # Import our command executor
                from command_executor import CommandExecutor, ExecutionMode
                
                # Create executor in live mode
                executor = CommandExecutor(ExecutionMode.LIVE)
                
                # Execute the installation
                result = executor.execute_command('install', package)
                
                if result['success']:
                    message = f"Successfully installed {package}!"
                    details = {
                        'package': package,
                        'dry_run': False,
                        'command': result.get('command'),
                        'output': result.get('output')
                    }
                    personality_msg = self._add_personality(
                        f"Great! {package} is now installed and ready to use.",
                        request.personality
                    )
                else:
                    message = f"Failed to install {package}: {result.get('error', 'Unknown error')}"
                    details = {
                        'package': package,
                        'dry_run': False,
                        'error': result.get('error'),
                        'command': result.get('command')
                    }
                    personality_msg = self._add_personality(
                        f"I had trouble installing {package}. {result.get('error', '')}",
                        request.personality
                    )
                    
                return ExecutionResponse(
                    success=result['success'],
                    message=message,
                    details=details,
                    personality_response=personality_msg,
                    suggestions=result.get('suggestions', [])
                )
                
            except Exception as e:
                logger.error(f"Error during installation: {e}")
                return ExecutionResponse(
                    success=False,
                    message=f"Error installing {package}: {str(e)}",
                    details={'package': package, 'error': str(e)},
                    suggestions=["Try running with --dry-run first", "Check if the package name is correct"],
                    personality_response=self._add_personality(
                        f"I encountered an error trying to install {package}. Let me know if you'd like me to try something else.",
                        request.personality
                    )
                )
    
    async def _handle_update(self, request: ExecutionRequest) -> ExecutionResponse:
        """Handle system update"""
        if request.dry_run:
            message = "Would update your NixOS system (channel update + rebuild switch)"
            details = {
                'operations': [
                    'nix-channel --update',
                    'nixos-rebuild switch'
                ],
                'dry_run': True
            }
        else:
            # Use the backend for real execution
            result = await self.backend.handle_intent('system.update', {})
            
            if result['success']:
                message = result['message']
                details = result
            else:
                message = "System update failed"
                details = {'error': result.get('error')}
        
        return ExecutionResponse(
            success=True,
            message=message,
            details=details,
            personality_response=self._add_personality(message, request.personality)
        )
    
    async def _handle_rollback(self, request: ExecutionRequest) -> ExecutionResponse:
        """Handle system rollback"""
        if request.dry_run:
            # Get generations to show what we'd roll back to
            generations = await self.backend.backend.list_generations()
            current_gen = next((g for g in generations if g.get('current')), None)
            
            if current_gen and len(generations) > 1:
                previous = generations[1] if generations[0].get('current') else generations[0]
                message = f"Would rollback from generation {current_gen['number']} to {previous['number']}"
            else:
                message = "Would rollback to previous generation"
                
            return ExecutionResponse(
                success=True,
                message=message,
                details={'dry_run': True, 'generations': generations[:3]},
                personality_response=self._add_personality(message, request.personality)
            )
        else:
            # Real rollback via backend
            result = await self.backend.handle_intent('system.rollback', {})
            return ExecutionResponse(
                success=result['success'],
                message=result['message'],
                details=result,
                personality_response=self._add_personality(result['message'], request.personality)
            )
    
    async def _handle_search(self, intent: Dict, request: ExecutionRequest) -> ExecutionResponse:
        """Handle package search"""
        query = intent.get('query', '')
        search_term = self._extract_search_term(query)
        
        message = f"To search for packages, use:\n"
        message += f"`nix search nixpkgs {search_term}`\n"
        message += f"Or visit https://search.nixos.org"
        
        return ExecutionResponse(
            success=True,
            message=message,
            suggestions=[
                f"nix search nixpkgs {search_term}",
                "Visit search.nixos.org for web interface"
            ],
            personality_response=self._add_personality(message, request.personality)
        )
    
    def _extract_search_term(self, query: str) -> str:
        """Extract search term from query"""
        # Remove common words
        stop_words = {'search', 'find', 'look', 'for', 'is', 'there', 'a', 'an', 'the'}
        words = query.lower().split()
        search_words = [w for w in words if w not in stop_words]
        return ' '.join(search_words) if search_words else 'package'
    
    def _add_personality(self, message: str, personality: str) -> str:
        """Add personality to response"""
        if personality == 'minimal':
            return message
        elif personality == 'friendly':
            return f"Hi there! {message}\n\nLet me know if you need any help! 😊"
        elif personality == 'encouraging':
            return f"Great question! {message}\n\nYou're doing awesome with NixOS! 🌟"
        elif personality == 'technical':
            return f"{message}\n\nNote: This follows NixOS's declarative paradigm."
        else:
            return message


class InteractiveExecutor:
    """Interactive command-line interface for the executor"""
    
    def __init__(self):
        self.executor = NaturalLanguageExecutor()
        self.dry_run = True
        self.personality = 'friendly'
    
    async def run(self):
        """Run interactive session"""
        print("🚀 Nix for Humanity - Natural Language Executor")
        print("=" * 50)
        print("Type 'help' for commands, 'quit' to exit")
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'} | Personality: {self.personality}")
        print("=" * 50)
        
        while True:
            try:
                query = input("\n❓ What would you like to do? ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye! We flow together! 🌊")
                    break
                
                if query.lower() == 'help':
                    self.show_help()
                    continue
                
                if query.lower().startswith('mode'):
                    self.toggle_mode()
                    continue
                
                if query.lower().startswith('personality'):
                    self.set_personality(query)
                    continue
                
                if not query:
                    continue
                
                # Execute the query
                request = ExecutionRequest(
                    query=query,
                    personality=self.personality,
                    dry_run=self.dry_run,
                    verbose=True
                )
                
                response = await self.executor.execute_query(request)
                
                # Display response
                print("\n" + "=" * 50)
                if response.personality_response:
                    print(f"💬 {response.personality_response}")
                else:
                    print(f"💬 {response.message}")
                
                if response.details and response.details.get('dry_run'):
                    print("\n⚠️  DRY RUN - No changes were made")
                
                if response.suggestions:
                    print("\n💡 Suggestions:")
                    for suggestion in response.suggestions:
                        print(f"   • {suggestion}")
                
                print("=" * 50)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
    
    def show_help(self):
        """Show help message"""
        print("""
📖 Available Commands:
━━━━━━━━━━━━━━━━━━━━
Natural Language:
  • "install firefox"           - Install a package
  • "update my system"          - Update NixOS
  • "rollback"                  - Rollback to previous generation
  • "search for editors"        - Search for packages

Control Commands:
  • mode                        - Toggle between DRY RUN and LIVE
  • personality [style]         - Set personality (minimal/friendly/encouraging/technical)
  • help                        - Show this help
  • quit                        - Exit

Examples:
  • "I need a web browser"
  • "My WiFi isn't working"
  • "Update everything"
  • "What text editors are available?"
""")
    
    def toggle_mode(self):
        """Toggle between dry run and live mode"""
        self.dry_run = not self.dry_run
        mode = 'DRY RUN' if self.dry_run else 'LIVE'
        print(f"\n🔄 Mode changed to: {mode}")
        if not self.dry_run:
            print("⚠️  WARNING: Commands will now execute for real!")
    
    def set_personality(self, command: str):
        """Set personality style"""
        parts = command.split()
        if len(parts) > 1:
            style = parts[1].lower()
            if style in ['minimal', 'friendly', 'encouraging', 'technical']:
                self.personality = style
                print(f"\n🎭 Personality set to: {style}")
            else:
                print(f"\n❌ Unknown personality: {style}")
                print("   Available: minimal, friendly, encouraging, technical")


async def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        # Command-line mode
        query = ' '.join(sys.argv[1:])
        request = ExecutionRequest(query=query)
        executor = NaturalLanguageExecutor()
        response = await executor.execute_query(request)
        
        if response.personality_response:
            print(response.personality_response)
        else:
            print(response.message)
    else:
        # Interactive mode
        interactive = InteractiveExecutor()
        await interactive.run()


if __name__ == "__main__":
    asyncio.run(main())