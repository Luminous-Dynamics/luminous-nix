# 📝 Naming Conventions - Luminous Nix

## 🌟 Project Names

### Full Name: **Luminous Nix**
- **Usage**: Official documentation, presentations, marketing
- **Context**: When we want to emphasize the full vision and philosophy
- **Example**: "Luminous Nix brings natural language to NixOS"

### Abbreviation: **Luminix**
- **Usage**: Where brevity is valuable (URLs, file paths, package names)
- **Context**: Technical contexts where shorter names are practical
- **Examples**:
  - GitHub URL: `github.com/Luminous-Dynamics/luminix` (future possibility)
  - Config directory: `~/.config/luminix/`
  - Python package: Could be `import luminix` for brevity

### Command: **ask-nix** (Always!)
- **Philosophy**: Conversational, humane, natural
- **Never abbreviate to**: `lnx`, `luminix`, `lmx`, etc.
- **Why**: "Ask" implies conversation and respect, not commanding
- **Examples**:
  ```bash
  ask-nix "install firefox"          # Natural
  ask-nix "help me with networking"  # Conversational
  ask-nix "what's installed?"        # Friendly
  ```

## 📂 File & Directory Naming

### Current (Recommended)
```
/srv/luminous-dynamics/11-meta-consciousness/luminous-nix/  # Full name for clarity
~/.config/luminous-nix/                                     # User knows what it is
```

### Alternative (When brevity needed)
```
~/.config/luminix/                  # Shorter for user configs
/var/lib/luminix/                   # System paths
/tmp/luminix-cache/                 # Temp files
```

## 🔧 Environment Variables

### Primary (Current)
```bash
LUMINOUS_NIX_PYTHON_BACKEND=true    # Clear and descriptive
LUMINOUS_NIX_DEBUG=1                # Obvious what project
```

### Alternative (If needed)
```bash
LUMINIX_PYTHON_BACKEND=true         # Shorter but still clear
LUMINIX_DEBUG=1                     # Abbreviated form
```

## 📦 Package Names

### Python Package
- **Current**: `luminous_nix` (underscore for Python convention)
- **Import**: `from luminous_nix import ...`
- **Alternative**: Could migrate to `luminix` for brevity if desired

### System Packages
- **NixOS package**: `luminous-nix` or `luminix`
- **Binary**: Always `ask-nix` (never change this!)
- **Service names**: `luminix.service` (shorter is better for systemd)

## 🎨 Branding Guidelines

### When to Use Each Form

**"Luminous Nix"**
- README headers
- Documentation titles
- User-facing messages
- Marketing materials
- Philosophy discussions

**"Luminix"**
- Technical configurations
- File paths when needed
- Package identifiers
- URLs (optional)
- Quick references

**"ask-nix"**
- ALWAYS for the command
- Never abbreviate
- Never change
- This is sacred - it embodies our conversational philosophy

## 💡 Examples in Practice

### Documentation
```markdown
# Luminous Nix User Guide          ✅ Full name in titles
Welcome to Luminous Nix!           ✅ Full name in greetings
Config at ~/.config/luminix/       ✅ Can abbreviate paths
Run: ask-nix "install firefox"     ✅ Always ask-nix for commands
```

### Code Comments
```python
# Luminous Nix Core Engine         ✅ Full name for major components
# Quick luminix cache check        ✅ Can abbreviate in casual comments
# Process ask-nix commands         ✅ Command name never changes
```

### Error Messages
```
Luminous Nix Error: Package not found    ✅ Full name in formal errors
Check ~/.config/luminix/settings.toml    ✅ Can abbreviate in paths
Try: ask-nix "search for firefox"        ✅ Always ask-nix in examples
```

## 🚫 What NOT to Do

### Never These Commands
```bash
luminix "install firefox"     ❌ Loses conversational nature
lnx "install firefox"         ❌ Too abbreviated
nix-ask "install firefox"     ❌ Wrong order, sounds robotic
lum-nix "install firefox"     ❌ Awkward abbreviation
```

### Never These Variables
```bash
NIX_HUMANITY_*                ❌ Old name
LNX_*                         ❌ Too abbreviated  
LUMNIX_*                      ❌ Weird spelling
ASK_NIX_*                     ❌ Command shouldn't be env prefix
```

## 🎯 The Golden Rule

> **"Luminous Nix" for beauty, "Luminix" for brevity, "ask-nix" for humanity**

The command `ask-nix` is the soul of the project - it makes technology approachable through natural conversation. Never compromise this for the sake of brevity.

## 📝 Migration Notes

### From "Nix for Humanity"
- `nix_for_humanity` → `luminous_nix` (Python package)
- `NIX_HUMANITY_*` → `LUMINOUS_NIX_*` (env vars)
- `/nix-for-humanity/` → `/luminous-nix/` (directories)
- Repository: `nix-for-humanity` → `luminous-nix` or `luminix`

### Command Stays Same
- `ask-nix` → `ask-nix` (NO CHANGE! This is perfect as is)

---

*Remember: Technology should adapt to humans, not the other way around. The name "ask-nix" embodies this philosophy perfectly.*