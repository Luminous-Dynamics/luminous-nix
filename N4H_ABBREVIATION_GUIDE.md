# N4H (Luminous Nix) Abbreviation Guide

## 🎯 Quick Reference
**N4H** = **N**ix **for** **H**umanity

## 📋 When to Use Each Form

### Use "N4H" in:
- **Internal code** - Variable names, constants, environment variables
- **Development documentation** - Technical docs, code comments
- **Log messages** - Debug output, system logs
- **Scripts & tooling** - Shell scripts, development tools
- **Directory names** - `n4h-tests/`, `n4h-utils/`
- **Configuration** - `N4H_CONFIG_PATH`, `N4H_DEBUG=true`

### Use "Luminous Nix" in:
- **User-facing content** - UI messages, error messages to users
- **Public documentation** - README, website, marketing
- **Release notes** - Changelogs, announcements
- **External communications** - GitHub issues, discussions
- **First mentions** - Always spell out first, then use N4H

## 🔧 Common Abbreviations

| Full Name | Abbreviation | Usage Example |
|-----------|--------------|---------------|
| Luminous Nix | N4H | `N4H_HOME=/path/to/n4h` |
| N4H Terminal UI | N4H-TUI | `n4h-tui --theme dark` |
| N4H Command Line | N4H-CLI | `n4h-cli install firefox` |
| N4H Voice Interface | N4H-Voice | `n4h-voice --model whisper` |
| N4H API Server | N4H-API | `N4H_API_PORT=8080` |
| N4H Python Backend | N4H-PB | `N4H_PB_ENABLED=true` |

## 💻 Environment Variables

```bash
# Recommended environment variables using N4H prefix
export N4H_HOME=/srv/luminous-dynamics/11-meta-consciousness/luminous-nix
export N4H_PYTHON_BACKEND=true  # Enable native Python-Nix API
export N4H_DEBUG=false           # Debug mode
export N4H_CONFIG_PATH=~/.config/n4h/settings.json
export N4H_CACHE_DIR=~/.cache/n4h
export N4H_LOG_LEVEL=INFO
```

## 📁 Directory Structure Recommendations

```
n4h/                    # Root project directory (short!)
├── n4h-core/          # Core backend
├── n4h-cli/           # CLI commands
├── n4h-tui/           # Terminal UI
├── n4h-voice/         # Voice interface
├── n4h-api/           # REST API
├── n4h-tests/         # Test suite
├── n4h-docs/          # Documentation
└── n4h-examples/      # Examples
```

## 🏷️ Git Conventions

```bash
# Commit messages
git commit -m "feat(n4h-core): add fuzzy package matching"
git commit -m "fix(n4h-cli): handle missing arguments"
git commit -m "docs(n4h): update installation guide"

# Branch naming
feature/n4h-voice-integration
bugfix/n4h-cli-timeout
release/n4h-v1.2.0
```

## 📝 Code Comments

```python
# N4H: Natural language processing for package discovery
def discover_packages():
    """N4H package discovery using fuzzy matching."""
    pass

# Initialize N4H backend with performance optimizations
n4h_backend = N4HBackend(enable_cache=True)
```

## 🔗 Import Statements

```python
# Internal imports can use n4h prefix
from n4h.core import Engine
from n4h.cli import execute_command
from n4h.utils import logger

# Or use full name for clarity
from nix_for_humanity.core import Engine
```

## 📊 Logging

```python
logger.info("N4H: Starting natural language processing")
logger.debug("N4H-CLI: Parsing command: %s", command)
logger.error("N4H-API: Connection failed to port %d", port)
```

## 🚀 Command Line Tools

```bash
# Consider renaming binaries for brevity
n4h ask "install firefox"      # Instead of: ask-nix "install firefox"
n4h-tui                        # Instead of: nix-tui
n4h-voice                      # Instead of: nix-voice
n4h config --wizard            # Configuration wizard
```

## ✅ Migration Checklist

When adopting N4H abbreviation:
- [ ] Update environment variable names
- [ ] Update log message prefixes
- [ ] Consider renaming long directory paths
- [ ] Update internal documentation
- [ ] Keep user-facing docs with full name
- [ ] Add this guide to new developer onboarding

## 🎯 Benefits of N4H

1. **Brevity** - Saves typing in development
2. **Recognition** - Easy to grep/search for
3. **Namespace** - Clear prefix for all related items
4. **Professional** - Common pattern (K8s, AWS, GCP)
5. **Memorable** - Short acronym sticks

## ⚠️ Important Notes

- **Always introduce the full name first** in any document
- **Keep the brand "Luminous Nix"** for public presence
- **N4H is for developer convenience**, not branding change
- **Be consistent** - pick one form per context

---

*Example introduction in docs:*
> "Luminous Nix (N4H) is a natural language interface for NixOS. Throughout this documentation, we'll refer to it as N4H for brevity."