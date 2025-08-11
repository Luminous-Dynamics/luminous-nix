# 🎯 Nix for Humanity - Quick Reference Card

## 🚀 Session Start
```bash
cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity
poetry install --all-extras
poetry shell  # or prefix commands with 'poetry run'
```

## 📦 Package Management (Poetry ONLY!)
```bash
poetry add package              # Add package
poetry add pytest --group dev   # Add dev dependency
poetry add textual --optional   # Add optional dependency
poetry remove package           # Remove package
poetry update                   # Update all
poetry show                     # List installed
```

## 🎨 Code Quality (Every Time!)
```bash
poetry run black .              # Format (88 chars)
poetry run ruff check --fix .   # Lint & fix
poetry run mypy .              # Type check
poetry run pre-commit run --all-files  # All checks
```

## 🧪 Testing
```bash
poetry run pytest               # Run all tests
poetry run pytest --cov         # With coverage
poetry run pytest -v           # Verbose
poetry run pytest tests/test_file.py  # Specific file
poetry run pytest -k "pattern" # Match pattern
```

## 📝 Git Commits (Conventional)
```bash
feat(scope): add new feature
fix(scope): fix bug
docs: update documentation
refactor: improve code
test: add tests
chore: maintenance
```

## 🐍 Python Standards
```python
# ✅ ALWAYS use type hints
def process(cmd: str, args: List[str]) -> Dict[str, Any]:
    """Docstring required."""
    pass

# ✅ ALWAYS use Black formatting (88 chars)
# ✅ ALWAYS handle specific exceptions
# ✅ ALWAYS use snake_case for functions/variables
# ✅ ALWAYS use PascalCase for classes
```

## ⚠️ NixOS Rebuild (NEVER direct!)
```bash
# ❌ WRONG - Will timeout
sudo nixos-rebuild switch

# ✅ CORRECT - Background
nohup sudo nixos-rebuild switch > /tmp/rebuild.log 2>&1 &
tail -f /tmp/rebuild.log
```

## 🚫 Never Do These
- ❌ `pip install` - Use Poetry
- ❌ `requirements.txt` - Use pyproject.toml
- ❌ Manual formatting - Use Black
- ❌ Skip type hints - Always type
- ❌ `python script.py` - Use `poetry run`
- ❌ 79 char lines - Use 88 (Black default)
- ❌ Broad exceptions - Be specific
- ❌ Direct nixos-rebuild - Use background

## 📂 Project Structure
```
├── pyproject.toml       # Config (source of truth)
├── poetry.lock         # Lock file (commit this!)
├── src/nix_for_humanity/  # Source code
├── tests/              # Tests
├── docs/               # Documentation
└── bin/                # Scripts
```

## 🔧 Environment Check
```bash
poetry --version        # Should show 1.x.x
python --version        # Should show 3.11+
poetry run black --version
poetry run ruff --version
poetry run pytest --version
```

## 📚 Essential Docs
- Setup: `CLAUDE_SETUP_INSTRUCTIONS.md`
- Standards: `docs/PYTHON-PACKAGING-STANDARDS.md`
- Code: `docs/03-DEVELOPMENT/04-CODE-STANDARDS.md`

---
**Remember**: Poetry > pip | Black > manual | Ruff > flake8 | 88 > 79
