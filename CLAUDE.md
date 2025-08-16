# 🤖 Claude Code Instructions - Luminous Nix

**Purpose**: Project-specific instructions for Claude Code sessions
**Parent Context**: `/srv/luminous-dynamics/CLAUDE.md`
**Setup Guide**: `CLAUDE_SETUP_INSTRUCTIONS.md`
**Naming Guide**: `NAMING_CONVENTIONS.md`

## 📝 Project Naming
- **Full name**: Luminous Nix (for documentation, branding)
- **Abbreviation**: Luminix (where brevity matters - URLs, configs)
- **Command**: `ask-nix` (ALWAYS - never abbreviate, keeps it conversational)

## ⚠️ CRITICAL: Update Documentation When Working

**ALWAYS update status documents when making changes:**
- `docs/04-OPERATIONS/CURRENT_STATUS_DASHBOARD.md` - Update scores, phase progress, TODOs count
- `docs/04-OPERATIONS/IMPLEMENTATION_STATUS.md` - Update feature completion status
- `.claude/session-notes.md` - Log work done in session
- Relevant feature docs when implementing/fixing

**Example**: The TODO count was 3,944 but actually only 116 - always verify and update!

## 📂 CRITICAL: Understanding the Source Structure

### Where to Find What (FINAL Structure - 2025-08-12)

**Directory Guide** (15 clean modules, down from 26+)

| Directory | Purpose | Key Files |
|-----------|---------|-----------|
| `core/` | Business logic | engine.py, executor.py, backend.py |
| `nix/` | NixOS integration | native_api.py, packages.py, config.py |
| `interfaces/` | ALL user interfaces | cli.py, voice.py, tui_components/, ui_components/ |
| `learning/` | AI/ML/NLP (unified) | nlp.py, personas.py, patterns.py |
| `api/` | REST/WebSocket | v1.py, schema.py |
| `cli/` | CLI commands | Individual command handlers |
| `config/` | Configuration | settings.py, profiles.py |
| `utils/` | ALL utilities | logging.py, cache.py, errors.py |
| `plugins/` | Plugin system | Plugin manager |
| `knowledge/` | Knowledge base | Documentation engine |

### ✅ What We Consolidated
- `backend/` + `core/` → `core/` only
- `ai/` + `nlp/` + `learning/` → `learning/` only  
- `ui/` + `tui/` + `voice/` → `interfaces/` only
- `utils/` + `logging/` + `monitoring/` + `cache/` + `errors/` → `utils/` only

### ⚠️ Import Changes Required
```python
# OLD imports (will break)
from nix_for_humanity.backend.native_nix_api import NixAPI
from nix_for_humanity.ai.nlp import NLPEngine
from nix_for_humanity.tui.app import TUIApp

# CURRENT imports (use these)
from luminous_nix.nix.native_api import NixAPI
from luminous_nix.learning.nlp import NLPEngine  
from luminous_nix.interfaces.tui_components.app import TUIApp
```

## 🚫 CRITICAL: Never Test Non-Existent Features

**GOLDEN RULE**: "Test what IS, build what WILL BE, document what WAS"

**NEVER CREATE TESTS FOR FEATURES THAT DON'T EXIST:**
- ❌ Don't write aspirational tests hoping features will appear
- ❌ Don't maintain tests for phantom features (we have 955 of these!)
- ❌ Don't claim coverage for non-existent code

**ALWAYS:**
- ✅ Test only features that are actually implemented
- ✅ Write tests WITH features, not before (TDD) or never (aspirational)
- ✅ Delete or archive tests for removed features
- ✅ Be honest about real coverage (8%, not 95%)

**REALITY CHECK**: We discovered 955 broken tests for features that were never built. This created false "95% coverage" when reality is 8%. Never repeat this mistake!

## 🌟 CRITICAL: Sophisticated Simplicity Philosophy

### Core Philosophy: Simple Building + Sophisticated Thinking = Elegant Results
**"Perfection is achieved not when there is nothing more to add, but when there is nothing left to take away."** - Antoine de Saint-Exupéry

