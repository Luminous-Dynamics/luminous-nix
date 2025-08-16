# Dependencies and Tools Checklist for Luminous Nix

## ✅ Already Installed

### Core Python Libraries
- ✅ **numpy** - Numerical computing
- ✅ **scipy** - Scientific computing (just added!)
- ✅ **pandas** - Data manipulation
- ✅ **scikit-learn** - Machine learning
- ✅ **torch** - Deep learning
- ✅ **transformers** - NLP models

### System Monitoring
- ✅ **psutil** - Process and system utilities
- ✅ **py-cpuinfo** - CPU information
- ✅ **sqlite3** - Database for historical data

### UI/UX
- ✅ **textual** - Terminal UI
- ✅ **rich** - Beautiful terminal output
- ✅ **blessed** - Terminal capabilities
- ✅ **click** - CLI framework
- ✅ **colorama** - Cross-platform colored output

### Development Tools
- ✅ **pytest** - Testing framework
- ✅ **black** - Code formatter
- ✅ **ruff** - Fast linter
- ✅ **mypy** - Type checking
- ✅ **poetry** - Package management

## 🔶 Should Consider Adding

### Performance & Monitoring
```nix
python313Packages.memory-profiler  # Memory usage profiling
python313Packages.py-spy          # Sampling profiler
python313Packages.scalene         # High-performance profiler
python313Packages.prometheus-client # Metrics export
```

### ML/AI Enhancement
```nix
python313Packages.langchain       # LLM orchestration
python313Packages.openai          # OpenAI API (for comparison)
python313Packages.huggingface-hub # Model downloading
python313Packages.datasets        # HuggingFace datasets
```

### Database & Caching
```nix
python313Packages.redis           # For distributed caching
python313Packages.diskcache       # Persistent cache
python313Packages.alembic         # Database migrations
```

### System Integration
```nix
python313Packages.dbus-python     # D-Bus integration (we're using this)
python313Packages.systemd-python  # Systemd integration
python313Packages.watchdog        # File system monitoring
```

### Security
```nix
python313Packages.cryptography    # Encryption support
python313Packages.python-jose     # JWT tokens
python313Packages.passlib         # Password hashing
```

### Voice/Audio (Currently Missing)
```nix
python313Packages.speechrecognition  # Speech to text
python313Packages.pyttsx3           # Text to speech
python313Packages.soundfile         # Audio file I/O
python313Packages.librosa           # Audio analysis
```

## 🚀 Nice to Have (Future)

### Advanced Analytics
```nix
python313Packages.plotly          # Interactive visualizations
python313Packages.dash            # Web dashboards
python313Packages.streamlit       # Quick ML apps
```

### Distributed Computing
```nix
python313Packages.celery          # Task queue
python313Packages.dask            # Parallel computing
python313Packages.ray             # Distributed AI
```

### Documentation
```nix
python313Packages.mkdocs          # Documentation site
python313Packages.pdoc            # Auto API docs
python313Packages.mermaid         # Diagram generation
```

## 🛠️ System Tools We Should Add

### Essential Missing Tools
```bash
# Add to shell.nix or flake.nix:

# File watching and automation
watchman          # Facebook's file watcher
entr              # Run commands on file change
inotify-tools     # Linux file system events

# Process management
supervisor        # Process control system
circus            # Process & socket manager

# Debugging
gdb               # GNU debugger
valgrind          # Memory debugger
strace            # System call tracer

# Network debugging  
tcpdump           # Packet analyzer
wireshark-cli     # Network protocol analyzer
mtr               # Network diagnostic tool

# Log management
logrotate         # Log rotation
lnav              # Log file navigator
```

## 📦 Recommended Additions for Immediate Use

### 1. For Better Self-Healing
```bash
poetry add memory-profiler py-spy prometheus-client
```

### 2. For Voice Interface Stability
```bash
poetry add speechrecognition soundfile librosa
```

### 3. For Better Caching
```bash
poetry add diskcache redis
```

### 4. For Security
```bash
poetry add cryptography python-jose
```

## 🎯 Priority Order

### High Priority (Add Now)
1. **dbus-python** - For D-Bus monitoring ⚠️ (needs system deps - see note below)
2. **prometheus-client** - For metrics export ✅
3. **watchdog** - For file system monitoring ✅
4. **diskcache** - For persistent caching ✅

### Medium Priority (Add Soon)
1. **speechrecognition** - For voice interface
2. **langchain** - For LLM orchestration
3. **redis** - For distributed caching
4. **memory-profiler** - For optimization

### Low Priority (Add Later)
1. **plotly/dash** - For dashboards
2. **celery** - For task queues
3. **ray** - For distributed computing

## 💾 How to Add Dependencies

### Using Poetry (Recommended)
```bash
# Add to pyproject.toml and lock file
poetry add package-name

# Add as dev dependency
poetry add --group dev package-name

# Add with extras
poetry add package-name --extras "feature"
```

### Using Nix Shell
```nix
# Edit shell.nix
buildInputs = with pkgs; [
  python313Packages.new-package
  # ...
];
```

### Using Flake
```nix
# Edit flake.nix in pythonEnv section
pythonEnv = pkgs.python313.withPackages (ps: with ps; [
  new-package
  # ...
]);
```

## 📋 Final Recommendations

### Immediate Actions
1. ✅ **scipy** - Already added!
2. Add **prometheus-client** for metrics
3. Add **watchdog** for file monitoring
4. Add **diskcache** for better caching

### Next Session
1. Improve voice interface dependencies
2. Add security libraries
3. Set up proper monitoring

### Long Term
1. Consider distributed computing needs
2. Add visualization tools
3. Implement proper CI/CD dependencies

## 🚨 Special Notes

### D-Bus Python Installation
The `dbus-python` package requires system dependencies (ninja, meson, dbus development headers) that are not easily installable via Poetry alone. For D-Bus integration:

1. **Option A**: Use system package manager
   ```bash
   # On NixOS, add to shell.nix:
   buildInputs = [ pkgs.python313Packages.dbus-python ];
   ```

2. **Option B**: Use subprocess calls to `dbus-send`
   ```python
   # Instead of dbus-python, use:
   subprocess.run(['dbus-send', '--system', ...])
   ```

3. **Option C**: Use alternative library
   ```bash
   poetry add pydbus  # Pure Python alternative (limited features)
   ```

## 🎉 Summary

We have successfully added:
- ✅ **scipy** - Scientific computing 
- ✅ **prometheus-client** - Metrics export
- ✅ **watchdog** - File system monitoring  
- ✅ **diskcache** - Persistent caching
- ⚠️ **dbus-python** - Needs system dependencies (see note above)

The system is well-equipped for its current features, with robust monitoring and caching capabilities now in place!

---

*"Dependencies are like spices - too few and it's bland, too many and it's overwhelming. Find the right balance!"*