# ⚙️ Configuration Reference

*Complete guide to configuring Luminous Nix*

---

💡 **Quick Context**: Comprehensive configuration options for personalizing your natural language NixOS experience
📍 **You are here**: Reference → Configuration Reference (Customization Guide)
🔗 **Related**: [User Guide](../06-TUTORIALS/USER_GUIDE.md) | [CLI Commands](./01-CLI-COMMANDS.md) | [Master Documentation Map](../MASTER_DOCUMENTATION_MAP.md)
⏱️ **Read time**: 20 minutes
📊 **Mastery Level**: 🌿 Intermediate - understanding of YAML, environment variables, and system configuration helpful

🌊 **Natural Next Steps**:
- **For setup**: Start with [Quick Start Guide](../03-DEVELOPMENT/03-QUICK-START.md) before diving into configuration
- **For troubleshooting**: Reference [Troubleshooting Guide](../04-OPERATIONS/03-TROUBLESHOOTING.md) when configuration issues arise
- **For advanced usage**: Continue to [CLI Commands Reference](./01-CLI-COMMANDS.md) for command-specific options
- **For comprehensive help**: Explore [User Guide](../06-TUTORIALS/USER_GUIDE.md) for configuration patterns in context

---

## Configuration Overview

Luminous Nix can be configured through multiple methods:
1. **Environment variables** - Quick runtime settings
2. **Configuration files** - Persistent user preferences
3. **Command-line flags** - Per-command overrides
4. **User profiles** - Persona-specific settings

## Configuration File Locations

### User Configuration
```bash
# Primary config file
~/.config/luminous-nix/config.yaml

# User data directory
~/.local/share/luminous-nix/

# Cache directory
~/.cache/luminous-nix/

# Legacy locations (automatically migrated)
~/.luminous-nix/config.yaml
```

### System Configuration
```bash
# System-wide settings (requires root)
/etc/luminous-nix/config.yaml

# NixOS module configuration
/etc/nixos/luminous-nix.nix
```

## Configuration File Format

### Basic Configuration (`config.yaml`)

```yaml
# Luminous Nix Configuration File
# Location: ~/.config/luminous-nix/config.yaml

# Core Settings
core:
  version: "0.8.3"
  backend: "python"                    # python, nodejs, or hybrid
  data_directory: "~/.local/share/luminous-nix"
  cache_directory: "~/.cache/luminous-nix"
  log_level: "info"                    # debug, info, warn, error

# User Interface Settings
ui:
  default_personality: "friendly"      # minimal, friendly, encouraging, technical, accessible
  response_format: "structured"        # plain, structured, json, yaml
  show_commands: true                  # Show underlying NixOS commands
  confirm_actions: true                # Ask before executing commands
  use_colors: true                     # Colored output
  progress_indicators: true            # Show progress bars

# Natural Language Processing
nlp:
  engine: "hybrid"                     # rule-based, statistical, neural, hybrid
  confidence_threshold: 0.7            # Minimum confidence for suggestions
  typo_correction: true                # Auto-correct common typos
  context_memory: 10                   # Remember last N interactions
  learning_enabled: true               # Learn from user interactions

# Performance Settings
performance:
  fast_mode: false                     # Prioritize speed over accuracy
  cache_responses: true                # Cache common responses
  parallel_processing: true            # Use multiple CPU cores
  memory_limit: "512MB"                # Maximum memory usage
  timeout: 30                          # Command timeout in seconds

# Privacy & Security
privacy:
  data_collection: "minimal"           # none, minimal, standard, full
  share_anonymous_stats: false         # Help improve the system
  local_only: true                     # Never send data externally
  encrypt_data: true                   # Encrypt stored data
  auto_cleanup: true                   # Clean old data automatically

# Learning System
learning:
  enabled: true                        # Enable learning from interactions
  personal_preferences: true           # Learn user preferences
  command_patterns: true               # Learn command usage patterns
  error_recovery: true                 # Learn from corrections
  privacy_mode: "strict"               # strict, balanced, open
  retention_days: 365                  # Keep learning data for N days

# Accessibility
accessibility:
  screen_reader: false                 # Optimize for screen readers
  high_contrast: false                 # Use high contrast colors
  large_text: false                    # Use larger text in TUI
  reduce_motion: false                 # Minimize animations
  keyboard_only: false                 # Optimize for keyboard navigation
  simple_language: false               # Use simpler vocabulary

# Voice Interface (when available)
voice:
  enabled: false                       # Enable voice commands
  wake_word: "hey nix"                 # Voice activation phrase
  language: "en-US"                    # Voice recognition language
  voice_feedback: true                 # Speak responses
  noise_reduction: true                # Filter background noise

# Development Settings
development:
  debug_mode: false                    # Enable debug features
  test_mode: false                     # Use test data
  api_logging: false                   # Log API calls
  performance_profiling: false         # Profile performance
  mock_execution: false                # Don't actually run commands
```

