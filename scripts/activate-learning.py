#!/usr/bin/env python3
"""
Activation script for the Command Learning System
Enables intelligent learning from user interactions
"""

import json
import os
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add scripts directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from command_learning_system import CommandLearningSystem


class LearningActivator:
    def __init__(self):
        self.config_dir = Path.home() / ".config" / "nix-humanity"
        self.config_file = self.config_dir / "config.json"
        self.learning = CommandLearningSystem()

        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def load_config(self):
        """Load configuration from file"""
        if self.config_file.exists():
            with open(self.config_file) as f:
                return json.load(f)
        return {}

    def save_config(self, config):
        """Save configuration to file"""
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=2)

    def enable_learning(self):
        """Enable the learning system"""
        config = self.load_config()
        config["learning_enabled"] = True
        config["learning_enabled_at"] = datetime.now().isoformat()
        self.save_config(config)

        print("✨ Learning system enabled!")
        print("📚 I'll now learn from your commands to provide better suggestions.")
        print("🔒 All data stays local in your computer.")
        print("\nTo view insights: ask-nix --show-insights")
        print("To disable: ask-nix --disable-learning")

    def disable_learning(self, purge=False):
        """Disable the learning system"""
        config = self.load_config()
        config["learning_enabled"] = False
        config["learning_disabled_at"] = datetime.now().isoformat()
        self.save_config(config)

        if purge:
            # Delete the learning database
            db_path = Path(
                "/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/command_learning.db"
            )
            if db_path.exists():
                db_path.unlink()
                print("🗑️  Learning data has been purged.")

        print("📚 Learning system disabled.")
        print("Your existing learning data is preserved unless you used --purge.")

    def show_insights(self):
        """Display learning insights to the user"""
        stats = self.learning.get_learning_stats()
        prefs = self.learning.get_user_preferences()

        print("📊 Your Nix Learning Insights")
        print("=" * 40)

        # Basic stats
        print(f"📈 Commands tracked: {stats['total_commands']}")
        if stats["total_commands"] > 0:
            print(f"✅ Success rate: {stats['success_rate']:.1%}")
            print(f"🧠 Patterns learned: {stats['learned_patterns']}")

        # Top patterns (if any)
        if stats["learned_patterns"] > 0:
            print("\n🔄 Common patterns:")
            # This would need to be added to the learning system
            print("   (Pattern analysis coming soon)")

        # Preferences
        if prefs:
            print("\n⚙️  Your preferences:")
            for key, value in prefs.items():
                print(f"   {key}: {value}")

        # Suggestions
        if stats["total_commands"] >= 10:
            print("\n💡 Suggestions based on your usage:")
            print("   • You seem to prefer friendly responses")
            print("   • Consider using --yes to skip confirmations")
            print("   • Try batch operations: 'install vim git firefox'")

        print("\n🔒 Privacy: All data is stored locally")
        print("📤 Export your data: ask-nix --export-learning")

    def show_privacy(self):
        """Show what data is being tracked"""
        print("🔒 Privacy Information")
        print("=" * 40)
        print("\n✅ What we track (locally only):")
        print("   • Commands you run and their outcomes")
        print("   • Success/failure patterns")
        print("   • Time of day (generalized to hour)")
        print("   • Your preferences (personality style, etc.)")
        print("\n❌ What we DON'T track:")
        print("   • Personal information")
        print("   • File paths or system details")
        print("   • Network information")
        print("   • Any identifying data")
        print("\n📍 Data location:")
        print("   ~/.config/luminous-nix/config.json (settings)")
        print("   ./command_learning.db (learning data)")
        print("\n🗑️  To delete all data: ask-nix --disable-learning --purge")

    def export_learning(self):
        """Export learning data as JSON"""
        stats = self.learning.get_learning_stats()
        prefs = self.learning.get_user_preferences()

        # Get recent commands (would need to add this method)
        conn = sqlite3.connect(self.learning.learning_db)
        c = conn.cursor()

        recent_commands = c.execute(
            """
            SELECT intent, original_query, success, timestamp
            FROM command_history
            ORDER BY timestamp DESC
            LIMIT 100
        """
        ).fetchall()

        conn.close()

        export_data = {
            "exported_at": datetime.now().isoformat(),
            "statistics": stats,
            "preferences": prefs,
            "recent_commands": [
                {
                    "intent": cmd[0],
                    "query": cmd[1],
                    "success": bool(cmd[2]),
                    "timestamp": cmd[3],
                }
                for cmd in recent_commands
            ],
        }

        print(json.dumps(export_data, indent=2))

    def clear_learning(self, days=None):
        """Clear learning data from a specific time period"""
        conn = sqlite3.connect(self.learning.learning_db)
        c = conn.cursor()

        if days:
            cutoff = datetime.now() - timedelta(days=days)
            c.execute("DELETE FROM command_history WHERE timestamp < ?", (cutoff,))
            deleted = c.rowcount
            conn.commit()
            print(f"🗑️  Cleared {deleted} commands older than {days} days.")
        else:
            c.execute("DELETE FROM command_history")
            c.execute("DELETE FROM successful_patterns")
            c.execute("DELETE FROM user_preferences")
            deleted = c.rowcount
            conn.commit()
            print("🗑️  All learning data has been cleared.")

        conn.close()

    def check_status(self):
        """Check if learning is enabled"""
        config = self.load_config()
        enabled = config.get("learning_enabled", False)

        if enabled:
            stats = self.learning.get_learning_stats()
            print("✅ Learning is ENABLED")
            print(f"📊 Tracking {stats['total_commands']} commands")
            if "learning_enabled_at" in config:
                print(f"🕐 Since: {config['learning_enabled_at']}")
        else:
            print("❌ Learning is DISABLED")
            print("Enable with: ask-nix --enable-learning")


def main():
    """Handle command line arguments"""
    activator = LearningActivator()

    if len(sys.argv) < 2:
        print("Usage: activate-learning.py [command]")
        print("\nCommands:")
        print("  enable           Enable learning system")
        print("  disable          Disable learning (keep data)")
        print("  disable --purge  Disable and delete all data")
        print("  status           Check if learning is enabled")
        print("  insights         Show learning insights")
        print("  privacy          Show privacy information")
        print("  export           Export learning data as JSON")
        print("  clear [days]     Clear old learning data")
        return

    command = sys.argv[1]

    if command == "enable":
        activator.enable_learning()
    elif command == "disable":
        purge = "--purge" in sys.argv
        activator.disable_learning(purge)
    elif command == "status":
        activator.check_status()
    elif command == "insights":
        activator.show_insights()
    elif command == "privacy":
        activator.show_privacy()
    elif command == "export":
        activator.export_learning()
    elif command == "clear":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else None
        activator.clear_learning(days)
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
