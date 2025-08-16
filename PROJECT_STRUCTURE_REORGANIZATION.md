# 🏗️ Luminous Nix - Project Structure Reorganization Plan

## 🚨 Current Issues Identified

### 1. **Duplicate CLI Scripts in `bin/`**
- `ask-nix` - Main CLI (526 lines)
- `ask-nix-enhanced` - Variant with tree-sitter (265 lines)
- `nix-humanity` - Another variant (134 lines)
- `nix-humanity-unified` - Yet another (166 lines)
- `nix-tui` and `nix-tui-enhanced` - Two TUI versions
- **Problem**: Multiple implementations confuse users and developers

### 2. **Sprawling `src/nix_for_humanity/` Structure**
Currently 28+ subdirectories with overlapping responsibilities:
- `backend/`, `core/`, `engine/` - Overlapping backend logic
- `cli/`, `interfaces/` - Duplicate interface code
- `ui/`, `tui/` - Separate UI implementations
- `voice/`, `interfaces/voice_interface.py` - Voice in multiple places
- `utils/`, `logging/`, `monitoring/` - Helper code scattered

### 3. **Archive Directories Everywhere**
- `archive/` - General archive
- `tests/archive/` - Test archive
- `docs/ARCHIVE/` - Documentation archive
- Multiple date-stamped archives scattered around

## ✅ Proposed Clean Structure

```
luminous-nix/
├── bin/
│   ├── ask-nix              # THE ONLY CLI ENTRY POINT
│   └── archive/             # All old variants moved here
│       ├── ask-nix-enhanced
│       ├── nix-humanity
│       └── ...
│
├── src/nix_for_humanity/
│   ├── __init__.py
│   ├── core/               # Core business logic
│   │   ├── __init__.py
│   │   ├── engine.py       # Main execution engine
│   │   ├── executor.py     # Command execution
│   │   ├── intents.py      # Intent recognition
│   │   └── knowledge.py    # Knowledge base
│   │
│   ├── nix/                # NixOS-specific integration
│   │   ├── __init__.py
│   │   ├── api.py          # Native Python-Nix API
│   │   ├── commands.py     # Nix command wrappers
│   │   ├── config.py       # Configuration generation
│   │   └── packages.py     # Package management
│   │
│   ├── interfaces/         # All user interfaces
│   │   ├── __init__.py
│   │   ├── cli.py          # CLI interface
│   │   ├── tui.py          # TUI interface
│   │   ├── voice.py        # Voice interface
│   │   └── api.py          # REST/WebSocket API
│   │
│   ├── learning/           # AI/ML components
│   │   ├── __init__.py
│   │   ├── nlp.py          # Natural language processing
│   │   ├── patterns.py     # Pattern recognition
│   │   └── personas.py     # User personas
│   │
│   ├── utils/              # Utilities and helpers
│   │   ├── __init__.py
│   │   ├── config.py       # Configuration management
│   │   ├── logging.py      # Logging setup
│   │   ├── cache.py        # Caching logic
│   │   └── errors.py       # Error handling
│   │
│   └── plugins/            # Plugin system
│       ├── __init__.py
│       └── manager.py
│
├── tests/                  # Clean test structure
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
├── docs/                   # Documentation (already well-organized)
├── examples/               # Example scripts and demos
├── scripts/                # Development and utility scripts
└── archive/                # SINGLE archive location
    └── 2025-08-12-reorganization/
```

## 🔄 Migration Steps

### Phase 1: Archive Duplicates (Immediate)
```bash
# Create archive directory
mkdir -p bin/archive
mkdir -p archive/2025-08-12-reorganization

# Move duplicate CLIs
mv bin/ask-nix-enhanced bin/archive/
mv bin/nix-humanity* bin/archive/
mv bin/nix-tui-enhanced bin/archive/
mv bin/demo-* bin/archive/
mv bin/nix-showcase bin/archive/
```

### Phase 2: Consolidate Source Code
1. **Merge backend implementations**:
   - Combine `backend/`, `core/`, into single `core/` module
   - Remove duplicate functionality

2. **Unify interfaces**:
   - Move all UI code to `interfaces/`
   - Single implementation per interface type

3. **Consolidate utilities**:
   - Merge `utils/`, `logging/`, `monitoring/` into `utils/`

### Phase 3: Update Imports
```python
# OLD: from nix_for_humanity.backend.engine import Engine
# NEW: from nix_for_humanity.core.engine import Engine

# OLD: from nix_for_humanity.tui.app import TUIApp
# NEW: from nix_for_humanity.interfaces.tui import TUIApp
```

### Phase 4: Single Entry Point
Make `bin/ask-nix` handle all modes:
```bash
ask-nix [command]           # CLI mode (default)
ask-nix --tui              # TUI mode
ask-nix --voice            # Voice mode
ask-nix --api              # API server mode
```

## 📝 What Each Directory Contains

### `bin/`
- **ask-nix**: Single CLI entry point, delegates to appropriate interface
- **archive/**: Historical implementations for reference

### `src/nix_for_humanity/core/`
Core business logic, independent of interface:
- Intent recognition and processing
- Command execution
- Knowledge management
- Response generation

### `src/nix_for_humanity/nix/`
NixOS-specific functionality:
- Native Python-Nix API integration
- Package discovery and management
- Configuration generation
- System operations

### `src/nix_for_humanity/interfaces/`
All user-facing interfaces:
- CLI: Command-line interface
- TUI: Terminal UI (Textual-based)
- Voice: Speech recognition/synthesis
- API: REST and WebSocket endpoints

### `src/nix_for_humanity/learning/`
AI/ML components:
- Natural language processing
- Pattern recognition
- User modeling
- Persona management

### `src/nix_for_humanity/utils/`
Shared utilities:
- Configuration management
- Logging setup
- Caching
- Error handling

## 🎯 Benefits of Reorganization

1. **Clear Single Source of Truth**
   - One CLI entry point
   - One implementation per feature
   - Clear module boundaries

2. **Easier Navigation**
   - Developers know exactly where to find code
   - No confusion about which variant to use
   - Clean separation of concerns

3. **Reduced Maintenance**
   - No duplicate code to maintain
   - Single place to fix bugs
   - Easier to add new features

4. **Better Testing**
   - Clear what to test
   - No duplicate test suites
   - Better coverage tracking

## ⚠️ Breaking Changes

- Scripts calling `ask-nix-enhanced` need to use `ask-nix --enhanced`
- Direct imports from old module paths need updating
- Some command-line arguments may change

## 📋 Implementation Checklist

- [ ] Create archive directories
- [ ] Move duplicate CLIs to archive
- [ ] Consolidate backend modules
- [ ] Unify interface implementations
- [ ] Update all imports
- [ ] Update bin/ask-nix to handle all modes
- [ ] Update documentation
- [ ] Update tests
- [ ] Update CLAUDE.md with new structure
- [ ] Create migration guide for users

## 🚀 Next Steps

1. **Get approval** for this plan
2. **Create backup** of current state
3. **Execute Phase 1** (archive duplicates) - Low risk
4. **Execute Phase 2-4** in a feature branch
5. **Test thoroughly**
6. **Merge and document**

This reorganization will make the project much more maintainable and understandable while preserving all functionality.