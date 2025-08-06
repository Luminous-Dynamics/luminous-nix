#!/usr/bin/env python3
"""
Proof of concept: Direct integration with nixos-rebuild-ng Python module
This demonstrates how Nix for Humanity can use the native Python API
"""

import sys
import os
import subprocess
from pathlib import Path

# First, find the nixos-rebuild-ng module in the nix store
def find_nixos_rebuild_module():
    """Find the nixos-rebuild Python module in nix store."""
    try:
        # Get the path to nixos-rebuild
        result = subprocess.run(
            ["which", "nixos-rebuild"],
            capture_output=True,
            text=True
        )
        rebuild_path = result.stdout.strip()
        
        # Follow symlinks to get the actual nix store path
        real_path = Path(rebuild_path).resolve()
        
        # Extract the nix store package path
        nix_package = str(real_path.parent.parent)
        
        # Construct the Python module path
        python_path = Path(nix_package) / "lib" / "python3.13" / "site-packages"
        
        if python_path.exists():
            return str(python_path)
        else:
            # Try python3.12 as fallback
            python_path = Path(nix_package) / "lib" / "python3.12" / "site-packages"
            if python_path.exists():
                return str(python_path)
                
    except Exception as e:
        print(f"Error finding nixos-rebuild module: {e}")
    
    return None

# Add the module to Python path
nixos_rebuild_path = find_nixos_rebuild_module()
if nixos_rebuild_path:
    sys.path.insert(0, nixos_rebuild_path)
    print(f"✅ Found nixos-rebuild-ng at: {nixos_rebuild_path}")
else:
    print("❌ Could not find nixos-rebuild-ng module")
    sys.exit(1)

# Now we can import the module
try:
    from nixos_rebuild import models, nix
    from nixos_rebuild.models import Action, Profile, BuildAttr, Flake
    print("✅ Successfully imported nixos_rebuild module!")
except ImportError as e:
    print(f"❌ Failed to import nixos_rebuild: {e}")
    sys.exit(1)

class NixForHumanitySystemManager:
    """
    Demonstrates how Nix for Humanity can integrate with nixos-rebuild-ng
    """
    
    def __init__(self):
        self.profile = Profile.from_arg("system")
        print(f"📦 Using profile: {self.profile.path}")
        
    def list_available_actions(self):
        """Show all available nixos-rebuild actions."""
        print("\n🎯 Available NixOS actions:")
        for action in Action:
            print(f"  - {action.value}: {self._describe_action(action)}")
    
    def _describe_action(self, action):
        """Natural language description of each action."""
        descriptions = {
            Action.SWITCH: "Apply configuration and switch to it immediately",
            Action.BOOT: "Apply configuration on next boot",
            Action.TEST: "Test configuration without making it permanent",
            Action.BUILD: "Build configuration without applying",
            Action.DRY_BUILD: "Show what would be built",
            Action.DRY_RUN: "Show what would happen without doing it",
            Action.BUILD_VM: "Build a virtual machine with this configuration",
            Action.LIST_GENERATIONS: "Show all system configurations"
        }
        return descriptions.get(action, "Unknown action")
    
    def check_flake_status(self):
        """Check if the system uses flakes."""
        flake_path = Path("/etc/nixos/flake.nix")
        if flake_path.exists():
            print(f"\n🌸 System uses flakes: {flake_path}")
            return True
        else:
            print("\n📜 System uses traditional configuration.nix")
            return False
    
    def demonstrate_build_attr(self):
        """Show how to create build attributes."""
        print("\n🔨 Build attribute examples:")
        
        # Default build attribute
        default_attr = BuildAttr.from_arg(None, None)
        print(f"  Default: {default_attr.path}")
        
        # Custom file
        if Path("/etc/nixos/configuration.nix").exists():
            custom_attr = BuildAttr.from_arg(
                "system",
                "/etc/nixos/configuration.nix"
            )
            print(f"  Custom: {custom_attr.path} with attr '{custom_attr.attr}'")
    
    def demonstrate_natural_language_mapping(self):
        """Show how natural language maps to nixos-rebuild actions."""
        print("\n💬 Natural language to action mapping:")
        
        mappings = [
            ("update my system", Action.SWITCH),
            ("update system", Action.SWITCH),
            ("apply changes", Action.SWITCH),
            ("test my changes", Action.TEST),
            ("check what would change", Action.DRY_RUN),
            ("prepare for next boot", Action.BOOT),
            ("show me past configurations", Action.LIST_GENERATIONS),
            ("build but don't apply", Action.BUILD),
        ]
        
        for phrase, action in mappings:
            print(f'  "{phrase}" → {action.value}')
    
    def show_integration_example(self):
        """Show how this would integrate with Nix for Humanity."""
        print("\n🤖 Integration example:")
        print("""
# In Nix for Humanity's backend:

async def handle_system_update(user_input):
    # 1. NLP understands intent
    if "test" in user_input or "try" in user_input:
        action = Action.TEST
    elif "next boot" in user_input or "later" in user_input:
        action = Action.BOOT
    else:
        action = Action.SWITCH
    
    # 2. Use nixos-rebuild-ng directly
    if has_flake():
        flake = Flake.parse("/etc/nixos")
        path = nix.build_flake("config.system.build.toplevel", flake)
    else:
        build_attr = BuildAttr.from_arg(None, None)
        path = nix.build("config.system.build.toplevel", build_attr)
    
    # 3. Apply configuration
    nix.switch_to_configuration(path, action, profile)
    
    # 4. Natural response
    return f"System updated! Configuration {action.value} complete."
""")

def main():
    print("🌟 Nix for Humanity - NixOS Rebuild Integration Demo\n")
    
    manager = NixForHumanitySystemManager()
    
    # Demonstrate various features
    manager.list_available_actions()
    manager.check_flake_status()
    manager.demonstrate_build_attr()
    manager.demonstrate_natural_language_mapping()
    manager.show_integration_example()
    
    print("\n✨ This demonstrates direct Python integration with nixos-rebuild!")
    print("🚀 No subprocess calls needed - we can use the native Python API!")

if __name__ == "__main__":
    main()