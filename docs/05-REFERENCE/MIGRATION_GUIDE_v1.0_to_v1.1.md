# Migration Guide: v1.0 → v1.1

## 🎯 Overview

Upgrading from v1.0 to v1.1 is seamless! All your existing CLI commands continue to work exactly the same, with new TUI and Voice interfaces as optional enhancements.

## ✅ What Stays the Same

- All CLI commands work identically
- Same configuration files
- Same performance benefits
- Same privacy guarantees
- Same local-first approach

## 🆕 What's New

### 1. Terminal UI (TUI)
- Launch with `nix-tui`
- Beautiful visualizations
- Living consciousness orb
- Keyboard-driven workflow

### 2. Voice Interface
- Launch with `nix-voice`
- Natural speech commands
- Multiple voice personas
- Wake word activation

## 📦 Upgrade Steps

### For NixOS Users

```bash
# Update flake input
nix flake update github:Luminous-Dynamics/nix-for-humanity

# Rebuild system
sudo nixos-rebuild switch
```

### For Development Install

```bash
# Pull latest changes
cd nix-for-humanity
git fetch origin
git checkout v1.1.0

# Update dependencies
nix develop
poetry install -E tui -E voice
```

## 🔧 Configuration Changes

### New Optional Settings

```yaml
# ~/.config/nix-humanity/config.yaml

# TUI settings (optional)
tui:
  theme: "default"  # or "minimal", "vibrant"
  animations: true
  complexity: "adaptive"  # or "beginner", "expert"

# Voice settings (optional)
voice:
  wake_word: "hey nix"
  persona: "friendly"  # or "professional", "technical"
  language: "en-US"
```

### Backward Compatibility

Your existing v1.0 config works without any changes. New settings are purely optional.

## 🚀 Quick Start Commands

```bash
# Still works exactly the same
ask-nix "install firefox"

# New TUI mode
nix-tui

# New voice mode
nix-voice
```

## 💡 Feature Comparison

| Feature | v1.0 | v1.1 |
|---------|------|------|
| CLI Commands | ✅ | ✅ |
| Native Performance | ✅ | ✅ |
| Natural Language | ✅ | ✅ |
| Config Generation | ✅ | ✅ |
| Terminal UI | ❌ | ✅ |
| Voice Interface | ❌ | ✅ |
| Consciousness Orb | ❌ | ✅ |

## 🎯 Choosing Your Interface

### Use CLI When:
- Quick one-off commands
- Scripting/automation
- SSH sessions
- Minimal resource usage

### Use TUI When:
- Extended work sessions
- Learning NixOS
- Monitoring operations
- Visual feedback desired

### Use Voice When:
- Hands-free operation
- Accessibility needs
- Natural interaction
- Multitasking

## ⚠️ Breaking Changes

**None!** v1.1 is fully backward compatible with v1.0.

## 🐛 Troubleshooting

### Issue: Old commands not working
This shouldn't happen. If it does:
```bash
# Verify version
ask-nix --version

# Should show 1.1.0
```

### Issue: TUI dependencies missing
```bash
# Reinstall with extras
poetry install -E tui -E voice
```

## 📚 Learning Resources

1. **TUI Guide**: `docs/06-TUTORIALS/TUI_GUIDE.md`
2. **Voice Guide**: `docs/06-TUTORIALS/VOICE_GUIDE.md`
3. **Video Tutorials**: Coming soon!

## 🔄 Rollback (If Needed)

```bash
# Rollback to v1.0
git checkout v1.0.0
poetry install
```

Your config and data remain compatible.

## 🎉 What Users Are Saying

> "The TUI makes learning NixOS so much easier!" - Beta Tester

> "Voice commands feel like magic" - Early Adopter

> "Finally, visual feedback for what's happening!" - Power User

## 🙏 Thank You

Thank you for being an early adopter of Nix for Humanity! Your journey from v1.0 to v1.1 helps us make NixOS accessible to everyone.

---

**Questions?** See [V1.1_TROUBLESHOOTING.md](./V1.1_TROUBLESHOOTING.md) or create an issue!
