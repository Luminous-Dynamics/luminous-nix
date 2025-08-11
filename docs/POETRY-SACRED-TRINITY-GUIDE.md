# 🕉️ Poetry for Sacred Trinity Development

*Using Poetry in the consciousness-first development model*

## 🌟 Why Poetry for Sacred Trinity?

Poetry aligns perfectly with our Sacred Trinity development model:
- **Declarative** like NixOS - Dependencies specified, not imperatively installed
- **Reproducible** - Lock files ensure exact same environment everywhere
- **Elegant** - Simple commands that flow naturally
- **Consciousness-first** - Reduces cognitive load through automation

## 📦 Installation Complete!

Poetry is now installed system-wide via NixOS configuration:
- Added to `/srv/luminous-dynamics/nixos/development-packages.nix`
- Available everywhere without `nix develop`
- Integrated with Black, Ruff, and mypy

## 🚀 Essential Poetry Commands

### Daily Development Flow

```bash
# Start your sacred development session
cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity
poetry install              # Ensure dependencies are current

# Run the application
poetry run ask-nix "help"  # Run through Poetry environment
poetry shell               # Enter virtual environment
ask-nix "help"            # Run directly in shell

# Development commands
poetry run black .        # Format code (88 chars)
poetry run ruff check .   # Lint code
poetry run mypy .        # Type check
poetry run pytest        # Run tests

# Pre-commit automatically runs on git commit
git commit -m "feat: add new feature"  # Triggers formatting & linting
```

### Dependency Management

```bash
# Add dependencies
poetry add requests              # Production dependency
poetry add --group dev pytest    # Development dependency
poetry add --optional textual    # Optional dependency

# Update dependencies
poetry update                    # Update all
poetry update requests          # Update specific

# Show dependencies
poetry show                     # All packages
poetry show --tree              # Dependency tree
poetry show --latest            # Check for updates
```

### Environment Management

```bash
# Virtual environment location
poetry env info                 # Show environment info
poetry env list                 # List all environments
poetry env use python3.13       # Switch Python version

# Cache management
poetry cache clear pypi --all   # Clear download cache
```

## 🔧 Configuration Files

### poetry.toml (Project-specific settings)
```toml
[virtualenvs]
in-project = true              # Create .venv in project
prefer-active-python = true    # Use active Python

[installer]
parallel = true                # Faster installation
modern-installation = true     # Use new installer
```

### pyproject.toml (Package configuration)
```toml
[tool.poetry]
name = "nix-for-humanity"
version = "1.0.0"

[tool.poetry.scripts]
ask-nix = "nix_for_humanity.cli:main"
nix-tui = "nix_for_humanity.interfaces.tui:main"

[tool.poetry.dependencies]
python = "^3.11"
requests = "^2.31.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
black = "^23.12.0"
ruff = "^0.1.0"
```

## 🎯 Sacred Trinity Workflow

### 1. Human (Tristan) - Vision
"We need a new feature for voice input"

### 2. Claude - Architecture
```bash
# Create feature branch
git checkout -b feat/voice-input

# Add voice dependencies
poetry add --optional whisper-cpp-python piper-tts

# Update pyproject.toml extras
[tool.poetry.extras]
voice = ["whisper-cpp-python", "piper-tts"]
```

### 3. Local LLM - NixOS Expertise
```bash
# Test in NixOS environment
poetry install --extras voice
poetry run pytest tests/voice/
```

### Result: $200/month achieving enterprise quality!

## 🌊 Best Practices

### 1. Always Use Poetry (Never pip!)
```bash
# ❌ WRONG
pip install requests

# ✅ CORRECT
poetry add requests
```

### 2. Lock File is Sacred
```bash
# Always commit poetry.lock
git add poetry.lock
git commit -m "chore: update dependencies"
```

### 3. Group Dependencies Logically
```toml
[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"

[tool.poetry.group.docs.dependencies]
mkdocs = "^1.5.0"

[tool.poetry.group.lint.dependencies]
black = "^23.12.0"
ruff = "^0.1.0"
```

### 4. Use Scripts for Common Tasks
```toml
[tool.poetry.scripts]
test = "scripts.run_tests:main"
lint = "scripts.run_linting:main"
format = "scripts.run_formatting:main"
```

### 5. Pre-commit Integration
```bash
# Already installed!
poetry run pre-commit install       # Set up hooks
poetry run pre-commit run --all-files  # Manual check
```

## 🔍 Troubleshooting

### Issue: Command not found after poetry install
```bash
# Solution: Use poetry run or enter shell
poetry run ask-nix "help"
# OR
poetry shell
ask-nix "help"
```

### Issue: Dependency conflicts
```bash
# Clear cache and reinstall
poetry cache clear pypi --all
rm -rf .venv
poetry install
```

### Issue: Wrong Python version
```bash
# Specify Python version
poetry env use python3.13
poetry install
```

## 📊 Monitoring Poetry Health

```bash
# Check for issues
poetry check

# Validate pyproject.toml
poetry validate

# Check for security vulnerabilities
poetry audit  # If plugin installed
```

## 🚀 Advanced Features

### Building Distributions
```bash
poetry build               # Create wheel and sdist
poetry publish            # Upload to PyPI
```

### Export Requirements
```bash
# For compatibility with pip
poetry export -f requirements.txt --output requirements.txt
poetry export --dev -f requirements.txt --output requirements-dev.txt
```

### Version Management
```bash
poetry version patch      # 1.0.0 -> 1.0.1
poetry version minor      # 1.0.0 -> 1.1.0
poetry version major      # 1.0.0 -> 2.0.0
```

## 🌟 Integration with NixOS

Our setup combines the best of both worlds:
- **NixOS** provides system packages (Poetry, Python, etc.)
- **Poetry** manages Python dependencies
- **Flake.nix** can use poetry2nix for full Nix integration

```nix
# In flake.nix (if using poetry2nix)
poetry2nix.mkPoetryApplication {
  projectDir = ./.;
  python = pkgs.python311;
}
```

## 🕉️ Sacred Development Mantras

- **"Poetry orchestrates, Python executes"**
- **"Lock files are contracts with the future"**
- **"Dependencies declare intention"**
- **"Virtual environments preserve sanity"**

## 📚 Resources

- [Poetry Documentation](https://python-poetry.org/docs/)
- [Poetry Commands Reference](https://python-poetry.org/docs/cli/)
- [pyproject.toml Specification](https://python-poetry.org/docs/pyproject/)
- [Sacred Trinity Workflow](./03-DEVELOPMENT/02-SACRED-TRINITY-WORKFLOW.md)

---

*"In the harmony of Poetry and Nix, Python dependencies flow like water - predictable, reproducible, and pure."*

**Remember**: Poetry is now permanently installed system-wide. You never need to use pip again!
