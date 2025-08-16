# 🎯 Alias Feature & Unified Architecture Design

## Problem Statement

1. **Users want custom aliases** - Should be able to set `lnix` or any preferred shorthand
2. **TUI and Voice are reinventing the wheel** - They import `NixForHumanityCore` directly instead of using `ask-nix`
3. **Duplication of logic** - Each interface reimplements command processing

## Proposed Solutions

### 1. Alias Feature for ask-nix

Users should be able to create custom aliases easily:

```bash
# Create an alias through ask-nix itself
ask-nix alias create lnix
ask-nix alias create nix
ask-nix alias create lux

# Or through config
ask-nix settings alias add luminix

# List current aliases
ask-nix alias list

# Remove an alias
ask-nix alias remove lnix
```

#### Implementation Approach

```python
# In ask-nix CLI during initialization
def setup_aliases():
    """Create shell aliases for ask-nix"""
    config = load_config()
    
    for alias in config.get('aliases', []):
        # Create symlink or shell alias
        create_alias(alias, 'ask-nix')
        
    # Default aliases (if user wants them)
    if config.get('default_aliases', False):
        create_alias('luminix', 'ask-nix')
        create_alias('lnix', 'ask-nix')
```

### 2. Unified Architecture - Everything Through ask-nix

**Current Problem (WHEEL REINVENTION):**
```
TUI → imports NixForHumanityCore → executes
Voice → imports NixForHumanityCore → executes  
CLI → imports NixForHumanityCore → executes
```

**Proposed Solution (UNIFIED):**
```
TUI → calls ask-nix CLI → executes
Voice → calls ask-nix CLI → executes
CLI → imports NixForHumanityCore → executes
```

### 3. How TUI Should Work

Instead of:
```python
# CURRENT (Wrong - reinventing wheel)
from luminous_nix.core import NixForHumanityCore

class TUIApp:
    def __init__(self):
        self.core = NixForHumanityCore()  # ❌ Direct import
    
    async def execute_command(self, command: str):
        response = self.core.process(command)  # ❌ Direct execution
```

Should be:
```python
# PROPOSED (Correct - unified through CLI)
import subprocess
import json

class TUIApp:
    async def execute_command(self, command: str):
        # Use ask-nix CLI with machine-readable output
        result = subprocess.run(
            ['ask-nix', '--json', command],
            capture_output=True,
            text=True
        )
        response = json.loads(result.stdout)  # ✅ Using CLI
```

### 4. Better Yet - ask-nix API Mode

Add an API mode to ask-nix for programmatic use:

```python
# ask-nix can provide a Python API wrapper
from luminous_nix.cli_wrapper import AskNixAPI

class TUIApp:
    def __init__(self):
        self.api = AskNixAPI()  # Wraps CLI calls
    
    async def execute_command(self, command: str):
        response = await self.api.execute(command)
```

The wrapper would:
- Handle subprocess calls to ask-nix
- Parse JSON output
- Manage environment variables
- Handle streaming for long operations

### 5. Benefits of Unified Architecture

#### Consistency
- One place for all command processing logic
- Single source of truth for configuration
- Unified error handling

#### Maintainability
- Fix bugs in one place
- Add features to ask-nix, all interfaces get them
- No duplicated code

#### User Experience
- Same behavior across all interfaces
- Settings apply everywhere
- Learning transfers between interfaces

### 6. Implementation Plan

#### Phase 1: Add Alias Feature to ask-nix
```bash
# New subcommand: alias
ask-nix alias create <name>    # Create alias
ask-nix alias list             # List aliases
ask-nix alias remove <name>    # Remove alias

# Auto-setup on first run
ask-nix --setup-aliases        # Creates shell integration
```

#### Phase 2: Add JSON/API Output Mode
```bash
# Machine-readable output
ask-nix --json "install firefox"
ask-nix --format=json "search editor"

# Streaming mode for TUI
ask-nix --stream "update system"
```

#### Phase 3: Create CLI Wrapper Library
```python
# luminous_nix/cli_wrapper.py
class AskNixAPI:
    """Programmatic interface to ask-nix CLI"""
    
    def execute(self, command: str) -> Response:
        """Execute command through CLI"""
        
    def stream_execute(self, command: str) -> AsyncIterator[str]:
        """Stream output for long operations"""
```

#### Phase 4: Refactor TUI and Voice
- Replace direct NixForHumanityCore imports
- Use AskNixAPI wrapper instead
- Remove duplicated logic

### 7. Alias Implementation Details

#### Shell Integration Script
```bash
#!/bin/bash
# ~/.config/luminix/shell-integration.sh

# Add to .bashrc/.zshrc
for alias in $(ask-nix alias list --raw); do
    alias $alias="ask-nix"
done

# Or create symlinks
for alias in $(ask-nix alias list --raw); do
    ln -sf $(which ask-nix) ~/.local/bin/$alias
done
```

#### Config File
```toml
# ~/.config/luminix/config.toml
[aliases]
enabled = true
list = ["luminix", "lnix", "nix-ask"]

[aliases.shell]
auto_setup = true
shell_type = "bash"  # or "zsh", "fish"
```

### 8. User Experience

#### First Run
```bash
$ ask-nix "install firefox"

Welcome! Would you like to set up convenient aliases?
You can type 'luminix' or 'lnix' instead of 'ask-nix'.

Set up aliases? [Y/n]: y

Great! You can now use:
  luminix "install firefox"
  lnix "install firefox"
  ask-nix "install firefox"

To add custom aliases: ask-nix alias create <name>
```

#### Custom Alias
```bash
$ ask-nix alias create n

✅ Created alias 'n' → 'ask-nix'

Now you can use:
  n "install firefox"

Add to your shell? [Y/n]: y
✅ Added to ~/.bashrc
```

## Conclusion

The key principles:
1. **ask-nix is the single entry point** - all interfaces use it
2. **Aliases are user choice** - easy to set up, but not forced
3. **No wheel reinvention** - TUI and Voice call ask-nix
4. **Machine-readable output** - --json flag for programmatic use
5. **Natural language stays** - 'ask-nix' command never changes

This gives us:
- **Consistency** across all interfaces
- **Flexibility** for user preferences  
- **Maintainability** with single implementation
- **Natural interaction** preserved

---

*"One CLI to rule them all, one interface to bind them, one command to bring them all, and in the light guide them."*