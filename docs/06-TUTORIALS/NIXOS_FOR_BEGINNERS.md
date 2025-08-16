# 🌟 NixOS for Beginners - Learn with Natural Language

Welcome to NixOS through Luminous Nix! This tutorial will teach you NixOS basics using natural language commands instead of complex technical syntax.

## 📚 Table of Contents

1. [What is NixOS?](#what-is-nixos)
2. [Getting Started](#getting-started)
3. [Basic Commands](#basic-commands)
4. [Package Management](#package-management)
5. [System Configuration](#system-configuration)
6. [Troubleshooting](#troubleshooting)
7. [Next Steps](#next-steps)

---

## 🤔 What is NixOS?

NixOS is a unique Linux distribution that:
- **Never breaks** - You can always roll back changes
- **Reproducible** - Same configuration = same system everywhere
- **Declarative** - Describe what you want, not how to get there

### Traditional Linux vs NixOS

| Traditional Linux | NixOS |
|------------------|--------|
| `apt install firefox` | `ask-nix "install firefox"` |
| Can break on updates | Rollback anytime |
| Hard to replicate | Copy one file to clone |
| Manual configuration | Declare and done |

### Why Luminous Nix?

Instead of learning complex Nix syntax:
```nix
environment.systemPackages = with pkgs; [ firefox vim git ];
```

Just say what you want:
```bash
ask-nix "install firefox, vim, and git"
```

---

## 🚀 Getting Started

### Step 1: Install Luminous Nix

```bash
# One command installation
curl -sSL https://luminous-nix.dev/install.sh | bash

# Or if you downloaded the repository
./quick-install.sh
```

### Step 2: Test Installation

```bash
# Check it works
ask-nix --help

# See version
ask-nix --version
```

### Step 3: Set Your Preference

```bash
# Safe mode (preview only, default)
ask-nix settings set dry-run true

# Real mode (actually make changes)
ask-nix settings set dry-run false
```

---

## 💡 Basic Commands

### Getting Help

```bash
# General help
ask-nix "help"

# Help about specific topic
ask-nix "how do I install packages?"
ask-nix "what is a generation?"
```

### System Information

```bash
# Check NixOS version
ask-nix "what version of nixos am I running?"

# See system status
ask-nix "show system status"

# List channels
ask-nix "what channels do I have?"
```

---

## 📦 Package Management

### Searching for Packages

```bash
# Find packages by name
ask-nix "search firefox"

# Find by description
ask-nix "search for text editors"
ask-nix "find me a markdown editor"

# Get package info
ask-nix "tell me about neovim"
```

### Installing Packages

```bash
# Install single package
ask-nix "install firefox"

# Install multiple
ask-nix "install vim, git, and htop"

# Install with description
ask-nix "I need a web browser"
# Luminous Nix will suggest: firefox, chromium, brave
```

### Removing Packages

```bash
# Remove package
ask-nix "remove firefox"
ask-nix "uninstall vim"

# Clean up unused packages
ask-nix "clean up old packages"
```

### Updating System

```bash
# Update everything
ask-nix "update my system"

# Update specific package
ask-nix "update firefox"

# Check for updates
ask-nix "are there any updates?"
```

---

## ⚙️ System Configuration

### Understanding Generations

NixOS keeps snapshots of your system called "generations". You can always go back!

```bash
# List all generations
ask-nix "show me all generations"

# See current generation
ask-nix "what generation am I on?"

# Rollback to previous
ask-nix "rollback to previous generation"

# Switch to specific generation
ask-nix "switch to generation 42"
```

### Configuration Basics

```bash
# View current configuration
ask-nix "show my configuration"

# Add a service
ask-nix "enable ssh server"

# Configure timezone
ask-nix "set timezone to America/New_York"

# Enable feature
ask-nix "enable bluetooth"
```

### User Management

```bash
# Add user
ask-nix "create user alice"

# Add user to group
ask-nix "add alice to wheel group"

# Set up home manager
ask-nix "set up home manager for me"
```

---

## 🎯 Common Tasks

### Development Environment

```bash
# Set up Python development
ask-nix "create python development environment"

# Node.js project
ask-nix "I need nodejs and npm"

# Rust development
ask-nix "set up rust development tools"
```

### Desktop Environment

```bash
# Install desktop apps
ask-nix "install vscode"
ask-nix "I need a music player"
ask-nix "install slack for chat"

# Configure display
ask-nix "set display resolution to 1920x1080"
ask-nix "enable dark theme"
```

### System Maintenance

```bash
# Check disk space
ask-nix "how much disk space do I have?"

# Clean up
ask-nix "clean up old generations"
ask-nix "remove unused packages"

# Optimize store
ask-nix "optimize nix store"
```

---

## 🔧 Troubleshooting

### When Things Go Wrong

```bash
# If something breaks
ask-nix "rollback"  # Go back to working state

# Check what changed
ask-nix "what changed in last update?"

# See error logs
ask-nix "show recent errors"
```

### Getting Help

```bash
# Built-in help
ask-nix "I'm having trouble with [problem]"

# Explain error
ask-nix "what does this error mean: [paste error]"

# Suggestions
ask-nix "firefox won't start"
# Luminous Nix will suggest solutions
```

---

## 🌈 Using the TUI (Terminal UI)

For a visual interface, use the TUI:

```bash
# Launch TUI
nix-tui
```

### TUI Features

- **Tab 1: Terminal** - Run commands with visual feedback
- **Tab 2: Search** - Live package search
- **Tab 3: History** - See all your commands
- **Tab 4: Generations** - Manage system snapshots
- **Tab 5: Settings** - Configure Luminous Nix
- **Tab 6: Status** - System monitoring

### TUI Shortcuts

| Key | Action |
|-----|--------|
| `F1` | Help |
| `F2` | Toggle dry-run |
| `Tab` | Switch tabs |
| `↑/↓` | Navigate history |
| `Ctrl+L` | Clear screen |
| `Ctrl+Q` | Quit |

---

## 📝 Example Workflows

### Setting Up a New System

```bash
# 1. Update system
ask-nix "update everything"

# 2. Install essential packages
ask-nix "install firefox, terminal, text editor, and file manager"

# 3. Set up development tools
ask-nix "install git, make, gcc, and python"

# 4. Configure git
ask-nix "set up git with name 'John Doe' and email 'john@example.com'"

# 5. Enable useful services
ask-nix "enable ssh and firewall"
```

### Daily Usage

```bash
# Morning: Check for updates
ask-nix "any updates today?"

# Install new tool you heard about
ask-nix "install ripgrep"

# Afternoon: Need a tool but don't know the name
ask-nix "I need something to download youtube videos"
# Suggests: youtube-dl, yt-dlp

# Evening: Clean up
ask-nix "clean up old stuff"
```

### Experimenting Safely

```bash
# Try something new (safe mode)
ask-nix --dry-run "install experimental-package"

# If it looks good, do it for real
ask-nix "install experimental-package"

# If it causes problems
ask-nix "rollback"
```

---

## 💡 Pro Tips

### 1. Use Natural Language
Don't think about package names, just describe what you need:
- ❌ `ask-nix "install rxvt-unicode"`
- ✅ `ask-nix "I need a lightweight terminal"`

### 2. Start in Dry-Run Mode
Always preview changes first:
```bash
ask-nix --dry-run "big system change"
```

### 3. Use Generations Liberally
Before big changes:
```bash
ask-nix "create a checkpoint"  # Creates new generation
ask-nix "try something risky"
ask-nix "rollback if needed"
```

### 4. Learn from Luminous Nix
```bash
# See what command would run
ask-nix --show-command "install firefox"

# Understand NixOS better
ask-nix --explain "what are derivations?"
```

---

## 📚 Learning Resources

### Built-in Learning

```bash
# Interactive tutorial
ask-nix "start tutorial"

# Learn about specific topics
ask-nix "teach me about flakes"
ask-nix "explain channels"
```

### Quick References

```bash
# Command cheatsheet
ask-nix "show cheatsheet"

# Common tasks
ask-nix "show common commands"

# Best practices
ask-nix "nixos best practices"
```

---

## 🎓 Advanced Topics (When You're Ready)

### Flakes (Modern Nix)

```bash
# Enable flakes
ask-nix "enable flakes"

# Create a flake
ask-nix "create flake for this project"
```

### Home Manager

```bash
# Personal dotfiles management
ask-nix "set up home manager"
ask-nix "manage my dotfiles"
```

### Custom Configurations

```bash
# Generate configuration
ask-nix "generate config for web server"
ask-nix "create development environment config"
```

---

## ❓ Frequently Asked Questions

### Q: Is it safe to experiment?
**A:** Yes! NixOS + Luminous Nix makes it safe:
- Dry-run mode shows changes without applying
- Generations let you rollback anytime
- Nothing is permanently broken

### Q: Do I need to learn Nix syntax?
**A:** No! Luminous Nix handles the syntax for you. But if you're curious:
```bash
ask-nix --show-nix "install firefox"
# Shows: environment.systemPackages = with pkgs; [ firefox ];
```

### Q: Can I use regular Linux commands?
**A:** Yes! NixOS is still Linux:
```bash
ls, cd, grep, etc.  # All work normally
```

### Q: How do I contribute or get help?
**A:** 
- **Report issues**: `ask-nix "report a problem"`
- **Join community**: https://discord.gg/luminous-nix
- **Documentation**: https://luminous-nix.dev/docs

---

## 🚀 Next Steps

### Continue Learning

1. **Explore the TUI**: `nix-tui` for visual interface
2. **Try voice control**: `nix-voice` (if installed)
3. **Read advanced docs**: `ask-nix "show advanced documentation"`

### Build Something

```bash
# Create a project
ask-nix "set up a python web app project"

# Configure a service
ask-nix "set up nginx with ssl"

# Automate tasks
ask-nix "create a backup script"
```

### Share Your Configuration

```bash
# Export your config
ask-nix "export my configuration"

# Share with others
ask-nix "create shareable system config"
```

---

## 🎉 Congratulations!

You now know the basics of NixOS through Luminous Nix! Remember:

- **Describe what you want** in plain English
- **Experiment freely** - you can always rollback
- **Ask for help** - `ask-nix "help with [anything]"`

### Final Exercise

Try this complete workflow:
```bash
# 1. Check current state
ask-nix "show system info"

# 2. Search for something interesting
ask-nix "search for games"

# 3. Install it (dry-run first)
ask-nix --dry-run "install chess"
ask-nix "install chess"

# 4. Verify it worked
ask-nix "is chess installed?"

# 5. You're now a NixOS user! 🎊
```

---

*Welcome to the NixOS community! With Luminous Nix, you're speaking the language of reproducible, unbreakable Linux.* 🌟