## Environment Variables

### Core Configuration
```bash
# Backend Selection
LUMINOUS_NIX_BACKEND=python                    # python, nodejs, hybrid
LUMINOUS_NIX_PYTHON_BACKEND=true               # Enable Python backend

# Data Directories
LUMINOUS_NIX_DATA_DIR=~/.local/share/luminous-nix
LUMINOUS_NIX_CACHE_DIR=~/.cache/luminous-nix
LUMINOUS_NIX_CONFIG_DIR=~/.config/luminous-nix

# Logging
LUMINOUS_NIX_LOG_LEVEL=info                    # debug, info, warn, error
LUMINOUS_NIX_DEBUG=true                        # Enable debug mode
LUMINOUS_NIX_VERBOSE=true                      # Verbose output
```

### Feature Flags
```bash
# Interface Features
LUMINOUS_NIX_VOICE_ENABLED=true                # Enable voice interface
LUMINOUS_NIX_TUI_ENABLED=true                  # Enable TUI
LUMINOUS_NIX_GUI_ENABLED=false                 # Enable GUI (future)

# Learning Features
LUMINOUS_NIX_LEARNING_ENABLED=true             # Enable learning system
LUMINOUS_NIX_PREFERENCES_ENABLED=true          # Learn user preferences
LUMINOUS_NIX_COMMUNITY_LEARNING=false          # Share anonymous patterns

# Safety Features
LUMINOUS_NIX_EXECUTE_COMMANDS=false            # Allow command execution
LUMINOUS_NIX_SAFE_MODE=true                    # Extra safety checks
LUMINOUS_NIX_CONFIRM_ALL=true                  # Confirm every action
```

### Performance Tuning
```bash
# Speed Optimization
LUMINOUS_NIX_FAST_MODE=true                    # Prioritize speed
LUMINOUS_NIX_LIGHTWEIGHT=true                  # Minimize resource usage
LUMINOUS_NIX_PARALLEL=true                     # Use parallel processing

# Resource Limits
LUMINOUS_NIX_MEMORY_LIMIT=512                  # Memory limit in MB
LUMINOUS_NIX_TIMEOUT=30                        # Command timeout in seconds
LUMINOUS_NIX_CACHE_SIZE=1000                   # Cache entries limit

# Network Settings
LUMINOUS_NIX_OFFLINE=true                      # Offline mode
LUMINOUS_NIX_PROXY=http://proxy:8080           # HTTP proxy
LUMINOUS_NIX_NO_NETWORK=true                   # Disable all network
```

### Accessibility Settings
```bash
# Screen Reader Support
LUMINOUS_NIX_SCREEN_READER=true                # Screen reader mode
LUMINOUS_NIX_ACCESSIBLE=true                   # Accessibility optimizations
LUMINOUS_NIX_STRUCTURED_OUTPUT=true            # Structured output

# Visual Accessibility
LUMINOUS_NIX_HIGH_CONTRAST=true                # High contrast colors
LUMINOUS_NIX_LARGE_TEXT=true                   # Large text mode
LUMINOUS_NIX_NO_COLOR=true                     # Disable colors

# Motor Accessibility
LUMINOUS_NIX_REDUCED_MOTION=true               # Minimize animations
LUMINOUS_NIX_KEYBOARD_ONLY=true                # Keyboard navigation only
LUMINOUS_NIX_PATIENT_MODE=true                 # No time limits
```

