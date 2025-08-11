# 🤖 Claude Code Instructions - Nix for Humanity

**Purpose**: Project-specific instructions for Claude Code sessions
**Parent Context**: `/srv/luminous-dynamics/CLAUDE.md`
**Setup Guide**: `CLAUDE_SETUP_INSTRUCTIONS.md`

## ⚠️ CRITICAL: Update Documentation When Working

**ALWAYS update status documents when making changes:**
- `docs/04-OPERATIONS/CURRENT_STATUS_DASHBOARD.md` - Update scores, phase progress, TODOs count
- `docs/04-OPERATIONS/IMPLEMENTATION_STATUS.md` - Update feature completion status
- `.claude/session-notes.md` - Log work done in session
- Relevant feature docs when implementing/fixing

**Example**: The TODO count was 3,944 but actually only 116 - always verify and update!

## 🚀 Session Initialization

When starting work on Nix for Humanity:

1. **Read Parent Context**: `/srv/luminous-dynamics/CLAUDE.md` - Overall philosophy
2. **Read Critical Workarounds**: `/srv/luminous-dynamics/.claude/NIXOS_REBUILD_WORKAROUND.md`
3. **Read Setup Instructions**: `CLAUDE_SETUP_INSTRUCTIONS.md` - Development environment
4. **Verify Environment**:
   ```bash
   cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity
   poetry --version  # Should show 1.x.x
   python --version  # Should show 3.11+
   ```

## 📦 Package Management Rules

### ALWAYS Use Poetry (Never pip!)
```bash
# ✅ CORRECT
poetry add requests
poetry run python script.py
poetry install --all-extras

# ❌ WRONG
pip install requests
python script.py
```

### Why This Matters:
- Poetry provides `poetry.lock` for reproducible builds
- Integrates with Nix via poetry2nix
- Manages virtual environments automatically
- Critical for NixOS philosophy of declarative, reproducible systems

## 🎨 Code Style Rules

### Python MUST Use:
- **Black**: 88-character lines (NOT 79 from PEP 8)
- **Ruff**: Lightning-fast linter with 700+ rules
- **mypy**: Strict type checking
- **Type hints**: MANDATORY on all functions

### Quick Formatting:
```bash
poetry run black .           # Format all Python
poetry run ruff check --fix . # Fix linting issues
poetry run mypy .           # Type check
```

## 🏗️ Project Structure

```
nix-for-humanity/
├── pyproject.toml      # Poetry config (THIS IS THE SOURCE OF TRUTH)
├── poetry.lock        # Locked dependencies (ALWAYS COMMIT)
├── src/
│   └── nix_for_humanity/  # Main package
├── tests/             # Pytest tests
├── docs/              # Documentation
└── bin/               # Executable scripts
```

## ⚠️ Critical NixOS Workarounds

### NEVER Run These Directly:
```bash
# ❌ WILL TIMEOUT IN CLAUDE CODE
sudo nixos-rebuild switch

# ✅ USE BACKGROUND WORKAROUND
nohup sudo nixos-rebuild switch > /tmp/rebuild.log 2>&1 &
tail -f /tmp/rebuild.log
```

See: `/srv/luminous-dynamics/.claude/NIXOS_REBUILD_WORKAROUND.md`

## 🧪 Testing Standards

### Always Test Via Poetry:
```bash
# Run all tests
poetry run pytest

# With coverage
poetry run pytest --cov=nix_for_humanity

# Specific tests
poetry run pytest tests/test_core.py
```

## 🔧 Pre-commit Hooks

### Already Configured:
- Black (formatting)
- Ruff (linting)
- isort (import sorting)
- mypy (type checking)
- bandit (security)
- markdownlint (docs)
- shellcheck (scripts)

### Run Checks:
```bash
poetry run pre-commit run --all-files
```

## 📝 Commit Message Format

Use Conventional Commits:
```bash
feat(core): add fuzzy package matching
fix(cli): handle missing arguments
docs: update Python standards
refactor(tui): simplify event handling
test: add integration tests for voice
```

## 🎯 Development Workflow

### 1. Start Session
```bash
cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity
poetry install --all-extras
```

### 2. Make Changes
```bash
# Edit files
# Format immediately
poetry run black src/nix_for_humanity/new_file.py
```

### 3. Before Committing
```bash
poetry run pre-commit run --all-files
poetry run pytest
```

### 4. Commit
```bash
git add .
git commit -m "feat: add new feature"
```

## 🚫 Common Mistakes to Avoid

1. **Using pip instead of Poetry**
2. **Skipping type hints**
3. **Manual formatting instead of Black**
4. **Using 79-char lines (use 88)**
5. **Running nixos-rebuild directly**
6. **Creating requirements.txt files**
7. **Using venv instead of Poetry**
8. **Broad exception handling**
9. **Not running pre-commit hooks**
10. **Not committing poetry.lock**

## 📊 Quick Reference

```bash
# Package Management
poetry add package          # Add dependency
poetry remove package       # Remove dependency
poetry update              # Update all
poetry shell               # Activate env
poetry run command         # Run in env

# Code Quality
poetry run black .         # Format
poetry run ruff check .    # Lint
poetry run mypy .         # Type check

# Testing
poetry run pytest          # Run tests
poetry run pytest --cov    # With coverage

# Pre-commit
pre-commit run --all-files # Run all checks
```

## 🔗 Essential Files

- **Setup Instructions**: `CLAUDE_SETUP_INSTRUCTIONS.md`
- **Python Standards**: `docs/PYTHON-PACKAGING-STANDARDS.md`
- **Code Standards**: `docs/03-DEVELOPMENT/04-CODE-STANDARDS.md`
- **Git Standards**: `docs/GIT-STANDARDS.md`
- **Package Decision**: `docs/PACKAGE-MANAGEMENT-DECISION.md`

## 🤝 AI Collaboration Context

This project demonstrates AI-assisted development:
- **Human (Tristan)**: Vision, architecture, testing, debugging
- **Claude Code**: Code generation, problem solving, documentation
- **Local LLM**: NixOS-specific expertise and best practices

AI tools cost ~$200/month and provide a significant productivity multiplier, enabling a solo developer to build sophisticated software that would traditionally require a small team.

## ✨ Remember

- **Poetry** orchestrates Python dependencies
- **Black** maintains consistent formatting
- **Ruff** catches issues before they matter
- **Type hints** make code self-documenting
- **Pre-commit** ensures quality automatically

This is consciousness-first development - every tool serves to reduce cognitive load and increase flow state.

---

*"In the harmony of Nix and Python, Poetry leads while Black and Ruff keep time."*
