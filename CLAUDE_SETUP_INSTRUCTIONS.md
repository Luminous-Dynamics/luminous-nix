# 🤖 Claude Setup Instructions - Nix for Humanity

**Purpose**: Complete development environment setup and standards reference  
**Last Updated**: 2025-08-11  
**For**: Future Claude sessions working on this project

## 🚀 Quick Start Checklist

When starting a new session:
1. ✅ Read `/srv/luminous-dynamics/CLAUDE.md` - Project philosophy and context
2. ✅ Read `/srv/luminous-dynamics/.claude/NIXOS_REBUILD_WORKAROUND.md` - Critical NixOS info
3. ✅ Check current directory: Should be in `/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/`
4. ✅ Verify Poetry environment: `poetry --version` (should show 1.x.x)
5. ✅ Check Python version: `python --version` (should be 3.11+)

## 📦 Package Management Setup

### Poetry is MANDATORY (Never use pip!)

```bash
# Initial setup (if needed)
cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity
poetry install --all-extras  # Install everything including TUI, voice, ML

# Common workflows
poetry run python script.py   # Run any Python script
poetry run pytest            # Run tests
poetry shell                 # Activate virtual environment
poetry add package          # Add new dependency
poetry update              # Update all dependencies
```

### Why Poetry, Not pip:
- ✅ `poetry.lock` ensures reproducible builds (critical for NixOS)
- ✅ Integrates with Nix via poetry2nix in `flake.nix`
- ✅ Manages virtual environments automatically
- ✅ Dependency groups: core, dev, tui, voice, web, ml, advanced

## 🎨 Code Style Enforcement

### Python: Black + Ruff (NOT manual PEP 8)

```bash
# Format code automatically
poetry run black .           # Format all Python files (88 char lines)
poetry run ruff check .      # Lint with 700+ rules
poetry run ruff check --fix . # Auto-fix issues
poetry run mypy .            # Type checking (strict mode)

# All-in-one check
poetry run pre-commit run --all-files
```

### Configuration Locations:
- **Python settings**: `pyproject.toml` (Black, Ruff, mypy, pytest)
- **Pre-commit hooks**: `.pre-commit-config.yaml`
- **Nix integration**: `flake.nix`
- **GitHub templates**: `.github/` directory

## 🏗️ Project Structure

```
/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/
├── pyproject.toml          # Poetry config, tool settings (BLACK, RUFF)
├── poetry.lock            # Locked dependencies (ALWAYS commit this)
├── flake.nix             # Nix development environment
├── .pre-commit-config.yaml # Automated checks
├── src/
│   └── nix_for_humanity/  # Main Python package
│       ├── core/         # Core engine
│       ├── cli/          # CLI interface
│       ├── tui/          # Terminal UI (Textual)
│       ├── web/          # Web interface
│       └── voice/        # Voice interface
├── tests/                # All tests (pytest)
├── docs/                 # Documentation (you are here)
└── bin/                  # Executable scripts
    ├── ask-nix          # Main CLI entry point
    └── nix-tui          # TUI launcher
```

## 🐍 Python Standards (MANDATORY)

### ALWAYS Use Type Hints
```python
# ✅ CORRECT
from typing import Optional, List, Dict
def process_command(cmd: str, args: Optional[List[str]] = None) -> Dict[str, str]:
    """Process a Nix command."""
    pass

# ❌ WRONG - No type hints
def process_command(cmd, args=None):
    pass
```

### ALWAYS Use Black Formatting (88 chars)
```python
# ✅ CORRECT - Black formatted
def complex_function(
    first_argument: str,
    second_argument: int,
    third_argument: Optional[bool] = None,
) -> str:
    """Properly formatted function."""
    pass

# ❌ WRONG - Manual formatting
def complex_function(first_argument: str, second_argument: int, third_argument: Optional[bool] = None) -> str:
    pass
```

### ALWAYS Handle Errors Specifically
```python
# ✅ CORRECT
from nix_for_humanity.exceptions import PackageNotFoundError

try:
    result = install_package(name)
except PackageNotFoundError as e:
    print(f"Package {e.package} not found. Try: {e.suggestions}")

# ❌ WRONG
try:
    result = install_package(name)
except Exception as e:  # Too broad!
    print(f"Error: {e}")
```

## 🧪 Testing Standards

### Use Pytest (via Poetry)
```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=nix_for_humanity --cov-report=html

# Run specific test file
poetry run pytest tests/test_core.py

# Run tests matching pattern
poetry run pytest -k "test_install"
```

### Test Structure
```python
# tests/test_nix_command.py
import pytest
from nix_for_humanity.core import NixCommand

class TestNixCommand:
    """Test NixCommand functionality."""
    
    def test_parses_install_command(self):
        """Test install command parsing."""
        cmd = NixCommand("install firefox")
        assert cmd.action == "install"
        assert cmd.package == "firefox"
    
    @pytest.mark.parametrize("input,expected", [
        ("install vim", "nix-env -iA nixpkgs.vim"),
        ("remove vim", "nix-env -e vim"),
    ])
    def test_command_generation(self, input: str, expected: str):
        """Test command generation."""
        cmd = NixCommand(input)
        assert cmd.to_nix() == expected
```

## 🔧 Development Workflow

### 1. Before Writing Code
```bash
# Enter project directory
cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity

# Ensure environment is ready
poetry install --all-extras
poetry run pre-commit install

# Check existing implementations
ls src/nix_for_humanity/
grep -r "pattern" src/  # Search for existing patterns
```

