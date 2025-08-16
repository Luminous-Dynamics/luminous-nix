#!/usr/bin/env python3
"""
Test and demonstrate environmental awareness features.
"""

import asyncio
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from datetime import datetime

# Add src to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from luminous_nix.environmental import (
    get_system_monitor,
    PredictiveAssistant,
    ContextAwareIntentRecognizer
)
from luminous_nix.service_with_awareness import AwareNixService

console = Console()


def format_bytes(bytes_val: int) -> str:
    """Format bytes to human readable"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.1f}{unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.1f}PB"


def create_status_table(monitor) -> Table:
    """Create a status table"""
    status = monitor.get_quick_status()
    
    table = Table(title="System Status", show_header=True)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_column("Status", style="yellow")
    
    # CPU
    cpu_status = "🟢" if status['cpu_percent'] < 70 else "🟡" if status['cpu_percent'] < 90 else "🔴"
    table.add_row(
        "CPU Usage",
        f"{status['cpu_percent']:.1f}%",
        cpu_status
    )
    
    # Memory
    mem_status = "🟢" if status['memory_percent'] < 70 else "🟡" if status['memory_percent'] < 90 else "🔴"
    table.add_row(
        "Memory Usage",
        f"{status['memory_percent']:.1f}% ({status['memory_available_gb']:.1f}GB free)",
        mem_status
    )
    
    # Load Average
    load = status['load_average']
    table.add_row(
        "Load Average",
        f"{load[0]:.2f}, {load[1]:.2f}, {load[2]:.2f}",
        "🟢"
    )
    
    # Disk Usage
    for mount, percent in status.get('disk_usage', {}).items():
        disk_status = "🟢" if percent < 80 else "🟡" if percent < 90 else "🔴"
        table.add_row(
            f"Disk {mount}",
            f"{percent:.1f}%",
            disk_status
        )
    
    # Uptime
    table.add_row(
        "Uptime",
        f"{status['uptime_hours']:.1f} hours",
        "🟢"
    )
    
    return table


def create_predictions_panel(assistant) -> Panel:
    """Create predictions panel"""
    predictions = assistant.analyze_system()
    
    if not predictions:
        content = Text("No predictions at this time - system is healthy!", style="green")
    else:
        content = Text()
        for i, pred in enumerate(predictions[:5], 1):
            # Priority icon
            icon = {
                'critical': '🚨',
                'high': '⚠️',
                'medium': '💡',
                'low': 'ℹ️'
            }.get(pred.priority, '•')
            
            content.append(f"{icon} ", style="bold")
            content.append(f"{pred.action}\n", style="yellow")
            content.append(f"   Reason: {pred.reason}\n", style="dim")
            content.append(f"   Confidence: {pred.confidence*100:.0f}%\n", style="cyan")
            
            if pred.data and 'command' in pred.data:
                content.append(f"   Command: ", style="dim")
                content.append(f"{pred.data['command']}\n", style="green")
            
            if i < len(predictions):
                content.append("\n")
    
    return Panel(content, title="🔮 Predictive Suggestions", border_style="blue")


def test_intent_recognition(recognizer):
    """Test context-aware intent recognition"""
    test_queries = [
        "my system is slow",
        "install firefox",
        "free up some space",
        "what's using all my memory?",
        "fix broken services",
        "update everything",
        "rollback to yesterday",
        "why is everything so sluggish?",
        "clean up old stuff",
        "check system status"
    ]
    
    console.print("\n[bold cyan]Testing Context-Aware Intent Recognition[/bold cyan]\n")
    
    for query in test_queries:
        console.print(f"[yellow]Query:[/yellow] {query}")
        
        intent = recognizer.recognize(query)
        
        console.print(f"  [green]Intent:[/green] {intent.intent_type.value}")
        console.print(f"  [cyan]Confidence:[/cyan] {intent.confidence:.2f}")
        
        if intent.entities:
            console.print(f"  [magenta]Entities:[/magenta] {intent.entities}")
        
        if intent.suggestions:
            console.print("  [blue]Suggestions:[/blue]")
            for suggestion in intent.suggestions:
                console.print(f"    • {suggestion}")
        
        if intent.warnings:
            console.print("  [red]Warnings:[/red]")
            for warning in intent.warnings:
                console.print(f"    ⚠️ {warning}")
        
        console.print()


async def test_aware_service():
    """Test the aware service"""
    console.print("\n[bold cyan]Testing Aware Nix Service[/bold cyan]\n")
    
    service = AwareNixService()
    
    # Test queries
    queries = [
        "my computer is running slow",
        "install a text editor",
        "clean up disk space",
        "show system health"
    ]
    
    for query in queries:
        console.print(f"[yellow]Processing:[/yellow] {query}")
        
        response = await service.process_natural_language(query)
        
        console.print(f"  [green]Intent:[/green] {response['intent']} (confidence: {response['confidence']:.2f})")
        
        if response.get('suggestions'):
            console.print("  [blue]Suggestions:[/blue]")
            for suggestion in response['suggestions']:
                console.print(f"    • {suggestion}")
        
        if response.get('warnings'):
            console.print("  [red]Warnings:[/red]")
            for warning in response['warnings']:
                console.print(f"    ⚠️ {warning}")
        
        if response.get('predictions'):
            console.print("  [magenta]System Predictions:[/magenta]")
            for pred in response['predictions']:
                console.print(f"    • {pred['action']} ({pred['priority']})")
        
        console.print()
    
    # Get system insights
    insights = service.get_system_insights()
    
    console.print("[bold cyan]System Insights[/bold cyan]")
    console.print(f"  Health Score: {insights['health_score']}/100")
    
    if insights['alerts']:
        console.print("  [red]Active Alerts:[/red]")
        for alert in insights['alerts']:
            console.print(f"    {alert}")
    else:
        console.print("  [green]No active alerts[/green]")
    
    service.shutdown()


async def live_monitoring():
    """Show live system monitoring"""
    monitor = get_system_monitor()
    assistant = PredictiveAssistant(monitor)
    
    # Start monitoring
    await monitor.start_monitoring()
    
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main"),
        Layout(name="predictions", size=10)
    )
    
    with Live(layout, refresh_per_second=1, console=console) as live:
        for _ in range(30):  # Run for 30 seconds
            # Update header
            header_text = Text()
            header_text.append("🖥️  Luminous Nix - Environmental Awareness Demo\n", style="bold cyan")
            header_text.append(f"Time: {datetime.now().strftime('%H:%M:%S')}", style="dim")
            layout["header"].update(Panel(header_text, border_style="blue"))
            
            # Update main status
            layout["main"].update(create_status_table(monitor))
            
            # Update predictions
            layout["predictions"].update(create_predictions_panel(assistant))
            
            await asyncio.sleep(1)
    
    await monitor.stop_monitoring()


async def main():
    """Main test function"""
    console.print("[bold cyan]🌟 Luminous Nix Environmental Awareness Demo 🌟[/bold cyan]\n")
    
    # Initialize monitor
    monitor = get_system_monitor()
    
    # Quick update to get fresh data
    await monitor.update_category('cpu')
    await monitor.update_category('memory')
    await monitor.update_category('disk')
    await monitor.update_category('services')
    
    # Show current status
    console.print("[bold]1. Current System Status[/bold]")
    console.print(create_status_table(monitor))
    
    # Show predictions
    console.print("\n[bold]2. Predictive Analysis[/bold]")
    assistant = PredictiveAssistant(monitor)
    console.print(create_predictions_panel(assistant))
    
    # Test intent recognition
    console.print("\n[bold]3. Context-Aware Intent Recognition[/bold]")
    recognizer = ContextAwareIntentRecognizer(monitor)
    test_intent_recognition(recognizer)
    
    # Test aware service
    console.print("\n[bold]4. Integrated Aware Service[/bold]")
    await test_aware_service()
    
    # Ask if user wants live monitoring
    console.print("\n[yellow]Would you like to see live monitoring? (y/n)[/yellow]")
    response = input().strip().lower()
    
    if response == 'y':
        console.print("\n[bold cyan]Starting 30-second live monitoring...[/bold cyan]")
        await live_monitoring()
    
    # Save snapshot
    snapshot_path = monitor.save_snapshot()
    console.print(f"\n[green]System snapshot saved to: {snapshot_path}[/green]")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()