# Nix for Humanity Demo Video Script (2-3 minutes)

## Opening (10 seconds)
"Hi! I'm going to show you Nix for Humanity - natural language for NixOS. No more memorizing commands!"

## Basic Demo (60 seconds)

### Installing Software (20s)
```bash
# Old way:
# nix-env -iA nixpkgs.firefox
# or editing configuration.nix...

# New way:
ask-nix "install firefox"
```
*"See? It just works. Let's try something harder..."*

### Finding Packages (20s)
```bash
# Need a video editor but don't know package names?
ask-nix "find me a video editor"

# It shows options with descriptions!
```

### Getting Help (20s)
```bash
# System acting weird?
ask-nix "why is my wifi not working?"

# Or learning:
ask-nix "what's a nix generation?"
```

## Advanced Features (45 seconds)

### Config Generation (25s)
```bash
# Need a web server?
ask-nix "create nginx config with PHP"

# It generates a complete configuration.nix snippet!
```

### System Management (20s)
```bash
# Check system health
ask-nix "check my system"

# Rollback if needed
ask-nix "go back to yesterday's configuration"
```

## Closing (25 seconds)
"That's Nix for Humanity - making NixOS accessible to everyone. It's 100% local, learns your patterns, and transforms errors into teaching moments.

Download it free at github.com/Luminous-Dynamics/nix-for-humanity

Built with the Sacred Trinity model - proving small teams with AI can create amazing tools.

Thanks for watching!"

## Video Notes
- Keep energy high and friendly
- Show real terminal with actual commands
- Include a small mistake to show error handling
- Use a clean terminal theme
- Add captions for accessibility