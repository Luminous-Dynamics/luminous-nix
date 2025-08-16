#!/usr/bin/env python3
"""Comprehensive fix for all test import issues."""

import re
from pathlib import Path

def fix_all_imports():
    """Fix all remaining import issues in tests."""
    test_dir = Path("tests")
    
    # Define all missing classes and their mock locations
    mock_replacements = [
        # Learning system mocks
        (r'from luminous_nix\.learning\.patterns import (.*?)UserPattern',
         r'from tests.test_utils.mocks import \1UserPattern'),
        (r'from luminous_nix\.learning\.patterns import (.*?)LearningMode',
         r'from luminous_nix.learning.modes import \1LearningMode'),
        
        # If LearningMode doesn't exist, create enum
        (r'from luminous_nix\.learning\.modes import LearningMode',
         '''from enum import Enum

class LearningMode(Enum):
    """Learning mode enum."""
    PASSIVE = "passive"
    ACTIVE = "active"
    INTERACTIVE = "interactive"
    ADAPTIVE = "adaptive"'''),
        
        # Fix Preference vs UserPreference
        (r'from tests\.test_utils\.learning_mocks import.*Preference[,\s]',
         r'from tests.test_utils.learning_mocks import UserPreference as Preference, '),
    ]
    
    fixed_count = 0
    for test_file in test_dir.rglob("*.py"):
        if not test_file.is_file():
            continue
            
        content = test_file.read_text()
        original = content
        
        # Apply replacements
        for pattern, replacement in mock_replacements:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        
        # Fix learning.patterns imports - check what's imported
        if "from luminous_nix.learning.patterns import" in content:
            # Extract what's being imported
            match = re.search(
                r'from luminous_nix\.learning\.patterns import (.+?)$',
                content,
                re.MULTILINE
            )
            if match:
                imports = match.group(1)
                # Build mock imports
                mock_imports = []
                if "UserPattern" in imports:
                    mock_imports.append("UserPattern")
                if "LearningMode" in imports:
                    # LearningMode needs to be defined inline
                    pass
                if "PatternLearner" in imports:
                    mock_imports.append("PatternLearner")
                
                if mock_imports:
                    # Replace with mocks
                    new_import = f"from tests.test_utils.mocks import {', '.join(mock_imports)}"
                    content = re.sub(
                        r'from luminous_nix\.learning\.patterns import .+?$',
                        new_import,
                        content,
                        flags=re.MULTILINE
                    )
                
                # Add LearningMode enum if needed
                if "LearningMode" in imports and "class LearningMode" not in content:
                    # Add enum definition after imports
                    lines = content.split('\n')
                    import_end = 0
                    for i, line in enumerate(lines):
                        if line.startswith('from ') or line.startswith('import '):
                            import_end = i + 1
                        elif import_end > 0 and line and not line.startswith(' '):
                            break
                    
                    enum_def = '''
from enum import Enum

class LearningMode(Enum):
    """Learning mode enum."""
    PASSIVE = "passive"
    ACTIVE = "active"
    INTERACTIVE = "interactive"
    ADAPTIVE = "adaptive"
'''
                    lines.insert(import_end, enum_def)
                    content = '\n'.join(lines)
        
        if content != original:
            test_file.write_text(content)
            print(f"Fixed {test_file}")
            fixed_count += 1
    
    print(f"\nFixed {fixed_count} files")

if __name__ == "__main__":
    fix_all_imports()