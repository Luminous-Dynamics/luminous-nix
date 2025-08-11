# 🚀 Quick Start Guide - Nix for Humanity

*Get started with natural language NixOS in 5 minutes*

---

💡 **Quick Context**: Complete onboarding guide from zero to productive NixOS conversations
📍 **You are here**: Development → Quick Start (5-minute setup)
🔗 **Related**: [Code Standards](./04-CODE-STANDARDS.md) | [Sacred Trinity Workflow](./02-SACRED-TRINITY-WORKFLOW.md) | [Master Documentation Map](../MASTER_DOCUMENTATION_MAP.md)
⏱️ **Read time**: 8 minutes
📊 **Mastery Level**: 🌱 Beginner - no prior NixOS or AI experience needed

🌊 **Natural Next Steps**:
- **For developers**: Continue to [Code Standards](./04-CODE-STANDARDS.md) after setup
- **For contributors**: Review [Sacred Trinity Workflow](./02-SACRED-TRINITY-WORKFLOW.md)
- **For researchers**: Explore [Learning System Architecture](../02-ARCHITECTURE/09-LEARNING-SYSTEM.md)
- **For users**: Try the [Testing Guide](./05-TESTING-GUIDE.md) to validate your setup

---

## What You'll Need

- NixOS system (or Linux with Nix)
- Python 3.11+
- 500MB free disk space
- Internet connection for setup
- That's it!

## Installation

### Development Setup (Current Method)
```bash
# Clone repository
git clone https://github.com/Luminous-Dynamics/nix-for-humanity
cd nix-for-humanity

# Enter development environment
./dev.sh

# Install Python dependencies
pip install -r requirements.txt

# Run the CLI tool
./bin/ask-nix "help"
```

### Future Installation (Coming Soon)
```bash
# Once released, you'll be able to:
nix-env -iA nixpkgs.nix-for-humanity
# or add to configuration.nix
```

## First Launch

Start the development version:

```bash
# From the project directory
./bin/ask-nix

# Or with the Python backend enabled (recommended)
export NIX_HUMANITY_PYTHON_BACKEND=true
./bin/ask-nix
```

You'll see:
```
Welcome to Nix for Humanity! 👋

I'll help you manage NixOS using natural conversation.
Just tell me what you want to do in your own words.

For example:
- "install firefox"
- "update my system"
- "my wifi isn't working"

What would you like to do?
>
```

## Your First Commands

### 1. Install Something
```
You: I need a web browser
System: I can help you install a web browser! Here are some options:
- Firefox (recommended, open source)
- Chrome
- Brave (privacy-focused)

Which would you like?

You: firefox
System: Installing Firefox... Done! Firefox is now available in your applications menu.
```

### 2. System Update
```
You: is my system up to date?
System: Let me check for updates... You have 12 packages that can be updated.
Would you like to see them or update everything?

You: update everything
System: Updating your system... This might take a few minutes.
[Progress bar]
Done! Your system is now up to date.
```

### 3. Get Help
```
You: help
System: I can help you with:
• Installing/removing software
• System updates and maintenance
• Network and WiFi issues
• User and permission management
• System information and monitoring

Just describe what you need in natural language!
```

## Choose Your Personality

The system adapts to how YOU like to communicate:

### See Current Style
```
You: how are you talking to me?
System: I'm using a friendly, helpful style. Would you like me to adjust how I communicate?
```

### Change Style
```
You: be more technical
System: Switching to minimal technical style.

You: be more fun
System: Switching to playful mode! Let's make computing fun! 🎮

You: just be normal
System: I'll use a friendly, professional tone.
```

### Available Styles
1. **Minimal** - Just the facts
2. **Friendly** - Warm and helpful (default)
3. **Encouraging** - Supportive and educational
4. **Playful** - Fun with personality
5. **Sacred** - Mindful computing (optional)

## Common Tasks

### Software Management
- "install [anything]" - Installs software
- "remove [software]" - Uninstalls software
- "search for [keyword]" - Finds packages
- "what's installed?" - Lists your software

### System Tasks
- "update system" - Updates everything
- "clean up space" - Frees disk space
- "restart" - Reboots system
- "check system health" - System status

### Getting Information
- "how much disk space?" - Storage info
- "what's using memory?" - Memory usage
- "show cpu usage" - Processor info
- "what version of linux?" - System info

### Network Help
- "connect to wifi" - Network setup
- "my internet isn't working" - Troubleshooting
- "what's my ip address?" - Network info

## Tips for Best Experience

### 1. Be Natural
```
Good: "I need something to edit photos"
Also good: "install photo editor"
Also good: "get me gimp"
```

### 2. Ask Questions
```
You: what's the difference between firefox and firefox-esr?
System: Firefox ESR (Extended Support Release) is more stable with fewer updates,
while regular Firefox has the latest features. Which suits your needs better?
```

### 3. Corrections Work
```
You: install fierfix
System: I'll install Firefox for you (I noticed the typo - no worries!)
```

### 4. Context Understood
```
You: install code editor
System: Installing VS Code...

You: actually, make it vim instead
System: Canceling VS Code installation. Installing Vim instead...
```

## Troubleshooting

### System Doesn't Understand
Try rephrasing or being more specific:
- ❌ "fix it"
- ✅ "fix my wifi connection"

### Wrong Package
Just say no and clarify:
```
System: Installing Chrome...
You: no, I meant Chromium
System: My mistake! Installing Chromium instead...
```

### Need More Options
Ask for alternatives:
```
You: show me text editors
System: Here are popular text editors:
- VS Code - Full featured IDE
- Vim - Powerful terminal editor
- Emacs - Extensible editor
- Sublime Text - Fast and minimal
Which interests you?
```

## Voice Control (Optional)

If you prefer speaking:

### Enable Voice
```
You: turn on voice control
System: Voice control enabled! Say "Hey Nix" to activate.
```

### Voice Commands
Say "Hey Nix" then:
- "Install Firefox"
- "Update my system"
- "What's my disk usage?"

## Privacy & Control

Your privacy is absolute:
- ✅ All processing happens locally
- ✅ No data ever leaves your computer
- ✅ You own all your data
- ✅ Learning can be disabled

### View What's Learned
```
You: what have you learned about me?
System: I've noticed you prefer brief responses and often install development tools.
```

### Reset Learning
```
You: forget everything about me
System: All learned patterns have been erased. Starting fresh!
```

## Next Steps

Now that you're started:

1. **Try Different Tasks** - Explore what you can do
2. **Find Your Style** - Adjust personality to your preference
3. **Learn Naturally** - The system adapts to you
4. **Get Help Anytime** - Just type "help" or ask questions

## Remember

- There's no wrong way to ask
- The system learns your preferences
- Everything stays private and local
- It gets better the more you use it

---

**Ready to go deeper?** Check out the full [User Guide](USER_GUIDE.md)

**Having issues?** See [Troubleshooting](TROUBLESHOOTING.md)

**Want to contribute?** Read [Contributing](../CONTRIBUTING.md)

---

*Sacred Humility Context: This onboarding guide represents our current understanding of effective user introduction to consciousness-first AI systems. While our 5-minute setup process has proven successful within our development environment, the broader applicability of our onboarding approach across diverse user technical backgrounds, system configurations, and learning preferences requires validation through real-world usage by diverse user communities. Our setup instructions reflect our specific NixOS and development context and may need adaptation for different operating systems, hardware configurations, and user requirements.*

*Welcome to natural language NixOS - where your computer finally speaks your language!* 🎉
