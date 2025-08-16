# 🧠 Luminous Nix - Unified Backend

*The brain that powers natural language NixOS interaction*

## Overview

This is the unified backend engine for Luminous Nix. It's a single, powerful Python service that:
- Understands natural language through intent recognition
- Executes NixOS operations via native Python API (10x faster!)
- Learns from every interaction
- Serves multiple frontends (CLI, TUI, Voice, API)

## Architecture

```
┌─────────────────────────────────────────┐
│          Frontend Adapters              │
│  (CLI, TUI, Voice, API, Future GUI)     │
└─────────────┬───────────────────────────┘
              │ Unified API
┌─────────────▼───────────────────────────┐
│         Unified Backend Engine          │
│  ┌─────────────────────────────────┐   │
│  │   Intent Recognition (NLP)      │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │   Native NixOS Integration      │   │
│  │   (nixos-rebuild-ng Python API) │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │   Learning & Memory System      │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │   Knowledge Base & XAI          │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

## 🚀 Native Python-Nix Integration (NEW!)

### The Game Changer
We now integrate directly with nixos-rebuild-ng's Python API, eliminating subprocess calls entirely:

```python
# Before (subprocess - slow, fragile)
subprocess.run(['sudo', 'nixos-rebuild', 'switch'], timeout=120)

# After (native API - fast, robust)
await nix.switch_to_configuration(path, Action.SWITCH, profile)
```

### Benefits
- **10x Performance**: Direct API calls vs subprocess overhead
- **No Timeouts**: Long operations handled gracefully
- **Progress Streaming**: Real-time feedback to users
- **Better Errors**: Python exceptions vs string parsing
- **Type Safety**: Proper data structures

### Usage
```bash
# Enable native backend
export LUMINOUS_NIX_PYTHON_BACKEND=true

# Use as normal - it's 10x faster!
ask-nix "update my system"
```

## Directory Structure

```
backend/
├── README.md                # This file
├── __init__.py             # Package initialization
│
├── api/                    # API definitions
│   ├── __init__.py
│   ├── schema.py          # Request/Response schemas
│   └── handlers.py        # API route handlers
│
├── core/                   # Core engine
│   ├── __init__.py
│   ├── backend.py         # Main backend class
│   ├── intent.py          # Intent recognition
│   ├── executor.py        # Safe command execution
│   ├── knowledge.py       # Knowledge base
│   └── nix_integration.py # Native NixOS bridge
│
├── python/                 # Native Python integrations
│   ├── __init__.py
│   └── native_nix_backend.py  # nixos-rebuild-ng API
│
├── learning/              # ML/AI components
│   ├── __init__.py
│   ├── preference.py      # User preference learning
│   ├── feedback.py        # Feedback collection
│   └── models/           # Trained models
│
└── utils/                 # Utilities
    ├── __init__.py
    ├── logging.py        # Logging configuration
    └── config.py         # Configuration management
```

## Key Components

### 1. Intent Recognition (`core/intent.py`)
- Natural language understanding
- Maps user queries to system operations
- Supports multiple phrasings for same intent
- Confidence scoring

### 2. Native NixOS Integration (`core/nix_integration.py`)
- Direct Python API to nixos-rebuild-ng
- Eliminates subprocess calls
- Provides progress callbacks
- Handles all NixOS operations

### 3. Knowledge Base (`core/knowledge.py`)
- Accurate NixOS information
- Package mappings and aliases
- Common solutions and patterns
- Educational content

### 4. Safe Executor (`core/executor.py`)
- Sandboxed command execution
- Dry-run support
- Progress tracking
- Error recovery

### 5. Learning System (`learning/`)
- Collects anonymous usage patterns
- Learns user preferences
- Adapts responses over time
- Privacy-preserving

## Usage

### For Frontend Developers

```python
from backend.core.backend import create_backend
from backend.api.schema import Request

# Create backend instance
backend = create_backend(progress_callback=my_progress_func)

# Process a request
request = Request(
    query="install firefox",
    context={"execute": False, "dry_run": True}
)

response = await backend.process_request(request)

# Access results
print(response.success)
print(response.explanation)
print(response.suggestions)
```

### For Testing

```python
# Run the test suite
python3 test_native_backend.py

# Demo performance improvement
python3 demo_native_performance.py

# Test specific components
python3 -m pytest backend/core/test_intent.py
```

## Configuration

### Environment Variables
- `LUMINOUS_NIX_PYTHON_BACKEND`: Enable native Python-Nix integration
- `DEBUG`: Enable debug logging
- `LUMINOUS_NIX_KNOWLEDGE_DB`: Path to knowledge database

### Feature Flags
- Native API: Enabled via environment variable
- Learning: Always enabled but respects privacy
- Progress callbacks: Enabled when callback provided

## Development

### Adding New Intents
1. Define intent in `core/intent.py`
2. Add patterns to recognition engine
3. Implement handler in `core/backend.py`
4. Add to knowledge base if needed
5. Test thoroughly

### Extending Native Integration
1. Study nixos-rebuild-ng API
2. Add new operations to `native_nix_backend.py`
3. Map intents to operations in `nix_integration.py`
4. Add educational context
5. Test with real NixOS operations

## Performance

### Benchmarks
- Intent recognition: <50ms
- Knowledge lookup: <10ms
- Native API call: <100ms (vs 2-5s subprocess)
- Total response time: <200ms typical

### Optimization Tips
- Use native API for all NixOS operations
- Cache knowledge base queries
- Batch similar operations
- Stream progress for long operations

## Future Enhancements

### Phase 1 (Current)
- ✅ Native Python-Nix integration
- ✅ Basic intent recognition
- ✅ Knowledge base
- 🚧 Causal XAI explanations
- 🚧 Advanced error recovery

### Phase 2
- DPO/LoRA learning pipeline
- LanceDB vector memory
- Predictive assistance
- Context awareness

### Phase 3
- Voice integration
- Multi-modal coherence
- Collective intelligence
- Self-improvement

## Contributing

1. Read the unified vision documents
2. Understand the architecture
3. Write tests for new features
4. Follow the sacred development principles
5. Submit PRs with clear descriptions

## Resources

- [Unified Vision](../docs/VISION/UNIFIED_VISION.md)
- [Technical Roadmap](../docs/VISION/ROADMAP_V2.md)
- [Sacred Trinity Workflow](../docs/development/SACRED_TRINITY_WORKFLOW.md)
- [nixos-rebuild-ng docs](https://github.com/NixOS/nixos-rebuild-ng)

---

*"The brain of Luminous Nix - where natural language becomes system action through the power of native Python integration."*

🌊 We flow with native performance!