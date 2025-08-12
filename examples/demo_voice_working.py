#!/usr/bin/env python3
"""
Voice Interface Demo - Working Version

Shows the revolutionary voice interface concept for Nix for Humanity.
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from nix_for_humanity.core import NixForHumanityBackend, IntentType


def show_banner():
    """Display welcome banner"""
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║                                                                ║
    ║      🎤 Voice Interface for Nix for Humanity 🎤               ║
    ║                                                                ║
    ║      "Making NixOS accessible through natural speech"         ║  
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
    
    Revolutionary Features:
    ✨ Natural language understanding
    🎯 Voice activity detection
    🔊 Text-to-speech feedback
    ♿ Perfect accessibility
    
    """)


def simulate_voice_interaction(text: str, backend: NixForHumanityBackend):
    """Simulate processing voice command"""
    print(f"👤 User: \"{text}\"")
    print("    [👂 Listening...]")
    time.sleep(0.3)
    print("    [🤔 Processing...]")
    time.sleep(0.3)
    
    # Process through backend
    response = backend.process_query(text)
    
    print(f"\n🤖 Nix: \"{response.message}\"")
    print("    [🗣️ Speaking...]")
    time.sleep(0.5)
    return response


def main():
    """Run the voice interface demo"""
    show_banner()
    
    backend = NixForHumanityBackend()
    
    print("🎭 DEMO MODE - Simulated Voice Interactions\n")
    
    # Demo scenarios
    scenarios = [
        ("Basic Installation", "Hey Nix, install Firefox"),
        ("Package Search", "Hey Nix, find me a text editor"),
        ("System Update", "Hey Nix, update my system"),
        ("Getting Help", "Hey Nix, how do I install packages?"),
        ("System Rollback", "Hey Nix, roll back to yesterday"),
    ]
    
    print("Starting demo in 1 second...")
    time.sleep(1)
    
    for title, command in scenarios:
        print("\n" + "="*60)
        print(f"📌 Scenario: {title}")
        print("="*60 + "\n")
        
        simulate_voice_interaction(command, backend)
        time.sleep(1)
    
    print("\n" + "="*60)
    print("\n✨ Demo Complete!\n")
    
    print("""
    👥 How Voice Helps Our 10 Personas:
    
    👵 Grandma Rose (75) - Just speak naturally!
    ⚡ Maya (16, ADHD) - Instant action, no reading
    🦯 Alex (28, blind) - Perfect audio accessibility
    📚 Marcus (22, dyslexic) - No command memorization
    👩‍⚕️ Dr. Sarah (35) - Hands-free operation
    💪 Jamal (30, RSI) - No keyboard strain
    🌍 Amira (24, ESL) - Natural language, not syntax
    👓 Lee (50) - No squinting at terminals
    ⌨️ Sam (40) - Faster than typing
    🎓 Riley (18) - Learn by conversation
    
    🚀 Implementation Status:
    
    ✅ Voice interface architecture designed
    ✅ Natural language processing integrated
    ✅ Demo created and working
    ⏳ Audio libraries integration pending
    ⏳ TUI waveform visualization pending
    
    This is the future of system management!
    """)


if __name__ == "__main__":
    main()