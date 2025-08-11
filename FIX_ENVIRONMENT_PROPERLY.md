# 🔧 Fixing Environment Issues Properly (NO MOCKS!)

## The Core Problems

1. **Python Version Mismatch**:
   - System has Python 3.13
   - Some dependencies need Python 3.11 (DoWhy)
   - shell.nix provides both but they conflict

2. **Module Name Confusion**:
   - Code imports from `nix_humanity` (wrong)
   - Should import from `nix_for_humanity` (correct)
   - Multiple duplicate imports throughout codebase

3. **Duplicate Files**:
   - Multiple copies of similar functionality
   - Confusion about which is canonical
   - Path issues with XAI and other features

## Proper Solution (Following NO MOCKS Principle)

### Step 1: Fix Module Imports

```bash
# Find and fix all wrong imports
find src/ scripts/ tests/ -name "*.py" -type f -exec grep -l "from nix_humanity" {} \; | \
  xargs sed -i 's/from nix_humanity/from nix_for_humanity/g'

find src/ scripts/ tests/ -name "*.py" -type f -exec grep -l "import nix_humanity" {} \; | \
  xargs sed -i 's/import nix_humanity/import nix_for_humanity/g'
```

### Step 2: Create Proper Development Shell

Create `shell-dev.nix`:
```nix
{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  name = "nix-for-humanity-dev";

  buildInputs = with pkgs; [
    # Use Python 3.11 for compatibility
    python311
    python311Packages.pip
    python311Packages.virtualenv

    # Poetry for dependency management
    poetry

    # Required system libraries
    pkg-config
    openssl

    # For TUI
    ncurses

    # Development tools
    git
    curl
    jq
  ];

  shellHook = ''
    echo "🌟 Nix for Humanity Development Environment"
    echo "Python: $(python3 --version)"

    # Create venv if it doesn't exist
    if [ ! -d "venv" ]; then
      echo "Creating virtual environment..."
      python3 -m venv venv
    fi

    # Activate venv
    source venv/bin/activate

    # Install dependencies
    if [ ! -f "venv/.deps_installed" ]; then
      echo "Installing dependencies..."
      pip install --upgrade pip
      pip install -e .
      pip install textual rich blessed
      touch venv/.deps_installed
    fi

    # Set PYTHONPATH
    export PYTHONPATH="$PWD/src:$PWD/features/v3.0/xai:$PYTHONPATH"

    # Enable features
    export NIX_HUMANITY_PYTHON_BACKEND=true

    echo "✅ Environment ready!"
    echo "Run: ./bin/ask-nix 'help'"
  '';
}
```

### Step 3: Fix Python Path Issues

Create `fix_imports.py`:
```python
#!/usr/bin/env python3
"""Fix all import issues in the codebase"""

import os
import re
from pathlib import Path

def fix_imports(directory):
    """Fix all import statements"""

    fixes = {
        r'from nix_humanity': 'from nix_for_humanity',
        r'import nix_humanity': 'import nix_for_humanity',
        r'nixos_rebuild_mock': 'nixos_rebuild',  # Remove mock references
    }

    py_files = Path(directory).rglob('*.py')

    for file_path in py_files:
        if 'venv' in str(file_path) or '__pycache__' in str(file_path):
            continue

        try:
            with open(file_path, 'r') as f:
                content = f.read()

            original = content
            for pattern, replacement in fixes.items():
                content = re.sub(pattern, replacement, content)

            if content != original:
                with open(file_path, 'w') as f:
                    f.write(content)
                print(f"✅ Fixed: {file_path}")

        except Exception as e:
            print(f"⚠️ Error processing {file_path}: {e}")

if __name__ == "__main__":
    fix_imports('src')
    fix_imports('scripts')
    fix_imports('tests')
    print("✅ Import fixes complete!")
```

### Step 4: Clean Up Duplicates

```bash
# Remove duplicate/archive directories
rm -rf src/archive/
rm -rf bin/archive/
rm -rf docs/archive/historical/

# Remove mock files
find . -name "*mock*.py" -type f -delete
find . -name "*Mock*.py" -type f -delete

# Remove duplicate virtual environments
rm -rf venv_tui venv_test venv_quick
```

### Step 5: Create Canonical Entry Points

Create `bin/ask-nix` (simplified):
```bash
#!/usr/bin/env bash
# Canonical ask-nix entry point

# Ensure we're in the right directory
cd "$(dirname "$0")/.." || exit 1

# Activate environment if needed
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Set Python path
export PYTHONPATH="$PWD/src:$PWD/features/v3.0/xai:$PYTHONPATH"

# Run the CLI
exec python3 -m nix_for_humanity.cli "$@"
```

### Step 6: Test Everything Works

```bash
# Enter development shell
nix-shell shell-dev.nix

# Test basic functionality
python3 -c "from nix_for_humanity.core.engine import NixForHumanityBackend; print('✅ Backend imports!')"

# Test XAI
python3 -c "from causal_xai_engine import CausalXAIEngine; print('✅ XAI imports!')"

# Test CLI
./bin/ask-nix "help"

# Test TUI
./bin/nix-tui
```

## Environment Documentation

### For Development
```bash
# Always use the dev shell
nix-shell shell-dev.nix

# This provides:
# - Python 3.11 (for compatibility)
# - Virtual environment (isolated)
# - All dependencies installed
# - Correct PYTHONPATH
# - Feature flags enabled
```

### For Production
```bash
# Use the flake
nix develop

# Or install via pip
pip install nix-for-humanity
```

### Known Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| "No module named nix_humanity" | Wrong import name | Run fix_imports.py |
| "Module not found: textual" | Missing TUI deps | pip install textual rich |
| "XAI not available" | Path not in PYTHONPATH | Export PYTHONPATH with features/v3.0/xai |
| Python 3.13 vs 3.11 | Version mismatch | Use shell-dev.nix (provides 3.11) |

## Testing Checklist

- [ ] Backend imports correctly
- [ ] XAI engine loads
- [ ] CLI runs without errors
- [ ] TUI launches properly
- [ ] No mock imports remain
- [ ] All tests pass

## NO MOCKS Compliance

✅ This solution:
- Fixes the real environment issues
- No mock implementations
- No workarounds or patches
- Proper dependency management
- Clear documentation

The environment will either work properly or fail with clear errors that point to the actual problem.
