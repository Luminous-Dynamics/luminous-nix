# Contributing to Nix for Humanity

Thank you for your interest in making NixOS accessible to everyone! Nix for Humanity v1.0.0 is now released with reliable CLI functionality.

## 🚀 Quick Start

```bash
# 1. Fork and clone
git clone https://github.com/YOUR_USERNAME/nix-for-humanity
cd nix-for-humanity

# 2. Enter development environment
nix develop

# 3. Run tests
pytest

# 4. Make your changes

# 5. Test your changes
./bin/ask-nix "help"  # Test CLI
pytest tests/         # Run test suite

# 6. Submit PR
```

## 🎯 What We Need Most

### Current Focus (v1.x improvements)
1. **Performance Optimization** - Make operations even faster
2. **Edge Cases** - Handle unusual package names and configurations
3. **Error Messages** - Make error messages even more helpful
4. **Documentation** - Keep docs accurate and helpful

### Coming in v1.1
1. **TUI Interface** - Beautiful terminal UI with Textual
2. **Voice Interface** - Natural speech interaction
3. **Advanced Learning** - Deeper personalization

## 📝 Development Guidelines

### Code Style
- Python 3.11+ with type hints
- Black for formatting
- Clear variable names over clever ones
- Comments explain "why", not "what"

### Testing
- Every new feature needs tests
- Integration tests > unit tests for this project
- Test with real NixOS commands, not mocks
- Consider all 10 user personas

### Commits
- Clear, descriptive messages
- Reference issues: "Fix #123: Install command timeout"
- Small, focused changes
- One feature/fix per PR

## 🏗️ Architecture Basics

```
backend/
├── core/           # Shared logic and utilities
├── nlp/            # Natural language processing
├── execution/      # Command runners with native Python-Nix API
└── api/            # Frontend communication

frontends/
├── cli/            # Terminal interface (v1.0 - working great!)
├── tui/            # Textual UI (v1.1 - coming soon)
└── voice/          # Speech interface (v1.1 - coming soon)
```

## 🐛 How to Fix a Bug

1. **Reproduce** - Confirm you can trigger the bug
2. **Write Test** - Add failing test that exposes the bug
3. **Fix** - Make the minimal change to pass the test
4. **Verify** - Run full test suite
5. **Document** - Update relevant docs if behavior changed

## ✨ How to Add a Feature

1. **Discuss First** - Open an issue to discuss the idea
2. **Design** - How does it fit the consciousness-first philosophy?
3. **Implement** - Start simple, iterate
4. **Test** - With all personas in mind
5. **Document** - Both user-facing and technical docs

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_nlp.py

# Run with coverage
pytest --cov=nix_for_humanity

# Test actual CLI
./bin/ask-nix "install firefox" --dry-run
```

## 📚 Understanding the Codebase

### v1.0.0 Status
- **CLI works** - All core commands reliable
- **Native Python-Nix API** - Lightning-fast operations
- **Learning system** - Improves with usage
- **Tests** - Comprehensive integration tests

### Key Files
- `backend/core/nlp.py` - Natural language processing
- `backend/execution/nix_executor.py` - Command execution with native API
- `frontends/cli/ask_nix.py` - Main CLI entry point
- `frontends/tui/app.py` - Textual UI (coming in v1.1)

## 🤝 Pull Request Process

1. **Fork** the repository
2. **Create branch**: `git checkout -b fix/install-timeout`
3. **Make changes** with tests
4. **Run checks**: `pytest && black .`
5. **Push branch**: `git push origin fix/install-timeout`
6. **Open PR** with clear description

### PR Template
```markdown
## What
Brief description of changes

## Why
What problem does this solve?

## How
Technical approach taken

## Testing
How to verify the fix works

## Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Real integration test added
```

## 💬 Communication

### GitHub Issues
- Bug reports with reproduction steps
- Feature discussions
- Documentation improvements

### Design Decisions
- Align with consciousness-first philosophy
- Consider all 10 personas
- Prioritize simplicity over features
- Local-first, privacy always

## 🌟 Recognition

All contributors will be recognized in our README. Your work helps make NixOS accessible to everyone.

## ❓ Questions?

- Open an issue for technical questions
- Check existing docs first
- Be patient - we're all learning together

---

**Remember**: We're building technology that amplifies human consciousness. Every contribution should move us closer to that goal.

Welcome to the Sacred Trinity! 🙏