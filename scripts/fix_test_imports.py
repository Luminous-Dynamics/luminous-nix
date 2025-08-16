#!/usr/bin/env python3
"""Fix test imports to use NixForHumanityBackend instead of NixForHumanityCore"""

import os
import re

# Files to fix
test_files = [
    "tests/unit/test_cli_adapter_comprehensive_v2.py",
    "tests/unit/test_core_engine.py",
    "tests/integration/test_cli_core_pipeline.py",
    "tests/e2e/test_persona_journeys.py",
    "tests/unit/test_engine_enhanced.py",
    "tests/unit/test_headless_engine.py",
    "tests/integration/test_cli_core_pipeline_simple.py",
    "tests/test_core.py",
    "tests/test_tui.py",
    "tests/unit/test_tui_app.py",
    "tests/unit/test_tui_xai_integration.py",
    "tests/unit/test_tui_app_simple.py",
    "tests/unit/test_cli_adapter_comprehensive.py",
    "tests/integration/test_debug_simple.py",
    "tests/cli/test_cli_adapter_comprehensive.py",
]

replacements = [
    # Simple replacements
    (r"\bNixForHumanityCore\b", "NixForHumanityBackend"),
    # Import statement replacements
    (
        r"from luminous_nix\.core import NixForHumanityCore",
        "from luminous_nix.core import NixForHumanityBackend",
    ),
    (
        r"from luminous_nix\.core import (.*?)NixForHumanityCore",
        r"from luminous_nix.core import \1NixForHumanityBackend",
    ),
    # Fix Query and ExecutionMode imports
    (
        r"from luminous_nix\.core import (.*?), Query, ExecutionMode",
        r"from luminous_nix.core import \1",
    ),
    (r"from luminous_nix\.core import Query, ExecutionMode", ""),
]

fixed_count = 0

for test_file in test_files:
    if not os.path.exists(test_file):
        print(f"⚠️  File not found: {test_file}")
        continue

    try:
        with open(test_file) as f:
            content = f.read()

        original_content = content

        # Apply replacements
        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content)

        # Remove empty import lines
        content = re.sub(r"\nfrom luminous_nix\.core import\s*\n", "\n", content)

        if content != original_content:
            with open(test_file, "w") as f:
                f.write(content)
            print(f"✅ Fixed: {test_file}")
            fixed_count += 1
        else:
            print(f"  No changes needed: {test_file}")

    except Exception as e:
        print(f"❌ Error processing {test_file}: {e}")

print(f"\n✅ Fixed {fixed_count} files")