### 📚 Essential Reading
- **[Sophisticated Simplicity V2](docs/philosophy/SOPHISTICATED_SIMPLICITY_V2.md)** - Our refined manifesto (MUST READ)
- **[The Litmus Test](docs/03-DEVELOPMENT/LITMUS_TEST_CHECKLIST.md)** - 5 questions before every commit

### 🎯 The Paradox Resolved: We Achieve BOTH
**Simple/Elegant AND Comprehensive/Sophisticated** through:
- **Sophisticated thinking** → Deep strategic analysis (vision documents)
- **Simple building** → Minimal implementation (658 lines)
- **Elegant composition** → Simple parts create complex behavior
- **Comprehensive outcomes** → Emergent sophistication handles all cases

### 🏗️ Engineering Principles (ALWAYS APPLY)
1. **KISS** - Keep It Simple, Stupid
2. **YAGNI** - You Aren't Gonna Need It  
3. **DRY** - Don't Repeat Yourself
4. **Less is More** - 74% less code = 74% fewer bugs
5. **Generic > Specific** - 3 categories beat 14 specific cases
6. **Platform-Native** - Use NixOS features, don't reinvent
7. **🆕 Emergent Sophistication** - Complex behavior from simple rules
8. **🆕 Compositional Power** - Unix philosophy: simple tools, powerful combinations

### ✅ Simplification Checklist
**Before adding ANY feature, ask:**
- Can existing code handle this? → Use it
- Is this truly needed now? → Probably not (YAGNI)
- Can a simpler solution work? → Always choose simpler
- Are we reinventing platform features? → Use platform instead
- Will this add complexity? → Reconsider approach
- Can simple composition achieve this? → Compose, don't complicate
- Will sophistication emerge naturally? → Wait for evolution

### 📊 Proven Results (Updated 2025-08-15)
- **Permission System**: 60% code reduction, 100x faster
- **Healing Engine**: 84% code reduction, 1,600x faster
- **Total System**: 74% smaller, dramatically better
- **Friction Monitoring**: 150 lines provide adaptive behavior
- **Strategic Distillation**: 213 pages → 5 actionable insights
- **Unix Composition**: 3 generic actions handle 95% of cases
- **🆕 Flow Protection**: 100 lines prevent 47% productivity loss from interruptions

### 🧠 How to Handle Strategic Documents
**When encountering sophisticated analysis (like vision documents):**
1. **Appreciate the depth** - Shows we understand the domain
2. **Extract simple insights** - Find 3-5 actionable items
3. **Archive the complexity** - Keep for future reference
4. **Implement minimally** - 10% of ideas = 90% of value
5. **Let sophistication emerge** - Don't force complex features

**The Formula:**
- Strategic Thinking (PhD level) + Simple Implementation (Hello World) = Revolutionary Software
- Example: 213 pages of analysis → 150 lines of friction monitoring → Adaptive behavior emerges

## 🛡️ CRITICAL: Prevent Code Sprawl

**BEFORE EVERY SESSION, RUN:**
```bash
python scripts/detect-sprawl.py  # Check sprawl score (must be <10)
```

**NEVER CREATE THESE FILES:**
- `*_enhanced.py` - Modify original instead
- `*_unified.py` - Use single implementation
- `*_consolidated.py` - Merge into original
- `*_v2.py`, `*_v3.py` - Use git branches
- `*_new.py`, `*_improved.py` - Update original
- `*_simple.py`, `*_complex.py` - One version only

