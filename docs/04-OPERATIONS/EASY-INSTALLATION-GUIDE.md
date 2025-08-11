# 🚀 Easy Installation Guide - Nix for Humanity

## ✨ One-Line Installation (Coming Soon!)

```bash
curl -L https://nix-humanity.org/install | sh
```

*Until then, follow our friendly manual installation:*

## 📋 Pre-Installation Check

```bash
# Run our friendly pre-flight check
curl -L https://nix-humanity.org/check | sh

# It will tell you:
✅ NixOS version: Compatible
✅ Python version: 3.11+ found
✅ Disk space: 2GB free
✅ Network: Connected
✅ Ready to install!
```

## 🎯 Installation Methods

### Method 1: Nix Flakes (Recommended) 
```bash
# Add to your flake.nix
{
  inputs.nix-humanity.url = "github:Luminous-Dynamics/nix-for-humanity";
  
  outputs = { self, nixpkgs, nix-humanity }: {
    nixosConfigurations.myhost = nixpkgs.lib.nixosSystem {
      modules = [
        nix-humanity.nixosModules.default
      ];
    };
  };
}

# Then rebuild
sudo nixos-rebuild switch --flake .#myhost
```

### Method 2: Traditional Channel
```bash
# Add channel
sudo nix-channel --add https://github.com/Luminous-Dynamics/nix-for-humanity/archive/main.tar.gz nix-humanity
sudo nix-channel --update

# Add to configuration.nix
{ config, pkgs, ... }: {
  imports = [
    <nix-humanity/nixos-module>
  ];
  
  programs.nix-humanity = {
    enable = true;
    defaultPersona = "friendly";  # Options: minimal, friendly, technical, sacred
  };
}

# Rebuild
sudo nixos-rebuild switch
```

### Method 3: Development Install
```bash
# Clone and enter shell
git clone https://github.com/Luminous-Dynamics/nix-for-humanity.git
cd nix-for-humanity
nix develop

# Test it works
./bin/ask-nix "hello"

# Link for system-wide use
sudo ln -s $(pwd)/bin/ask-nix /usr/local/bin/
```

## 🔧 Common Installation Issues & Fixes

### Issue: "Permission denied"
```bash
# ❌ Error
bash: /usr/local/bin/ask-nix: Permission denied

# ✅ Fix
sudo chmod +x /usr/local/bin/ask-nix
# Or use Nix-native installation instead
```

### Issue: "Python module not found"
```bash
# ❌ Error  
ModuleNotFoundError: No module named 'nix_humanity'

# ✅ Fix - Enter development shell
nix develop
# All dependencies are provided automatically!
```

### Issue: "Nix command not found"
```bash
# ❌ Error
bash: nix: command not found

# ✅ Fix - Install Nix first
curl -L https://nixos.org/nix/install | sh
# Then retry Nix for Humanity installation
```

### Issue: "Slow first startup"
```bash
# 🐌 First run downloading dependencies...

# ✅ Fix - Pre-fetch for faster start
nix-store --realise $(nix-build --no-out-link)
# Now first run will be instant!
```

## 🎨 Post-Installation Setup

### 1. Run First-Time Wizard
```bash
$ ask-nix --setup

🌟 Welcome to Nix for Humanity Setup!

Let's personalize your experience:

1. Choose your preferred style:
   [ ] Minimal - Just the facts
   [x] Friendly - Encouraging and warm
   [ ] Technical - Detailed information
   [ ] Sacred - Consciousness-first

2. Enable features:
   [x] Smart suggestions
   [x] Educational errors
   [x] Command history
   [ ] Anonymous usage sharing

3. Accessibility needs:
   [ ] High contrast mode
   [ ] Screen reader optimization
   [ ] Large text
   [x] None needed

✅ Setup complete! Try: ask-nix "help"
```

### 2. Quick Functionality Test
```bash
# Test basic commands
ask-nix "help"                    # Should show guide
ask-nix "search editor"           # Should list editors
ask-nix "install firefox --dry"   # Should preview

# If any fail, run diagnostics
ask-nix --diagnose
```

