#!/usr/bin/env python3
"""
Fix all test import issues comprehensively.
"""

import os
import re
import ast
import subprocess
from pathlib import Path
from typing import Set, Dict, List

def find_missing_imports() -> Dict[str, Set[str]]:
    """Find all missing imports by analyzing test errors."""
    
    missing = {}
    
    # Run pytest to collect errors
    result = subprocess.run(
        ["poetry", "run", "pytest", "--collect-only", "tests/unit/", "-q"],
        capture_output=True,
        text=True,
        cwd="/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity"
    )
    
    # Parse errors
    for line in result.stderr.split('\n'):
        if "cannot import name" in line:
            match = re.search(r"cannot import name '([^']+)' from '([^']+)'", line)
            if match:
                name, module = match.groups()
                if module not in missing:
                    missing[module] = set()
                missing[module].add(name)
    
    return missing

def find_actual_locations() -> Dict[str, str]:
    """Find where classes and functions are actually defined."""
    
    locations = {}
    
    # Common imports and their actual locations
    mappings = {
        'ValidationResult': 'luminous_nix.core.executor',
        'SafeExecutor': 'luminous_nix.core.executor',
        'PersonalityStyle': 'luminous_nix.core.personality',
        'Command': 'luminous_nix.api.schema',
        'Context': 'luminous_nix.api.schema',
        'Result': 'luminous_nix.api.schema',
        'Query': 'luminous_nix.api.schema',
        'CLIAdapter': 'luminous_nix.cli',
        'CacheLayer': 'luminous_nix.cache.redis_cache',
        'RedisCache': 'luminous_nix.cache.redis_cache',
        'LearningMetrics': 'luminous_nix.learning.patterns',
        'LearningMode': 'luminous_nix.learning.patterns',
        'UserPattern': 'luminous_nix.learning.patterns',
        'ExecutionContext': 'luminous_nix.types',
        'QueryResult': 'luminous_nix.types',
    }
    
    return mappings

def fix_imports_in_file(filepath: str, mappings: Dict[str, str]) -> bool:
    """Fix imports in a single file."""
    
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        original = content
        
        # Fix ValidationResult import
        content = re.sub(
            r'from luminous_nix\.core import ([^)]*\b)ValidationResult',
            r'from luminous_nix.core.executor import ValidationResult\nfrom luminous_nix.core import \1',
            content
        )
        
        # Fix PersonalityStyle import
        content = re.sub(
            r'from luminous_nix\.core import ([^)]*\b)PersonalityStyle',
            r'from luminous_nix.core.personality import PersonalityStyle\nfrom luminous_nix.core import \1',
            content
        )
        
        # Fix Command, Context, Query, Result imports
        content = re.sub(
            r'from luminous_nix\.core\.intents import Command',
            'from luminous_nix.api.schema import Context',
            content
        )
        
        # Fix CLIAdapter imports
        content = re.sub(
            r'from luminous_nix\.adapters\.cli_adapter import CLIAdapter',
            'from scripts.adapters.cli_adapter import CLIAdapter',
            content
        )
        
        # Fix caching imports
        content = re.sub(
            r'from luminous_nix\.caching import',
            'from luminous_nix.cache.redis_cache import',
            content
        )
        
        # Fix learning imports
        content = re.sub(
            r'from luminous_nix\.learning\.preferences import LearningMetrics',
            'from luminous_nix.learning.patterns import UserPattern as LearningMetrics',
            content
        )
        
        # Clean up empty import statements
        content = re.sub(r'from luminous_nix\.core import\s*\n', '', content)
        content = re.sub(r'from luminous_nix\.core\.backend import\s*\n', '', content)
        
        # Remove duplicate imports
        lines = content.split('\n')
        seen_imports = set()
        cleaned = []
        
        for line in lines:
            if line.strip().startswith(('from ', 'import ')):
                if line.strip() not in seen_imports:
                    seen_imports.add(line.strip())
                    cleaned.append(line)
            else:
                cleaned.append(line)
        
        content = '\n'.join(cleaned)
        
        if content != original:
            with open(filepath, 'w') as f:
                f.write(content)
            return True
            
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
    
    return False

def add_missing_exports():
    """Add missing exports to __init__ files."""
    
    # Add ValidationResult to core/__init__.py
    core_init = "src/nix_for_humanity/core/__init__.py"
    
    with open(core_init, 'r') as f:
        content = f.read()
    
    if 'ValidationResult' not in content:
        # Add import
        content = content.replace(
            'from .executor import SafeExecutor',
            'from .executor import SafeExecutor, ValidationResult'
        )
        
        # Add to __all__
        content = content.replace(
            '"SafeExecutor",',
            '"SafeExecutor",\n    "ValidationResult",'
        )
        
        with open(core_init, 'w') as f:
            f.write(content)
        
        print(f"Added ValidationResult to {core_init}")

def main():
    print("🔧 Fixing all test import issues...")
    
    # Step 1: Add missing exports
    print("\n📦 Adding missing exports...")
    add_missing_exports()
    
    # Step 2: Get import mappings
    mappings = find_actual_locations()
    
    # Step 3: Fix all test files
    print("\n🔨 Fixing test imports...")
    fixed = 0
    
    for root, dirs, files in os.walk("tests"):
        if '__pycache__' in root:
            continue
            
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                if fix_imports_in_file(filepath, mappings):
                    print(f"  Fixed: {filepath}")
                    fixed += 1
    
    print(f"\n✅ Fixed {fixed} test files")
    
    # Step 4: Verify fixes
    print("\n🧪 Verifying fixes...")
    result = subprocess.run(
        ["poetry", "run", "pytest", "--collect-only", "tests/unit/", "-q"],
        capture_output=True,
        text=True,
        cwd="/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity"
    )
    
    # Count collected tests
    if "collected" in result.stdout:
        match = re.search(r"collected (\d+) item", result.stdout)
        if match:
            print(f"✅ Successfully collected {match.group(1)} tests!")
    
    # Check for remaining errors
    error_count = result.stderr.count("ERROR")
    if error_count > 0:
        print(f"⚠️  Still {error_count} import errors remaining")
        print("\nRemaining errors:")
        for line in result.stderr.split('\n'):
            if "ImportError" in line or "ModuleNotFoundError" in line:
                print(f"  {line.strip()}")
    else:
        print("✅ All import errors fixed!")

if __name__ == "__main__":
    main()