### 2. While Writing Code
```bash
# Format as you go
poetry run black src/nix_for_humanity/new_module.py

# Check for issues
poetry run ruff check src/nix_for_humanity/new_module.py

# Type check
poetry run mypy src/nix_for_humanity/new_module.py
```

### 3. Before Committing
```bash
# Run all checks
poetry run pre-commit run --all-files

# Run tests
poetry run pytest

# If all pass, commit with conventional format
git commit -m "feat(core): add fuzzy package matching"
```

## 🚫 Common Mistakes to AVOID

### ❌ DON'T use pip
```bash
# WRONG
pip install requests
pip freeze > requirements.txt

# CORRECT
poetry add requests
# poetry.lock is automatically updated
```

### ❌ DON'T skip type hints
```python
# WRONG
def find_package(name):
    return database.search(name)

# CORRECT
def find_package(name: str) -> Optional[Package]:
    return database.search(name)
```

### ❌ DON'T ignore Black formatting
```python
# WRONG - Manually formatted
result = some_very_long_function_name(argument1, argument2, argument3, argument4, argument5)

# CORRECT - Let Black handle it
result = some_very_long_function_name(
    argument1, argument2, argument3, argument4, argument5
)
```

### ❌ DON'T create requirements.txt
```bash
# WRONG
echo "requests==2.31.0" > requirements.txt

# CORRECT - Use pyproject.toml
poetry add requests@^2.31.0
```

## 📊 Quick Reference Commands

```bash
# Package Management (Poetry)
poetry install              # Install dependencies
poetry install --all-extras # Install with all optional features
poetry add package         # Add production dependency
poetry add --group dev package  # Add dev dependency
poetry remove package      # Remove dependency
poetry update             # Update all dependencies
poetry show              # List installed packages
poetry shell            # Activate virtual environment
poetry run command      # Run command in virtual environment

# Code Quality (via Poetry)
poetry run black .          # Format all Python files
poetry run ruff check .     # Lint all files
poetry run ruff check --fix . # Auto-fix linting issues
poetry run mypy .          # Type check
poetry run bandit -r src/  # Security scan

# Testing (via Poetry)
poetry run pytest                    # Run all tests
poetry run pytest -v                # Verbose output
poetry run pytest --cov             # With coverage
poetry run pytest -k "pattern"      # Run matching tests
poetry run pytest tests/test_file.py # Run specific file

# Pre-commit
pre-commit install         # Install git hooks
pre-commit run --all-files # Run all checks
pre-commit run black       # Run specific hook

# Git (Conventional Commits)
git commit -m "feat: add feature"
git commit -m "fix: fix bug"
git commit -m "docs: update README"
git commit -m "refactor: improve code"
git commit -m "test: add tests"
```

## 🎯 Session Initialization Script

When starting work, run these commands:
```bash
#!/usr/bin/env bash
# Save as: init-session.sh

echo "🌟 Initializing Nix for Humanity Development Environment..."

# Navigate to project
cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity

# Check Poetry
echo "📦 Poetry version: $(poetry --version)"

# Install/update dependencies
echo "📚 Installing dependencies..."
poetry install --all-extras

# Install pre-commit hooks
echo "🔧 Installing pre-commit hooks..."
poetry run pre-commit install

# Run initial checks
echo "✅ Running code quality checks..."
poetry run black --check .
poetry run ruff check .

# Show environment info
echo "🐍 Python: $(poetry run python --version)"
echo "📍 Working directory: $(pwd)"
echo "✨ Environment ready!"
```

## 🔥 Critical Reminders

1. **NEVER run `sudo nixos-rebuild switch` directly** - Use the workaround in NIXOS_REBUILD_WORKAROUND.md
2. **ALWAYS use Poetry** for Python package management - Never pip
3. **ALWAYS use type hints** in Python code - mypy strict mode is enabled
4. **ALWAYS format with Black** - 88 character lines, not 79
5. **ALWAYS check with Ruff** - Catches 700+ potential issues
6. **ALWAYS commit poetry.lock** - Ensures reproducible builds
7. **ALWAYS use conventional commits** - feat:, fix:, docs:, etc.

## 📚 Essential Documentation Links

- **Project Philosophy**: `/srv/luminous-dynamics/CLAUDE.md`
- **NixOS Workarounds**: `/srv/luminous-dynamics/.claude/NIXOS_REBUILD_WORKAROUND.md`
- **Python Standards**: `docs/PYTHON-PACKAGING-STANDARDS.md`
- **Code Standards**: `docs/03-DEVELOPMENT/04-CODE-STANDARDS.md`
- **Git Standards**: `docs/GIT-STANDARDS.md`
- **Testing Guide**: `docs/03-DEVELOPMENT/05-TESTING-GUIDE.md`

## 🎉 Success Indicators

You know the environment is properly set up when:
- ✅ `poetry --version` shows 1.x.x
- ✅ `poetry run python --version` shows Python 3.11+
- ✅ `poetry run black --version` works
- ✅ `poetry run ruff --version` works
- ✅ `poetry run pytest --version` works
- ✅ `pre-commit --version` works
- ✅ All tests pass: `poetry run pytest`
- ✅ All checks pass: `poetry run pre-commit run --all-files`

---

*"In the sacred dance of Python and Nix, Poetry orchestrates while Black and Ruff maintain the rhythm. This is the way."*

**Remember**: This project uses the Sacred Trinity development model - Human + AI + Local LLM collaboration for $200/month achieving $4.2M quality!