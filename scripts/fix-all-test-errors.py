#!/usr/bin/env python3
"""
Comprehensive script to fix ALL test collection errors.
"""

import os
import re
import ast
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Tuple

class TestFixer:
    def __init__(self):
        self.project_root = Path("/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity")
        self.src_path = self.project_root / "src"
        self.tests_path = self.project_root / "tests"
        
        # Map of where things actually are
        self.import_map = {
            # Core module
            'ValidationResult': 'luminous_nix.core.executor',
            'SafeExecutor': 'luminous_nix.core.executor',
            'Intent': 'luminous_nix.core.intents',
            'IntentType': 'luminous_nix.core.intents',
            'IntentRecognizer': 'luminous_nix.core.intents',
            
            # API/Schema
            'Context': 'luminous_nix.api.schema',
            'Result': 'luminous_nix.api.schema',
            'Query': 'luminous_nix.api.schema',
            'Request': 'luminous_nix.api.schema',
            'Response': 'luminous_nix.api.schema',
            'ExecutionResult': 'luminous_nix.api.schema',
            
            # Backend
            'NixForHumanityBackend': 'luminous_nix.core.backend',
            'get_backend': 'luminous_nix.core.backend',
            'create_backend': 'luminous_nix.core.backend',
            
            # Personality
            'PersonalityStyle': 'luminous_nix.core.personality',
            'PersonalityManager': 'luminous_nix.core.personality',
            'PersonalitySystem': 'luminous_nix.core.personality',
            
            # Types
            'ExecutionContext': 'luminous_nix.types',
            'QueryResult': 'luminous_nix.types',
            'Command': 'luminous_nix.types',
            
            # Learning
            'LearningMetrics': 'luminous_nix.learning.patterns',
            'UserPattern': 'luminous_nix.learning.patterns',
            'LearningMode': 'luminous_nix.learning.patterns',
            'PreferenceManager': 'luminous_nix.learning.preferences',
            
            # CLI
            'CLIAdapter': 'scripts.adapters.cli_adapter',
            
            # Cache
            'CacheLayer': 'luminous_nix.cache.redis_cache',
            'RedisCache': 'luminous_nix.cache.redis_cache',
            'CacheManager': 'luminous_nix.cache.redis_cache',
        }
        
        self.errors_fixed = 0
        self.files_processed = 0

    def get_test_errors(self) -> Dict[str, List[str]]:
        """Get all test collection errors."""
        result = subprocess.run(
            ["poetry", "run", "pytest", "--collect-only", "tests/unit/", "-q"],
            capture_output=True,
            text=True,
            cwd=str(self.project_root)
        )
        
        errors = {}
        current_file = None
        
        for line in result.stderr.split('\n'):
            if "ERROR collecting" in line:
                match = re.search(r'ERROR collecting (tests/[^:]+\.py)', line)
                if match:
                    current_file = match.group(1)
                    errors[current_file] = []
            elif current_file and ("ImportError" in line or "ModuleNotFoundError" in line):
                errors[current_file].append(line)
        
        return errors

    def fix_imports_in_file(self, filepath: str) -> bool:
        """Fix all import issues in a single file."""
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            
            original = content
            
            # Fix common import patterns
            fixes = [
                # Remove duplicate imports on same line
                (r'from ([^)]+) import ([^,]+),\s*,', r'from \1 import \2,'),
                
                # Fix trailing commas in imports
                (r'from ([^)]+) import ([^,\n]+),\s*$', r'from \1 import \2', re.MULTILINE),
                
                # Fix empty imports after comma
                (r'from ([^)]+) import ([^,]+),\s*\n', r'from \1 import \2\n'),
                
                # Fix unified_backend references
                (r'from luminous_nix\.core\.unified_backend', 
                 'from luminous_nix.core.backend'),
                
                # Fix adapters module (doesn't exist)
                (r'from luminous_nix\.adapters\.cli_adapter',
                 'from scripts.adapters.cli_adapter'),
                
                # Fix caching module (should be cache.redis_cache)
                (r'from luminous_nix\.caching\b',
                 'from luminous_nix.cache.redis_cache'),
                
                # Fix Command import from intents (should be from types)
                (r'from luminous_nix\.core\.intents import Command',
                 'from luminous_nix.types import Command'),
                
                # Fix missing module paths
                (r'from luminous_nix\.core import ValidationResult',
                 'from luminous_nix.core.executor import ValidationResult'),
                
                (r'from luminous_nix\.core import PersonalityStyle',
                 'from luminous_nix.core.personality import PersonalityStyle'),
            ]
            
            for pattern, replacement, *flags in fixes:
                if flags:
                    content = re.sub(pattern, replacement, content, flags=flags[0])
                else:
                    content = re.sub(pattern, replacement, content)
            
            # Fix specific imports based on our map
            for name, module in self.import_map.items():
                # Fix incorrect module imports
                pattern = f'from luminous_nix\\.\\w+(?:\\.\\w+)* import ([^)]*\\b){name}\\b'
                if re.search(pattern, content):
                    # Check if it's importing from wrong module
                    if f'from {module} import' not in content:
                        # Add correct import
                        import_line = f'from {module} import {name}\n'
                        # Find a good place to add it (after other imports)
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if line.startswith('from luminous_nix'):
                                lines.insert(i + 1, import_line)
                                content = '\n'.join(lines)
                                break
            
            # Remove duplicate import lines
            seen_imports = set()
            lines = []
            for line in content.split('\n'):
                if line.strip().startswith(('from ', 'import ')):
                    if line.strip() not in seen_imports:
                        seen_imports.add(line.strip())
                        lines.append(line)
                else:
                    lines.append(line)
            
            content = '\n'.join(lines)
            
            # Remove empty imports
            content = re.sub(r'from [^)]+? import\s*\n', '', content)
            
            if content != original:
                with open(filepath, 'w') as f:
                    f.write(content)
                self.errors_fixed += 1
                return True
                
        except Exception as e:
            print(f"Error processing {filepath}: {e}")
        
        return False

    def create_missing_mocks(self):
        """Create mock implementations for test dependencies."""
        mocks_dir = self.tests_path / "mocks"
        mocks_dir.mkdir(exist_ok=True)
        
        # Create __init__.py
        init_file = mocks_dir / "__init__.py"
        init_content = '''"""
Test mocks for missing dependencies.
"""

from .adapters import CLIAdapter
from .caching import CacheLayer, RedisCache, CacheManager
from .missing_imports import Command, LearningMetrics

__all__ = [
    "CLIAdapter",
    "CacheLayer", 
    "RedisCache",
    "CacheManager",
    "Command",
    "LearningMetrics",
]
'''
        init_file.write_text(init_content)
        
        # Create comprehensive mocks
        adapters_mock = '''"""Mock CLI adapter."""

class CLIAdapter:
    def __init__(self, backend=None):
        self.backend = backend
    
    def build_request(self, query, **kwargs):
        return {"query": query, **kwargs}
    
    def process_command(self, command, **kwargs):
        return {"success": True, "output": f"Processed: {command}"}
    
    def format_response(self, response):
        return str(response)
'''
        
        caching_mock = '''"""Mock caching module."""

class CacheLayer:
    def __init__(self):
        self.cache = {}
    
    def get(self, key):
        return self.cache.get(key)
    
    def set(self, key, value, ttl=None):
        self.cache[key] = value
        return True
    
    def clear(self):
        self.cache.clear()

class RedisCache(CacheLayer):
    pass

class CacheManager:
    def __init__(self):
        self.cache = CacheLayer()
    
    def get_cache(self, cache_type=None):
        return self.cache
'''
        
        missing_imports = '''"""Mock missing imports."""

class Command:
    def __init__(self, text="", context=None):
        self.text = text
        self.context = context or {}

class LearningMetrics:
    def __init__(self):
        self.accuracy = 0.95
        self.response_time = 0.1
        self.user_satisfaction = 0.9
'''
        
        (mocks_dir / "adapters.py").write_text(adapters_mock)
        (mocks_dir / "caching.py").write_text(caching_mock)
        (mocks_dir / "missing_imports.py").write_text(missing_imports)
        
        print(f"Created mock files in {mocks_dir}")

    def fix_all_tests(self):
        """Fix all test files systematically."""
        print("🔧 Fixing all test collection errors...")
        
        # Create mocks first
        self.create_missing_mocks()
        
        # Get current errors
        errors = self.get_test_errors()
        print(f"\n📊 Found {len(errors)} files with errors")
        
        # Process each file
        for filepath in errors:
            full_path = self.project_root / filepath
            if full_path.exists():
                if self.fix_imports_in_file(str(full_path)):
                    print(f"  ✅ Fixed: {filepath}")
                self.files_processed += 1
        
        print(f"\n📈 Progress:")
        print(f"  Files processed: {self.files_processed}")
        print(f"  Errors fixed: {self.errors_fixed}")
        
        # Verify fixes
        print("\n🧪 Verifying fixes...")
        result = subprocess.run(
            ["poetry", "run", "pytest", "--collect-only", "tests/unit/", "-q"],
            capture_output=True,
            text=True,
            cwd=str(self.project_root)
        )
        
        # Count remaining errors
        remaining_errors = result.stderr.count("ERROR collecting")
        if remaining_errors > 0:
            print(f"⚠️  {remaining_errors} errors still remaining")
        else:
            print("✅ All collection errors fixed!")
        
        # Count collected tests
        if "collected" in result.stdout:
            match = re.search(r"collected (\d+) item", result.stdout)
            if match:
                print(f"✅ Successfully collected {match.group(1)} tests!")
        
        return remaining_errors == 0

def main():
    fixer = TestFixer()
    success = fixer.fix_all_tests()
    
    if success:
        print("\n🎉 All test collection errors fixed!")
        print("\nNext steps:")
        print("  1. Run: poetry run pytest tests/unit/ --cov=nix_for_humanity")
        print("  2. Check coverage report")
        print("  3. Add tests for uncovered modules")
    else:
        print("\n⚠️  Some errors remain. Manual intervention may be needed.")
        print("\nTo debug remaining issues:")
        print("  1. Run: poetry run pytest tests/unit/[specific_test].py -xvs")
        print("  2. Check the detailed error message")
        print("  3. Fix imports manually if needed")

if __name__ == "__main__":
    main()