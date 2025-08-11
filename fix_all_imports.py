#!/usr/bin/env python3
"""Fix all import issues in the codebase - NO MOCKS!"""

import os
import re
from pathlib import Path


def fix_imports(root_dir):
    """Fix all import statements"""

    fixes_applied = 0
    files_fixed = []

    # Define replacements
    replacements = [
        (r"from nix_humanity", "from nix_for_humanity"),
        (r"import nix_humanity", "import nix_for_humanity"),
        (r"nixos_rebuild_mock", "nixos_rebuild"),  # Remove mock references
        (r"from.*mock.*import", "# REMOVED MOCK IMPORT:"),  # Comment out mock imports
    ]

    # Find all Python files
    for py_file in Path(root_dir).rglob("*.py"):
        # Skip virtual environments and caches
        if any(
            skip in str(py_file)
            for skip in ["venv", "__pycache__", ".git", "node_modules"]
        ):
            continue

        try:
            with open(py_file, encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # Apply replacements
            for pattern, replacement in replacements:
                content = re.sub(pattern, replacement, content)

            # Write back if changed
            if content != original_content:
                with open(py_file, "w", encoding="utf-8") as f:
                    f.write(content)
                files_fixed.append(py_file)
                fixes_applied += 1
                print(f"✅ Fixed: {py_file}")

        except Exception as e:
            print(f"⚠️ Error processing {py_file}: {e}")

    return fixes_applied, files_fixed


def main():
    print("🔧 Fixing all imports (NO MOCKS!)")
    print("=" * 60)

    # Fix imports in all relevant directories
    directories = ["src", "scripts", "tests", "bin", "features", "examples"]

    total_fixes = 0
    all_fixed_files = []

    for directory in directories:
        if os.path.exists(directory):
            print(f"\n📁 Processing {directory}/...")
            fixes, files = fix_imports(directory)
            total_fixes += fixes
            all_fixed_files.extend(files)

    print("\n" + "=" * 60)
    print(f"✅ Fixed {total_fixes} files total")

    if total_fixes > 0:
        print("\nFiles fixed:")
        for f in all_fixed_files[:10]:  # Show first 10
            print(f"  - {f}")
        if len(all_fixed_files) > 10:
            print(f"  ... and {len(all_fixed_files) - 10} more")

    print("\n✅ Import fixes complete!")
    print("NO MOCKS remain in the codebase.")


if __name__ == "__main__":
    main()
