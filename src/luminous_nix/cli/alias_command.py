"""
Alias management for ask-nix CLI.

Allows users to create custom command aliases like 'luminix', 'lnix', etc.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import List, Optional

from ..utils.config import get_config_dir, load_config, save_config
from ..utils.logging import get_logger

logger = get_logger(__name__)


class AliasManager:
    """Manage command aliases for ask-nix"""
    
    def __init__(self):
        self.config_dir = get_config_dir()
        self.config = load_config()
        self.aliases = self.config.get('aliases', {}).get('list', [])
        self.ask_nix_path = self._find_ask_nix()
        
    def _find_ask_nix(self) -> Path:
        """Find the ask-nix executable path"""
        # First try relative to this file
        project_root = Path(__file__).parent.parent.parent.parent
        ask_nix = project_root / "bin" / "ask-nix"
        if ask_nix.exists():
            return ask_nix
            
        # Try which command
        try:
            result = subprocess.run(
                ['which', 'ask-nix'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return Path(result.stdout.strip())
        except Exception:
            pass
            
        # Default fallback
        return Path("/usr/local/bin/ask-nix")
    
    def create_alias(self, name: str) -> bool:
        """
        Create a new alias for ask-nix.
        
        Args:
            name: Alias name (e.g., 'luminix', 'lnix')
            
        Returns:
            Success status
        """
        if name == 'ask-nix':
            print("❌ 'ask-nix' is the main command, not an alias")
            return False
            
        if name in self.aliases:
            print(f"✅ Alias '{name}' already exists")
            return True
            
        # Add to config
        self.aliases.append(name)
        self._save_aliases()
        
        # Create symlink
        success = self._create_symlink(name)
        
        if success:
            print(f"✅ Created alias '{name}' → 'ask-nix'")
            print(f"\nYou can now use: {name} \"install firefox\"")
            
            # Offer shell integration
            self._offer_shell_integration(name)
        else:
            print(f"⚠️ Alias '{name}' saved but symlink creation failed")
            print(f"You can manually create it with:")
            print(f"  ln -s {self.ask_nix_path} ~/.local/bin/{name}")
            
        return success
    
    def _create_symlink(self, name: str) -> bool:
        """Create a symlink for the alias"""
        # Ensure ~/.local/bin exists
        local_bin = Path.home() / ".local" / "bin"
        local_bin.mkdir(parents=True, exist_ok=True)
        
        symlink_path = local_bin / name
        
        try:
            # Remove existing if present
            if symlink_path.exists() or symlink_path.is_symlink():
                symlink_path.unlink()
                
            # Create new symlink
            symlink_path.symlink_to(self.ask_nix_path)
            
            # Make sure ~/.local/bin is in PATH
            if str(local_bin) not in os.environ.get('PATH', ''):
                print(f"\n⚠️ Add ~/.local/bin to your PATH:")
                print(f"  export PATH=\"$HOME/.local/bin:$PATH\"")
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to create symlink: {e}")
            return False
    
    def remove_alias(self, name: str) -> bool:
        """Remove an alias"""
        if name not in self.aliases:
            print(f"❌ Alias '{name}' does not exist")
            return False
            
        # Remove from config
        self.aliases.remove(name)
        self._save_aliases()
        
        # Remove symlink
        local_bin = Path.home() / ".local" / "bin"
        symlink_path = local_bin / name
        
        try:
            if symlink_path.exists() or symlink_path.is_symlink():
                symlink_path.unlink()
                print(f"✅ Removed alias '{name}'")
            else:
                print(f"✅ Removed alias '{name}' from config")
        except Exception as e:
            print(f"⚠️ Removed from config but couldn't delete symlink: {e}")
            
        return True
    
    def list_aliases(self, raw: bool = False) -> List[str]:
        """List all configured aliases"""
        if raw:
            # For scripting
            for alias in self.aliases:
                print(alias)
        else:
            # For humans
            if not self.aliases:
                print("No aliases configured.")
                print("\nCreate one with: ask-nix alias create <name>")
                print("Example: ask-nix alias create luminix")
            else:
                print("🌟 Configured aliases for ask-nix:\n")
                for alias in self.aliases:
                    # Check if symlink exists
                    symlink = Path.home() / ".local" / "bin" / alias
                    if symlink.exists():
                        print(f"  ✅ {alias} → ask-nix")
                    else:
                        print(f"  ⚠️  {alias} → ask-nix (symlink missing)")
                        
                print(f"\nYou can use any of these instead of 'ask-nix'")
                
        return self.aliases
    
    def _save_aliases(self):
        """Save aliases to config file"""
        if 'aliases' not in self.config:
            self.config['aliases'] = {}
        self.config['aliases']['list'] = self.aliases
        save_config(self.config)
    
    def _offer_shell_integration(self, name: str):
        """Offer to add alias to shell configuration"""
        shell = os.environ.get('SHELL', '/bin/bash')
        shell_name = Path(shell).name
        
        if shell_name == 'bash':
            rc_file = Path.home() / '.bashrc'
        elif shell_name == 'zsh':
            rc_file = Path.home() / '.zshrc'
        elif shell_name == 'fish':
            rc_file = Path.home() / '.config' / 'fish' / 'config.fish'
        else:
            return
            
        print(f"\nAdd alias to {rc_file.name}? [y/N]: ", end='')
        response = input().strip().lower()
        
        if response in ['y', 'yes']:
            alias_line = f"alias {name}='ask-nix'"
            
            try:
                # Check if already present
                if rc_file.exists():
                    content = rc_file.read_text()
                    if alias_line in content:
                        print("✅ Alias already in shell configuration")
                        return
                        
                # Add to file
                with open(rc_file, 'a') as f:
                    f.write(f"\n# Luminous Nix alias\n")
                    f.write(f"{alias_line}\n")
                    
                print(f"✅ Added to {rc_file.name}")
                print(f"   Reload with: source {rc_file}")
                
            except Exception as e:
                logger.error(f"Failed to update shell config: {e}")
                print(f"⚠️ Couldn't update {rc_file.name} automatically")
                print(f"   Add manually: {alias_line}")
    
    def setup_default_aliases(self):
        """Set up recommended default aliases"""
        print("🌟 Setting up recommended aliases...\n")
        
        defaults = ['luminix', 'lnix']
        created = []
        
        for alias in defaults:
            if self.create_alias(alias):
                created.append(alias)
                
        if created:
            print(f"\n✨ You can now use: {', '.join(created)}")
        

def handle_alias_command(args):
    """Handle alias subcommands"""
    manager = AliasManager()
    
    if len(args) == 0 or args[0] == 'list':
        # List aliases
        raw = '--raw' in args
        manager.list_aliases(raw=raw)
        
    elif args[0] == 'create' and len(args) > 1:
        # Create alias
        name = args[1]
        manager.create_alias(name)
        
    elif args[0] == 'remove' and len(args) > 1:
        # Remove alias
        name = args[1]
        manager.remove_alias(name)
        
    elif args[0] == 'setup':
        # Set up default aliases
        manager.setup_default_aliases()
        
    else:
        print("Usage:")
        print("  ask-nix alias list              # List all aliases")
        print("  ask-nix alias create <name>     # Create new alias")
        print("  ask-nix alias remove <name>     # Remove alias")
        print("  ask-nix alias setup             # Set up defaults (luminix, lnix)")
        print("\nExamples:")
        print("  ask-nix alias create luminix")
        print("  ask-nix alias create n")
        print("  ask-nix alias list")


if __name__ == "__main__":
    # For testing
    handle_alias_command(sys.argv[1:] if len(sys.argv) > 1 else [])