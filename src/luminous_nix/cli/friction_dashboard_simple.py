#!/usr/bin/env python3
"""
Embarrassingly Simple Friction Dashboard - 1 Day Version.

Instead of a complex real-time TUI, just show a session summary.
This delivers 80% of the value with 1% of the complexity.

Based on the principle: Start embarrassingly simple, let sophistication emerge.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

def show_session_summary():
    """
    Display a simple text summary of the session's friction metrics.
    
    This is the Day 1 implementation - just the facts, no fancy UI.
    """
    # Simple file-based tracking (no database needed)
    session_file = Path.home() / ".luminous-nix" / "current_session.json"
    
    if not session_file.exists():
        print("No session data yet. Start using ask-nix to generate metrics!")
        return
    
    try:
        with open(session_file) as f:
            data = json.load(f)
    except:
        print("Session data corrupted. Starting fresh next time!")
        return
    
    # Calculate simple friction score
    total_actions = data.get('total_actions', 0)
    errors = data.get('error_count', 0)
    help_requests = data.get('help_count', 0)
    undos = data.get('undo_count', 0)
    
    if total_actions == 0:
        print("📊 No actions recorded yet")
        return
    
    # Simple friction calculation
    friction_score = (errors + help_requests * 0.5 + undos * 0.3) / max(1, total_actions)
    
    # Display the embarrassingly simple dashboard
    print("\n" + "="*50)
    print("📊 SESSION FRICTION SUMMARY")
    print("="*50)
    
    print(f"""
Actions taken: {total_actions}
Errors encountered: {errors}
Help requested: {help_requests} times
Commands undone: {undos}

Friction Score: {friction_score:.2f}
""")
    
    # Simple interpretation
    if friction_score < 0.1:
        level = "✨ Smooth sailing!"
        advice = "You're in the flow. Keep going!"
    elif friction_score < 0.3:
        level = "😊 Minor friction"
        advice = "Mostly smooth with a few bumps."
    elif friction_score < 0.5:
        level = "🤔 Moderate friction"
        advice = "Consider using 'ask-nix help' for guidance."
    else:
        level = "😰 High friction"
        advice = "The system will adapt to help you more."
    
    print(f"Status: {level}")
    print(f"Advice: {advice}")
    
    # Show most common errors (if any)
    if errors > 0 and 'error_types' in data:
        print("\nMost common issues:")
        for error_type, count in list(data['error_types'].items())[:3]:
            print(f"  • {error_type}: {count} times")
    
    print("\n" + "="*50)
    print("💡 Tip: Lower friction = better flow state")
    print("="*50 + "\n")


def track_action(action: str, success: bool = True, error_type: str = None):
    """
    Track a single action for friction calculation.
    
    This is called by other parts of the system to build metrics.
    Dead simple: just increment counters in a JSON file.
    """
    session_file = Path.home() / ".luminous-nix" / "current_session.json"
    session_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Load or create session data
    if session_file.exists():
        with open(session_file) as f:
            data = json.load(f)
    else:
        data = {
            'session_start': datetime.now().isoformat(),
            'total_actions': 0,
            'error_count': 0,
            'help_count': 0,
            'undo_count': 0,
            'error_types': {}
        }
    
    # Update counters (embarrassingly simple)
    data['total_actions'] += 1
    
    if not success:
        data['error_count'] += 1
        if error_type:
            data['error_types'][error_type] = data['error_types'].get(error_type, 0) + 1
    
    if action == 'help':
        data['help_count'] += 1
    elif action == 'undo' or action == 'rollback':
        data['undo_count'] += 1
    
    # Save (no fancy database, just JSON)
    with open(session_file, 'w') as f:
        json.dump(data, f)


def reset_session():
    """Start a fresh session"""
    session_file = Path.home() / ".luminous-nix" / "current_session.json"
    if session_file.exists():
        # Archive old session (simple timestamp)
        archive_name = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        archive_file = session_file.parent / "archives" / archive_name
        archive_file.parent.mkdir(exist_ok=True)
        session_file.rename(archive_file)
        print(f"✅ Session archived to {archive_name}")
    print("🆕 Starting fresh session")


# CLI integration
def main():
    """Simple CLI for the friction dashboard"""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "reset":
            reset_session()
        elif command == "track":
            # Hidden command for other parts of system
            if len(sys.argv) > 2:
                action = sys.argv[2]
                success = sys.argv[3] == "success" if len(sys.argv) > 3 else True
                track_action(action, success)
        else:
            print(f"Unknown command: {command}")
            print("Usage: friction_dashboard [reset]")
    else:
        show_session_summary()


if __name__ == "__main__":
    main()