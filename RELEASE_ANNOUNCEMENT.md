# 🎉 Luminous Nix v1.0.1 Released!

## Critical Bug Fix for Natural Language Processing

We've just released **v1.0.1**, a critical patch that fixes pattern recognition in natural language queries.

### What Was Fixed

The bug where queries like "i need firefox" incorrectly identified "need" as the package name has been resolved. Natural language now works as intended!

### Verified Patterns Now Working
- ✅ "i need firefox" 
- ✅ "i want vim"
- ✅ "help me install brave"
- ✅ "can you install htop"
- ✅ "please install git"

### Test Coverage Improvements
- 44 new tests added
- Pattern recognition 100% tested
- Integration tests for CLI interface
- 59% coverage on knowledge engine

### How to Update

```bash
# If using git
git pull origin main
git checkout v1.0.1
poetry install --all-extras

# Test the fix
./bin/ask-nix "i need firefox"
```

### Verify It's Working

```bash
# Run the pattern tests
poetry run pytest tests/unit/test_pattern_fix.py -v
# Should show 12 tests passing
```

### Links
- 📦 [GitHub Release](https://github.com/Luminous-Dynamics/luminous-nix/releases/tag/v1.0.1)
- 📖 [Full Release Notes](https://github.com/Luminous-Dynamics/luminous-nix/blob/v1.0.1/RELEASE-v1.0.1.md)
- 🐛 [Report Issues](https://github.com/Luminous-Dynamics/luminous-nix/issues)

### What's Next (v1.1.0)
- Terminal UI (TUI) interface
- Voice interface foundation
- 80% test coverage target
- Performance optimizations

### Thank You!
Thanks to everyone who reported issues and provided feedback. Your input helps make NixOS accessible to everyone through natural conversation!

---

**Making NixOS accessible through natural language** 🌊

#NixOS #OpenSource #Accessibility #NaturalLanguage