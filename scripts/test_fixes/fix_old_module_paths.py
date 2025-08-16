#!/usr/bin/env python3
"""Fix old module paths in test files."""

from pathlib import Path

def fix_old_paths():
    """Fix old module paths like src.nix_humanity."""
    test_dir = Path("tests")
    
    replacements = [
        ("from src.nix_humanity", "from luminous_nix"),
        ("import src.nix_humanity", "import luminous_nix"),
        ("from nix_humanity", "from luminous_nix"),
        ("import nix_humanity", "import luminous_nix"),
    ]
    
    fixed_count = 0
    for test_file in test_dir.rglob("*.py"):
        if not test_file.is_file():
            continue
            
        content = test_file.read_text()
        original = content
        
        for old, new in replacements:
            content = content.replace(old, new)
        
        if content != original:
            test_file.write_text(content)
            print(f"Fixed {test_file}")
            fixed_count += 1
    
    print(f"\nFixed {fixed_count} files")

if __name__ == "__main__":
    fix_old_paths()