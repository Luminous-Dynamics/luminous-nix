# Luminous Nix - Production MVP

## What Actually Works (v0.1.0)

This is a **minimal viable product** that provides basic natural language interface for NixOS package management.

### ✅ Working Features

- **Natural language to Nix command translation** 
  - `ask-nix install firefox` → `nix profile install nixpkgs#firefox`
  - `ask-nix search python` → `nix search nixpkgs python`
  - `ask-nix list installed` → `nix profile list`
  - `ask-nix system info` → `nixos-version`

- **Modern Nix support** - Automatically detects and uses `nix profile` vs legacy `nix-env`
- **Dry-run mode** - Preview commands without executing: `ask-nix --dry-run install vim`
- **Safety checks** - Blocks dangerous commands, requires confirmation for system changes
- **Command suggestions** - Helpful hints when commands aren't understood

### 📦 Installation

```bash
cd /srv/luminous-dynamics/11-meta-consciousness/luminous-nix
chmod +x bin/ask-nix

# Add to PATH (optional)
export PATH="$PWD/bin:$PATH"
```

### 🚀 Usage

```bash
# Show help
ask-nix --help

# Show example commands
ask-nix --suggest

# Install a package (with confirmation)
ask-nix install firefox

# Search for packages
ask-nix search python

# List installed packages
ask-nix list installed

# System information
ask-nix system info

# Preview without executing
ask-nix --dry-run install vim

# Auto-confirm (skip prompts)
ask-nix --yes install git
```

### 🧪 Testing

```bash
# Run basic test suite
python3 test_mvp.py

# Test dry-run mode
./bin/ask-nix --dry-run install firefox
```

### 📂 Project Structure (Actual)

```
luminous-nix/
├── bin/
│   └── ask-nix              # Entry point script
├── src/
│   └── nix_for_humanity/
│       ├── __init__.py      # Package init
│       ├── cli/
│       │   ├── __init__.py
│       │   └── main.py      # CLI argument parsing
│       └── core/
│           ├── __init__.py
│           ├── translator.py # Natural language → Nix commands
│           └── executor.py   # Safe command execution
└── test_mvp.py              # Basic test suite
```

### ⚠️ Limitations

- Basic pattern matching (not AI/ML)
- Limited command vocabulary 
- No voice interface yet
- No TUI yet
- No advanced features from the ambitious documentation

### 🎯 Next Steps for Production

1. **Expand command patterns** - Add more common NixOS operations
2. **Improve error messages** - Better guidance when commands fail
3. **Add configuration file** - User preferences and aliases
4. **Package properly** - Create a proper Nix derivation
5. **Real tests** - Unit tests with pytest
6. **Documentation** - Update main README to reflect reality

### 🤝 Contributing

This MVP needs real-world testing and feedback:

1. Try it with your daily NixOS tasks
2. Report what commands you wish worked
3. Submit pattern additions for common operations
4. Help identify edge cases and safety concerns

### 📝 Version History

- **v0.1.0** - Initial MVP with basic command translation
  - Pattern-based natural language processing
  - Modern `nix profile` support
  - Safety checks and dry-run mode
  - Basic test coverage

### 🔧 Technical Notes

- **No subprocess for simple operations** - Direct pattern matching is fast
- **Auto-detects Nix version** - Works with both legacy and modern Nix
- **Timeout handling** - Search operations get 120s, others 30s
- **Python 3.11+** required (as configured in pyproject.toml)

---

This is a **working tool** that does what it says. The ambitious vision in the main README is aspirational - this MVP is the foundation we can actually build on.