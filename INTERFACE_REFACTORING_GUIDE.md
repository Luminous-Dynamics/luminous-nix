# 🔄 Interface Refactoring Guide

## How Each Interface Should Use the Service Layer

### 1. CLI Interface (`bin/ask-nix`)

**Current (Complex):**
```python
# Lots of direct backend manipulation
backend = NixForHumanityBackend()
backend.dry_run = not args.execute
await backend.initialize()
context = Context()
result = await backend.execute(query, context)
# Handle learning, aliases, etc.
```

**Refactored (Simple):**
```python
from luminous_nix.service import create_cli_service

# Create service with options
service = await create_cli_service(
    execute=args.execute,
    json_output=args.json,
    verbose=args.verbose
)

# Execute command
response = await service.execute_command(query)

# Display result
if args.json:
    print(json.dumps(response.to_dict()))
else:
    print(response.output)
```

### 2. TUI Interface (`interfaces/tui.py`)

**Current (Reinventing Wheel):**
```python
from luminous_nix.core import NixForHumanityCore

class TUIApp:
    def __init__(self):
        self.core = NixForHumanityCore()  # Direct core usage
    
    async def execute_command(self, command: str):
        query = Query(text=command)
        response = self.core.process(query)  # Bypasses all CLI features
```

**Refactored (Using Service):**
```python
from luminous_nix.service import create_tui_service

class TUIApp:
    async def on_mount(self):
        self.service = await create_tui_service(
            user_id=self.get_user_id()  # For personalization
        )
    
    async def execute_command(self, command: str):
        # Show loading
        self.show_spinner("Processing...")
        
        # Execute through service (gets all features)
        response = await self.service.execute_command(command)
        
        # Display response
        self.display_response(response)
```

### 3. Voice Interface (`interfaces/voice.py`)

**Current (Duplicate Logic):**
```python
from luminous_nix.core import NixForHumanityCore, Query, Response

class VoiceInterface:
    def __init__(self):
        self.core = NixForHumanityCore()  # Another direct usage
    
    def process_voice_command(self, text: str) -> Response:
        query = Query(text=text, context={"interface": "voice"})
        return self.core.process(query)  # Misses CLI features
```

**Refactored (Using Service):**
```python
from luminous_nix.service import create_voice_service

class VoiceInterface:
    async def initialize(self):
        self.service = await create_voice_service(
            quiet=True  # Less verbose for voice
        )
    
    async def process_voice_command(self, text: str):
        # Get response through service
        response = await self.service.execute_command(text)
        
        # Speak appropriate response
        if response.success:
            self.speak(self.summarize_for_voice(response.output))
        else:
            self.speak(f"Sorry, {response.error}")
```

### 4. Web API (`interfaces/api.py`)

**Future Implementation:**
```python
from luminous_nix.service import create_api_service
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.post("/execute")
async def execute_command(query: str, execute: bool = False):
    service = await create_api_service()
    
    try:
        response = await service.execute_command(query, execute=execute)
        return {
            "success": response.success,
            "output": response.output,
            "error": response.error
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Benefits of This Approach

### 1. Consistency
All interfaces get the same features:
- Alias resolution
- Learning/personalization
- Settings management
- Error handling

### 2. Performance
- Direct Python calls (no subprocess)
- Shared backend instance
- Efficient resource usage

### 3. Maintainability
- Single place to fix bugs
- Features added once, available everywhere
- Clear separation of concerns

### 4. Testability
```python
# Easy to test the service
async def test_service():
    service = LuminousNixService(ServiceOptions(execute=False))
    response = await service.execute_command("install firefox")
    assert response.success
    assert "would install" in response.output.lower()
```

## Migration Plan

### Phase 1: Service Layer ✅
- Created `service.py` with unified interface
- Handles settings, aliases, learning

### Phase 2: Update CLI
```python
# Minimal changes to bin/ask-nix
# Replace direct backend usage with service
```

### Phase 3: Update TUI
```python
# Replace NixForHumanityCore with service
# Remove duplicate command processing
```

### Phase 4: Update Voice
```python
# Replace NixForHumanityCore with service
# Use service for all command execution
```

## Alias Feature Integration

The alias feature is now part of the service layer:

```python
# Any interface can manage aliases
service.create_alias("lnix")
service.create_alias("luminix")
aliases = service.list_aliases()
service.remove_alias("lnix")
```

This means:
- CLI can offer `ask-nix alias create`
- TUI can have an alias management screen
- Voice can respond to "create an alias called luminix"

## Summary

### Do:
- ✅ Use `LuminousNixService` for all command execution
- ✅ Let service handle settings, aliases, learning
- ✅ Keep interfaces focused on UI concerns only

### Don't:
- ❌ Import `NixForHumanityCore` directly in interfaces
- ❌ Reimplement command processing logic
- ❌ Bypass the service layer

### Result:
- Clean architecture
- Consistent behavior
- Better performance
- Easier maintenance

The service layer is the bridge that connects all interfaces to the core functionality while maintaining consistency and adding shared features like aliases and learning.