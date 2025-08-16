# Luminous Nix v1.0.0 Installation Guide

## System Requirements

- **OS**: NixOS 24.11 or newer (25.11 recommended for best performance)
- **RAM**: 2GB minimum, 4GB recommended
- **Disk**: 500MB for core, 2GB with all features
- **Python**: 3.11+ (provided by Nix)
- **Optional**: Microphone for voice interface

## Installation Methods

### Method 1: NixOS Module (Recommended)

1. Add to your `configuration.nix`:

```nix
{ config, pkgs, ... }:

{
  # Add Luminous Nix
  services.nixForHumanity = {
    enable = true;
    package = pkgs.nixForHumanity;
    
    # Optional features
    voice = {
      enable = true;
      wakeWord = "hey nix";
    };
    
    learning = {
      enable = true;
      privacy = "local-only";
    };
    
    # Personalization
    defaultPersona = "maya";  # Fast responses for ADHD
    theme = "consciousness";  # Sacred theme
  };
}
```

2. Rebuild your system:
```bash
sudo nixos-rebuild switch
```

### Method 2: Flakes (Modern Approach)

1. Create or update your `flake.nix`:

```nix
{
  description = "My NixOS configuration with Luminous Nix";
  
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
    luminous-nix.url = "github:Luminous-Dynamics/luminous-nix/v{version}";
  };
  
  outputs = { self, nixpkgs, luminous-nix }: {
    nixosConfigurations.myhost = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        ./configuration.nix
        luminous-nix.nixosModules.default
        {
          services.nixForHumanity.enable = true;
        }
      ];
    };
  };
}
```

2. Enable flakes and rebuild:
```bash
sudo nixos-rebuild switch --flake .#myhost
```

### Method 3: User Installation (No System Changes)

1. Clone and enter environment:
```bash
git clone https://github.com/Luminous-Dynamics/luminous-nix
cd luminous-nix
nix develop
```

2. Install to user profile:
```bash
./install-user.sh
```

3. Add to PATH:
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Method 4: Try Without Installing

```bash
nix run github:Luminous-Dynamics/luminous-nix#1.0.0 -- "help"
```

## Post-Installation Setup

### 1. Initial Configuration

Run the setup wizard:
```bash
ask-nix settings wizard
```

This will:
- Select your preferred interaction style
- Configure voice settings (if enabled)
- Set up learning preferences
- Create initial aliases

### 2. Voice Setup (Optional)

If voice is enabled:
```bash
ask-nix voice setup
```

Test voice:
```bash
ask-nix voice test
Say: "Hey Nix, what's the weather?"
```

### 3. Verify Installation

```bash
# Check version
ask-nix --version

# Run diagnostics
ask-nix diagnose

# Test core features
ask-nix "help"
ask-nix "list installed packages"
```

## Troubleshooting

### Common Issues

**"Command not found"**
- Ensure PATH includes installation directory
- Run `hash -r` to refresh command cache

**"Permission denied"**
- Some operations require sudo
- Check with `ask-nix "why does this need sudo?"`

**Voice not working**
- Check microphone permissions
- Ensure PulseAudio/PipeWire running
- Run `ask-nix voice diagnose`

**Slow responses**
- Enable Python backend: `export LUMINOUS_NIX_PYTHON_BACKEND=true`
- Check system resources: `ask-nix performance check`

### Getting Help

- **Quick help**: `ask-nix help [topic]`
- **Documentation**: `ask-nix docs`
- **Community**: https://github.com/Luminous-Dynamics/luminous-nix/discussions
- **Issues**: https://github.com/Luminous-Dynamics/luminous-nix/issues

## Uninstallation

### NixOS Module
Remove from `configuration.nix` and rebuild

### User Installation
```bash
~/.local/share/luminous-nix/uninstall.sh
```

### Clean all data
```bash
rm -rf ~/.config/luminous-nix
rm -rf ~/.local/share/luminous-nix
rm -rf ~/.cache/luminous-nix
```

---

**Next Steps**: Run `ask-nix tutorial` to start learning!
