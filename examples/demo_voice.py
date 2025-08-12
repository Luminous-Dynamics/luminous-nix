#!/usr/bin/env python3
"""
Voice Interface Demo for Nix for Humanity

Run this to experience the revolutionary voice control for NixOS!

Usage:
    python demo_voice.py          # Interactive demo
    python demo_voice.py --test   # Test without microphone
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from nix_for_humanity.interfaces.voice_interface import (
    VoiceInterface,
    VoiceConfig,
    VoiceState,
    create_voice_interface
)
from nix_for_humanity.core import Response


def print_banner():
    """Print welcome banner"""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║     🎤 Nix for Humanity - Voice Interface Demo 🎤           ║
    ║                                                              ║
    ║     "Making NixOS accessible through natural speech"        ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    
    Revolutionary Features:
    ✨ Natural language understanding
    🎯 Voice activity detection  
    🔊 Text-to-speech feedback
    🌍 Multi-language ready
    ♿ Perfect accessibility
    
    """)


def demo_without_mic():
    """Demo mode without microphone (simulated)"""
    print("🎭 DEMO MODE - Simulating voice interactions\n")
    
    # Create interface
    interface = create_voice_interface()
    
    # Simulated conversations
    conversations = [
        {
            "user": "Hey Nix, install Firefox",
            "nix": "I'll help you install Firefox. This will add Firefox to your system configuration. Should I proceed?",
            "user": "Yes, go ahead",
            "nix": "Installing Firefox... Done! Firefox has been added to your configuration. Run 'sudo nixos-rebuild switch' to apply.",
        },
        {
            "user": "Hey Nix, what packages do I have installed?",
            "nix": "I'll list your installed packages. You have 247 packages installed including: firefox, vim, git, python3, nodejs, and many system packages.",
        },
        {
            "user": "Hey Nix, search for text editors",
            "nix": "I found several text editors: vim, neovim, emacs, nano, vscode, sublime-text, atom, and helix. Would you like to install any of these?",
        },
        {
            "user": "Hey Nix, update my system",
            "nix": "I'll update your NixOS system. This will download the latest packages and configurations. The update will: Update 23 packages, Add 2 new dependencies, and Remove 1 obsolete package. Proceed?",
        },
        {
            "user": "Hey Nix, roll back to yesterday",
            "nix": "I'll roll back your system to generation 42 from yesterday at 3:47 PM. This will undo today's Firefox installation and package updates. Confirm rollback?",
        }
    ]
    
    # State change callback
    def on_state_change(state: VoiceState):
        state_icons = {
            VoiceState.IDLE: "😴",
            VoiceState.LISTENING: "👂",
            VoiceState.PROCESSING: "🤔",
            VoiceState.SPEAKING: "🗣️",
            VoiceState.ERROR: "❌",
        }
        print(f"\n[State: {state_icons.get(state, '?')} {state.value}]")
    
    interface.on_state_change = on_state_change
    
    # Run through conversations
    for i, conv in enumerate(conversations, 1):
        print(f"\n{'='*60}")
        print(f"Conversation {i}:")
        print(f"{'='*60}")
        
        for j in range(0, len(conv), 2):
            user_says = conv.get(f"user", None) if j == 0 else list(conv.values())[j]
            nix_says = list(conv.values())[j + 1]
            
            # Simulate user speaking
            print(f"\n👤 User: \"{user_says}\"")
            interface._update_state(VoiceState.LISTENING)
            
            # Simulate processing
            interface._update_state(VoiceState.PROCESSING)
            
            # Simulate Nix response
            interface._update_state(VoiceState.SPEAKING)
            print(f"\n🤖 Nix: \"{nix_says}\"")
            
            interface._update_state(VoiceState.IDLE)
            
            # Pause for effect
            import time
            time.sleep(1)
    
    print(f"\n{'='*60}")
    print("✨ Demo Complete!")
    print(f"{'='*60}\n")
    
    print("""
    Imagine this with real voice:
    - Just speak naturally
    - No typing required
    - Instant feedback
    - Works for everyone
    
    This is the future of system management!
    """)


def demo_with_mic():
    """Interactive demo with microphone"""
    print("🎤 INTERACTIVE MODE - Using your microphone\n")
    
    # Create interface
    interface = create_voice_interface()
    
    # Test audio
    print("Testing audio systems...")
    if not interface.test_audio():
        print("⚠️ Audio test failed. Please check your microphone and speakers.")
        print("Falling back to demo mode...")
        demo_without_mic()
        return
    
    print("✅ Audio systems working!\n")
    
    # Instructions
    print("""
    Instructions:
    1. Say "Hey Nix" followed by your command
    2. Examples:
       - "Hey Nix, install Firefox"
       - "Hey Nix, search for editors"
       - "Hey Nix, update my system"
       - "Hey Nix, what can you do?"
    3. Say "exit" to quit
    
    Listening... (Ctrl+C to stop)
    """)
    
    # State display
    def on_state_change(state: VoiceState):
        states = {
            VoiceState.IDLE: "😴 Ready",
            VoiceState.LISTENING: "👂 Listening...",
            VoiceState.PROCESSING: "🤔 Processing...",
            VoiceState.SPEAKING: "🗣️ Speaking...",
            VoiceState.ERROR: "❌ Error",
        }
        print(f"\r{states.get(state, '?')}", end="", flush=True)
    
    def on_transcription(text: str):
        print(f"\n📝 Heard: \"{text}\"")
    
    def on_response(response: Response):
        if response.success:
            print(f"✅ {response.message}")
        else:
            print(f"❌ {response.message}")
    
    interface.on_state_change = on_state_change
    interface.on_transcription = on_transcription
    interface.on_response = on_response
    
    # Run continuous listening
    try:
        asyncio.run(interface.start_continuous_listening())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    finally:
        interface.stop()


def main():
    """Main entry point"""
    print_banner()
    
    # Check for demo mode
    if "--test" in sys.argv or "--demo" in sys.argv:
        demo_without_mic()
    else:
        try:
            # Try interactive mode
            demo_with_mic()
        except Exception as e:
            print(f"\n⚠️ Interactive mode failed: {e}")
            print("Running demo mode instead...\n")
            demo_without_mic()
    
    print("""
    🚀 Next Steps:
    
    1. Integration with TUI for visual feedback
    2. Waveform visualization
    3. Multi-language support
    4. Voice training for personalization
    5. Offline speech recognition
    
    This is just the beginning!
    """)


if __name__ == "__main__":
    main()