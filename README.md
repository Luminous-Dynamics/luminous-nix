# 🗣️ Nix for Humanity

> "Making NixOS accessible to every human through natural conversation."

[![Status](https://img.shields.io/badge/Status-Alpha-orange)](STATUS.md)
[![Version](https://img.shields.io/badge/Version-0.8.3-blue)](CHANGELOG.md)
[![Coverage](https://img.shields.io/badge/Coverage-74%25-yellow)](STATUS.md)
[![License](https://img.shields.io/badge/License-MIT-blue)](LICENSE)
[![Documentation](https://img.shields.io/badge/Docs-Comprehensive-green)](docs/README.md)

## 📊 Current Reality

**[📍 Read STATUS.md](STATUS.md) for transparent, up-to-date project status**

- **Test Coverage**: 74% (improving daily - was 57% last week!)
- **Performance**: Working on performance optimization (benchmarks coming soon)
- **Status**: Alpha but stable for core features
- **Active Focus**: Fixing test suite and aligning documentation with reality

## What is Nix for Humanity?

Nix for Humanity transforms NixOS from command-line complexity into natural conversation. Instead of memorizing commands, you simply talk to your computer in plain English.

### 🎯 What Actually Works Today

- **🗣️ Natural Language CLI**: Say "install Firefox" or "update my system" 
- **🎨 Beautiful TUI**: Terminal interface with keyboard navigation
- **🧠 Multiple Personalities**: 5 response styles (minimal → symbiotic)
- **👥 Accessibility First**: Designed for 10 diverse personas
- **🔒 100% Private**: Everything runs locally - no cloud dependencies

### 💬 Example Interactions

```
You: "I need something to edit photos"
Nix: "I can suggest GIMP (full-featured like Photoshop) or Krita (great for digital art). Which sounds better?"

You: "My internet is broken"
Nix: "I'll help diagnose that. Checking your connection... I see WiFi is disabled. Should I enable it?"

You: "Install that thing for PDFs"
Nix: "Installing Okular PDF viewer for you... Done! You'll find it in your applications menu."
```

## 🎉 NEW: Learning Mode for Step-by-Step Guidance!

Version 0.5.1 introduces Learning Mode - perfect for users like Carlos who need examples with every command. Combined with our Adaptive Response System, it provides the most supportive NixOS learning experience available.

### 📚 Learning Mode Features
- **Step-by-step walkthroughs** - Never skip ahead or get lost
- **Examples with every command** - See exactly what to type
- **Practice exercises** - Build confidence with guided tasks
- **Progress tracking** - See how far you've come
- **Troubleshooting help** - Get unstuck quickly
- **Adaptive responses** - Matches your learning style

Try it with `ask-nix-learning` - perfect for beginners!

### 🧠 Adaptive Response System
The system automatically adjusts to your needs:
- **Detects frustration** → Provides reassurance and simpler steps
- **Sees learning desire** → Activates step-by-step mode
- **Recognizes urgency** → Gives concise answers  
- **Notices accessibility needs** → Optimizes for screen readers

Try adaptive mode with `ask-nix-adaptive` or use the standard `ask-nix` command.

## 🎉 Unified ask-nix Command

We've consolidated all our tools into a single, feature-complete `ask-nix` command that combines the best of all versions.

### ✅ What's Working NOW (v0.5.0)
- **🌟 UNIFIED COMMAND** - Single `ask-nix` combines ALL features
- **🚀 AUTOMATIC EXECUTION** - Commands run directly, no more copy-paste!
- **⚡ INTELLIGENT CACHING** - 100-1000x faster package searches!
- **📚 COMMAND LEARNING** - System learns from successes and failures
- **Natural language understanding** - "install firefox", "update my system", "my wifi isn't working"
- **Safety confirmations** - Asks before installing/removing packages
- **Modern nix profile** - Uses latest NixOS commands, not deprecated nix-env
- **Progress indicators** - Beautiful visual progress with graceful fallback
- **Package validation** - Checks packages exist before trying to install
- **4 personality styles** - Minimal, friendly, encouraging, technical
- **Intent detection** - See how your queries are understood
- **Multiple safety modes** - Dry-run, execute, and no-dry-run options

### 🚧 Currently Polishing
- **Better error messages** - More helpful when things go wrong
- **Progress indicators** - Visual feedback during operations
- **More commands** - Rollback, garbage collection, service management
- **Home Manager integration** - User-level package management without sudo

### 🔮 Future Vision
- **Voice interface** - Speak naturally to your system
- **Learning system** - Adapts to your preferences over time
- **Visual fading** - Interface becomes invisible as you gain mastery
- **Collective wisdom** - Community patterns (privacy-preserved)

## 📚 Documentation

We have extensive documentation covering every aspect of the project:

- **[📖 Complete Documentation Index](docs/README.md)** - Start here!
- **[🌟 Vision](docs/project/VISION.md)** - What we're building and why
- **[🗺️ Roadmap](docs/project/ROADMAP.md)** - 3-month development plan
- **[👥 The 10 Core Personas](docs/project/PERSONAS.md)** - Who we're building for
- **[🏗️ Architecture](docs/technical/ARCHITECTURE.md)** - How it all works
- **[🧠 Philosophy](docs/philosophy/README.md)** - Consciousness-first computing

## 🚀 Quick Start - Try It NOW!

### Installation (NEW: Modern Python Package!)

```bash
# Clone the repository
git clone https://github.com/Luminous-Dynamics/nix-for-humanity
cd nix-for-humanity

# Install with your preferred features
pip install .                    # Minimal (CLI only)
pip install ".[tui]"            # With beautiful TUI
pip install ".[tui,voice]"      # With TUI + voice
pip install ".[all]"            # Everything

# For development
pip install -e ".[dev]"         # Editable install with dev tools
```

See [Requirements Migration Guide](docs/REQUIREMENTS_MIGRATION.md) for details on the new package structure.

### Phase 1: Real Execution! 🎉
```bash
# ACTUALLY INSTALLS FIREFOX (with confirmation)
ask-nix "install firefox"

# Other working examples:
ask-nix "search tree"           # Search for packages
ask-nix "install vim"           # Install with confirmation
ask-nix --yes "install htop"    # Skip confirmation
ask-nix --dry-run "install git" # Test without executing

# With personality
ask-nix --personality minimal "install python"
ask-nix --personality encouraging "update my system"

# Beautiful TUI (if installed with [tui])
nix-tui

# Show intent detection
ask-nix --show-intent "I need docker"
```

See [WORKING_COMMANDS.md](WORKING_COMMANDS.md) for all working features.

## 🤝 Contributing

We're actively seeking contributors who believe in making technology accessible to everyone!

### How You Can Help

- **🐛 Test & Report**: Try the early versions and share feedback
- **💻 Code**: Check our [roadmap](docs/project/ROADMAP.md) for current priorities
- **📝 Document**: Help improve our guides and tutorials
- **🎨 Design**: Create accessible, beautiful interfaces
- **🗣️ Translate**: Make Nix for Humanity speak your language
- **💡 Ideas**: Share your vision for human-computer interaction

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### Current Priority Tasks

1. ✅ **Phase 1 COMPLETE** - Real execution works! No more copy-paste!
2. **Add remove/uninstall** - Natural language package removal
3. **System updates** - Handle `nixos-rebuild switch` safely
4. **Configuration editing** - Modify configuration.nix naturally
5. **Rollback support** - "undo my last change"
6. **Voice interface** - Talk to your computer ([#5](https://github.com/Luminous-Dynamics/nix-for-humanity/issues/5))

## 💰 Revolutionary Development Model

This project is being built with:
- **1 human developer** (Tristan Stoltz)
- **Claude Code Max** ($200/month)
- **Total budget**: $10,440/year

Compared to traditional development:
- **Traditional cost**: $4.2M (team of 6-8 for 18 months)
- **Our cost**: $10k (99.7% reduction)
- **Proof that AI democratizes development**

Learn more: [Development Model](docs/development/NIX_CLAUDE_CODE_DEVELOPMENT.md)

## 🎯 Success Metrics

We measure success differently:

### ❌ What We DON'T Track
- Daily active users
- Time in app
- Engagement metrics

### ✅ What We DO Track  
- Task completion time (lower is better)
- User confidence growth
- Interface fade progression
- "Forgot I was using it" moments

## 🌟 The Journey Ahead

Nix for Humanity evolves through three stages:

1. **🏛️ Sanctuary** (Months 1-3): Rich visual guidance, hand-holding, learning together
2. **🏃 Gymnasium** (Months 4-9): Adaptive growth, pattern recognition, skill building  
3. **🌅 Open Sky** (Months 10+): Invisible excellence, pure intention, transcendent interaction

The ultimate success? When users forget they're using an interface at all.

## 📬 Get Involved

- **GitHub**: [Issues](https://github.com/Luminous-Dynamics/nix-for-humanity/issues) & [Discussions](https://github.com/Luminous-Dynamics/nix-for-humanity/discussions)
- **Matrix**: #nix-for-humanity:matrix.org (coming soon)
- **Blog**: [luminous-dynamics.org/blog](https://luminous-dynamics.org/blog) (coming soon)

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

Built with love by the [Luminous-Dynamics](https://github.com/Luminous-Dynamics) community.

Special thanks to:
- The NixOS community for creating such a powerful system
- Everyone who believes computers should adapt to humans, not the other way around
- The 10 core personas who guide every design decision

---

<p align="center">
  <i>"The best interface is no interface. The best assistant is one that speaks your language."</i>
  <br><br>
  <b>Let's make NixOS accessible to everyone. Together.</b>
</p>