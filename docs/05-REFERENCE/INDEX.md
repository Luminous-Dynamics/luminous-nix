# 📖 05-REFERENCE

*Technical reference materials for Nix for Humanity*

---

💡 **Quick Context**: Complete technical reference for APIs, commands, and configuration  
📍 **Location**: `docs/05-REFERENCE/`  
🔗 **Parent**: [Documentation Hub](../README.md)  
⏱️ **Read time**: 2 minutes for navigation  
📊 **Mastery Level**: 🌿 Intermediate to 🌳 Advanced - technical reference

---

## 🎯 Quick Navigation

### 🔧 Commands & CLI
- **[01-CLI-COMMANDS](01-CLI-COMMANDS.md)** - Complete CLI reference ⭐
- **[CONFIGURATION](CONFIGURATION.md)** - Configuration options

### 🌐 APIs & SDKs
- **[02-API-REFERENCE](02-API-REFERENCE.md)** - REST API documentation
- **[03-PYTHON-SDK](03-PYTHON-SDK.md)** - Python client library
- **[04-JAVASCRIPT-SDK](04-JAVASCRIPT-SDK.md)** - JavaScript/TypeScript library
- **[API_REFERENCE](API_REFERENCE.md)** - Additional API details
- **[openapi.yaml](openapi.yaml)** - OpenAPI specification

### 📚 Guides & FAQ
- **[FAQ](FAQ.md)** - Frequently asked questions
- **[ENHANCED_BACKEND_USER_GUIDE](ENHANCED_BACKEND_USER_GUIDE.md)** - Backend usage guide

---

## 📊 Quick Reference

### CLI Examples
```bash
# Natural language commands
ask-nix "install firefox"
ask-nix "find markdown editor"
ask-nix "create python dev environment"

# Advanced features
ask-nix --diagnose
ask-nix --metrics
ask-nix export-data
```

### Configuration
```yaml
# ~/.config/nix-for-humanity/config.yaml
backend: python
loglevel: info
localOnly: true
personas:
  default: developer
  voice: grandma-rose
```

### API Usage
```python
# Python SDK
from nix_for_humanity import Client

client = Client()
response = client.query("install firefox")
print(response.command)
```

---

## 🔍 Reference Categories

### System Commands
- Package management (install, remove, update)
- Configuration generation
- System health checks
- Rollback and recovery

### Configuration Options
- Backend settings
- Persona customization
- Performance tuning
- Privacy controls

### API Endpoints
- `/api/query` - Natural language processing
- `/api/execute` - Command execution
- `/api/learn` - Learning feedback
- `/api/metrics` - Performance data

### Error Codes
- 1xx - Input errors
- 2xx - Execution errors
- 3xx - System errors
- 4xx - Network errors

---

## 📈 Performance Reference

### Response Times
- Intent recognition: <50ms
- Command building: <100ms
- Total response: <200ms

### Resource Usage
- Memory: <150MB idle, <500MB peak
- CPU: <1% idle, <25% active
- Disk: <100MB base, <500MB with cache

---

## Original Documentation


*Technical reference materials for Nix for Humanity*

---

💡 **Quick Context**: Complete technical reference hub for APIs, configuration, commands, and specifications  
📍 **You are here**: Reference → Reference Hub (Technical Navigation Center)  
🔗 **Related**: [System Architecture](../02-ARCHITECTURE/01-SYSTEM-ARCHITECTURE.md) | [User Guide](../06-TUTORIALS/USER_GUIDE.md) | [Master Documentation Map](../MASTER_DOCUMENTATION_MAP.md)  
⏱️ **Read time**: 5 minutes (navigation) + varies by section  
📊 **Mastery Level**: 🌿 Intermediate - technical reference for developers and advanced users

🌊 **Natural Next Steps**:
- **For API integration**: Start with [REST API Reference](./01-REST-API.md) for HTTP endpoints
- **For configuration**: Jump to [Configuration Reference](./CONFIGURATION.md) for complete setup options  
- **For daily usage**: Reference [CLI Commands](./01-CLI-COMMANDS.md) for command-line operations
- **For troubleshooting**: Keep [Error Codes](./11-ERROR-CODES.md) handy for debugging

---

## Overview

This section contains reference documentation including API specifications, configuration options, glossaries, and system requirements.

## Documents

### API Documentation
1. **[REST API Reference](./02-API-REFERENCE.md)** 🆕 - Complete REST API documentation with examples
2. **[OpenAPI Specification](./openapi.yaml)** 🆕 - Machine-readable API specification
3. **[Python SDK](./03-PYTHON-SDK.md)** 🆕 - Python client library documentation
4. **[JavaScript SDK](./04-JAVASCRIPT-SDK.md)** 🆕 - JavaScript/TypeScript client library
5. **[Plugin API Reference](./03-PLUGIN-API.md)** - Extension development

### Configuration
4. **[Configuration Reference](./04-CONFIGURATION.md)** - All configuration options
5. **[Environment Variables](./05-ENVIRONMENT.md)** - Environment configuration
6. **[Feature Flags](./06-FEATURE-FLAGS.md)** - Runtime feature control

### Command Reference
7. **[CLI Commands](./07-CLI-COMMANDS.md)** - ask-nix command reference
8. **[TUI Shortcuts](./08-TUI-SHORTCUTS.md)** - Keyboard shortcuts
9. **[Voice Commands](./09-VOICE-COMMANDS.md)** - Natural language patterns

### Technical Specifications
10. **[System Requirements](./10-SYSTEM-REQUIREMENTS.md)** - Hardware and software needs
11. **[Error Codes](./11-ERROR-CODES.md)** - Complete error reference
12. **[File Formats](./12-FILE-FORMATS.md)** - Data format specifications

### Glossary & Appendices
13. **[Glossary](./13-GLOSSARY.md)** - Technical terms and definitions
14. **[Acronyms](./14-ACRONYMS.md)** - Project acronyms
15. **[Resources](./15-RESOURCES.md)** - External links and references

## Quick Reference

### Common Configuration
```yaml
# config.yaml
backend:
  type: python
  native_api: true
  
nlp:
  model: hybrid
  cache_size: 1000
  
personality:
  default: friendly
  adapt_to_user: true
  
learning:
  enabled: true
  privacy_mode: strict
```

### Environment Variables
```bash
# Core settings
NIX_HUMANITY_BACKEND=python
NIX_HUMANITY_LOG_LEVEL=info

# Features
NIX_HUMANITY_VOICE_ENABLED=true
NIX_HUMANITY_LEARNING_ENABLED=true

# Paths
NIX_HUMANITY_DATA_DIR=~/.local/share/nix-for-humanity
NIX_HUMANITY_CACHE_DIR=~/.cache/nix-for-humanity
```

### Common Commands
```bash
# Basic usage
ask-nix "install firefox"
ask-nix --help
ask-nix --version

# Advanced usage
ask-nix --personality technical "explain generations"
ask-nix --execute "update system"
ask-nix --summary

# TUI
nix-tui
```

## API Quick Start

### Python API
```python
from nix_for_humanity import NixForHumanity

# Initialize
nfh = NixForHumanity()

# Process query
response = await nfh.process("install firefox")
print(response.explanation)
print(response.command)
```

### REST API
```bash
# Query endpoint
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "install firefox"}'

# Health check
curl http://localhost:8000/health
```

---

*"Good documentation is like a map - it helps you find your way."*

🌊 We flow with clarity!