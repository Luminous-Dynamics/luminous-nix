#!/usr/bin/env python3
"""
Skip all NixOS-dependent tests to establish real baseline coverage.
These tests can't run in development/CI without NixOS.
"""

import os
from pathlib import Path

def add_pytest_skip(file_path):
    """Add pytest.skip to files that require NixOS"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check if already has skip
    if "pytest.skip" in content and "allow_module_level=True" in content:
        return False
        
    # Check if it needs NixOS
    needs_nixos = any([
        "NativeOperations" in content,
        "native_operations" in content,
        "NativeNixBackend" in content,
        "/nix/store" in content,
        "nixos_rebuild" in content,
        "from python.native_nix_backend" in content,
    ])
    
    if needs_nixos:
        # Add skip at the top
        skip_code = '''import pytest
import os

# Skip if not on NixOS
if not os.path.exists("/nix/store"):
    pytest.skip("NixOS required for this test", allow_module_level=True)

'''
        # Insert after imports
        lines = content.split('\n')
        insert_pos = 0
        for i, line in enumerate(lines):
            if line.strip() and not line.startswith('#') and not line.startswith('import') and not line.startswith('from'):
                insert_pos = i
                break
        
        if insert_pos > 0:
            lines.insert(insert_pos, skip_code)
            with open(file_path, 'w') as f:
                f.write('\n'.join(lines))
            return True
    return False

def main():
    test_dir = Path("tests")
    skipped = []
    
    for test_file in test_dir.rglob("test_*.py"):
        if add_pytest_skip(test_file):
            skipped.append(test_file)
    
    print(f"✅ Skipped {len(skipped)} NixOS-dependent test files:")
    for f in skipped:
        print(f"   - {f}")
    
    print("\n📊 Now run: poetry run pytest --co -q | wc -l")
    print("   to see how many tests can actually run")

if __name__ == "__main__":
    main()