### 3. Enable Shell Integration (Optional)
```bash
# For Bash
echo 'source <(ask-nix --shell-integration bash)' >> ~/.bashrc

# For Zsh  
echo 'source <(ask-nix --shell-integration zsh)' >> ~/.zshrc

# For Fish
ask-nix --shell-integration fish > ~/.config/fish/conf.d/nix-humanity.fish

# This enables:
# - Smart autocomplete
# - Command suggestions
# - Inline help
```

## 🏥 Installation Health Check

```bash
$ ask-nix --health

🏥 Nix for Humanity Health Check

Core Systems:
✅ Backend engine: Operational
✅ Knowledge base: Loaded (15,234 packages)
✅ NLP engine: Ready
✅ Learning system: Active

Performance:
✅ Startup time: 0.3s (Good)
✅ Command response: 0.08s (Excellent)
✅ Memory usage: 45MB (Normal)

Optional Features:
✅ Voice interface: Available
⚠️  Local LLM: Not configured (Optional)
✅ TUI mode: Ready

Overall: 🟢 Healthy
```

## 🔐 Verification

### Verify Installation Integrity
```bash
# Check signatures
nix-store --verify-path $(which ask-nix)

# Verify functionality
ask-nix --self-test

# Check for updates
ask-nix --check-updates
```

## 🌍 Platform-Specific Notes

### NixOS
- Native installation works best
- Systemd service included
- Auto-updates with system

### Non-NixOS Linux
- Requires Nix package manager
- Works on Ubuntu, Fedora, Arch, etc.
- May need `--experimental-features 'nix-command flakes'`

### macOS
- Full support on Intel and Apple Silicon
- May need to allow in Security settings
- Voice features use macOS TTS

### WSL2
- Full support in WSL2
- Requires systemd enabled
- Native Windows support planned

## 🆘 Still Having Issues?

### Automated Troubleshooter
```bash
# Run our intelligent troubleshooter
curl -L https://nix-humanity.org/troubleshoot | sh

# It will:
# - Detect your environment
# - Identify common issues
# - Suggest specific fixes
# - Offer to fix automatically
```

### Manual Diagnostics
```bash
# Collect diagnostic info
ask-nix --diagnose > diagnostic.log

# Check the log for:
# - Missing dependencies
# - Permission issues  
# - Configuration problems
# - Version conflicts
```

### Community Support
- 💬 [GitHub Discussions](https://github.com/Luminous-Dynamics/nix-for-humanity/discussions)
- 🐛 [Issue Tracker](https://github.com/Luminous-Dynamics/nix-for-humanity/issues)
- 📧 Email: support@nix-humanity.org
- 💭 Discord: [Join our Sacred Trinity](https://discord.gg/nix-humanity)

## 🎉 Installation Success!

Once installed, you'll see:
```bash
$ ask-nix "hello"

👋 Hello! I'm Nix for Humanity, your friendly NixOS assistant.

I can help you:
- Install software naturally: "install a web browser"
- Search packages: "find video editors"
- Generate configs: "set up a web server"
- Fix problems: "why is audio not working"

What would you like to do today?
```

## 📚 Next Steps

1. **Quick Start**: `ask-nix tutorial`
2. **Explore Features**: `ask-nix showcase`
3. **Read Guide**: [User Guide](../06-TUTORIALS/USER_GUIDE.md)
4. **Watch Demos**: [Video Tutorials](../06-TUTORIALS/VIDEO-DEMO-SCRIPTS.md)

---

## 🚧 Troubleshooting Principles

Our error messages follow these principles:

1. **Assume Nothing**: Every error explains itself
2. **Provide Solutions**: Never just report problems
3. **Educational**: Each error teaches something
4. **Encouraging**: Errors are learning opportunities

Example:
```bash
# Instead of:
ERROR: Failed to install package

# We show:
📦 I couldn't install firefox because:
   The Nix daemon isn't running

💡 To fix this:
   1. Start the daemon: sudo systemctl start nix-daemon
   2. Or run without daemon: ask-nix --no-daemon "install firefox"

📚 Learn more: ask-nix "help nix daemon"
```

---

*Installation should be the easiest part of your Nix journey. If it's not, we've failed - please let us know so we can improve!*

**Remember**: Every installation issue fixed helps the next person have a smoother experience. Your struggle today is someone else's success tomorrow! 🌟