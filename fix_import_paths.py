#!/usr/bin/env python3
"""Fix incorrect import paths in test files."""

import os
import re

# Map of incorrect imports to correct ones
IMPORT_FIXES = {
    "from nix_for_humanity.core.interface import": "from nix_for_humanity.core import",
    "from nix_for_humanity.core.types import": "from nix_for_humanity.types import",
    "from nix_for_humanity.core.intents import IntentType": "from nix_for_humanity.core import IntentType",
    "from nix_for_humanity.core.intent import": "from nix_for_humanity.core import",
    "from nix_for_humanity.intent_engine import": "from nix_for_humanity.core import",
    "from nix_for_humanity.engine import": "from nix_for_humanity.core.engine import",
    "from nix_for_humanity.headless import": "from nix_for_humanity.core import",
    "from nix_for_humanity.backend import": "from nix_for_humanity.core import",
    "from nix_for_humanity.knowledge_base import": "from nix_for_humanity.core.knowledge import",
    "from nix_for_humanity.personality import": "from nix_for_humanity.core.personality import",
    "from nix_for_humanity.nlp import": "from nix_for_humanity.ai.nlp import",
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
        if "IntentType" in content and "from nix_for_humanity" in content:
            # Make sure IntentType imports are from the right place
            content = re.sub(
                r'from nix_for_humanity\.[a-z_.]+? import ([^,\n]*,\s*)?IntentType',
                r'from nix_for_humanity.core import \1IntentType',
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