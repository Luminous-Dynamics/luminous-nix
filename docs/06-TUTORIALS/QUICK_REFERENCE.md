# ⚡ Luminous Nix Quick Reference

A quick reference for common NixOS tasks using natural language with Luminous Nix.

## 🎯 Most Common Commands

| What You Want | What You Type |
|---------------|---------------|
| Install package | `ask-nix "install firefox"` |
| Search packages | `ask-nix "search text editor"` |
| Update system | `ask-nix "update everything"` |
| Rollback changes | `ask-nix "rollback"` |
| See what changed | `ask-nix "what changed?"` |
| Get help | `ask-nix "help"` |

## 📦 Package Management

### Searching
```bash
ask-nix "search [name]"              # By name
ask-nix "find [description]"         # By description  
ask-nix "what provides [command]?"   # By command
ask-nix "alternatives to [package]"  # Similar packages
```

### Installing
```bash
ask-nix "install [package]"          # Single package
ask-nix "install [p1], [p2], [p3]"   # Multiple packages
ask-nix "I need a [description]"     # By description
ask-nix "install [package] for user" # User-only install
```

### Removing
```bash
ask-nix "remove [package]"           # Remove package
ask-nix "uninstall [package]"        # Same as remove
ask-nix "clean up unused"            # Remove orphans
ask-nix "purge [package]"            # Remove with config
```

### Updating
```bash
ask-nix "update system"               # Full system update
ask-nix "update [package]"           # Single package
ask-nix "check for updates"          # See available updates
ask-nix "update channel"             # Update package lists
```

## 🔄 Generation Management

### Viewing
```bash
ask-nix "list generations"           # Show all
ask-nix "current generation"         # Show current
ask-nix "compare generations 41 42"  # See differences
ask-nix "generation history"         # Recent changes
```

### Switching
```bash
ask-nix "rollback"                   # Previous generation
ask-nix "switch to generation 42"    # Specific generation
ask-nix "rollback 2 generations"     # Go back multiple
ask-nix "boot into generation 42"    # Set for next boot
```

### Cleanup
```bash
ask-nix "delete old generations"     # Keep recent ones
ask-nix "keep last 5 generations"    # Specific number
ask-nix "delete generation 40"       # Specific one
ask-nix "clean generations older than 30 days"
```

## ⚙️ System Configuration

### Services
```bash
ask-nix "enable ssh"                 # Enable service
ask-nix "disable bluetooth"          # Disable service
ask-nix "restart nginx"              # Restart service
ask-nix "status of postgresql"       # Check service
ask-nix "list running services"      # See all services
```

### Users
```bash
ask-nix "create user alice"          # New user
ask-nix "add alice to wheel"         # Add to group
ask-nix "set alice's shell to zsh"   # Change shell
ask-nix "list users"                 # Show all users
```

### Network
```bash
ask-nix "set hostname to mypc"       # Change hostname
ask-nix "configure wifi"             # WiFi setup
ask-nix "enable firewall"            # Firewall on
ask-nix "open port 8080"            # Open port
```

### Hardware
```bash
ask-nix "enable bluetooth"           # Bluetooth support
ask-nix "configure printer"          # Printer setup
ask-nix "enable nvidia drivers"      # Graphics drivers
ask-nix "mount usb drive"           # USB mounting
```

## 🛠️ Development

### Environments
```bash
ask-nix "create python env"          # Python development
ask-nix "setup node project"         # Node.js project
ask-nix "rust development tools"     # Rust toolchain
ask-nix "c++ development"           # C++ environment
```

### Shells
```bash
ask-nix "enter shell with python"    # Temporary shell
ask-nix "shell with gcc and make"   # Build tools
ask-nix "create shell.nix"          # Shell file
ask-nix "load development shell"    # From shell.nix
```

### Docker/Containers
```bash
ask-nix "enable docker"              # Docker support
ask-nix "install podman"            # Podman alternative
ask-nix "setup kubernetes tools"    # K8s tools
```

## 🔍 Information & Debugging

### System Info
```bash
ask-nix "system info"                # Overview
ask-nix "nixos version"             # Version info
ask-nix "disk usage"                # Storage info
ask-nix "memory usage"              # RAM info
ask-nix "list channels"             # Package channels
```

