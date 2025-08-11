#!/usr/bin/env python3
"""
Systematically fix test collection errors.
"""

import os
import re
from pathlib import Path

def fix_import_errors():
    """Fix common import errors in test files."""
    
    fixes_applied = 0
    test_dir = Path("tests")
    
    # Common import fixes
    import_fixes = {
        # Wrong module names
        "from src.nix_for_humanity": "from nix_for_humanity",
        "from nix_for_humanity.utils.decorators": "from nix_for_humanity.core.decorators",
        "from adapters": "from scripts.adapters",
        "from feedback_collector": "from nix_for_humanity.learning.feedback_collector",
        
        # Wrong class names
        "'Personality'": "'PersonalityStyle'",
        "Personality,": "PersonalityStyle,",
        "Personality.": "PersonalityStyle.",
        
        # Missing imports
        "UnifiedNixBackend": "NixForHumanityBackend",
        "NATIVE_API_AVAILABLE": "NativeOperations",
    }
    
    # Process each test file
    for test_file in test_dir.rglob("test_*.py"):
        if test_file.name.startswith("test_"):
            try:
                content = test_file.read_text()
                original_content = content
                
                # Apply fixes
                for old_pattern, new_pattern in import_fixes.items():
                    if old_pattern in content:
                        content = content.replace(old_pattern, new_pattern)
                        print(f"Fixed '{old_pattern}' in {test_file}")
                
                # Special case: Fix bayesian imports
                if "bayesian_knowledge_tracer" in content:
                    content = re.sub(
                        r"from src\.nix_for_humanity\.core\.bayesian_knowledge_tracer",
                        "from nix_for_humanity.research.dynamic_user_modeling",
                        content
                    )
                    print(f"Fixed bayesian imports in {test_file}")
                
                # Write back if changed
                if content != original_content:
                    test_file.write_text(content)
                    fixes_applied += 1
                    
            except Exception as e:
                print(f"Error processing {test_file}: {e}")
    
    return fixes_applied

def add_missing_dependencies():
    """Check for missing test dependencies."""
    
    missing_deps = []
    
    # Check for hypothesis
    try:
        import hypothesis
    except ImportError:
        missing_deps.append("hypothesis")
    
    # Check for other test dependencies
    test_deps = ["pytest-mock", "pytest-asyncio", "pytest-cov", "requests-mock"]
    
    if missing_deps:
        print("\n⚠️ Missing test dependencies detected:")
        for dep in missing_deps:
            print(f"  - {dep}")
        print("\nTo install:")
        print(f"  poetry add --group dev {' '.join(missing_deps)}")
    
    return missing_deps

def fix_test_fixtures():
    """Add missing fixtures to conftest.py files."""
    
    conftest_template = '''"""Common test fixtures."""
import pytest
from unittest.mock import Mock, MagicMock
from pathlib import Path
import tempfile

@pytest.fixture
def mock_backend():
    """Mock backend for testing."""
    backend = MagicMock()
    backend.execute.return_value = {"success": True, "output": ""}
    return backend

@pytest.fixture
def temp_config_dir():
    """Temporary config directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def mock_context():
    """Mock context for testing."""
    from nix_for_humanity.core.unified_backend import Context
    return Context(user_id="test_user")
'''
    
    # Check if tests/conftest.py exists
    conftest_path = Path("tests/conftest.py")
    if not conftest_path.exists():
        conftest_path.write_text(conftest_template)
        print(f"Created {conftest_path}")
        return 1
    return 0

def main():
    """Main function to fix test collection errors."""
    
    print("🔧 Fixing Test Collection Errors")
    print("=" * 50)
    
    # Fix imports
    print("\n📝 Fixing import errors...")
    fixes = fix_import_errors()
    print(f"  Fixed {fixes} files")
    
    # Check dependencies
    print("\n📦 Checking dependencies...")
    missing = add_missing_dependencies()
    
    # Fix fixtures
    print("\n🔨 Checking fixtures...")
    fixture_fixes = fix_test_fixtures()
    print(f"  Fixed {fixture_fixes} fixture files")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Summary:")
    print(f"  Import fixes: {fixes}")
    print(f"  Missing dependencies: {len(missing)}")
    print(f"  Fixture fixes: {fixture_fixes}")
    
    print("\n✨ Run 'poetry run pytest --co -q' to check remaining errors")

if __name__ == "__main__":
    main()