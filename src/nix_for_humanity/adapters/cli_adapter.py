# CLI Adapter
"""
Adapter for the ask-nix CLI to use the headless core
"""

import sys
import os
import uuid
from typing import Optional
from pathlib import Path

# Import core components
from ..core import (
    NixForHumanityCore,
    Query,
    Response,
    ExecutionMode,
    PersonalityStyle
)


class CLIAdapter:
    """Adapts the headless core for CLI usage"""
    
    def __init__(self):
        # Initialize core with CLI-specific config
        config = {
            'dry_run': False,  # CLI defaults to execution
            'default_personality': 'friendly',
            'enable_learning': True,
            'collect_feedback': True
        }
        
        self.core = NixForHumanityCore(config)
        self.session_id = str(uuid.uuid4())[:8]
        
        # CLI-specific settings
        self.show_progress = True
        self.visual_mode = self._check_rich_available()
        
    def _check_rich_available(self) -> bool:
        """Check if Rich is available for better visuals"""
        try:
            import rich
            return True
        except ImportError:
            return False
            
    def process_query(self, 
                     query_text: str,
                     personality: Optional[str] = None,
                     dry_run: bool = False,
                     execute: bool = True,
                     show_intent: bool = False) -> Response:
        """Process a query from the CLI"""
        
        # Determine execution mode
        if dry_run:
            mode = ExecutionMode.DRY_RUN
        elif execute:
            mode = ExecutionMode.EXECUTE
        else:
            mode = ExecutionMode.EXPLAIN
            
        # Create query object
        query = Query(
            text=query_text,
            personality=personality or 'friendly',
            mode=mode,
            session_id=self.session_id,
            user_id=self._get_user_id()
        )
        
        # Show intent if requested
        if show_intent:
            # Quick intent check
            intent = self.core.intent_engine.recognize(query_text)
            print(f"\n🎯 Intent detected: {intent.type.value}")
            if intent.target:
                print(f"📦 Target: {intent.target}")
            print()
            
        # Process through core
        response = self.core.process(query)
        
        return response
        
    def _get_user_id(self) -> str:
        """Get a stable user ID for learning"""
        # Use username as simple ID
        return os.environ.get('USER', 'anonymous')
        
    def display_response(self, response: Response):
        """Display response in CLI format"""
        
        if self.visual_mode:
            self._display_rich(response)
        else:
            self._display_simple(response)
            
    def _display_simple(self, response: Response):
        """Simple text display"""
        print(response.text)
        
        if response.suggestions:
            print("\n💡 Suggestions:")
            for suggestion in response.suggestions:
                print(f"   • {suggestion}")
                
        if response.feedback_requested:
            self._gather_feedback(response)
            
    def _display_rich(self, response: Response):
        """Rich display with colors and formatting"""
        try:
            from rich.console import Console
            from rich.panel import Panel
            from rich.markdown import Markdown
            
            console = Console()
            
            # Main response in a panel
            console.print(Panel(
                Markdown(response.text),
                title="Response",
                border_style="cyan"
            ))
            
            # Suggestions if any
            if response.suggestions:
                console.print("\n[bold yellow]💡 Suggestions:[/bold yellow]")
                for suggestion in response.suggestions:
                    console.print(f"   [dim]•[/dim] {suggestion}")
                    
            # Feedback request
            if response.feedback_requested:
                console.print()
                self._gather_feedback(response)
                
        except ImportError:
            # Fallback to simple display
            self._display_simple(response)
            
    def _gather_feedback(self, response: Response):
        """Gather user feedback"""
        try:
            print("\n" + "=" * 50)
            helpful = input("Was this helpful? (y/n/skip): ").lower().strip()
            
            if helpful in ['y', 'yes']:
                # Record positive feedback
                # This would call back to the core's learning system
                print("Great! Thank you for the feedback.")
            elif helpful in ['n', 'no']:
                # Ask for improvement
                print("\nI'd love to learn how to help better!")
                better = input("What would have been better? (or press Enter to skip): ").strip()
                if better:
                    print("Thank you! I'll use this to improve.")
                    
        except KeyboardInterrupt:
            pass
            
    def set_personality(self, style: str):
        """Set the personality style"""
        try:
            self.core.personality_system.set_style(PersonalityStyle(style))
        except ValueError:
            print(f"Unknown personality style: {style}")
            
    def get_stats(self):
        """Get and display system statistics"""
        stats = self.core.get_system_stats()
        
        print("\n📊 System Statistics")
        print("=" * 50)
        
        for key, value in stats.items():
            if isinstance(value, dict):
                print(f"\n{key}:")
                for sub_key, sub_value in value.items():
                    print(f"  {sub_key}: {sub_value}")
            else:
                print(f"{key}: {value}")