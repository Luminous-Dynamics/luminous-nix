# 🚀 Quick Start Guide - Your First 5 Minutes

> From zero to productive in 5 minutes or less!

## 🎯 What You'll Achieve

In the next 5 minutes, you'll:
- ✅ Install a package using natural language
- ✅ Search for software without memorizing commands
- ✅ Create a development environment
- ✅ Set up personal shortcuts
- ✅ Feel confident using NixOS!

## ⏱️ Minute 1: First Command

No setup needed! Just type:

```bash
ask-nix "install firefox"
```

What happens:
- 🔍 Finds the correct package name
- 📦 Shows what will be installed
- ✅ Confirms it's safe (dry-run by default)

Ready to actually install? Add `--execute`:

```bash
ask-nix --execute "install firefox"
```

**That's it!** No memorizing `nix-env -iA nixos.firefox` or other cryptic commands.

## ⏱️ Minute 2: Find Software

Not sure of the exact package name? No problem:

```bash
ask-nix "find text editor"
```

You'll see:
```
Found 8 text editors:
  1. vscode - Visual Studio Code
  2. vim - Vi Improved
  3. neovim - Vim-fork focused on extensibility
  4. emacs - Extensible text editor
  5. sublime-text - Sophisticated text editor
  ...
```

Want more details?

```bash
ask-nix "tell me about vscode"
```

## ⏱️ Minute 3: Development Environment

Need a quick development setup?

```bash
ask-nix "python development environment"
```

This creates a complete environment with:
- Python 3.11+
- pip & virtualenv
- Common development tools
- Proper PATH setup

Enter the environment:
```bash
nix-shell
# You're now in a Python dev environment!
python --version
```

## ⏱️ Minute 4: Personal Shortcuts

Make it even faster with aliases:

```bash
# Create shortcuts
ask-nix-config alias --add i "install"
ask-nix-config alias --add s "search"
ask-nix-config alias --add py "python development environment"

# Now use them!
ask-nix i vim        # Install vim
ask-nix s docker     # Search for docker
ask-nix py          # Python environment
```

## ⏱️ Minute 5: See Your Progress

Check what you've done:

```bash
# View your command history
ask-nix-config history

# See your statistics
ask-nix-config stats

# View your aliases
ask-nix-config alias --show
```

## 🎉 Congratulations!

You've just:
- ✅ Installed software naturally
- ✅ Searched without memorizing commands
- ✅ Created development environments
- ✅ Personalized your workflow
- ✅ Tracked your progress

## 🏃 Keep Going! Next Steps

### Essential Commands to Try

```bash
# System updates
ask-nix "update my system safely"

# Package removal
ask-nix "remove package firefox"

# System cleanup
ask-nix "clean up old packages"

# See what's installed
ask-nix "list installed packages"

# Roll back changes
ask-nix "undo last system change"
```

### Power User Features

```bash
# Multiple packages at once
ask-nix "install git vim and tmux"

# Specific versions
ask-nix "install python 3.11"

# Development environments
ask-nix "rust development with web framework"

# System configuration
ask-nix "configure ssh server"

# Generate NixOS configurations
ask-nix "web server with nginx and ssl"
```

## 💡 Pro Tips for Beginners

### 1. Everything is Safe by Default

```bash
ask-nix "install something"  # Just shows what would happen
ask-nix --execute "install something"  # Actually does it
```

### 2. Get Help Anytime

```bash
ask-nix "help"
ask-nix "how do I update packages"
ask-nix "explain this error: [paste error]"
```

### 3. Natural Language Works

Instead of memorizing commands, just describe what you want:

- ❌ `nix-env -qaP | grep -i office | head -20`
- ✅ `ask-nix "find office software"`

- ❌ `nix-shell -p nodejs-18_x yarn python311`
- ✅ `ask-nix "development with node 18, yarn, and python"`

### 4. Learn as You Go

The system learns your preferences:
- Frequently used packages appear first in searches
- Common patterns become suggestions
- Your aliases speed up workflows

## 🔍 Common First-Day Tasks

### "I need a web browser"
```bash
ask-nix "find web browser"
ask-nix "install brave"  # or firefox, chromium, etc.
```

### "I need development tools"
```bash
ask-nix "install git and vscode"
ask-nix "python with jupyter notebook"
ask-nix "nodejs with npm and yarn"
```

### "I need office software"
```bash
ask-nix "install libreoffice"
# or
ask-nix "find pdf reader"
```

### "I need multimedia"
```bash
ask-nix "install vlc media player"
ask-nix "find image editor"  # GIMP, Krita, etc.
```

## 🚨 If Something Goes Wrong

### Can't find a package?
```bash
ask-nix "search all packages for [keyword]"
ask-nix "find alternatives to [software]"
```

### Made a mistake?
```bash
ask-nix "undo last change"
ask-nix "rollback system"
```

### Need explanation?
```bash
ask-nix "explain error: [error message]"
ask-nix "why did this fail"
```

## 📊 What You've Saved

In just 5 minutes, you've avoided:
- 📚 30 minutes of documentation reading
- 🤯 Memorizing 10+ complex commands
- ❌ Multiple syntax errors
- 😤 Frustration with cryptic error messages

## 🎓 Next Learning Steps

1. **[Migration Guide](./02-migration-guide.md)** - For existing NixOS users
2. **[Python Development](./dev-environments/python.md)** - Set up Python projects
3. **[System Configuration](./system-configs/web-server.md)** - Configure services
4. **[Troubleshooting](./troubleshooting/common-errors.md)** - Solve problems

## 🌟 Welcome to Easier NixOS!

You're now part of a community making NixOS accessible to everyone. Share your experience:

```bash
# See how much time you've saved
ask-nix-config stats

# Share your success!
# "I just set up my dev environment in 30 seconds with Nix for Humanity!"
```

---

*Remember: Every complex NixOS task is now just a simple sentence away. No more command memorization, just natural communication!*

**Next step:** Try installing your favorite software with `ask-nix "install [software]"`