## User Profiles

### Creating Persona Profiles

You can create configuration profiles for different personas:

```bash
# Create profile directory
mkdir -p ~/.config/luminous-nix/profiles

# Grandma Rose profile
cat > ~/.config/luminous-nix/profiles/grandma-rose.yaml << EOF
ui:
  default_personality: "encouraging"
  simple_language: true
  patience_mode: true
  voice_enabled: true

accessibility:
  large_text: true
  simple_vocabulary: true
  extra_confirmations: true

performance:
  fast_mode: false  # Accuracy over speed
EOF

# Maya (ADHD) profile
cat > ~/.config/luminous-nix/profiles/maya.yaml << EOF
ui:
  default_personality: "minimal"
  response_format: "plain"
  show_commands: false
  progress_indicators: false

performance:
  fast_mode: true
  timeout: 10  # Shorter timeouts

nlp:
  confidence_threshold: 0.6  # Lower threshold for speed
EOF

# Alex (blind developer) profile
cat > ~/.config/luminous-nix/profiles/alex.yaml << EOF
ui:
  default_personality: "accessible"
  response_format: "structured"
  use_colors: false

accessibility:
  screen_reader: true
  structured_output: true
  keyboard_only: true
  consistent_terminology: true

development:
  show_all_details: true
EOF
```

### Using Profiles

```bash
# Use a specific profile
ask-nix --profile grandma-rose "install firefox"
ask-nix --profile maya "update system"
ask-nix --profile alex "search for text editors"

# Set default profile
echo "default_profile: maya" >> ~/.config/luminous-nix/config.yaml

# List available profiles
ask-nix --list-profiles
```

## Advanced Configuration

### Custom Personalities

Create custom personality definitions:

```yaml
# ~/.config/luminous-nix/personalities/custom.yaml
custom_teacher:
  name: "Patient Teacher"
  description: "Educational responses with examples"

  response_style:
    verbosity: "detailed"
    tone: "encouraging"
    include_examples: true
    include_explanations: true

  language:
    vocabulary_level: "intermediate"
    technical_terms: "explained"
    sentence_length: "medium"

  behavior:
    ask_follow_ups: true
    offer_alternatives: true
    provide_practice: true
    remember_mistakes: true
```

### NLP Engine Configuration

Fine-tune the natural language processing:

```yaml
nlp:
  engines:
    rule_based:
      enabled: true
      weight: 0.4
      patterns_file: "~/.config/luminous-nix/patterns/custom.yaml"

    statistical:
      enabled: true
      weight: 0.3
      model_path: "~/.local/share/luminous-nix/models/statistical.model"

    neural:
      enabled: true
      weight: 0.3
      model_name: "local-llm"
      temperature: 0.7

  pattern_matching:
    fuzzy_threshold: 0.8
    typo_distance: 2
    synonym_expansion: true

  context_tracking:
    conversation_memory: 10
    session_persistence: true
    cross_session_learning: true
```

### Plugin Configuration

Configure the plugin system:

```yaml
plugins:
  enabled: true
  directory: "~/.config/luminous-nix/plugins"
  auto_update: false

  # Core plugins
  weather:
    enabled: true
    api_key: "your-api-key"
    default_location: "auto"

  system_monitor:
    enabled: true
    update_interval: 60
    show_details: false

  # Custom plugins
  development_tools:
    enabled: true
    auto_setup_environments: true
    preferred_languages: ["python", "rust", "javascript"]
```

## Configuration Management

### Backup and Restore

```bash
# Backup configuration
ask-nix --backup-config ~/nix-humanity-backup.tar.gz

# Restore configuration
ask-nix --restore-config ~/nix-humanity-backup.tar.gz

# Export settings for sharing
ask-nix --export-config config-export.yaml

# Import shared settings
ask-nix --import-config config-export.yaml
```

### Configuration Validation

```bash
# Validate current configuration
ask-nix --validate-config

# Check for configuration errors
ask-nix --config-check

# Show current configuration
ask-nix --show-config

# Reset to defaults
ask-nix --reset-config
```

### Migration

