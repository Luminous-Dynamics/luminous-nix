#!/usr/bin/env python3
"""Fix incorrect import paths in test files."""

import os
import re


def fix_imports_in_file(filepath):
    """Fix import paths in a single test file."""
    with open(filepath) as f:
        content = f.read()

    # Replace incorrect import paths
    replacements = [
        (r"nix_for_humanity\.adapters\.cli_adapter", "nix_humanity.interfaces.cli"),
        (r"nix_for_humanity\.core", "nix_humanity.core"),
        (r"nix_for_humanity\.knowledge", "nix_humanity.knowledge"),
        (r"nix_for_humanity\.tui", "nix_humanity.ui"),
    ]

    modified = False
    for old_pattern, new_pattern in replacements:
        new_content = re.sub(old_pattern, new_pattern, content)
        if new_content != content:
            modified = True
            content = new_content

    if modified:
        with open(filepath, "w") as f:
            f.write(content)
        print(f"✅ Fixed imports in {filepath}")
    else:
        print(f"✓ No changes needed in {filepath}")


# Fix all test files
test_dirs = ["tests/cli", "tests/tui", "tests/unit", "tests/integration"]
for test_dir in test_dirs:
    if os.path.exists(test_dir):
        for root, dirs, files in os.walk(test_dir):
            for file in files:
                if file.endswith(".py"):
                    filepath = os.path.join(root, file)
                    fix_imports_in_file(filepath)

print("\n🎯 Import fixes complete!")
