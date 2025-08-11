# 🚀 Start Here - Nix for Humanity

**Make NixOS simple through natural language.** Type what you want, we handle the complexity.

## What Actually Works (v1.0)

✅ **Natural language commands** - "install firefox" just works
✅ **Lightning fast** - <0.5s response times via native Python-Nix integration
✅ **Smart learning** - Improves based on your usage patterns
✅ **Educational errors** - Transforms cryptic Nix errors into helpful guidance

## Choose Your Path

### 👤 I want to USE it
```bash
# Install
pip install nix-for-humanity

# Try it
ask-nix "install firefox"
ask-nix "update my system"
ask-nix "find markdown editor"
```
**Next**: [User Guide](./06-TUTORIALS/USER_GUIDE.md) → [Troubleshooting](./TROUBLESHOOTING.md)

### 🛠️ I want to CONTRIBUTE
```bash
# Setup
git clone https://github.com/Luminous-Dynamics/nix-for-humanity
cd nix-for-humanity
pip install -e .

# Test
pytest tests/
```
**Next**: [Quick Start](./03-DEVELOPMENT/03-QUICK-START.md) → [Architecture](./02-ARCHITECTURE/01-SYSTEM-ARCHITECTURE.md)

### 🚀 I want to DEPLOY it
```bash
# NixOS module
services.nix-for-humanity.enable = true;
```
**Next**: [Installation](./04-OPERATIONS/EASY-INSTALLATION-GUIDE.md) → [Configuration](./05-REFERENCE/CONFIGURATION.md)

## Coming Soon (v1.1)
🚧 Terminal UI (TUI) - Beautiful interface
🚧 Voice control - Speak naturally
📅 Advanced personas - Adaptive to your style

## Questions?
- **It's broken**: [Troubleshooting](./TROUBLESHOOTING.md)
- **How does it work?**: [Architecture](./02-ARCHITECTURE/01-SYSTEM-ARCHITECTURE.md)
- **Report issues**: [GitHub Issues](https://github.com/Luminous-Dynamics/nix-for-humanity/issues)

---
*That's it. Pick your path and go.*
