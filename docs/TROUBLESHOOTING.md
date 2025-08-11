# 🔧 Troubleshooting Guide

Quick fixes for common problems. If your issue isn't here, [file a bug report](https://github.com/Luminous-Dynamics/nix-for-humanity/issues).

## Common Issues

### "Command not found: ask-nix"

**Problem**: The command isn't in your PATH
**Solution**:
```bash
# If installed via pip
export PATH="$HOME/.local/bin:$PATH"

# If using development version
cd /path/to/nix-for-humanity
./bin/ask-nix "your command"
```

### "Permission denied" when running commands

**Problem**: NixOS operations need sudo
**Solution**:
```bash
# ask-nix handles sudo automatically, but if it fails:
sudo ask-nix "install package"

# Or grant your user nix permissions:
sudo usermod -a -G nix-users $USER
```

### "No module named nix_for_humanity"

**Problem**: Python can't find the package
**Solution**:
```bash
# Reinstall
pip uninstall nix-for-humanity
pip install -e .

# Check Python path
python -c "import sys; print(sys.path)"
```

### Response times are slow (>1 second)

**Problem**: Not using native Python backend
**Solution**:
```bash
# Enable native backend
export NIX_HUMANITY_PYTHON_BACKEND=true

# Verify it's working
ask-nix --diagnose
```

### "nix-env: command not found"

**Problem**: Nix isn't installed or not in PATH
**Solution**:
```bash
# Check if Nix is installed
which nix-env

# If not found, you need Nix or NixOS
curl -L https://nixos.org/nix/install | sh
```

### Natural language not working

**Problem**: Intent recognition failing
**Examples that should work**:
```bash
ask-nix "install firefox"          # ✅ Works
ask-nix "install the firefox"      # ✅ Works
ask-nix "get me firefox browser"   # ✅ Works
ask-nix "sudo apt install firefox" # ❌ Don't include other package managers
```

### Database locked error

**Problem**: SQLite database is locked
**Solution**:
```bash
# Kill any stuck processes
pkill -f ask-nix

# Remove lock file
rm ~/.local/share/nix-for-humanity/cache.db-journal

# Reset database
ask-nix --reset-cache
```

### Import errors with Textual/TUI

**Problem**: TUI dependencies not installed
**Solution**:
```bash
# Install TUI extras
pip install nix-for-humanity[tui]

# Or manually
pip install textual rich
```

## Performance Issues

### High memory usage

**Check current usage**:
```bash
ask-nix --metrics
```

**Clear caches**:
```bash
ask-nix --clear-cache
rm -rf ~/.cache/nix-for-humanity/
```

### Slow package searches

**Use specific terms**:
```bash
# Slow
ask-nix "find editor"

# Fast
ask-nix "find markdown editor"
```

## Configuration Problems

### Settings not taking effect

**Location**: `~/.config/nix-for-humanity/config.yaml`

**Verify config**:
```bash
ask-nix --show-config
```

**Reset to defaults**:
```bash
rm ~/.config/nix-for-humanity/config.yaml
ask-nix --init-config
```

## Debug Mode

**Get detailed output**:
```bash
# Enable debug logging
export NIX_HUMANITY_DEBUG=true
ask-nix "your command"

# Full diagnostic
ask-nix --diagnose > debug.log
```

## Known Limitations

### What DOESN'T work yet

- ❌ Voice control (coming v1.1)
- ❌ GUI (planned)
- ❌ Windows support (use WSL)
- ❌ Nix flakes commands (coming soon)

### NixOS-specific issues

**Rebuild timeouts**: NixOS rebuilds can timeout. Run in background:
```bash
nohup sudo nixos-rebuild switch &
tail -f nohup.out
```

## Emergency Reset

**Nuclear option - reset everything**:
```bash
# Stop all processes
pkill -f nix-for-humanity

# Remove all data
rm -rf ~/.local/share/nix-for-humanity
rm -rf ~/.config/nix-for-humanity
rm -rf ~/.cache/nix-for-humanity

# Reinstall
pip uninstall nix-for-humanity -y
pip install nix-for-humanity
```

## Still Stuck?

1. Check [GitHub Issues](https://github.com/Luminous-Dynamics/nix-for-humanity/issues)
2. Run diagnostics: `ask-nix --diagnose`
3. File a bug with the diagnostic output

---
*Remember: Most issues are PATH or permission problems. Start there.*
