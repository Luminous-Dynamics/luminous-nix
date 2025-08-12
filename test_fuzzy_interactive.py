#!/usr/bin/env python3
"""
Test interactive fuzzy search with fzf
"""

from nix_for_humanity.cli.search_command import SearchCommand

# Create search command
cmd = SearchCommand()

print("=" * 60)
print("🔍 Interactive Fuzzy Search Test")
print("=" * 60)
print()
print("This will open an interactive fuzzy finder (fzf)")
print("Type to filter packages, use arrow keys to select")
print("Press Enter to select, ESC to cancel")
print()
input("Press Enter to start...")

# Run interactive search
result = cmd.search("", interactive=True)

if result:
    print(f"\n✅ You selected: {result[0].name}")
    if result[0].description:
        print(f"   {result[0].description}")
else:
    print("\n❌ No package selected")

print("\nWould you like to try search with install option? [y/N]: ", end="")
response = input().strip().lower()

if response in ['y', 'yes']:
    package = cmd.search_with_install("editor", interactive=False)
    if package:
        print(f"\n📦 Ready to install: {package}")
        print(f"   Command: nix-env -iA nixos.{package}")
    else:
        print("\n❌ No package selected for installation")