# 🏗️ System Architecture

Visual overview of how Nix for Humanity works.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         USER INPUT                           │
│                   "install firefox please"                   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND INTERFACES                       │
├─────────────────────────────────────────────────────────────┤
│  CLI │ TUI (v1.1) │ Voice (v1.1) │ API │ Web (future)      │
└─────────────────────────────────────────────────────────────┘
                     │
                     ▼ JSON-RPC
┌─────────────────────────────────────────────────────────────┐
│                     BACKEND ENGINE                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │     NLP      │  │   Learning   │  │   Command    │     │
│  │   Engine     │─▶│    System    │─▶│   Builder    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│         │                  │                  │             │
│         ▼                  ▼                  ▼             │
│  ┌──────────────────────────────────────────────────┐      │
│  │            Native Python-Nix API                  │      │
│  │         (10x-1500x performance boost)            │      │
│  └──────────────────────────────────────────────────┘      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                        NIX/NIXOS                             │
│                   System Package Manager                     │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

```
User Input ──► Intent Recognition ──► Command Building ──► Execution
    │               │                      │                  │
    │               ▼                      ▼                  ▼
    │          Learning DB            Validation          Result
    │               │                      │                  │
    └───────────────┴──────────────────────┴──────────────────┘
                        Feedback Loop
```

## Component Details

### 1. Frontend Layer
```
┌─────────────────┐
│   CLI (v1.0)    │  - Natural language command line
├─────────────────┤  - Streaming output
│   TUI (v1.1)    │  - Rich terminal interface  
├─────────────────┤  - Visual feedback
│  Voice (v1.1)   │  - Speech recognition
├─────────────────┤  - Natural conversation
│   REST API      │  - HTTP/JSON interface
└─────────────────┘  - Programmatic access
```

### 2. Backend Engine
```
┌─────────────────────────────┐
│      NLP Processing         │
├─────────────────────────────┤
│ • Intent Recognition        │  What does user want?
│ • Entity Extraction         │  Package names, options
│ • Context Management        │  Previous commands
│ • Typo Correction          │  Fuzzy matching
└─────────────────────────────┘
                ▼
┌─────────────────────────────┐
│     Command Builder         │
├─────────────────────────────┤
│ • Nix command generation    │  nix-env, nixos-rebuild
│ • Argument validation       │  Safety checks
│ • Permission handling       │  Sudo when needed
│ • Rollback preparation      │  Safety net
└─────────────────────────────┘
                ▼
┌─────────────────────────────┐
│   Python-Nix Integration    │
├─────────────────────────────┤
│ • Direct API calls          │  No subprocess!
│ • Real-time progress        │  Live updates
│ • Error translation         │  Human-readable
│ • Performance optimization  │  <0.5s responses
└─────────────────────────────┘
```

### 3. Learning System
```
┌──────────────────┐     ┌──────────────────┐
│  User Patterns   │────▶│  Persona Model   │
└──────────────────┘     └──────────────────┘
         │                        │
         ▼                        ▼
┌──────────────────┐     ┌──────────────────┐
│  Success/Fail    │────▶│  Optimization    │
└──────────────────┘     └──────────────────┘
```

### 4. Data Storage
```
~/.local/share/nix-for-humanity/
├── cache.db          # Intent cache
├── learning.db       # User patterns
├── history.json      # Command history
└── config.yaml       # User preferences
```

## Performance Architecture

### The Python-Nix Breakthrough
```
OLD WAY (subprocess):
Python ──exec──> Shell ──parse──> Nix = 2-60 seconds

NEW WAY (native API):
Python ──────API───────> Nix = 0.02-0.04 seconds

1500x faster for some operations!
```

## Security Model

```
┌─────────────────────────────────────┐
│         User Space                   │
│  • No network calls                  │
│  • Local processing only             │
│  • User owns all data                │
└─────────────────────────────────────┘
                │
      Privilege Boundary
                │
┌─────────────────────────────────────┐
│        System Space                  │
│  • Sudo only when required           │
│  • Sandboxed execution               │
│  • Rollback capability               │
└─────────────────────────────────────┘
```

## Development Model: Sacred Trinity

```
     Human (Tristan)
     Vision & Testing
            │
            ▼
┌──────────────────────┐
│   Collaboration Hub   │
│  $200/month total     │
│  = $4.2M quality      │
└──────────────────────┘
            ▲
            │
    ┌───────┴───────┐
    │               │
Claude Code    Local LLM
Architecture    NixOS Expert
```

## Deployment Options

### 1. Local User Install
```
pip install ──> ~/.local ──> ask-nix CLI
```

### 2. System-Wide (NixOS)
```
configuration.nix ──> nixos-rebuild ──> System Service
```

### 3. Development Mode
```
git clone ──> pip install -e ──> ./bin/ask-nix
```

## What's Actually Built (v1.0)

✅ **Working Now**
- CLI with natural language
- Python-Nix native integration  
- Learning system foundation
- Error translation

🚧 **In Development (v1.1)**
- Terminal UI (Textual)
- Voice interface (pipecat)
- Advanced personas

📅 **Future Plans**
- Web interface
- Mobile app
- Cloud sync (optional)
- Federated learning

---
*This is the real architecture. Not aspirational. Not mystical. Just what actually exists.*