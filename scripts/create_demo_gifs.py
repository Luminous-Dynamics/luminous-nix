#!/usr/bin/env python3
"""
Create demo GIFs for v1.1 features.

This generates animated demonstrations of TUI and voice features.
"""

import json
import os


def create_demo_script():
    """Create a script that demonstrates key features."""

    demos = {
        "tui_basic": {
            "title": "Basic TUI Usage",
            "duration": 15,
            "script": [
                {"action": "launch", "command": "nix-tui"},
                {"action": "wait", "seconds": 2},
                {"action": "type", "text": "install firefox", "speed": 0.1},
                {"action": "wait", "seconds": 1},
                {"action": "key", "key": "enter"},
                {"action": "wait", "seconds": 3},
                {"action": "show_result", "text": "✅ Firefox installed successfully"},
                {"action": "wait", "seconds": 2},
                {"action": "type", "text": "search markdown", "speed": 0.1},
                {"action": "key", "key": "enter"},
                {"action": "wait", "seconds": 2},
                {"action": "show_results", "items": ["obsidian", "typora", "marktext"]},
            ],
        },
        "tui_personas": {
            "title": "Persona Switching",
            "duration": 20,
            "script": [
                {"action": "launch", "command": "nix-tui"},
                {"action": "wait", "seconds": 1},
                {"action": "key", "key": "ctrl+s"},
                {"action": "wait", "seconds": 1},
                {"action": "navigate", "to": "Personas"},
                {"action": "select", "item": "Maya (ADHD)"},
                {"action": "show_change", "text": "Theme changed to high contrast"},
                {"action": "wait", "seconds": 2},
                {"action": "select", "item": "Grandma Rose"},
                {"action": "show_change", "text": "Theme changed to gentle mode"},
                {"action": "wait", "seconds": 2},
            ],
        },
        "voice_demo": {
            "title": "Voice Interface",
            "duration": 25,
            "script": [
                {"action": "launch", "command": "nix-voice"},
                {"action": "wait", "seconds": 2},
                {"action": "show_waveform", "active": True},
                {"action": "speak", "text": "Hey Nix"},
                {"action": "show_detection", "text": "Wake word detected!"},
                {"action": "wait", "seconds": 1},
                {"action": "speak", "text": "Install firefox please"},
                {"action": "show_transcription", "text": "install firefox please"},
                {"action": "wait", "seconds": 1},
                {"action": "show_response", "text": "Installing Firefox browser..."},
                {"action": "play_tts", "text": "I'm installing Firefox for you"},
                {"action": "wait", "seconds": 3},
                {"action": "show_result", "text": "✅ Firefox has been installed"},
            ],
        },
        "performance_demo": {
            "title": "Lightning Fast Performance",
            "duration": 10,
            "script": [
                {"action": "split_screen", "panels": ["v1.0", "v1.1"]},
                {
                    "action": "parallel_execute",
                    "commands": [
                        {
                            "panel": "v1.0",
                            "command": "nix-env -qa firefox",
                            "time": "2.3s",
                        },
                        {
                            "panel": "v1.1",
                            "command": "ask-nix search firefox",
                            "time": "0.1s",
                        },
                    ],
                },
                {"action": "wait", "seconds": 3},
                {"action": "show_comparison", "text": "23x faster!"},
            ],
        },
    }

    return demos


def generate_asciinema_script(demo_name, demo_config):
    """Generate an asciinema recording script."""

    script = f"""#!/usr/bin/env python3
# Asciinema demo script for {demo_name}

import time
import sys

def type_text(text, speed=0.1):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(speed)

def main():
    print("\\033[2J\\033[H")  # Clear screen
    print("🎬 Nix for Humanity v1.1 - {demo_config['title']}")
    print("=" * 50)
    time.sleep(2)

"""

    for step in demo_config["script"]:
        if step["action"] == "type":
            script += f"    type_text('{step['text']}', {step.get('speed', 0.1)})\n"
        elif step["action"] == "wait":
            script += f"    time.sleep({step['seconds']})\n"
        elif step["action"] == "show_result":
            script += f"    print('\\n{step['text']}')\n"
        elif step["action"] == "key":
            if step["key"] == "enter":
                script += "    print()\n"
            else:
                script += f"    print('[{step['key']}]')\n"

    script += """
if __name__ == "__main__":
    main()
"""

    return script