### Package Info
```bash
ask-nix "info about firefox"        # Package details
ask-nix "dependencies of vim"       # Dependencies
ask-nix "what owns /bin/ls"        # File ownership
ask-nix "size of package"           # Disk usage
```

### Troubleshooting
```bash
ask-nix "check system health"       # Health check
ask-nix "verify configuration"      # Config check
ask-nix "rebuild test"              # Test build
ask-nix "show recent errors"        # Error logs
ask-nix "why is X failing?"        # Diagnose issue
```

## 🎨 Customization

### Configuration Files
```bash
ask-nix "edit configuration"        # Open config
ask-nix "show configuration"        # View config
ask-nix "backup configuration"      # Save backup
ask-nix "restore configuration"     # From backup
```

### Flakes (Advanced)
```bash
ask-nix "enable flakes"             # Turn on flakes
ask-nix "create flake"              # New flake
ask-nix "update flake"              # Update inputs
ask-nix "build flake"               # Build flake
```

### Home Manager
```bash
ask-nix "install home manager"      # Setup
ask-nix "configure vim"             # App config
ask-nix "manage dotfiles"           # Dotfile management
ask-nix "backup home config"        # Save home config
```

## ⌨️ Keyboard Shortcuts (TUI)

| Key | Action |
|-----|--------|
| `F1` | Show help |
| `F2` | Toggle dry-run mode |
| `F3` | Toggle voice input |
| `F5` | Refresh |
| `Tab` | Next field/tab |
| `↑/↓` | Navigate history |
| `Ctrl+L` | Clear screen |
| `Ctrl+K` | Clear cache |
| `Ctrl+P` | Package search |
| `Ctrl+Q` | Quit |

## 🔧 Command Options

### Global Flags
```bash
ask-nix --dry-run "..."            # Preview only
ask-nix --verbose "..."            # Detailed output
ask-nix --quiet "..."              # Minimal output
ask-nix --json "..."               # JSON output
ask-nix --help                     # Show help
ask-nix --version                  # Show version
```

### Settings
```bash
ask-nix settings list               # Show all settings
ask-nix settings get dry-run       # Get setting value
ask-nix settings set dry-run false # Change setting
ask-nix settings reset              # Default settings
```

## 💡 Natural Language Tips

### Be Descriptive
```bash
# Instead of package names:
ask-nix "I need to edit videos"     # Suggests: kdenlive, openshot
ask-nix "terminal file manager"     # Suggests: ranger, mc, nnn
ask-nix "burn iso to usb"          # Suggests: dd, etcher
```

### Ask Questions
```bash
ask-nix "how do I ...?"            # Get instructions
ask-nix "what is ...?"             # Get explanations
ask-nix "why does ...?"            # Troubleshooting
ask-nix "can I ...?"               # Check possibilities
```

### Use Context
```bash
ask-nix "install it"               # Refers to last search
ask-nix "same but for python 3.11" # Modifies last command
ask-nix "undo that"                # Reverses last action
```

## 🆘 Emergency Commands

```bash
ask-nix "rollback now"             # Immediate rollback
ask-nix "boot previous"            # Boot old generation
ask-nix "repair system"            # Fix corruptions
ask-nix "reset to defaults"        # Factory reset
ask-nix "emergency help"           # Crisis assistance
```

## 📝 Examples

### Complete System Setup
```bash
# Update first
ask-nix "update system"

# Install desktop apps
ask-nix "install firefox, thunderbird, libreoffice, vlc"

# Development tools
ask-nix "install vscode, git, docker, nodejs"

# Enable services
ask-nix "enable ssh, firewall, and bluetooth"

# Configure
ask-nix "set timezone to America/New_York"
```

### Daily Workflow
```bash
# Morning
ask-nix "check for updates"
ask-nix "update if needed"

# Working
ask-nix "create python project"
ask-nix "install pytest"

# Cleanup
ask-nix "clean old generations"
ask-nix "optimize store"
```

### Safe Experimentation
```bash
# Save state
ask-nix "checkpoint"

# Try something
ask-nix --dry-run "major change"
ask-nix "major change"

# If problems
ask-nix "rollback to checkpoint"
```

---

*Remember: Just describe what you want in plain English. Luminous Nix handles the complex Nix syntax for you!* 🌟