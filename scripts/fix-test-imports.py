#!/usr/bin/env python3
"""
Fix test import errors systematically.
"""

import os
import re
from pathlib import Path

def analyze_test_errors():
    """Analyze common import error patterns in tests."""
    
    import subprocess
    result = subprocess.run(
        ["poetry", "run", "pytest", "--collect-only", "-q"],
        capture_output=True,
        text=True
    )
    
    error_patterns = {
        'unified_backend': [],
        'ExecutionMode': [],
        'Query': [],
        'NixForHumanityBackend': [],
        'other': []
    }
    
    for line in result.stderr.split('\n'):
        if 'ImportError' in line or 'cannot import' in line:
            if 'unified_backend' in line:
                error_patterns['unified_backend'].append(line)
            elif 'ExecutionMode' in line:
                error_patterns['ExecutionMode'].append(line)
            elif 'Query' in line:
                error_patterns['Query'].append(line)
            elif 'NixForHumanityBackend' in line:
                error_patterns['NixForHumanityBackend'].append(line)
            else:
                error_patterns['other'].append(line)
    
    return error_patterns

def fix_common_imports(test_dir="tests"):
    """Fix common import issues in test files."""
    
    fixes_applied = 0
    
    for root, dirs, files in os.walk(test_dir):
        if '__pycache__' in root:
            continue
            
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                
                try:
                    with open(filepath, 'r') as f:
                        content = f.read()
                    
                    original = content
                    
                    # Fix unified_backend references
                    content = re.sub(
                        r'from luminous_nix\.core\.unified_backend',
                        'from luminous_nix.core.backend',
                        content
                    )
                    
                    # Fix ExecutionMode imports (should be from api.schema)
                    content = re.sub(
                        r'from luminous_nix\.core\.backend import ([^)]*\b)ExecutionMode',
                        r'from luminous_nix.api.schema import ExecutionMode\nfrom luminous_nix.core.backend import \1',
                        content
                    )
                    
                    # Fix Query imports (should be from api.schema)
                    content = re.sub(
                        r'from luminous_nix\.core\.backend import ([^)]*\b)Query',
                        r'from luminous_nix.api.schema import Query\nfrom luminous_nix.core.backend import \1',
                        content
                    )
                    
                    # Fix Context imports
                    content = re.sub(
                        r'from luminous_nix\.core\.backend import ([^)]*\b)Context',
                        r'from luminous_nix.api.schema import Context\nfrom luminous_nix.core.backend import \1',
                        content
                    )
                    
                    # Fix Result imports
                    content = re.sub(
                        r'from luminous_nix\.core\.backend import ([^)]*\b)Result',
                        r'from luminous_nix.api.schema import Result\nfrom luminous_nix.core.backend import \1',
                        content
                    )
                    
                    # Clean up duplicate import lines
                    lines = content.split('\n')
                    seen_imports = set()
                    cleaned = []
                    
                    for line in lines:
                        if line.strip().startswith('from ') or line.strip().startswith('import '):
                            if line.strip() in seen_imports:
                                continue
                            seen_imports.add(line.strip())
                        cleaned.append(line)
                    
                    content = '\n'.join(cleaned)
                    
                    # Remove empty import statements
                    content = re.sub(r'from luminous_nix\.core\.backend import\s*\n', '', content)
                    content = re.sub(r'from \.\.core\.backend import\s*\n', '', content)
                    
                    if content != original:
                        with open(filepath, 'w') as f:
                            f.write(content)
                        print(f"Fixed: {filepath}")
                        fixes_applied += 1
                        
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")
    
    return fixes_applied

def create_missing_mocks():
    """Create mock objects for missing test dependencies."""
    
    mock_content = '''"""
Test mocks for missing dependencies.
"""

from unittest.mock import MagicMock

# Mock ExecutionMode if not available
try:
    from luminous_nix.api.schema import ExecutionMode
except ImportError:
    class ExecutionMode:
        NORMAL = "normal"
        DRY_RUN = "dry_run"
        PREVIEW = "preview"

# Mock Query if not available  
try:
    from luminous_nix.api.schema import Query
except (ImportError, AttributeError):
    class Query:
        def __init__(self, text="", context=None):
            self.text = text
            self.context = context or {}

# Export mocks
__all__ = ["ExecutionMode", "Query"]
'''
    
    mock_file = "tests/test_utils/mocks.py"
    os.makedirs(os.path.dirname(mock_file), exist_ok=True)
    
    with open(mock_file, 'w') as f:
        f.write(mock_content)
    
    print(f"Created mock file: {mock_file}")

def main():
    print("🔧 Analyzing test import errors...")
    errors = analyze_test_errors()
    
    print("\n📊 Error summary:")
    for category, items in errors.items():
        if items:
            print(f"  {category}: {len(items)} errors")
    
    print("\n🔨 Fixing common import issues...")
    fixed = fix_common_imports()
    print(f"  Fixed {fixed} test files")
    
    print("\n🎭 Creating mock objects...")
    create_missing_mocks()
    
    print("\n✅ Test import fixes complete!")
    print("\nNext steps:")
    print("  1. Run: poetry run pytest --collect-only")
    print("  2. Fix any remaining specific errors")
    print("  3. Run full test suite with coverage")

if __name__ == "__main__":
    main()