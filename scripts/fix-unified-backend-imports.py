#!/usr/bin/env python3
"""
Fix all imports from unified_backend to use backend instead.
"""

import os
import re
from pathlib import Path

def fix_unified_backend_imports(directory: str = "."):
    """Find and fix all unified_backend imports."""
    
    files_fixed = 0
    
    for root, dirs, files in os.walk(directory):
        # Skip certain directories
        if any(skip in root for skip in ['.git', '__pycache__', '.venv', 'archive', 'node_modules']):
            continue
            
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                
                try:
                    with open(filepath, 'r') as f:
                        content = f.read()
                    
                    original_content = content
                    
                    # Fix various import patterns
                    replacements = [
                        # Direct unified_backend imports
                        (r'from luminous_nix\.core\.unified_backend import',
                         'from luminous_nix.core.backend import'),
                        (r'from \.\.core\.unified_backend import',
                         'from ..core.backend import'),
                        (r'from \.unified_backend import',
                         'from .backend import'),
                        
                        # Import unified_backend module
                        (r'import luminous_nix\.core\.unified_backend',
                         'import luminous_nix.core.backend'),
                         
                        # Fix Context and Result imports
                        (r'from luminous_nix\.core\.backend import ([^(]*)?Context',
                         r'from luminous_nix.api.schema import Context\nfrom luminous_nix.core.backend import \1'),
                        (r'from \.\.core\.backend import ([^(]*)?Context',
                         r'from ..api.schema import Context\nfrom ..core.backend import \1'),
                    ]
                    
                    for pattern, replacement in replacements:
                        content = re.sub(pattern, replacement, content)
                    
                    # Clean up duplicate imports
                    lines = content.split('\n')
                    cleaned_lines = []
                    seen_imports = set()
                    
                    for line in lines:
                        # Skip duplicate import lines
                        if line.startswith('from ') or line.startswith('import '):
                            import_sig = line.strip()
                            if import_sig in seen_imports:
                                continue
                            seen_imports.add(import_sig)
                        cleaned_lines.append(line)
                    
                    content = '\n'.join(cleaned_lines)
                    
                    if content != original_content:
                        with open(filepath, 'w') as f:
                            f.write(content)
                        print(f"Fixed: {filepath}")
                        files_fixed += 1
                        
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")
    
    return files_fixed

def main():
    print("🔧 Fixing unified_backend imports...")
    
    # Fix source files
    fixed_src = fix_unified_backend_imports("src/")
    print(f"  Fixed {fixed_src} files in src/")
    
    # Fix bin files
    fixed_bin = fix_unified_backend_imports("bin/")
    print(f"  Fixed {fixed_bin} files in bin/")
    
    # Fix test files
    fixed_tests = fix_unified_backend_imports("tests/")
    print(f"  Fixed {fixed_tests} files in tests/")
    
    # Fix scripts
    fixed_scripts = fix_unified_backend_imports("scripts/")
    print(f"  Fixed {fixed_scripts} files in scripts/")
    
    total = fixed_src + fixed_bin + fixed_tests + fixed_scripts
    print(f"\n✅ Total files fixed: {total}")
    
    if total > 0:
        print("\n📝 Note: Some imports may need manual adjustment if they import")
        print("   Context or Result from backend instead of api.schema")

if __name__ == "__main__":
    main()