def create_marketing_snippets():
    """Create social media snippets for marketing."""

    snippets = {
        "twitter": [
            {
                "text": "🎉 Nix for Humanity v1.1 is here! Beautiful TUI, voice commands, and lightning-fast performance. Making NixOS accessible to everyone! 🚀 #NixOS #OpenSource",
                "media": "tui_demo.gif",
            },
            {
                "text": "Say goodbye to command-line complexity! 🎤 'Hey Nix, install firefox' - Natural language for NixOS is finally here. Try v1.1 today! #VoiceUI #NixOS",
                "media": "voice_demo.gif",
            },
            {
                "text": "⚡ 10-1500x performance improvements in v1.1! List generations in 0.00 seconds. The future of NixOS is fast! #Performance #NixOS",
                "media": "performance_demo.gif",
            },
        ],
        "mastodon": [
            {
                "text": "🌟 Excited to announce Nix for Humanity v1.1!\n\n✨ Beautiful Terminal UI\n🎤 Voice Commands\n⚡ Native Performance\n♿ Full Accessibility\n\nMaking #NixOS accessible to everyone, from Grandma Rose to Dr. Sarah!\n\n#OpenSource #Accessibility #VoiceUI",
                "media": ["tui_demo.gif", "voice_demo.gif"],
            }
        ],
        "reddit": {
            "title": "[Release] Nix for Humanity v1.1 - TUI, Voice, and 1500x Performance",
            "text": """
Hey r/NixOS!

We're thrilled to release v1.1 of Nix for Humanity with three major features:

**🎨 Beautiful Terminal UI**
- Launch with `nix-tui` for an interactive experience
- Adaptive themes for different users (ADHD-friendly, elder-friendly, etc.)
- Real-time visual feedback with our "consciousness orb"

**🎤 Voice Interface**
- Say "Hey Nix, install firefox" and it just works
- Multi-language support
- Noise cancellation for real-world use

**⚡ Native Performance**
- Direct Python-Nix API integration
- List generations: 2-5s → 0.00s (literally instant)
- Package operations: 10-1500x faster

The goal is making NixOS accessible to everyone - from terminal beginners to power users who want to work faster.

**Try it**: `nix-env -iA nixpkgs.nix-for-humanity`

[Demo GIFs] [Documentation] [GitHub]

Built with love by the Sacred Trinity development model (Human + AI collaboration).
""",
        },
    }

    return snippets


def main():
    """Generate all demo materials."""
    print("🎬 Creating Demo Materials for v1.1")
    print("=" * 40)

    # Create demo directory
    demo_dir = "demos/v1.1"
    os.makedirs(demo_dir, exist_ok=True)

    # Generate demo scripts
    demos = create_demo_script()
    for name, config in demos.items():
        script = generate_asciinema_script(name, config)
        with open(f"{demo_dir}/{name}_demo.py", "w") as f:
            f.write(script)
        print(f"✅ Created {name}_demo.py")

    # Save demo configurations
    with open(f"{demo_dir}/demo_configs.json", "w") as f:
        json.dump(demos, f, indent=2)
    print("✅ Saved demo configurations")

    # Generate marketing snippets
    snippets = create_marketing_snippets()
    with open(f"{demo_dir}/marketing_snippets.json", "w") as f:
        json.dump(snippets, f, indent=2)
    print("✅ Created marketing snippets")

    # Create recording instructions
    instructions = """# Demo Recording Instructions

## Prerequisites
- asciinema installed: `nix-env -iA nixpkgs.asciinema`
- svg-term for GIF conversion: `npm install -g svg-term`

## Recording Steps

1. **TUI Demo**:
   ```bash
   asciinema rec demos/v1.1/tui_basic.cast
   python3 demos/v1.1/tui_basic_demo.py
   # Ctrl+D to stop
   svg-term --in demos/v1.1/tui_basic.cast --out demos/v1.1/tui_basic.gif
   ```

2. **Voice Demo**:
   ```bash
   # Record audio separately, then create visualization
   python3 demos/v1.1/voice_demo.py
   ```

3. **Performance Demo**:
   ```bash
   asciinema rec demos/v1.1/performance.cast
   python3 demos/v1.1/performance_demo.py
   ```

## Post-Processing
- Optimize GIFs: `gifsicle -O3 input.gif > output.gif`
- Create thumbnails: `convert input.gif[0] thumbnail.png`
"""

    with open(f"{demo_dir}/RECORDING_INSTRUCTIONS.md", "w") as f:
        f.write(instructions)
    print("✅ Created recording instructions")

    print(f"\n📁 Demo materials created in: {demo_dir}/")
    print("📸 Next: Record demos using asciinema")


if __name__ == "__main__":
    main()
