#!/usr/bin/env python3
"""Basic test to verify TUI can be imported and initialized"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from nix_for_humanity.tui.app import NixForHumanityTUI
    print("✅ TUI imports successfully")
    
    # Try to create an instance (won't run it)
    app = NixForHumanityTUI()
    print("✅ TUI instance created")
    
    # Check it has expected attributes
    assert hasattr(app, 'CSS')
    assert hasattr(app, 'compose')
    print("✅ TUI has expected attributes")
    
    print("\n🎉 TUI is ready to use!")
    print("Run with: poetry run python bin/nix-tui")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\nMake sure textual is installed:")
    print("  poetry add textual")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()