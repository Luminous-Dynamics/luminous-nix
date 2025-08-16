#!/usr/bin/env python3
"""
🌟 TUI Demo for Nix for Humanity

Interactive demonstration of the beautiful terminal interface.
Shows off the consciousness orb, natural language processing, and rich feedback.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    """Run the TUI demo"""
    try:
        from luminous_nix.tui.app import NixForHumanityTUI
        
        print("🌟 Nix for Humanity TUI Demo")
        print("=" * 50)
        print()
        print("This beautiful terminal interface provides:")
        print("  🔮 Consciousness orb visualization")
        print("  💬 Natural language command input")
        print("  📜 Rich command history")
        print("  ⚡ Real-time feedback")
        print("  🎨 Beautiful, accessible design")
        print()
        print("Controls:")
        print("  F1 - Show help")
        print("  F2 - Toggle dry run mode")
        print("  Ctrl+L - Clear history")
        print("  Q or Ctrl+C - Quit")
        print()
        print("=" * 50)
        print()
        input("Press Enter to launch the TUI...")
        
        # Launch TUI
        app = NixForHumanityTUI()
        app.run()
        
        print("\n✨ Thank you for trying Nix for Humanity!")
        
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("\nPlease ensure textual is installed:")
        print("  poetry add textual")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n✨ Demo interrupted. Thank you!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()