# ⚙️ Configuration System - v0.2.0

## 🎯 Overview

Luminous Nix now supports user configuration files for customization! Personalize your experience with custom commands, aliases, and preferences.

## 📁 Config File Location

The config file is stored at:
```
~/.config/luminous-nix/config.json
```

## 🚀 Quick Start

### Initialize Config
```bash
ask-nix --init-config
```
Creates a config file with helpful examples and documentation.

### View Current Config
```bash
ask-nix --show-config
```

### Add Aliases On-the-Fly
```bash
ask-nix --set-alias npm nodePackages.npm
ask-nix --set-alias pip python3Packages.pip
```

### Add Custom Commands
```bash
ask-nix --set-command "safe update" "sudo nixos-rebuild test && sudo nixos-rebuild switch"
ask-nix --set-command "clean all" "nix-collect-garbage -d && nix-store --optimise"
```

## 📋 Configuration Options

### Preferences
```json
{
  "preferences": {
    "default_dry_run": false,      // Always preview commands first
    "auto_confirm": false,          // Skip confirmation prompts
    "show_command": true,           // Display actual command before running
    "use_nix_profile": true,        // Use modern nix profile vs legacy nix-env
    "search_timeout": 120,          // Timeout for search operations (seconds)
    "command_timeout": 30,          // Timeout for other commands (seconds)
    "verbose": false                // Show detailed output
  }
}
```

### Package Aliases
Map common names to actual Nix package names:
```json
{
  "aliases": {
    "npm": "nodePackages.npm",
    "yarn": "nodePackages.yarn",
    "pip": "python3Packages.pip",
    "cargo": "rustPackages.cargo"
  }
}
```

Now you can use: `ask-nix "install npm"`

### Custom Commands
Define your own command shortcuts:
```json
{
  "custom_commands": {
    "safe update": "sudo nixos-rebuild test && sudo nixos-rebuild switch",
    "clean all": "nix-collect-garbage -d && nix-store --optimise",
    "backup": "sudo nixos-rebuild boot",
    "list big": "nix path-info -rSh /run/current-system | sort -k2h"
  }
}
```

Use them naturally: `ask-nix "safe update"`

### Package Mappings
Override default package choices:
```json
{
  "package_mappings": {
    "code": "vscodium",           // Use VSCodium instead of VSCode
    "chrome": "ungoogled-chromium" // Use ungoogled-chromium instead
  }
}
```

### Disabled Commands
Prevent certain commands from running (safety):
```json
{
  "disabled_commands": [
    "rm -rf /",
    "sudo rm -rf /*"
  ]
}
```

## 🔧 Advanced Usage

### Use Custom Config File
```bash
ask-nix --config ~/my-config.json "install firefox"
```

### Programmatic Config Updates
```python
from nix_for_humanity.core.config import Config

config = Config()
config.set('preferences.default_dry_run', True)
config.add_alias('code', 'vscodium')
config.save()
```

## 📝 Full Example Config

```json
{
  "version": "0.2.0",
  "preferences": {
    "default_dry_run": false,
    "auto_confirm": false,
    "show_command": true,
    "use_nix_profile": true,
    "search_timeout": 120,
    "command_timeout": 30,
    "verbose": false
  },
  "aliases": {
    "npm": "nodePackages.npm",
    "yarn": "nodePackages.yarn",
    "pip": "python3Packages.pip",
    "docker-compose": "docker-compose",
    "make": "gnumake"
  },
  "custom_commands": {
    "safe update": "sudo nixos-rebuild test && sudo nixos-rebuild switch",
    "clean all": "nix-collect-garbage -d && nix-store --optimise",
    "backup": "sudo nixos-rebuild boot",
    "show big packages": "nix path-info -rSh /run/current-system | sort -k2h",
    "update flake inputs": "nix flake update && nix flake check"
  },
  "package_mappings": {
    "code": "vscodium",
    "chrome": "brave"
  },
  "disabled_commands": []
}
```

## 🎉 Benefits

- **Personalized Experience**: Tailor the tool to your workflow
- **Team Consistency**: Share configs across team members
- **Safety First**: Disable dangerous commands
- **Quick Shortcuts**: Define complex operations as simple phrases
- **No More Typos**: Map common misspellings to correct packages

## 🔄 Config Priority

Commands are resolved in this order:
1. **Custom Commands** (highest priority)
2. **Config Aliases** 
3. **Built-in Aliases**
4. **Package Mappings**
5. **Standard Patterns** (lowest priority)

This ensures your customizations always take precedence!

## 🌟 Next Steps

- Share your config with teammates
- Build a library of useful custom commands
- Contribute popular aliases back to the project
- Create workflow-specific configs (dev.json, ops.json)

---

The config system makes Luminous Nix truly *yours*. Happy customizing! 🚀