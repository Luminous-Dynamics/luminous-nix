"""
Example of adaptive UI complexity in action

This demonstrates how the TUI adapts based on user mastery level,
implementing the Three-Stage Evolution pattern.
"""

from backend.ui.adaptive_complexity import (
    AdaptiveComplexityManager, ComplexityStage
)
from nix_humanity.core.personality import PersonalityManager, PersonalityStyle
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich import box
import time


def demonstrate_sanctuary_mode():
    """Show Sanctuary mode - protective simplicity"""
    console = Console()
    
    console.print("\n[bold blue]🛡️ SANCTUARY MODE - New User Experience[/bold blue]\n")
    
    # Simple, guided interface
    panel = Panel(
        "[green]Welcome to Nix for Humanity![/green]\n\n"
        "I'll guide you through everything step by step.\n"
        "Don't worry about making mistakes - I'm here to help!\n\n"
        "[yellow]What would you like to do?[/yellow]\n"
        "1. Install software\n"
        "2. Update system\n"
        "3. Get help\n"
        "4. Learn more\n"
        "5. Exit",
        title="Main Menu",
        box=box.ROUNDED,
        padding=(1, 2)
    )
    console.print(panel)
    
    # Show limited options with clear guidance
    console.print("\n[dim]Type a number (1-5) and press Enter[/dim]")
    console.print("[dim]Everything is safe - I'll confirm before making changes[/dim]")
    

def demonstrate_gymnasium_mode():
    """Show Gymnasium mode - learning and exploration"""
    console = Console()
    
    console.print("\n[bold yellow]🎯 GYMNASIUM MODE - Building Mastery[/bold yellow]\n")
    
    # More options, keyboard shortcuts visible
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main"),
        Layout(name="footer", size=3)
    )
    
    # Header
    layout["header"].update(
        Panel("[bold]Nix for Humanity - Gymnasium Mode[/bold]", 
              box=box.MINIMAL)
    )
    
    # Main content with more options
    main_table = Table(show_header=False, box=None, padding=(0, 1))
    main_table.add_column("Key", style="cyan")
    main_table.add_column("Action")
    main_table.add_column("Description", style="dim")
    
    main_table.add_row("i", "Install", "Install packages or applications")
    main_table.add_row("u", "Update", "Update system or packages")
    main_table.add_row("s", "Search", "Search for packages")
    main_table.add_row("r", "Remove", "Remove packages")
    main_table.add_row("g", "Generations", "Manage system generations")
    main_table.add_row("c", "Config", "Edit configuration")
    main_table.add_row("n", "Network", "Network management")
    main_table.add_row("?", "Help", "Context-sensitive help")
    main_table.add_row(":", "Command", "Direct command mode")
    main_table.add_row("q", "Quit", "Exit application")
    
    layout["main"].update(Panel(main_table, title="Quick Actions", box=box.DOUBLE))
    
    # Footer with stats
    layout["footer"].update(
        "[dim]Commands: 47 | Success: 92% | Stage Progress: 64%[/dim]"
    )
    
    console.print(layout)
    

def demonstrate_open_sky_mode():
    """Show Open Sky mode - invisible excellence"""
    console = Console()
    
    console.print("\n[bold white]☁️ OPEN SKY MODE - Invisible Excellence[/bold white]\n")
    
    # Minimal interface, maximum power
    console.print("[dim]>_[/dim]", end="")
    time.sleep(0.5)
    console.print(" install firefox", style="white")
    time.sleep(0.3)
    console.print("[dim]↵[/dim]")
    time.sleep(0.2)
    console.print("[dim]✓[/dim]", style="green")
    
    console.print("\n[dim]The interface has disappeared. Only intention remains.[/dim]")
    console.print("[dim]Predictive assistance active. Natural rhythm detected.[/dim]")
    

def show_progression():
    """Demonstrate progression through stages"""
    console = Console()
    manager = AdaptiveComplexityManager()
    
    # Simulate user progression
    user_id = "demo_user"
    
    console.print("\n[bold magenta]User Progression Journey[/bold magenta]\n")
    
    # Show initial state
    mastery = manager.get_user_mastery(user_id)
    progress = manager.get_progression_feedback(user_id)
    
    table = Table(title="Current Progress", box=box.SIMPLE)
    table.add_column("Metric", style="cyan")
    table.add_column("Current", justify="right")
    table.add_column("Required", justify="right")
    table.add_column("Progress", justify="right")
    
    for metric, data in progress['progress_metrics'].items():
        table.add_row(
            metric.title(),
            f"{data['current']:.2f}",
            f"{data['required']:.2f}",
            f"{data['percentage']:.0f}%"
        )
        
    console.print(table)
    
    # Simulate successful interactions
    console.print("\n[yellow]Simulating user interactions...[/yellow]")
    for i in range(25):
        manager.update_mastery(user_id, command_success=(i % 5 != 0))
        
    # Show updated progress
    progress = manager.get_progression_feedback(user_id)
    if progress.get('ready_to_advance'):
        console.print("\n[bold green]🎉 Ready to advance to the next stage![/bold green]")
        

def show_personality_integration():
    """Show how personality adapts with complexity"""
    console = Console()
    pm = PersonalityManager()
    cm = AdaptiveComplexityManager()
    
    console.print("\n[bold cyan]Personality + Complexity Integration[/bold cyan]\n")
    
    # Different personality recommendations per stage
    stage_personalities = {
        ComplexityStage.SANCTUARY: [
            PersonalityStyle.ENCOURAGING,
            PersonalityStyle.TEACHER,
            PersonalityStyle.COMPANION
        ],
        ComplexityStage.GYMNASIUM: [
            PersonalityStyle.FRIENDLY,
            PersonalityStyle.PROFESSIONAL,
            PersonalityStyle.PLAYFUL
        ],
        ComplexityStage.OPEN_SKY: [
            PersonalityStyle.MINIMAL,
            PersonalityStyle.ZEN,
            PersonalityStyle.HACKER
        ]
    }
    
    for stage, personalities in stage_personalities.items():
        console.print(f"\n[yellow]{cm.get_stage_description(stage)}[/yellow]")
        console.print("Recommended personalities:")
        
        for personality in personalities:
            pm.set_style(personality)
            desc = pm.get_style_description()
            response = pm.get_response('greeting')
            console.print(f"  • {desc}")
            console.print(f"    Example: [dim]{response}[/dim]")
            

def main():
    """Run all demonstrations"""
    console = Console()
    
    console.print("[bold magenta]Adaptive UI Complexity Demonstration[/bold magenta]")
    console.print("=" * 50)
    
    # Show each stage
    demonstrate_sanctuary_mode()
    input("\nPress Enter to see Gymnasium mode...")
    
    demonstrate_gymnasium_mode()
    input("\nPress Enter to see Open Sky mode...")
    
    demonstrate_open_sky_mode()
    input("\nPress Enter to see progression system...")
    
    show_progression()
    input("\nPress Enter to see personality integration...")
    
    show_personality_integration()
    
    console.print("\n[bold green]✨ The interface evolves with the user's consciousness ✨[/bold green]")


if __name__ == "__main__":
    main()