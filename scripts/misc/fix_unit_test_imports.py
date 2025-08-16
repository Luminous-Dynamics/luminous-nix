#!/usr/bin/env python3
"""
Fix import paths in unit tests to match the actual project structure
"""

import re
from pathlib import Path


def fix_imports_in_file(file_path):
    """Fix imports in a single test file"""
    with open(file_path) as f:
        content = f.read()

    # Map of old imports to new imports
    replacements = [
        # Core imports
        (
            r"from luminous_nix\.core\.intent_engine import",
            "from luminous_nix.core.intents import",
        ),
        (
            r"from luminous_nix\.core\.types import",
            "from luminous_nix.core.intents import",
        ),
        (
            r"from luminous_nix\.core\.knowledge_base import",
            "from luminous_nix.core.knowledge import",
        ),
        (
            r"from luminous_nix\.core\.execution_engine import",
            "from luminous_nix.core.executor import",
        ),
        (
            r"from luminous_nix\.core\.personality_system import",
            "from luminous_nix.core.responses import",
        ),
        (
            r"from luminous_nix\.core\.learning_system import",
            "from luminous_nix.learning.preferences import",
        ),
        (
            r"from luminous_nix\.core\.nix_integration import",
            "from luminous_nix.core.nix_integration import",
        ),
        (
            r"from luminous_nix\.core\.engine import",
            "from luminous_nix.core.engine import",
        ),
        (r"from luminous_nix\.core import", "from luminous_nix.core import"),
        # Security imports
        (
            r"from luminous_nix\.security\.input_validator import",
            "from luminous_nix.security.input_validator import",
        ),
        (
            r"from luminous_nix\.security\.enhanced_validator import",
            "from luminous_nix.security.input_validator import",
        ),
        (
            r"from luminous_nix\.security import",
            "from luminous_nix.security import",
        ),
        # XAI imports
        (
            r"from luminous_nix\.xai\.causal_xai_engine import",
            "from luminous_nix.nix_humanity.xai.engine import",
        ),
        (
            r"from luminous_nix\.xai import",
            "from luminous_nix.nix_humanity.xai import",
        ),
        # API imports
        (
            r"from luminous_nix\.interfaces import",
            "from luminous_nix.api.schema import",
        ),
        # Update class names
        (r"IntentEngine", "IntentRecognizer"),
        (r"ExecutionEngine", "SafeExecutor"),
        (r"KnowledgeBase\(\)", "KnowledgeBase()"),
        (r"PersonalitySystem", "ResponseGenerator"),
        (r"LearningSystem", "PreferenceManager"),
    ]

    # Apply replacements
    original = content
    for old, new in replacements:
        content = re.sub(old, new, content)

    # Only write if changes were made
    if content != original:
        with open(file_path, "w") as f:
            f.write(content)
        return True
    return False


def main():
    """Fix imports in all unit test files"""
    test_dir = Path("tests/unit")

    if not test_dir.exists():
        print(f"Test directory {test_dir} not found")
        return

    fixed_count = 0
    for test_file in test_dir.glob("test_*.py"):
        print(f"Checking {test_file.name}...")
        if fix_imports_in_file(test_file):
            print(f"  ✓ Fixed imports in {test_file.name}")
            fixed_count += 1

    print(f"\nFixed imports in {fixed_count} files")


if __name__ == "__main__":
    main()
