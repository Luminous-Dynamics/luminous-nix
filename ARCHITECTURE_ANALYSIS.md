# 🏗️ Architecture Analysis: CLI vs Core Library

## Current Situation

We have multiple interfaces (CLI, TUI, Voice) that need to execute NixOS commands. The question is: should they all go through the CLI, or should they use a shared core library?

## Option 1: Everything Through CLI (Current Proposal)

```
TUI → subprocess → ask-nix CLI → Core → NixOS
Voice → subprocess → ask-nix CLI → Core → NixOS  
Web → subprocess → ask-nix CLI → Core → NixOS
```

### Pros:
- ✅ Single point of truth for command execution
- ✅ All settings/config handled in one place
- ✅ CLI features (aliases, learning, etc.) available everywhere
- ✅ Easy to test - just test the CLI

### Cons:
- ❌ Performance overhead of subprocess calls
- ❌ Complex error handling through process boundaries
- ❌ Harder to get rich data structures (must serialize to JSON)
- ❌ Async/streaming more complex through subprocesses
- ❌ Feels like a hack - using CLI as an API

## Option 2: Shared Core Library (Better Architecture)

```
CLI → Core Library → NixOS
TUI → Core Library → NixOS
Voice → Core Library → NixOS
Web → Core Library → NixOS
```

### Pros:
- ✅ Clean, proper architecture
- ✅ Direct Python function calls (fast)
- ✅ Rich data structures, proper exceptions
- ✅ Easy async/await patterns
- ✅ Natural for Python ecosystem

### Cons:
- ❌ Need to ensure consistency across interfaces
- ❌ Settings/config must be shared properly
- ❌ Some duplication of interface logic

## Option 3: Hybrid Approach (RECOMMENDED) 🌟

```
CLI → Core Service Layer → Core Library → NixOS
TUI → Core Service Layer → Core Library → NixOS
Voice → Core Service Layer → Core Library → NixOS
Web → Core Service Layer → Core Library → NixOS
```

### The Architecture:

```python
# luminous_nix/core/service.py
class LuminousNixService:
    """
    Unified service layer that all interfaces use.
    Handles settings, learning, aliases, etc.
    """
    def __init__(self, interface_type: str = "cli"):
        self.core = NixForHumanityCore()
        self.settings = SettingsManager()
        self.learning = LearningSystem()
        self.interface = interface_type
        
    async def execute(self, query: str, options: Dict) -> Response:
        # Apply settings
        # Track learning
        # Handle aliases
        # Execute through core
        # Return rich response
```

### Implementation:

1. **Core Library** (`luminous_nix.core`)
   - Pure business logic
   - NixOS operations
   - No UI concerns

2. **Service Layer** (`luminous_nix.service`)
   - Settings management
   - Learning system
   - Alias resolution
   - Unified interface for all UIs

3. **Interface Layer**
   - CLI (`bin/ask-nix`) - Command line interface
   - TUI (`interfaces/tui.py`) - Terminal UI
   - Voice (`interfaces/voice.py`) - Speech interface
   - API (`interfaces/api.py`) - REST/WebSocket

### Why This Is Best:

1. **Performance**: Direct Python calls, no subprocess overhead
2. **Consistency**: Service layer ensures uniform behavior
3. **Flexibility**: Each interface can have unique features
4. **Testability**: Can test service layer independently
5. **Pythonic**: Follows Python best practices

## Practical Implementation Plan

### Phase 1: Create Service Layer
```python
# luminous_nix/service.py
from .core import NixForHumanityCore
from .settings import SettingsManager
from .learning import LearningSystem

class LuminousNixService:
    """Single source of truth for all interfaces"""
    
    def __init__(self, interface="cli", user_id=None):
        self.core = NixForHumanityCore()
        self.settings = SettingsManager(user_id)
        self.learning = LearningSystem(user_id) if user_id else None
        self.interface = interface
    
    async def execute_command(self, query: str, execute: bool = False) -> Response:
        """Execute a command with all features"""
        # Resolve aliases
        query = self.settings.resolve_alias(query)
        
        # Track for learning
        if self.learning:
            self.learning.track_command(query)
        
        # Execute
        response = await self.core.execute(query, dry_run=not execute)
        
        # Track response
        if self.learning:
            self.learning.track_response(response)
        
        return response
    
    def create_alias(self, name: str) -> bool:
        """Create command alias"""
        return self.settings.add_alias(name, "ask-nix")
```

### Phase 2: Update Interfaces

**CLI** (`bin/ask-nix`):
```python
from luminous_nix.service import LuminousNixService

service = LuminousNixService(interface="cli")
response = await service.execute_command(query, execute=args.execute)
```

**TUI** (`interfaces/tui.py`):
```python
from luminous_nix.service import LuminousNixService

class TUIApp:
    def __init__(self):
        self.service = LuminousNixService(interface="tui")
    
    async def execute_command(self, query: str):
        response = await self.service.execute_command(query)
        self.display_response(response)
```

**Voice** (`interfaces/voice.py`):
```python
from luminous_nix.service import LuminousNixService

class VoiceInterface:
    def __init__(self):
        self.service = LuminousNixService(interface="voice")
    
    def process_voice_command(self, text: str):
        response = await self.service.execute_command(text)
        self.speak_response(response)
```

### Phase 3: Alias Feature

The alias feature becomes a method on the service:

```python
# In CLI
if args[0] == "alias":
    if args[1] == "create":
        service.create_alias(args[2])
    elif args[1] == "list":
        service.list_aliases()
```

## Decision: Hybrid Service Layer ✅

### Why:
1. **Clean Architecture**: Proper separation of concerns
2. **Performance**: No subprocess overhead
3. **Consistency**: Single service layer for all interfaces
4. **Flexibility**: Each interface can customize as needed
5. **Future-Proof**: Easy to add new interfaces

### What About the CLI Wrapper?

The `cli_wrapper.py` can still exist for:
- External tools that need to call ask-nix
- Shell scripts that need programmatic access
- Testing the CLI interface itself

But our internal interfaces (TUI, Voice) should use the service layer directly.

## Implementation Priority

1. **Keep existing Core** - It works, don't break it
2. **Create Service Layer** - Thin wrapper with settings/learning
3. **Update CLI** - Use service layer
4. **Update TUI/Voice** - Use service layer
5. **Add Alias Feature** - In service layer
6. **Keep cli_wrapper.py** - For external integration

## Conclusion

The hybrid approach with a service layer gives us:
- ✅ Clean architecture
- ✅ High performance  
- ✅ Consistency across interfaces
- ✅ Flexibility for interface-specific features
- ✅ Proper Python patterns

This is the most practical and maintainable approach.