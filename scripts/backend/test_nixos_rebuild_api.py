#!/usr/bin/env python3
"""Quick test to find nixos-rebuild-ng API"""

import subprocess
import sys
from pathlib import Path

print("🔍 Searching for nixos-rebuild-ng API...")

# Method 1: Find nixos-rebuild location
try:
    result = subprocess.run(['which', 'nixos-rebuild'], capture_output=True, text=True)
    if result.returncode == 0:
        rebuild_path = Path(result.stdout.strip())
        print(f"✅ Found nixos-rebuild at: {rebuild_path}")
        
        # Follow symlinks
        real_path = rebuild_path.resolve()
        print(f"📍 Real path: {real_path}")
        
        # Extract nix store path
        nix_package = str(real_path.parent.parent)
        print(f"📦 Nix package: {nix_package}")
        
        # Look for Python modules
        for python_version in ['python3.13', 'python3.12', 'python3.11']:
            python_path = Path(nix_package) / 'lib' / python_version / 'site-packages'
            if python_path.exists():
                print(f"✅ Found Python modules at: {python_path}")
                
                # Try to import
                sys.path.insert(0, str(python_path))
                try:
                    import nixos_rebuild
                    print(f"🎉 Successfully imported nixos_rebuild!")
                    print(f"   Module location: {nixos_rebuild.__file__}")
                    
                    # Check available components
                    from nixos_rebuild import models, nix
                    print(f"✅ Can import models and nix submodules")
                    
                    # List available actions
                    from nixos_rebuild.models import Action
                    print(f"\n📋 Available actions:")
                    for action in Action:
                        print(f"   - {action.name}: {action.value}")
                    
                except ImportError as e:
                    print(f"❌ Could not import: {e}")
                    
except Exception as e:
    print(f"❌ Error: {e}")
    
print("\n🔍 Searching for nixos-rebuild-ng in nix store...")
result = subprocess.run(['ls', '-la', '/nix/store/'], capture_output=True, text=True)
rebuild_ng_paths = [line for line in result.stdout.split('\n') if 'nixos-rebuild-ng' in line]
if rebuild_ng_paths:
    print(f"Found {len(rebuild_ng_paths)} nixos-rebuild-ng packages:")
    for path in rebuild_ng_paths[:3]:
        print(f"  {path}")
else:
    print("No nixos-rebuild-ng found in /nix/store/")