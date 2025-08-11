#!/usr/bin/env python3
"""
Voice Interface Demo (Simplified) for Nix for Humanity

Demonstrates the voice interface concept without requiring audio libraries.

Usage:
    python demo_voice_simple.py
"""

import sys
import time
from pathlib import Path
from typing import Dict, List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from nix_for_humanity.core import NixForHumanityBackend
from nix_for_humanity.core.types import Query, Response


class VoiceSimulator:
    """Simulates voice interface interactions"""
    
    def __init__(self):
        self.core = NixForHumanityBackend()
        self.conversation_history = []
        
    def process_voice(self, spoken_text: str) -> str:
        """Process simulated voice input"""
        # Clean up the wake word
        command = spoken_text.lower().replace("hey nix,", "").strip()
        
        # Process through core
        query = Query(text=command, context={"interface": "voice"})
        response = self.core.process(query)
        
        # Format response for speech
        if response.success:
            return self._make_speakable(response.message)
        else:
            return f"I had trouble with that. {response.message}"
    
    def _make_speakable(self, text: str) -> str:
        """Convert text to more natural speech"""
        # Make technical terms more speakable
        text = text.replace("NixOS", "nix O S")
        text = text.replace("sudo", "pseudo")
        text = text.replace("nixos-rebuild", "nix O S rebuild")
        
        # Add pauses
        text = text.replace(".", ". ")
        text = text.replace(",", ", ")
        
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
    
    🌟 Revolutionary Features:
    ├── Natural language understanding
    ├── Voice activity detection  
    ├── Text-to-speech feedback
    ├── Multi-language support (coming)
    └── Perfect accessibility for all users
    
    """)


def show_personas():
    """Show how voice helps each persona"""
    personas = [
        ("👵 Grandma Rose (75)", "Just speak naturally, no typing needed!"),
        ("⚡ Maya (16, ADHD)", "Instant action without reading walls of text"),
        ("🦯 Alex (28, blind)", "Perfect accessibility with audio feedback"),
        ("📚 Marcus (22, dyslexic)", "No complex command memorization"),
        ("👩‍⚕️ Dr. Sarah (35)", "Hands-free while multitasking"),
        ("💪 Jamal (30, RSI)", "No keyboard strain on injured arm"),
        ("🌍 Amira (24, ESL)", "Natural language, not command syntax"),
        ("👓 Lee (50, presbyopia)", "No squinting at small terminal text"),
        ("⌨️ Sam (40, power user)", "Even faster than typing for common tasks"),
        ("🎓 Riley (18, student)", "Learn by conversation, not documentation"),
    ]
    
    print("    👥 How Voice Helps Our 10 Personas:\n")
    for persona, benefit in personas:
        print(f"    {persona}")
        print(f"       └─ {benefit}\n")


def run_conversation(simulator: VoiceSimulator, conversation: Dict[str, str]):
    """Run a simulated conversation"""
    print("\n" + "="*70)
    
    for speaker, text in conversation.items():
        if speaker == "scenario":
            print(f"\n📌 Scenario: {text}")
        elif speaker.startswith("user"):
            print(f"\n👤 User: \"{text}\"")
            time.sleep(0.5)
            
            # Show listening state
            print("    [👂 Listening...]")
            time.sleep(0.3)
            print("    [🤔 Processing...]")
            time.sleep(0.3)
            
            # Process and respond
            response = simulator.process_voice(text)
            print(f"\n🤖 Nix: \"{response}\"")
            print("    [🗣️ Speaking...]")
            time.sleep(0.5)
        elif speaker == "note":
            print(f"\n    💡 Note: {text}")
    
    print("\n" + "="*70)


def main():
    """Run the voice interface demo"""
    show_banner()
    
    simulator = VoiceSimulator()
    
    # Demo conversations
    conversations = [
        {
            "scenario": "Basic Package Installation",
            "user1": "Hey Nix, install Firefox",
            "note": "Notice how natural the command is - no technical syntax!"
        },
        {
            "scenario": "Searching for Software",
            "user1": "Hey Nix, find me a text editor",
            "note": "Voice makes discovery easy - just ask for what you need"
        },
        {
            "scenario": "System Maintenance",
            "user1": "Hey Nix, update my system",
            "note": "Complex operations become simple voice commands"
        },
        {
            "scenario": "Getting Help",
            "user1": "Hey Nix, how do I install software?",
            "note": "Educational responses help users learn"
        },
        {
            "scenario": "Error Recovery",
            "user1": "Hey Nix, something went wrong with my last update",
            "note": "Natural language for troubleshooting"
        }
    ]
    
    print("    🎭 DEMO MODE - Simulated Voice Interactions\n")
    print("    Imagine speaking these commands naturally...")
    print("    No typing, no memorization, just conversation!\n")
    
    input("    Press Enter to begin the demo...")
    
    for conv in conversations:
        run_conversation(simulator, conv)
        time.sleep(1)
    
    print("\n" + "="*70)
    print("\n    ✨ Demo Complete!\n")
    
    show_personas()
    
    print("""
    🚀 Implementation Roadmap:
    
    Phase 1 (This Week):
    ├── ✅ Voice interface architecture
    ├── ✅ Natural language processing integration
    ├── ⏳ Audio capture with sounddevice
    └── ⏳ Text-to-speech with pyttsx3
    
    Phase 2 (Next Week):
    ├── TUI integration with waveform display
    ├── Real-time transcription feedback
    ├── Voice activity detection
    └── Wake word detection ("Hey Nix")
    
    Phase 3 (Month 1):
    ├── Offline speech recognition (Whisper)
    ├── Multi-language support
    ├── Voice personalization
    └── Conversational context
    
    Future Vision:
    ├── Proactive assistance
    ├── Voice-driven tutorials
    ├── Accessibility profiles
    └── Community voice models
    
    """)
    
    print("""
    💡 The Impact:
    
    Traditional NixOS:
    ❌ Memorize complex commands
    ❌ Read dense documentation
    ❌ Type precise syntax
    ❌ Understand error messages
    
    Voice-Enabled NixOS:
    ✅ Speak naturally
    ✅ Get instant help
    ✅ Learn by doing
    ✅ Access for everyone
    
    This isn't just a feature - it's a revolution in
    human-computer interaction for system management!
    """)
    
    print("    🎯 Try the real thing once audio libraries are configured!")
    print("    📚 See VOICE_INTERFACE.md for technical details")
    print("    🤝 Join us in making technology truly accessible!\n")


if __name__ == "__main__":
    main()