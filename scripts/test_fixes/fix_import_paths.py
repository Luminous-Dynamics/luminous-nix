#!/usr/bin/env python3
"""Fix incorrect import paths in test files."""

import os
import re

# Map of incorrect imports to correct ones
IMPORT_FIXES = {
    "from luminous_nix.core.interface import": "from luminous_nix.core import",
    "from luminous_nix.core.types import": "from luminous_nix.types import",
    "from luminous_nix.core.intents import IntentType": "from luminous_nix.core import IntentType",
    "from luminous_nix.core.intent import": "from luminous_nix.core import",
    "from luminous_nix.intent_engine import": "from luminous_nix.core import",
    "from luminous_nix.engine import": "from luminous_nix.core.engine import",
    "from luminous_nix.headless import": "from luminous_nix.core import",
    "from luminous_nix.backend import": "from luminous_nix.core import",
    "from luminous_nix.knowledge_base import": "from luminous_nix.core.knowledge import",
    "from luminous_nix.personality import": "from luminous_nix.core.personality import",
    "from luminous_nix.nlp import": "from luminous_nix.ai.nlp import",
}

# Find all Python test files
test_files = []
for root, dirs, files in os.walk("tests"):
    for file in files:
        if file.endswith(".py"):
            test_files.append(os.path.join(root, file))

print(f"Found {len(test_files)} test files to check")

fixed_count = 0
for filepath in test_files:
    try:
        with open(filepath, "r") as f:
            content = f.read()
        
        original_content = content
        changed = False
        
        # Apply all import fixes
        for old_import, new_import in IMPORT_FIXES.items():
            if old_import in content:
                content = content.replace(old_import, new_import)
                changed = True
                print(f"Fixed import in {filepath}: {old_import} -> {new_import}")
        
        # Fix specific class imports that might be on separate lines
        if "IntentType" in content and "from luminous_nix" in content:
            # Make sure IntentType imports are from the right place
            content = re.sub(
                r'from luminous_nix\.[a-z_.]+? import ([^,\n]*,\s*)?IntentType',
                r'from luminous_nix.core import \1IntentType',
                content
            )
            if content != original_content:
                changed = True
        
        if changed:
            with open(filepath, "w") as f:
                f.write(content)
            fixed_count += 1
            print(f"✓ Fixed {filepath}")
    
    except Exception as e:
        print(f"Error processing {filepath}: {e}")

print(f"\n✅ Fixed imports in {fixed_count} files")