```bash
# Migrate from older versions
ask-nix --migrate-config

# Upgrade configuration format
ask-nix --upgrade-config

# Check compatibility
ask-nix --config-compatibility
```

## Security Configuration

### Privacy Settings

```yaml
privacy:
  # Data collection levels
  data_collection: "none"              # none, minimal, standard, full

  # What to never log
  never_log:
    - "passwords"
    - "ssh_keys"
    - "personal_files"
    - "network_credentials"

  # Data retention
  log_retention_days: 30
  cache_retention_days: 7
  learning_data_retention_days: 365

  # Encryption
  encrypt_logs: true
  encrypt_cache: true
  encrypt_learning_data: true
  encryption_key_file: "~/.config/luminous-nix/keys/main.key"
```

### Access Control

```yaml
security:
  # Command execution
  allow_sudo: false                    # Allow sudo commands
  allowed_commands:                    # Whitelist of allowed commands
    - "nix-env"
    - "nixos-rebuild"
    - "nix-channel"

  # File system access
  restrict_paths: true                 # Restrict file system access
  allowed_paths:                       # Allowed paths
    - "/etc/nixos/"
    - "~/.config/"
    - "~/Downloads/"

  # Network access
  allow_network: false                 # Allow network operations
  allowed_hosts:                       # Allowed hosts
    - "cache.nixos.org"
    - "github.com"
```

## Integration Configuration

### Shell Integration

```bash
# Add to ~/.bashrc or ~/.zshrc
eval "$(ask-nix --setup-shell-integration)"

# Or manually:
# Aliases
alias nix='ask-nix'
alias ni='ask-nix --minimal'
alias nh='ask-nix --help'

# Functions
install() { ask-nix "install $*"; }
search() { ask-nix "search for $*"; }
update() { ask-nix "update system"; }

# Completion
eval "$(ask-nix --completion bash)"  # or zsh, fish
```

### Editor Integration

```yaml
# Editor integration settings
editors:
  vscode:
    enabled: true
    extension_path: "~/.vscode/extensions/luminous-nix"

  vim:
    enabled: true
    plugin_path: "~/.vim/pack/luminous-nix"

  emacs:
    enabled: true
    package_path: "~/.emacs.d/packages/luminous-nix"
```

## Troubleshooting Configuration

### Common Issues

```bash
# Configuration file not found
ask-nix --create-default-config

# Invalid configuration format
ask-nix --validate-config --fix

# Permissions issues
sudo chown -R $USER ~/.config/luminous-nix/
chmod 600 ~/.config/luminous-nix/config.yaml

# Reset corrupt configuration
ask-nix --reset-config --backup-first
```

### Debug Configuration

```yaml
debug:
  enabled: true
  log_file: "/tmp/luminous-nix-debug.log"
  log_level: "trace"
  include_stack_traces: true
  profile_performance: true
  trace_nlp_processing: true
  dump_configuration: true
```

## Configuration Examples

### Minimal Setup (Maya - ADHD)
```yaml
ui:
  default_personality: "minimal"
  show_commands: false
  use_colors: false
  progress_indicators: false

performance:
  fast_mode: true
  timeout: 5

nlp:
  confidence_threshold: 0.5
```

### Learning Setup (Carlos - Student)
```yaml
ui:
  default_personality: "encouraging"
  show_commands: true
  confirm_actions: true

learning:
  enabled: true
  personal_preferences: true
  provide_examples: true

nlp:
  context_memory: 20
  explain_reasoning: true
```

### Professional Setup (Dr. Sarah - Researcher)
```yaml
ui:
  default_personality: "technical"
  response_format: "structured"
  show_commands: true

development:
  debug_mode: true
  api_logging: true

performance:
  fast_mode: false  # Accuracy over speed
```

### Accessibility Setup (Alex - Blind Developer)
```yaml
ui:
  default_personality: "accessible"
  response_format: "structured"
  use_colors: false

accessibility:
  screen_reader: true
  structured_output: true
  keyboard_only: true
  consistent_terminology: true

voice:
  enabled: true
  voice_feedback: true
```

---

*"Configuration is not about complexity - it's about adaptation to your unique needs."*

🌊 Flow with personalized configuration!
