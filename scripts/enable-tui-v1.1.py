#!/usr/bin/env python3
"""
Enable TUI for v1.1 Release

This script:
1. Verifies TUI components exist
2. Tests backend connection
3. Prepares for v1.1 release
"""

import sys
import subprocess
from pathlib import Path

def check_tui_files():
    """Verify TUI files exist"""
    print("🔍 Checking TUI files...")
    
    tui_files = [
        "src/nix_humanity/ui/main_app.py",
        "src/nix_humanity/ui/consciousness_orb.py", 
        "src/nix_humanity/ui/adaptive_interface.py",
        "src/nix_humanity/interfaces/tui.py",
        "bin/nix-tui"
    ]
    
    all_exist = True
    for file in tui_files:
        path = Path(file)
        if path.exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - MISSING")
            all_exist = False
            
    return all_exist

def test_backend_connection():
    """Test if TUI can connect to backend"""
    print("\n🔗 Testing backend connection...")
    
    try:
        # Test Python path
        sys.path.insert(0, 'src')
        
        # Try importing backend
        from nix_humanity.core.backend import NixForHumanityBackend
        print("  ✅ Backend imports successfully")
        
        # Create instance
        backend = NixForHumanityBackend()
        print("  ✅ Backend instance created")
        
        # Test a simple query
        result = backend.execute_command("help", dry_run=True)
        print("  ✅ Backend responds to queries")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Backend connection failed: {e}")
        return False

def create_v1_1_changelog():
    """Create v1.1 changelog entry"""
    print("\n📝 Creating v1.1 changelog...")
    
    changelog = """
## v1.1.0 - TUI & Voice Release (Coming Soon)

### Added
- 🎨 Beautiful Terminal UI with Textual framework
- 🌟 Living consciousness orb visualization
- 🎤 Basic voice interface (experimental)
- 📊 Real-time operation progress display
- 🎯 Adaptive complexity based on user expertise

### Changed
- Enhanced error messages with visual feedback
- Improved help system with interactive panels
- Better performance monitoring in TUI

### Technical
- TUI runs with `nix-tui` command
- Voice interface with `nix-voice` (experimental)
- All v1.0 CLI commands still work unchanged
- Backend fully supports both CLI and TUI modes
"""
    
    with open("CHANGELOG_v1.1_preview.md", "w") as f:
        f.write(changelog)
    print("  ✅ Created CHANGELOG_v1.1_preview.md")

def main():
    print("🚀 Nix for Humanity v1.1 TUI Enablement")
    print("=" * 50)
    
    # Check files
    if not check_tui_files():
        print("\n❌ Some TUI files are missing!")
        return 1
        
    # Test backend
    if not test_backend_connection():
        print("\n❌ Backend connection issues!")
        return 1
        
    # Create changelog
    create_v1_1_changelog()
    
    print("\n✨ TUI is ready for v1.1 release!")
    print("\nNext steps:")
    print("1. Install TUI dependencies: poetry install -E tui")
    print("2. Test TUI: poetry run nix-tui")
    print("3. Update version to 1.1.0 in pyproject.toml")
    print("4. Update documentation")
    print("5. Ship v1.1 in 2-4 weeks!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())