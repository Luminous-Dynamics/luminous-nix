# 🐍 Python Packaging & Style Standards for Nix for Humanity

**Decision Date**: 2025-08-11
**Status**: RECOMMENDED
**Context**: NixOS-integrated Python project with multiple deployment targets

## 📦 Package Management: Poetry, NOT pip

### Why NOT pip?

For a NixOS-integrated project like Nix for Humanity, **pip is the WRONG choice**. Here's why:

1. **No Lock Files**: pip doesn't provide reproducible builds
2. **No Version Resolution**: Manual conflict resolution is error-prone
3. **Poor Nix Integration**: pip fights with Nix's declarative model
4. **No Dependency Groups**: Can't separate dev/prod/optional dependencies
5. **No Virtual Environment Management**: Requires separate tooling

### Why Poetry? ✅

Poetry is the **CORRECT choice** for this project:

1. **Lock Files**: `poetry.lock` ensures reproducible builds
2. **Dependency Resolution**: Automatic conflict resolution
3. **Nix Integration**: Works beautifully with poetry2nix
4. **Dependency Groups**: Clean separation of concerns
5. **Virtual Environments**: Built-in management
6. **PEP 517/518 Compliant**: Modern Python packaging standards

### Current Implementation Analysis

Looking at your `pyproject.toml`:
- ✅ **Already using Poetry** - Excellent!
- ✅ **Well-organized dependency groups** (core, tui, voice, web, ml, advanced)
- ✅ **Poetry extras** for optional features
- ✅ **Version constraints** properly specified
- ✅ **Scripts defined** for CLI entry points

### Recommended Package Management Workflow

```bash
# Development workflow
poetry install              # Install all dependencies
poetry install --with dev   # Include dev dependencies
poetry install --extras tui # Install with TUI support
poetry install --all-extras # Install everything

# Adding dependencies
poetry add requests         # Add production dependency
poetry add pytest --group dev  # Add dev dependency
poetry add textual --optional  # Add optional dependency

# Update dependencies
poetry update              # Update all dependencies
poetry update requests     # Update specific package

# Build package
poetry build              # Creates wheel and sdist

# Run in virtual environment
poetry run python script.py
poetry run pytest
poetry shell              # Activate virtual environment
```

## 🎨 Code Style: Black + Ruff, NOT just PEP 8

### Why NOT just PEP 8?

PEP 8 alone is **insufficient** for modern Python projects:

1. **Too General**: PEP 8 is a guideline, not enforcement
2. **No Automation**: Requires manual compliance checking
3. **Subjective**: Different interpretations cause inconsistency
4. **Limited Scope**: Doesn't cover modern Python features
5. **No Performance**: Doesn't catch performance issues

### Why Black + Ruff? ✅

Your current setup is **EXCELLENT**:

```toml
[tool.black]
line-length = 88  # Black's default, better than PEP 8's 79
target-version = ['py311']

[tool.ruff]
target-version = "py311"
line-length = 88
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "UP",   # pyupgrade
    "S",    # bandit (security)
    "B",    # flake8-bugbear
    # ... more rules
]
```

### Benefits of Your Current Setup

1. **Black**: Opinionated formatter - no debates about style
2. **Ruff**: Lightning-fast linter with 700+ rules
3. **Automatic**: Pre-commit hooks enforce standards
4. **Modern**: Supports latest Python features
5. **Security**: Bandit integration catches vulnerabilities

### Recommended Python Standards

```python
# ✅ GOOD: Black-formatted, type-hinted, documented
from typing import Optional, List
from nix_for_humanity.core import NixCommand

def execute_command(
    command: str,
    args: Optional[List[str]] = None,
    dry_run: bool = False
) -> NixCommand:
    """Execute a Nix command with optional arguments.

    Args:
        command: The Nix command to execute
        args: Optional list of arguments
        dry_run: If True, only simulate execution

    Returns:
        NixCommand object with execution results

    Raises:
        NixCommandError: If command execution fails
    """
    args = args or []
    # Implementation...

# ❌ BAD: No types, poor formatting, no docs
def execute_command(command,args=None,dry_run=False):
    if args == None: args = []
    # Implementation...
```

## 📋 Configuration File Updates Needed

### 1. Update `.pre-commit-config.yaml`

Your current config uses line-length 100, but Black is configured for 88:

```yaml
# Fix this inconsistency
- repo: https://github.com/psf/black
  rev: 24.1.1
  hooks:
    - id: black
      args: ['--line-length=88']  # Match pyproject.toml
```

### 2. Consider Adding to pyproject.toml

```toml
[tool.ruff]
# Add these useful rules
select = [
    # ... existing rules ...
    "PT",   # flake8-pytest-style
    "RUF",  # Ruff-specific rules
    "TRY",  # tryceratops (exception handling)
    "FLY",  # flynt (string formatting)
    "PERF", # performance anti-patterns
]

[tool.ruff.isort]
known-first-party = ["nix_for_humanity"]

[tool.mypy]
# Stricter type checking
strict = true
warn_unreachable = true
pretty = true
show_error_context = true
```

## 🚀 Migration from pip (if needed elsewhere)

If you have any legacy `requirements.txt` files:

```bash
# Convert requirements.txt to Poetry
poetry add $(cat requirements.txt)

# Or use poetry import plugin
poetry self add poetry-plugin-import
poetry import requirements.txt
```

## 🎯 Summary of Recommendations

### Package Management
- ✅ **KEEP Poetry** - You're already using the right tool
- ❌ **AVOID pip** - Except for quick experiments
- ✅ **USE poetry2nix** - For Nix integration
- ✅ **MAINTAIN poetry.lock** - Commit it for reproducibility

### Code Style
- ✅ **KEEP Black** - Opinionated formatting is good
- ✅ **KEEP Ruff** - Fast, comprehensive linting
- ✅ **88 characters** - Better than PEP 8's 79
- ✅ **Type hints** - Use them everywhere
- ✅ **Docstrings** - Google or NumPy style

### Enforcement
- ✅ **Pre-commit hooks** - Already configured
- ✅ **CI/CD checks** - Run same checks in CI
- ✅ **Editor integration** - VSCode/PyCharm plugins

## 🔧 Quick Setup Commands

```bash
# For new developers
poetry install --all-extras  # Install everything
pre-commit install           # Set up git hooks
poetry run black .           # Format all code
poetry run ruff check .      # Lint all code
poetry run mypy .            # Type check
poetry run pytest            # Run tests

# One command to rule them all
poetry run pre-commit run --all-files
```

## 📊 Why This Matters for Nix for Humanity

1. **Reproducibility**: Critical for NixOS philosophy
2. **Accessibility**: Consistent code is easier to understand
3. **Sacred Trinity**: AI can parse consistent code better
4. **Performance**: Ruff catches performance issues
5. **Security**: Bandit prevents vulnerabilities
6. **Maintenance**: Less time debating style

## 🏆 Verdict

Your current setup with **Poetry + Black + Ruff** is **EXCELLENT** and aligns perfectly with:
- NixOS declarative philosophy
- Modern Python best practices
- Consciousness-first development
- Sacred Trinity collaboration model

**Do NOT switch to pip**. **Do NOT use only PEP 8**. Your current tooling is superior.

---

*"In the sacred dance of Python and Nix, Poetry orchestrates the harmony while Black and Ruff maintain the rhythm."*