**ALWAYS:**
- Start with simplest possible solution
- Question every line of code added
- Remove code before adding code
- Trust platform features over custom solutions
- Archive old code when replacing (don't keep both)

## 🚀 Session Initialization

When starting work on Luminous Nix:

1. **Read Parent Context**: `/srv/luminous-dynamics/CLAUDE.md` - Overall philosophy
2. **Read Critical Workarounds**: `/srv/luminous-dynamics/.claude/NIXOS_REBUILD_WORKAROUND.md`
3. **Read Setup Instructions**: `CLAUDE_SETUP_INSTRUCTIONS.md` - Development environment
4. **Verify Environment**:
   ```bash
   cd /srv/luminous-dynamics/11-meta-consciousness/luminous-nix
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

### 🚨 CRITICAL: Always Add Missing Dependencies
**NEVER create simplified versions without dependencies!**
- If code needs scipy → `poetry add scipy`
- If code needs pandas → `poetry add pandas`  
- If code needs any library → ADD IT, don't work around it

Creating "simpler versions" without dependencies breaks the system and wastes time. Always add the proper dependencies instead.

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

## 🏗️ Service Layer Architecture (NEW 2025-08-12)

### 🌟 Unified Service Layer Pattern
We now use a **Service Layer Architecture** to eliminate code duplication between CLI, TUI, Voice, and API interfaces. All interfaces use the same service layer for consistency and performance.

**Architecture Decision**: `/srv/luminous-dynamics/11-meta-consciousness/luminous-nix/ARCHITECTURE_ANALYSIS.md`

### Key Components:
- **Service Layer** (`src/luminous_nix/service.py` or `service_simple.py`) - Single source of truth
- **Direct Python calls** - No subprocess overhead between interfaces  
- **Shared functionality** - Aliases, settings, learning all in one place
- **Backend abstraction** - Interfaces don't need to know backend details

### Benefits:
- ✅ No code duplication between interfaces
- ✅ 10x performance (no subprocess calls)
- ✅ Consistent behavior across all interfaces
- ✅ Easier testing and maintenance
- ✅ Single place to add new features

## 🏗️ Project Structure (REORGANIZED 2025-08-12)

### ✅ Clean, Single-Purpose Structure
```
luminous-nix/
├── pyproject.toml          # Poetry config (SOURCE OF TRUTH)
├── poetry.lock             # Locked dependencies (ALWAYS COMMIT)
│
├── bin/                    # CLI Entry Points (MINIMAL)
│   ├── ask-nix            # THE ONLY CLI - handles all modes
│   ├── nix-tui            # TUI launcher (calls ask-nix --tui)
│   ├── nix-voice          # Voice launcher (calls ask-nix --voice)
│   └── archive/           # Old variants archived here
│
├── src/luminous_nix/       # Main Package (can abbreviate to luminix in URLs/configs)
│   ├── core/              # Core business logic
│   │   ├── engine.py      # Main execution engine
│   │   ├── executor.py    # Command execution
│   │   ├── intents.py     # Intent recognition
│   │   └── knowledge.py   # Knowledge base
│   │
│   ├── nix/               # NixOS integration
│   │   ├── api.py         # Native Python-Nix API
│   │   ├── commands.py    # Nix command wrappers
│   │   └── config.py      # Configuration generation
│   │
│   ├── interfaces/        # All user interfaces
│   │   ├── cli.py         # CLI interface
│   │   ├── tui.py         # TUI interface (Textual)
│   │   ├── voice.py       # Voice interface
│   │   └── api.py         # REST/WebSocket API
│   │
│   ├── learning/          # AI/ML components
│   │   ├── nlp.py         # Natural language processing
│   │   └── personas.py    # User personas
│   │
│   └── utils/             # Utilities
│       ├── config.py      # Configuration management
│       ├── logging.py     # Logging setup
│       └── errors.py      # Error handling
│
├── tests/                  # Test suite
├── docs/                   # Documentation
├── examples/               # Example scripts
└── archive/                # Historical code
```

### 🎯 Key Principles
- **ONE CLI**: `bin/ask-nix` is the ONLY entry point
- **NO DUPLICATES**: One implementation per feature
- **CLEAR BOUNDARIES**: Each module has a single purpose
- **ARCHIVE OLD CODE**: Don't delete, archive for reference

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
cd /srv/luminous-dynamics/11-meta-consciousness/luminous-nix
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
