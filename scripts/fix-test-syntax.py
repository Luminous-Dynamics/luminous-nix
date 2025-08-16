#!/usr/bin/env python3
"""
Fix syntax errors in test files.
"""

import os
import re
import ast
from pathlib import Path

def fix_syntax_errors(directory="tests"):
    """Fix common syntax errors in test files."""
    
    fixed = 0
    
    for root, dirs, files in os.walk(directory):
        if '__pycache__' in root:
            continue
            
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                
                try:
                    with open(filepath, 'r') as f:
                        content = f.read()
                    
                    original = content
                    
                    # Fix trailing commas in imports
                    content = re.sub(
                        r'from ([^)]+) import ([^,\n]+),\s*\n',
                        r'from \1 import \2\n',
                        content
                    )
                    
                    # Fix empty imports after commas
                    content = re.sub(
                        r'from ([^)]+) import ([^,]+),\s*,',
                        r'from \1 import \2,',
                        content
                    )
                    
                    # Fix double commas
                    content = re.sub(r',,', ',', content)
                    
                    # Fix incomplete imports (missing name after PersonalityStyle)
                    content = re.sub(
                        r'from luminous_nix\.core\.personality import\s*\n',
                        'from luminous_nix.core.personality import PersonalityStyle\n',
                        content
                    )
                    
                    # Fix imports with trailing comma and nothing after
                    content = re.sub(
                        r'from ([^)]+) import ([^,\n]+),\s*$',
                        r'from \1 import \2',
                        content, flags=re.MULTILINE
                    )
                    
                    # Try to compile to check for syntax errors
                    try:
                        compile(content, filepath, 'exec')
                    except SyntaxError as e:
                        print(f"Syntax error in {filepath}: {e}")
                        
                        # Additional fixes based on error
                        if "trailing comma" in str(e):
                            # Remove trailing commas in import statements
                            lines = content.split('\n')
                            for i, line in enumerate(lines):
                                if 'import' in line and line.strip().endswith(','):
                                    lines[i] = line.rstrip(',')
                            content = '\n'.join(lines)
                    
                    if content != original:
                        with open(filepath, 'w') as f:
                            f.write(content)
                        print(f"Fixed: {filepath}")
                        fixed += 1
                        
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")
    
    return fixed

def main():
    print("🔧 Fixing syntax errors in test files...")
    
    fixed = fix_syntax_errors()
    print(f"\n✅ Fixed {fixed} files")
    
    # Verify all files compile
    print("\n🧪 Verifying all test files compile...")
    errors = 0
    
    for root, dirs, files in os.walk("tests"):
        if '__pycache__' in root:
            continue
            
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                
                try:
                    with open(filepath, 'r') as f:
                        compile(f.read(), filepath, 'exec')
                except SyntaxError as e:
                    print(f"❌ Still has syntax error: {filepath}")
                    print(f"   {e}")
                    errors += 1
    
    if errors == 0:
        print("✅ All test files compile successfully!")
    else:
        print(f"⚠️  {errors} files still have syntax errors")

if __name__ == "__main__":
    main()