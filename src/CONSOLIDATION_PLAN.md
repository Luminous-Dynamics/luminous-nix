# Source Code Consolidation Plan

## Current Overlap Analysis

### 1. Backend vs Core
- `backend/` has only 1 file: `native_nix_api.py`
- `core/` has 40+ files including duplicate functionality
- Many `.bak` files indicating previous refactoring attempts

### 2. UI vs TUI vs Interfaces
- `ui/` - 10+ files for various UI components
- `tui/` - 5 files for terminal UI
- `interfaces/` - Already has cli.py, tui.py, voice.py (correct structure!)

### 3. Voice Scattered
- `interfaces/voice.py` AND `interfaces/voice_interface.py`
- `tui/voice_widget.py`
- `voice/` directory also exists

## Consolidation Actions

### Phase 1: Move backend → nix/
```bash
# backend/native_nix_api.py → nix/native_api.py
mv src/nix_for_humanity/backend/native_nix_api.py src/nix_for_humanity/nix/native_api.py
rmdir src/nix_for_humanity/backend
```

### Phase 2: Clean up core/
```bash
# Remove .bak files (we have git)
rm src/nix_for_humanity/core/*.bak

# Move Nix-specific files to nix/
mv src/nix_for_humanity/core/nix_*.py src/nix_for_humanity/nix/
mv src/nix_for_humanity/core/native_operations*.py src/nix_for_humanity/nix/
mv src/nix_for_humanity/core/nixos_version.py src/nix_for_humanity/nix/
mv src/nix_for_humanity/core/package_discovery.py src/nix_for_humanity/nix/
mv src/nix_for_humanity/core/flake_manager.py src/nix_for_humanity/nix/
mv src/nix_for_humanity/core/generation_manager.py src/nix_for_humanity/nix/
mv src/nix_for_humanity/core/home_manager.py src/nix_for_humanity/nix/
mv src/nix_for_humanity/core/config_generator.py src/nix_for_humanity/nix/
```

### Phase 3: Consolidate UI
```bash
# Move TUI components to interfaces/
mv src/nix_for_humanity/tui/* src/nix_for_humanity/interfaces/tui/
rmdir src/nix_for_humanity/tui

# Move UI components to interfaces/
mv src/nix_for_humanity/ui/* src/nix_for_humanity/interfaces/ui/
rmdir src/nix_for_humanity/ui
```

### Phase 4: Unify voice
```bash
# Keep only one voice implementation
# Merge voice_interface.py into voice.py
```

## Final Structure

```
src/nix_for_humanity/
├── core/              # Core business logic ONLY
│   ├── backend.py     # Main backend
│   ├── engine.py      # Execution engine
│   ├── executor.py    # Command execution
│   ├── intents.py     # Intent recognition
│   ├── knowledge.py   # Knowledge base
│   ├── cache.py       # Caching
│   └── errors.py      # Error handling
│
├── nix/               # ALL NixOS-specific code
│   ├── native_api.py  # Native Python-Nix API
│   ├── operations.py  # Nix operations
│   ├── packages.py    # Package management
│   ├── config.py      # Config generation
│   ├── flakes.py      # Flake management
│   └── home.py        # Home manager
│
├── interfaces/        # ALL user interfaces
│   ├── cli.py         # CLI interface
│   ├── tui/           # TUI components
│   │   ├── app.py
│   │   └── widgets.py
│   ├── ui/            # UI components
│   │   └── components.py
│   ├── voice.py       # Voice interface
│   └── api.py         # REST/WebSocket
│
├── learning/          # AI/ML
├── utils/             # Utilities
└── plugins/           # Plugins
```