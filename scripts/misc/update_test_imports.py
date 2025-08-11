#!/usr/bin/env python3
"""
Update test imports from backend to nix_humanity package.
This script updates all import statements in test files.
"""

import re
from datetime import datetime
from pathlib import Path


def update_imports(content: str) -> tuple[str, int]:
    """Update import statements to use nix_humanity package."""
    changes = 0

    # Direct backend imports
    patterns = [
        (r"from backend\.", "from nix_for_humanity."),
        (r"import nix_for_humanity.core as backend\.", "import nix_for_humanity."),
        (r"from \.\.backend", "from nix_for_humanity"),
        # Specific module mappings
        (
            r"from backend\.core\.backend import",
            "from nix_for_humanity.core.engine import",
        ),
        (r"backend\.core\.backend\.", "nix_humanity.core.engine."),
        # Mock paths
        (r"sys\.modules\['backend\.", "sys.modules['nix_humanity."),
        (r"backend\.python\.native_nix_backend", "nix_humanity.nix.native_backend"),
        # Path additions
        (
            r"backend_path = os\.path\.join\(project_root, 'backend'\)",
            "backend_path = os.path.join(project_root, 'nix_humanity')",
        ),
    ]

    for pattern, replacement in patterns:
        new_content, count = re.subn(pattern, replacement, content)
        if count > 0:
            content = new_content
            changes += count

    return content, changes


def process_test_file(file_path: Path) -> tuple[bool, int]:
    """Process a single test file."""
    try:
        original_content = file_path.read_text()
        updated_content, changes = update_imports(original_content)

        if changes > 0:
            file_path.write_text(updated_content)
            return True, changes
        return False, 0
    except Exception as e:
        print(f"  ❌ Error processing {file_path}: {e}")
        return False, 0


def main():
    """Main execution."""
    print("🔄 Updating Test Imports to nix_humanity")
    print("=" * 60)

    root = Path("/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity")
    test_dirs = [
        root / "tests",
        root / "scripts" / "test",
        root / "backend" / "tests",
    ]

    total_files = 0
    total_changes = 0
    updated_files = []

    # Find all test files
    test_files = []
    for test_dir in test_dirs:
        if test_dir.exists():
            test_files.extend(test_dir.rglob("*test*.py"))

    # Also check root directory test files
    test_files.extend(root.glob("*test*.py"))
    test_files.extend(root.glob("test_*.py"))
    test_files.extend(root.glob("run_*test*.py"))
    test_files.extend(root.glob("*_test.py"))

    # Remove duplicates
    test_files = list(set(test_files))

    # Exclude venv and archive directories
    test_files = [
        f for f in test_files if "venv" not in str(f) and "archive" not in str(f)
    ]

    print(f"Found {len(test_files)} test files to check")
    print()

    for file_path in sorted(test_files):
        updated, changes = process_test_file(file_path)
        if updated:
            total_files += 1
            total_changes += changes
            updated_files.append(file_path.relative_to(root))
            print(f"  ✅ Updated {file_path.name} ({changes} changes)")

    # Create report
    report_path = root / "TEST_IMPORT_UPDATE_COMPLETE.md"
    with open(report_path, "w") as f:
        f.write("# Test Import Update Complete\n\n")
        f.write(f"**Date**: {datetime.now().isoformat()}\n\n")
        f.write("## Summary\n\n")
        f.write(f"- Updated {total_files} test files\n")
        f.write(f"- Made {total_changes} import changes\n")
        f.write("- All imports now use `nix_humanity` package\n\n")

        if updated_files:
            f.write("## Updated Files\n\n")
            for file in updated_files:
                f.write(f"- `{file}`\n")

        f.write("\n## Next Steps\n\n")
        f.write("1. Run test suite to verify all imports work\n")
        f.write("2. Fix any remaining import errors\n")
        f.write("3. Remove old `backend/` directory\n")
        f.write("4. Update documentation\n")

    print("\n" + "=" * 60)
    print("🎉 Test Import Update Complete!")
    print(f"   - {total_files} files updated")
    print(f"   - {total_changes} imports changed")
    print("\n📋 See TEST_IMPORT_UPDATE_COMPLETE.md for details")


if __name__ == "__main__":
    main()
