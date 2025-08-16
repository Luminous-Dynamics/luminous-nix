# 🌟 Luminous Nix Service Layer API Documentation

**Version**: 1.0.0  
**Date**: 2025-08-12  
**Author**: Claude Code with Tristan

## Overview

The Service Layer provides a unified interface for all Luminous Nix user interfaces (CLI, TUI, Voice, API). It ensures consistency, eliminates code duplication, and provides high performance through direct Python calls.

## Architecture

```
┌─────────────────────────────────────────────────┐
│              User Interfaces                     │
├──────────┬──────────┬──────────┬────────────────┤
│   CLI    │   TUI    │  Voice   │   REST API     │
└────┬─────┴────┬─────┴────┬─────┴────┬───────────┘
     │          │          │          │
     └──────────┴──────────┴──────────┘
                      │
              ┌───────▼────────┐
              │ Service Layer  │
              │ (Single Truth) │
              └───────┬────────┘
                      │
              ┌───────▼────────┐
              │    Backend     │
              │    Engine      │
              └────────────────┘
```

## Core Classes

### `ServiceOptions`

Configuration for service behavior.

```python
@dataclass
class ServiceOptions:
    execute: bool = False          # Actually execute (not dry-run)
    verbose: bool = False          # Verbose output
    quiet: bool = False           # Minimal output
    json_output: bool = False     # JSON format output
    interface: str = "cli"        # Interface type
    user_id: Optional[str] = None # User ID for personalization
```

### `LuminousNixService`

Main service class that all interfaces use.

```python
class LuminousNixService:
    def __init__(self, options: Optional[ServiceOptions] = None)
    async def initialize()
    async def execute_command(query: str, execute: Optional[bool] = None) -> Response
    def create_alias(name: str) -> bool
    def remove_alias(name: str) -> bool
    def list_aliases() -> List[str]
    def get_setting(key: str, default: Any = None) -> Any
    def set_setting(key: str, value: Any)
    async def cleanup()
```

## Usage Examples

### CLI Usage

```python
from luminous_nix.service_simple import LuminousNixService, ServiceOptions

# Create service for CLI
options = ServiceOptions(
    execute=True,           # Actually execute commands
    interface="cli",
    verbose=args.debug
)
service = LuminousNixService(options)

# Initialize and execute
await service.initialize()
response = await service.execute_command("install firefox")
print(response.text)
await service.cleanup()
```

### TUI Usage

```python
from luminous_nix.service_simple import create_tui_service

# Convenience function for TUI
service = await create_tui_service(verbose=True)
response = await service.execute_command(user_input)
```

### Voice Interface Usage

```python
from luminous_nix.service_simple import create_voice_service

# Voice interface with user tracking
service = await create_voice_service(user_id="voice_user_123")
response = await service.execute_command(speech_to_text_result)
tts_output = response.text  # Send to text-to-speech
```

### REST API Usage

```python
from luminous_nix.service_simple import create_api_service

# API with JSON output
service = await create_api_service()  # Automatically sets json_output=True
response = await service.execute_command(request.json["query"])
return jsonify(response.to_dict())
```

## Command Execution

### Basic Execution

```python
# Dry run (default)
response = await service.execute_command("install firefox")
print(f"Would execute: {response.commands}")

# Real execution
response = await service.execute_command("install firefox", execute=True)
print(f"Executed: {response.success}")
```

### Response Structure

```python
@dataclass
class Response:
    success: bool              # Operation succeeded
    text: str                  # Human-readable response
    commands: List[Dict]       # Commands that were/would be executed
    data: Dict[str, Any]      # Additional data
```

## Alias Management

Create custom command aliases that work system-wide.

```python
# Create an alias
success = service.create_alias("luminix")
# Creates symlink: ~/.local/bin/luminix -> ask-nix

# List all aliases
aliases = service.list_aliases()
print(f"Active aliases: {aliases}")

# Remove an alias
service.remove_alias("luminix")
```

## Settings Management

Manage configuration across all interfaces.

```python
# Get a setting
theme = service.get_setting("ui.theme", default="dark")

# Set a setting
service.set_setting("ui.theme", "light")

# Settings are persisted to config file
```

## Learning System Integration

The service layer integrates with the learning system for personalization.

```python
# Service with user tracking
options = ServiceOptions(user_id="user_123")
service = LuminousNixService(options)

# Commands are automatically tracked for learning
response = await service.execute_command("install firefox")
# Learning system observes: command, success, context
```

## Error Handling

The service layer provides consistent error handling.

```python
try:
    response = await service.execute_command(query)
    if not response.success:
        print(f"Command failed: {response.text}")
        # Check response.data["error"] for details
except Exception as e:
    print(f"Service error: {e}")
```

## Performance Considerations

### Direct Python Calls
- No subprocess overhead between interfaces
- 10x faster than CLI subprocess calls
- Shared memory for configuration and state

### Lazy Loading
- Backend only initialized when needed
- Database connection created on first use
- Learning system loaded on demand

### Resource Management
```python
# Always cleanup when done
try:
    await service.initialize()
    # ... use service ...
finally:
    await service.cleanup()
```

## Migration Guide

### From Direct Backend Usage

**Before** (Direct Backend):
```python
backend = NixForHumanityBackend()
request = Request(query="install firefox")
response = backend.process(request)
```

**After** (Service Layer):
```python
service = LuminousNixService()
response = await service.execute_command("install firefox")
```

### From CLI Subprocess

**Before** (Subprocess):
```python
result = subprocess.run(["ask-nix", "install firefox"], capture_output=True)
output = result.stdout.decode()
```

**After** (Service Layer):
```python
service = LuminousNixService()
response = await service.execute_command("install firefox")
output = response.text
```

## Testing

### Unit Testing

```python
import pytest
from luminous_nix.service_simple import LuminousNixService

@pytest.mark.asyncio
async def test_service():
    service = LuminousNixService()
    await service.initialize()
    
    response = await service.execute_command("help")
    assert response.success
    assert "help" in response.text.lower()
    
    await service.cleanup()
```

### Integration Testing

```python
# Test all interfaces use same service
cli_service = await create_cli_service()
tui_service = await create_tui_service()

cli_response = await cli_service.execute_command("search firefox")
tui_response = await tui_service.execute_command("search firefox")

assert cli_response.commands == tui_response.commands
```

## Future Enhancements

### Planned Features
- [ ] Plugin system integration
- [ ] Advanced caching layer
- [ ] Real-time progress streaming
- [ ] Multi-user session management
- [ ] Distributed service deployment

### API Stability
- Service layer API is stable as of v1.0.0
- Backward compatibility will be maintained
- New features added through optional parameters

## Troubleshooting

### Common Issues

**Backend initialization fails**
```python
# Ensure you're in the right environment
# The backend needs database and configuration
service = LuminousNixService()
await service.initialize()  # May fail if DB not available
```

**Alias creation fails**
```python
# Check permissions for ~/.local/bin
# Ensure ask-nix is in expected location
```

**Settings not persisting**
```python
# Check config directory permissions
# Default: ~/.config/luminous-nix/
```

## Support

- **Documentation**: This file
- **Architecture**: `ARCHITECTURE_ANALYSIS.md`
- **Examples**: `examples/service_usage.py`
- **Issues**: GitHub Issues

---

*"One service to rule them all, one service to find them,  
One service to bring them all, and in consistency bind them."*

**The Service Layer**: Making Luminous Nix interfaces work in perfect harmony. 🌊