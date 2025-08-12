#!/usr/bin/env python3
"""
Voice Interface Demo (Standalone Working Version) for Nix for Humanity

This demo simulates voice interface interactions without any project dependencies.
Shows what the voice interface will provide once Whisper and Piper are integrated.

Usage:
    python demo_voice_working_standalone.py
"""

import time
import json
from pathlib import Path
from typing import Dict, List, Any


class VoiceSimulator:
    """Simulates voice interface interactions"""
    
    def __init__(self):
        self.is_listening = False
        self.conversation_history = []
        
    def simulate_voice_input(self, text: str) -> str:
        """Simulate hearing voice input"""
        print(f"\n🔊 User says: '{text}'")
        return text.lower().replace("hey nix, ", "").replace("hey nix ", "")
        
    def simulate_voice_output(self, text: str):
        """Simulate speaking response"""
        print(f"🤖 Nix responds: {text}")
        # Simulate TTS delay
        time.sleep(0.5)
        
    def process_command(self, command: str) -> str:
        """Process voice command and return response"""
        print(f"💭 Processing: '{command}'")
        
        # Simple pattern matching for demo
        if "what" in command and "installed" in command:
            return "You have 247 packages installed. Key ones include firefox, git, python3, and nodejs."
            
        elif "help" in command or "how" in command:
            return "I can help you install software, search for packages, update your system, or manage configurations. Just ask naturally!"
            
        elif "update" in command:
            return "I would update your system with: sudo nixos-rebuild switch. This applies your configuration changes."
            
        elif "search" in command or "find" in command:
            # Extract search query
            query = command
            for prefix in ["search for ", "find me ", "find "]:
                if prefix in query:
                    query = query.split(prefix)[-1]
                    break
            query = query.replace("a ", "").replace("an ", "").strip()
            return f"I found several {query} packages. Popular options include vim, neovim, and emacs for text editing."
            
        elif "install" in command:
            # Extract package name
            package = command.replace("install ", "").strip()
            return f"I would install {package} for you. In dry-run mode, the command would be: nix-env -iA nixos.{package}"
            
        else:
            return f"I understood you want to: {command}. Let me help you with that. Try asking to install, search, or update something."
            
    def _make_speakable(self, text: str) -> str:
        """Convert technical text to natural speech"""
        text = text.replace("NixOS", "nix O S")
        text = text.replace("sudo", "pseudo")
        text = text.replace("nixos-rebuild", "nix O S rebuild")
        text = text.replace("nix-env", "nix env")
        return text


def show_banner():
    """Display the demo banner"""
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║                                                                  ║
    ║       🎤 Nix for Humanity - Voice Interface Demo 🎤             ║
    ║                                                                  ║
    ║       "Making NixOS accessible through natural speech"          ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    
    🌟 Phase 3 Features (In Development):
    ├── Whisper speech recognition (offline)
    ├── Piper text-to-speech (natural voices)
    ├── Wake word detection ("Hey Nix")
    ├── Multi-language support
    └── Conversational context awareness
    
    """)


def show_personas():
    """Show how voice helps each persona"""
    personas = [
        ("👵 Grandma Rose (75)", "Just speak naturally, no typing needed!"),
        ("⚡ Maya (16, ADHD)", "Instant action without reading walls of text"),
        ("🦯 Alex (28, blind)", "Perfect accessibility with audio feedback"),
        ("📚 Marcus (22, dyslexic)", "No complex command memorization"),
    ]
    
    print("    👥 Key Personas Served by Voice:\n")
    for persona, benefit in personas:
        print(f"    {persona}")
        print(f"       └─ {benefit}\n")


def run_demo():
    """Run the voice interface demo"""
    show_banner()
    
    simulator = VoiceSimulator()
    
    # Demo conversation scenarios
    scenarios = [
        ("Hey Nix, install firefox", "Installing a web browser"),
        ("Hey Nix, find me a text editor", "Searching for software"),
        ("Hey Nix, update my system", "System maintenance"),
        ("Hey Nix, what packages are installed?", "Checking installed software"),
        ("Hey Nix, how do I install software?", "Getting help"),
    ]
    
    print("    🎭 DEMO MODE - Simulated Voice Interactions\n")
    print("    This shows what will happen when Whisper and Piper are connected.")
    print("    Currently these are simulated responses.\n")
    
    print("    Starting demo in 2 seconds...")
    time.sleep(2)
    
    for command, description in scenarios:
        print(f"\n{'='*70}")
        print(f"🎬 Scenario: {description}")
        print("-" * 40)
        
        # Simulate wake word detection
        if "hey nix" in command.lower():
            print("👂 Wake word detected!")
            simulator.is_listening = True
            
        # Simulate voice input
        clean_command = simulator.simulate_voice_input(command)
        
        # Show listening state
        print("    [👂 Listening...]")
        time.sleep(0.3)
        print("    [🤔 Processing...]")
        time.sleep(0.3)
        
        # Process command
        response = simulator.process_command(clean_command)
        
        # Make response speakable
        speakable_response = simulator._make_speakable(response)
        
        # Simulate voice output
        simulator.simulate_voice_output(speakable_response)
        print("    [🗣️ Speaking...]")
        
        # Pause between scenarios
        time.sleep(1)
    
    print("\n" + "="*70)
    print("\n    ✨ Demo Complete!\n")
    
    show_personas()
    
    print("""
    📊 Implementation Status (Phase 3 - 30% Complete):
    
    ✅ Completed:
    ├── Voice interface architecture
    ├── WhisperPiper class created
    ├── TUI voice widget designed
    └── Demo simulations working
    
    🚧 In Progress:
    ├── Whisper integration (needs openai-whisper)
    ├── Piper TTS setup (needs piper binary)
    ├── Microphone access configuration
    └── Wake word detection implementation
    
    📅 Next Steps:
    1. Install voice dependencies:
       poetry add openai-whisper pyttsx3 sounddevice
    2. Download Piper binary from GitHub
    3. Connect to TUI voice widget
    4. Test with real audio input/output
    5. Implement Calculus of Interruption
    
    🎯 Goal: Complete Phase 3 voice features for v1.3.0 release
    
    💡 The Impact:
    Traditional NixOS: Memorize complex commands
    Voice-Enabled: Just speak naturally!
    
    This isn't just a feature - it's accessibility for everyone!
    """)
    
    print("    🎯 Run 'poetry add openai-whisper' to start real voice integration!")
    print("    📚 See src/nix_for_humanity/voice/ for implementation details")
    print("    🤝 Join us in making technology truly accessible!\n")


if __name__ == "__main__":
    try:
        run_demo()
    except KeyboardInterrupt:
        print("\n\n    👋 Demo interrupted. Thanks for watching!")
    except Exception as e:
        print(f"\n    ❌ Error: {e}")
        print("    💡 This is a simulation demo - no real voice processing yet")