#!/usr/bin/env python3
"""
Flow state management commands for the CLI.

Allows users to enter/exit flow state to control notification batching.
Based on research showing 47% productivity loss from context switching.
"""

import asyncio
from typing import Optional
from ..self_healing.healing_engine_v2 import create_self_healing_engine
from ..self_healing.notification_queue import get_notification_queue

# Global engine instance
_healing_engine: Optional['SimplifiedHealingEngine'] = None

def get_healing_engine():
    """Get or create healing engine instance"""
    global _healing_engine
    if _healing_engine is None:
        _healing_engine = create_self_healing_engine()
    return _healing_engine


async def enter_flow_state(duration_minutes: Optional[int] = None):
    """
    Enter flow state - batch non-critical notifications.
    
    Args:
        duration_minutes: Optional duration before auto-exit
    """
    engine = get_healing_engine()
    queue = get_notification_queue()
    
    engine.enter_flow_state()
    
    print("🧘 Flow State Activated")
    print("━" * 40)
    print("✨ You're entering deep work mode")
    print("📬 Non-critical notifications will be batched")
    print("🚨 Critical issues will still alert immediately")
    
    if duration_minutes:
        print(f"⏱️  Auto-exit in {duration_minutes} minutes")
        # Schedule auto-exit
        await asyncio.sleep(duration_minutes * 60)
        await exit_flow_state()
    else:
        print("💡 Use 'ask-nix flow exit' when ready")
    
    # Show current queue status
    status = queue.get_status()
    if status['held_notifications'] > 0:
        print(f"\n📋 {status['held_notifications']} notifications held")


async def exit_flow_state():
    """Exit flow state - deliver batched notifications"""
    engine = get_healing_engine()
    queue = get_notification_queue()
    
    status = queue.get_status()
    held = status['held_notifications']
    
    engine.exit_flow_state()
    
    print("📬 Flow State Ended")
    print("━" * 40)
    
    if held > 0:
        print(f"✨ Delivering {held} batched notifications...")
        # Notifications will be displayed by the queue
    else:
        print("✅ No notifications were held")
    
    print("\n🙏 Great work session!")


async def flow_status():
    """Check current flow state and notification queue"""
    engine = get_healing_engine()
    queue = get_notification_queue()
    
    status = queue.get_status()
    friction = engine.get_friction_metrics()
    
    print("🌊 Flow State Status")
    print("━" * 40)
    
    # Flow state
    if status['in_flow_state']:
        print("🧘 Status: IN FLOW STATE")
        print(f"📬 Notifications held: {status['held_notifications']}")
        print(f"⏱️  Next batch in: {status['time_until_flush']:.0f}s")
    else:
        print("💼 Status: Normal mode")
        print("📬 Notifications: Delivered immediately")
    
    # Friction awareness
    print(f"\n🎯 Friction Score: {friction['friction_score']:.2f}")
    if friction['user_confused']:
        print("🤔 High friction detected - verbose mode active")
    
    # Settings
    print(f"\n⚙️  Settings:")
    print(f"   Batch interval: {status['batch_interval']}s")
    print(f"   Auto-adapt: {'Yes' if friction['adaptations']['verbose_mode'] else 'No'}")


async def toggle_flow():
    """Toggle flow state on/off"""
    queue = get_notification_queue()
    status = queue.get_status()
    
    if status['in_flow_state']:
        await exit_flow_state()
    else:
        await enter_flow_state()


# CLI command mapping
FLOW_COMMANDS = {
    'enter': enter_flow_state,
    'exit': exit_flow_state,
    'status': flow_status,
    'toggle': toggle_flow,
}


def handle_flow_command(subcommand: str, *args):
    """
    Handle flow-related commands.
    
    Usage:
        ask-nix flow enter [duration]  # Enter flow state
        ask-nix flow exit              # Exit flow state
        ask-nix flow status            # Check status
        ask-nix flow toggle            # Toggle on/off
    """
    if subcommand not in FLOW_COMMANDS:
        print(f"Unknown flow command: {subcommand}")
        print("Available: enter, exit, status, toggle")
        return
    
    # Parse duration if provided
    duration = None
    if subcommand == 'enter' and args:
        try:
            duration = int(args[0])
        except ValueError:
            print(f"Invalid duration: {args[0]}")
            return
    
    # Run the command
    if subcommand == 'enter' and duration:
        asyncio.run(enter_flow_state(duration))
    else:
        asyncio.run(FLOW_COMMANDS[subcommand]())


# Example integration with main CLI
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: flow_commands.py <enter|exit|status|toggle> [duration_minutes]")
        sys.exit(1)
    
    command = sys.argv[1]
    args = sys.argv[2:] if len(sys.argv) > 2 else []
    
    handle_flow_command(command, *args)