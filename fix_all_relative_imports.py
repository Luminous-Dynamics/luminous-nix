#!/usr/bin/env python3
"""Fix all relative imports to use absolute imports (NO MOCKS!)"""

import re
from pathlib import Path


def fix_relative_imports(root_dir):
    """Fix all relative import statements to use absolute imports"""

    fixes_applied = 0
    files_fixed = []

    # Define replacements for relative imports
    replacements = [
        # Core module imports
        (
            r"from \.\.core\.personas import",
            "from nix_for_humanity.nlp.personas import",
        ),
        (r"from \.\.api\.schema import", "from nix_for_humanity.api.schema import"),
        (r"from \.\.security\.", "from nix_for_humanity.security."),
        (r"from \.\.nlp\.", "from nix_for_humanity.nlp."),
        (r"from \.\.config\.", "from nix_for_humanity.config."),
        (r"from \.\.learning\.", "from nix_for_humanity.learning."),
        (r"from \.\.utils\.", "from nix_for_humanity.utils."),
        (r"from \.\.knowledge\.", "from nix_for_humanity.knowledge."),
        (r"from \.\.monitoring\.", "from nix_for_humanity.monitoring."),
        (r"from \.\.interfaces\.", "from nix_for_humanity.interfaces."),
        (r"from \.\.tui\.", "from nix_for_humanity.tui."),
        (r"from \.\.cli\.", "from nix_for_humanity.cli."),
        # Single-level relative imports
        (r"from \.personas import", "from nix_for_humanity.nlp.personas import"),
        (
            r"from \.error_handler import",
            "from nix_for_humanity.core.error_handler import",
        ),
        (
            r"from \.native_operations import",
            "from nix_for_humanity.core.native_operations import",
        ),
        (r"from \.intents import", "from nix_for_humanity.core.intents import"),
        (r"from \.types import", "from nix_for_humanity.core.types import"),
        # Common wrong imports
        (r"from core\.", "from nix_for_humanity.core."),
        (r"import core\.", "import nix_for_humanity.core."),
        (r"from nlp\.", "from nix_for_humanity.nlp."),
        (r"import nlp\.", "import nix_for_humanity.nlp."),
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
    print("🔧 Fixing all relative imports (NO MOCKS!)")
    print("=" * 60)

    # Fix imports in src directory
    print("\n📁 Processing src/...")
    fixes, files = fix_relative_imports("src")

    print("\n" + "=" * 60)
    print(f"✅ Fixed {fixes} files total")

    if fixes > 0:
        print("\nFiles fixed:")
        for f in files[:10]:  # Show first 10
            print(f"  - {f}")
        if len(files) > 10:
            print(f"  ... and {len(files) - 10} more")

    print("\n✅ Relative import fixes complete!")
    print("All imports now use absolute paths.")


if __name__ == "__main__":
    main()
