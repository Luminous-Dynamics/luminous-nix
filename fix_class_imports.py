#!/usr/bin/env python3
"""Fix incorrect class imports in test files."""

import os
import re

# Map of incorrect imports to correct ones
CLASS_IMPORT_FIXES = {
    # PersonalityStyle is in personality, not responses
    "from nix_for_humanity.core.responses import PersonalityStyle": 
        "from nix_for_humanity.core.personality import PersonalityStyle",
    
    # Fix combined imports with PersonalityStyle
    "from nix_for_humanity.core.responses import PersonalityStyle, ResponseGenerator":
        "from nix_for_humanity.core.personality import PersonalityStyle\nfrom nix_for_humanity.core.responses import ResponseGenerator",
    
    # NixKnowledgeEngine is likely in knowledge module
    "from nix_for_humanity.core import NixKnowledgeEngine":
        "from nix_for_humanity.knowledge.engine import NixOSKnowledgeEngine",
    
    # PersonalitySystem -> PersonalityManager
    "from nix_for_humanity.core.personality import PersonalitySystem":
        "from nix_for_humanity.core.personality import PersonalityManager",
    
    # NixIntegration -> backend or nix_integration
    "from nix_for_humanity.core import NixIntegration":
        "from nix_for_humanity.core.nix_integration import NixIntegration",
    
    # SafeExecutor might be in executor
    "from nix_for_humanity.core.executor import SafeExecutor":
        "from nix_for_humanity.core import SafeExecutor",
        
    # LearningSystem in learning module
    "from nix_for_humanity.core import LearningSystem":
        "from nix_for_humanity.learning import LearningSystem",
}

# Find all Python test files
test_files = []
for root, dirs, files in os.walk("tests"):
    for file in files:
        if file.endswith(".py"):
            test_files.append(os.path.join(root, file))

# Also check scripts directory
for root, dirs, files in os.walk("scripts"):
    for file in files:
        if file.endswith(".py"):
            test_files.append(os.path.join(root, file))

print(f"Found {len(test_files)} Python files to check")

fixed_count = 0
for filepath in test_files:
    try:
        with open(filepath, "r") as f:
            content = f.read()
        
        original_content = content
        changed = False
        
        # Apply all import fixes
        for old_import, new_import in CLASS_IMPORT_FIXES.items():
            if old_import in content:
                content = content.replace(old_import, new_import)
                changed = True
                print(f"Fixed: {old_import}")
        
        # Also fix class name changes
        if "PersonalitySystem(" in content or "PersonalitySystem." in content:
            content = content.replace("PersonalitySystem(", "PersonalityManager(")
            content = content.replace("PersonalitySystem.", "PersonalityManager.")
            changed = True
        
        if changed:
            with open(filepath, "w") as f:
                f.write(content)
            fixed_count += 1
            print(f"✓ Fixed {filepath}")
    
    except Exception as e:
        print(f"Error processing {filepath}: {e}")

print(f"\n✅ Fixed class imports in {fixed_count} files")