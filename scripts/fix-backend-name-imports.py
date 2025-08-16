#!/usr/bin/env python3
"""
Fix the NixForHumanityCore -> NixForHumanityBackend renaming issue.
"""

import os
import re
from pathlib import Path

def fix_backend_naming():
    """Fix all references to NixForHumanityCore -> NixForHumanityBackend."""
    
    test_dir = Path("/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/tests")
    fixed = 0
    
    # Also fix other common naming issues
    replacements = [
        # Core -> Backend renaming
        (r'NixForHumanityCore', 'NixForHumanityBackend'),
        
        # Fix import paths
        (r'from luminous_nix\.core\.engine import NixForHumanityBackend',
         'from luminous_nix.core.engine import NixForHumanityBackend'),
         
        # Fix unified_backend references
        (r'from luminous_nix\.core\.unified_backend', 
         'from luminous_nix.core.backend'),
         
        # Fix ExecutionMode (doesn't exist anymore)
        (r'ExecutionMode\.DRY_RUN', '"dry_run"'),
        (r'ExecutionMode\.NORMAL', '"normal"'),
        (r'ExecutionMode', 'str'),
        
        # Fix Response import
        (r'from luminous_nix\.core import.*Response',
         'from luminous_nix.api.schema import Response'),
         
        # Fix test utils imports
        (r'from test_utils', 'from tests.test_utils'),
        
        # Fix planning module (if it doesn't exist)
        (r'from luminous_nix\.core\.planning import Plan',
         'from luminous_nix.types import dict as Plan'),
    ]
    
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
                    
                    for pattern, replacement in replacements:
                        content = re.sub(pattern, replacement, content)
                    
                    if content != original:
                        with open(filepath, 'w') as f:
                            f.write(content)
                        print(f"Fixed: {filepath}")
                        fixed += 1
                        
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")
    
    return fixed

def main():
    print("🔧 Fixing backend naming issues...")
    
    fixed = fix_backend_naming()
    print(f"\n✅ Fixed {fixed} files")
    
    # Test if it works now
    import subprocess
    result = subprocess.run(
        ["poetry", "run", "pytest", "--collect-only", "tests/unit/", "-q"],
        capture_output=True,
        text=True,
        cwd="/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity"
    )
    
    errors = result.stderr.count("ERROR collecting")
    if errors > 0:
        print(f"\n⚠️  Still {errors} collection errors")
        
        # Show first few errors
        print("\nRemaining errors:")
        for line in result.stderr.split('\n'):
            if "ImportError" in line or "ModuleNotFoundError" in line:
                print(f"  {line.strip()}")
                if "cannot import name" in line:
                    match = re.search(r"cannot import name '([^']+)'", line)
                    if match:
                        print(f"    -> Need to fix: {match.group(1)}")
    else:
        print("\n✅ All collection errors fixed!")
        
        # Count tests
        if "collected" in result.stdout:
            match = re.search(r"collected (\d+) item", result.stdout)
            if match:
                print(f"✅ Successfully collected {match.group(1)} tests!")

if __name__ == "__main__":
    main()