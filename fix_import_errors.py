#!/usr/bin/env python3
"""
Script to identify and show import errors in test files.
"""

import os
import sys
from pathlib import Path

# Test files with collection errors
test_files = [
    "tests/test_config_generator.py",  # Fixed
    "tests/test_config_system.py",  # Fixed
    "tests/test_error_handling.py",  # Fixed
    "tests/test_performance_regression.py",
    "tests/test_tui_components.py",
    "tests/e2e/test_persona_journeys.py",
    "tests/integration/test_debug_simple.py",
    "tests/integration/test_error_intelligence_integration.py",
    "tests/integration/test_security_execution.py",
    "tests/integration/test_tui_integration.py",
    "tests/performance/test_v1_1_benchmarks.py",
    "tests/security/test_enhanced_validator.py",
    "tests/tui/test_tui_app_comprehensive.py",
    "tests/unit/test_core_coverage.py",
    "tests/unit/test_core_engine.py",
    "tests/unit/test_core_types.py",
    "tests/unit/test_learning_system.py",
    "tests/unit/test_nix_api_server.py",
    "tests/unit/test_nix_api_server_simple.py",
]

def check_file_imports(filepath):
    """Check a file for import errors"""
    print(f"\n{'='*60}")
    print(f"Checking: {filepath}")
    print('='*60)
    
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return
    
    # Try to compile the file to find syntax errors
    try:
        with open(filepath, 'r') as f:
            code = f.read()
        compile(code, filepath, 'exec')
        print("✅ No syntax errors")
    except SyntaxError as e:
        print(f"❌ Syntax error at line {e.lineno}: {e.msg}")
        if e.text:
            print(f"   {e.text.strip()}")
        return
    
    # Try to identify import errors by executing just the imports
    import_lines = []
    with open(filepath, 'r') as f:
        lines = f.readlines()
        in_import = False
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('import ') or stripped.startswith('from '):
                in_import = True
                import_lines.append((i, line))
            elif in_import and (stripped and not stripped.startswith('(') and not stripped.endswith(',') and not stripped.endswith('\\')):
                # End of multi-line import
                if not (stripped.startswith('import ') or stripped.startswith('from ')):
                    in_import = False
            elif in_import:
                import_lines.append((i, line))
    
    print(f"Found {len(import_lines)} import lines")
    
    # Check each import
    for line_num, line in import_lines:
        stripped = line.strip()
        if stripped.startswith('#'):
            continue
            
        # Extract module name from import
        if 'from ' in line:
            try:
                module = line.split('from ')[1].split(' import')[0].strip()
                print(f"  Line {line_num}: Checking module '{module}'...")
                
                # Special handling for relative imports
                if module.startswith('.'):
                    print(f"    ⚠️  Relative import - may need adjustment")
                elif 'nix_for_humanity' in module:
                    # Try to import it
                    try:
                        exec(f"import {module}")
                        print(f"    ✅ Module exists")
                    except ImportError as e:
                        print(f"    ❌ Import error: {e}")
            except:
                pass

if __name__ == "__main__":
    for test_file in test_files:
        check_file_imports(test_file)
    
    print("\n" + "="*60)
    print("Summary: Check complete")
    print("="*60)