#!/usr/bin/env python3
"""
Fix test imports to use backend/ instead of nix_for_humanity
"""

import re
from pathlib import Path


def fix_imports_in_file(file_path):
    """Fix imports in a single file"""
    with open(file_path) as f:
        content = f.read()

    original_content = content

    # Map of replacements
    replacements = [
        # Core modules
        (
            r"from luminous_nix\.core\.engine import",
            "from luminous_nix.core.engine import",
        ),
        (
            r"from luminous_nix\.core\.types import",
            "from luminous_nix.core.intents import",
        ),
        (
            r"from luminous_nix\.core\.intent_engine import",
            "from luminous_nix.core.intents import",
        ),
        (
            r"from luminous_nix\.core\.intent import",
            "from luminous_nix.core.intents import",
        ),
        (
            r"from luminous_nix\.core\.execution_engine import",
            "from luminous_nix.core.executor import",
        ),
        (
            r"from luminous_nix\.core\.executor import",
            "from luminous_nix.core.executor import",
        ),
        (
            r"from luminous_nix\.core\.knowledge_base import",
            "from luminous_nix.core.knowledge import",
        ),
        (
            r"from luminous_nix\.core\.knowledge import",
            "from luminous_nix.core.knowledge import",
        ),
        (
            r"from luminous_nix\.core\.backend import",
            "from luminous_nix.core.engine import",
        ),
        (
            r"from luminous_nix\.core\.personality_system import",
            "from luminous_nix.core.personality import",
        ),
        (
            r"from luminous_nix\.core\.interface import",
            "from luminous_nix.core.interface import",
        ),
        # NLP modules
        (
            r"from luminous_nix\.nlp\.intent_engine import",
            "from luminous_nix.core.intents import",
        ),
        (
            r"from luminous_nix\.nlp\.pattern_matcher import",
            "from luminous_nix.core.intents import",
        ),
        # Learning modules
        (
            r"from luminous_nix\.learning\.preferences import",
            "from luminous_nix.learning.preferences import",
        ),
        (
            r"from luminous_nix\.learning\.pattern_learner import",
            "from luminous_nix.learning.pattern_learner import",
        ),
        # XAI modules
        (
            r"from luminous_nix\.xai\.engine import",
            "from luminous_nix.xai.engine import",
        ),
        (
            r"from luminous_nix\.xai\.causal_engine import",
            "from luminous_nix.xai.causal_engine import",
        ),
        (
            r"from luminous_nix\.xai\.explanation_formatter import",
            "from luminous_nix.xai.explanation_formatter import",
        ),
        # TUI modules
        (
            r"from luminous_nix\.tui\.app import",
            "from luminous_nix.tui.app import",
        ),
        (
            r"from luminous_nix\.tui\.enhanced_app import",
            "from luminous_nix.tui.enhanced_app import",
        ),
        (
            r"from luminous_nix\.tui\.persona_styles import",
            "from luminous_nix.tui.persona_styles import",
        ),
        # Voice modules
        (
            r"from luminous_nix\.voice\.interface import",
            "from luminous_nix.voice.interface import",
        ),
        (
            r"from luminous_nix\.voice\.model_manager import",
            "from luminous_nix.voice.model_manager import",
        ),
        (
            r"from luminous_nix\.voice\.voice_config import",
            "from luminous_nix.voice.voice_config import",
        ),
        # Security modules
        (
            r"from luminous_nix\.security\.validator import",
            "from luminous_nix.security.validator import",
        ),
        (
            r"from luminous_nix\.security\.enhanced_validator import",
            "from luminous_nix.security.enhanced_validator import",
        ),
        # Accessibility modules
        (
            r"from luminous_nix\.accessibility\.screen_reader import",
            "from luminous_nix.accessibility.screen_reader import",
        ),
        (
            r"from luminous_nix\.accessibility\.persona_accessibility import",
            "from luminous_nix.accessibility.persona_accessibility import",
        ),
        # Monitoring modules
        (
            r"from luminous_nix\.monitoring\.performance_monitor import",
            "from luminous_nix.monitoring.performance_monitor import",
        ),
        # Adapters
        (
            r"from luminous_nix\.adapters\.cli_adapter import",
            "from luminous_nix.adapters.cli_adapter import",
        ),
        # Caching modules
        (
            r"from luminous_nix\.caching\.response_cache import",
            "from luminous_nix.caching.response_cache import",
        ),
        (
            r"from luminous_nix\.caching\.xai_cache import",
            "from luminous_nix.caching.xai_cache import",
        ),
        # Testing modules
        (
            r"from luminous_nix\.testing\.persona_testing_framework import",
            "from luminous_nix.testing.persona_testing_framework import",
        ),
        # General catch-all for any missed imports
        (r"from luminous_nix\.", "from luminous_nix."),
        (r"import luminous_nix\.", "import luminous_nix."),
    ]

    # Apply replacements
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)

    # Write back if changed
    if content != original_content:
        with open(file_path, "w") as f:
            f.write(content)
        return True
    return False


def main():
    """Fix imports in all test files"""
    test_dir = Path(__file__).parent / "tests"

    fixed_count = 0
    total_count = 0

    # Find all Python test files
    for test_file in test_dir.rglob("*.py"):
        total_count += 1
        if fix_imports_in_file(test_file):
            fixed_count += 1
            print(f"Fixed imports in: {test_file.relative_to(test_dir.parent)}")

    print(f"\nFixed {fixed_count} out of {total_count} test files")


if __name__ == "__main__":
    main()
