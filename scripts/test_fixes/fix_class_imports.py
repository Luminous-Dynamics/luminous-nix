#!/usr/bin/env python3
"""Fix incorrect class imports in test files."""

import os
import re

# Map of incorrect imports to correct ones
CLASS_IMPORT_FIXES = {
    # PersonalityStyle is in personality, not responses
    "from luminous_nix.core.responses import PersonalityStyle": 
        "from luminous_nix.core.personality import PersonalityStyle",
    
    # Fix combined imports with PersonalityStyle
    "from luminous_nix.core.responses import PersonalityStyle, ResponseGenerator":
        "from luminous_nix.core.personality import PersonalityStyle\nfrom luminous_nix.core.responses import ResponseGenerator",
    
    # NixKnowledgeEngine is likely in knowledge module
    "from luminous_nix.core import NixKnowledgeEngine":
        "from luminous_nix.knowledge.engine import NixOSKnowledgeEngine",
    
    # PersonalitySystem -> PersonalityManager
    "from luminous_nix.core.personality import PersonalitySystem":
        "from luminous_nix.core.personality import PersonalityManager",
    
    # NixIntegration -> backend or nix_integration
    "from luminous_nix.core import NixIntegration":
        "from luminous_nix.core.nix_integration import NixIntegration",
    
    # SafeExecutor might be in executor
    "from luminous_nix.core.executor import SafeExecutor":
        "from luminous_nix.core import SafeExecutor",
        
    # LearningSystem in learning module
    "from luminous_nix.core import LearningSystem":
        "from luminous_nix.learning import LearningSystem",
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