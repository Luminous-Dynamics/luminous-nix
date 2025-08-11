#!/usr/bin/env python3
"""Just test if we can import the API"""

import sys

# Add the known nixos-rebuild-ng path
nixos_path = "/nix/store/lwmjrs31xfgn2q1a0b9f81a61ka4ym6z-nixos-rebuild-ng-0.0.0/lib/python3.13/site-packages"
sys.path.insert(0, nixos_path)

try:
    from nixos_rebuild import models, nix
    from nixos_rebuild.models import Action

    print("✅ nixos-rebuild API imported successfully!")
    print(f"Available actions: {[a.value for a in Action]}")

    # Test basic functionality
    from nixos_rebuild.models import Profile

    profile = Profile.from_name("system")
    print(f"✅ System profile: {profile}")

except ImportError as e:
    print(f"❌ Import failed: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
