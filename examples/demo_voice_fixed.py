#!/usr/bin/env python3
"""
Fixed Voice Interface Demo for Nix for Humanity

This demo shows what the voice interface would do if fully implemented.
Currently simulates voice input/output since Whisper/Piper aren't fully connected.

Usage:
    poetry run python demo_voice_fixed.py
"""

import sys
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from nix_for_humanity.core.backend import NixForHumanityBackend


class VoiceInterfaceDemo:
    """Demonstrates voice interface capabilities"""
    
    def __init__(self):
        print("🎤 Initializing voice interface...")
        self.backend = NixForHumanityBackend()
        self.is_listening = False
        print("✅ Voice interface ready!")
        
    def simulate_voice_input(self, text: str) -> str:
        """Simulate hearing voice input"""
        print(f"\n🔊 User says: '{text}'")
        return text.lower().replace("hey nix, ", "").replace("hey nix ", "")
        
    def simulate_voice_output(self, text: str):
        """Simulate speaking response"""
        print(f"🤖 Nix responds: {text}")
        # Simulate TTS delay
        time.sleep(0.5)
        
    def process_command(self, command: str):
        """Process voice command through backend"""
        print(f"💭 Processing: '{command}'")
        
        # Process through backend
        from nix_for_humanity.core.intents import Intent, IntentType
        
        # Create appropriate intent based on command
        if "install" in command:
            intent = Intent(
                type=IntentType.INSTALL_PACKAGE,
                entities={"package": command.replace("install ", "")},
                confidence=0.9,
                raw_text=command
            )
        elif "search" in command:
            intent = Intent(
                type=IntentType.SEARCH_PACKAGE,  # Fixed: was SEARCH_PACKAGES
                entities={"query": command.replace("search for ", "")},
                confidence=0.9,
                raw_text=command
            )
        elif "what" in command and "installed" in command:
            intent = Intent(
                type=IntentType.LIST_INSTALLED,
                entities={},
                confidence=0.95,
                raw_text=command
            )
        else:
            intent = Intent(
                type=IntentType.UNKNOWN,
                entities={"raw_text": command},
                confidence=0.3,
                raw_text=command
            )
            
        # Get response from backend
        # The backend.process method expects an Intent directly
        response = self.backend.process(intent)
        
        # Make response more voice-friendly
        if hasattr(response, 'message'):
            voice_response = self._make_speakable(response.message)
        elif hasattr(response, 'summary'):
            voice_response = self._make_speakable(response.summary)
        elif isinstance(response, str):
            voice_response = self._make_speakable(response)
        else:
            voice_response = "I processed your request successfully."
        return voice_response
        
    def _make_speakable(self, text: str) -> str:
        """Convert technical text to natural speech"""
        text = text.replace("NixOS", "nix O S")
        text = text.replace("sudo", "pseudo")
        text = text.replace("nixos-rebuild", "nix O S rebuild")
        text = text.replace("nix-env", "nix env")
        # Simplify command output for voice
        if "Would execute:" in text:
            text = text.replace("Would execute:", "I would run:")
        return text
        
    def run_demo(self):
        """Run the interactive voice demo"""
        print("\n" + "="*60)
        print("🎙️  NIX FOR HUMANITY - VOICE INTERFACE DEMO")
        print("="*60)
        print("\nThis demo simulates what the voice interface will do")
        print("when Whisper (speech recognition) and Piper (text-to-speech)")
        print("are fully integrated.\n")
        
        # Demo conversation scenarios
        scenarios = [
            ("Hey Nix, install firefox", "Installing a web browser"),
            ("Hey Nix, search for text editors", "Finding packages by description"),
            ("Hey Nix, what packages are installed?", "Listing installed packages"),
            ("Hey Nix, how do I update my system?", "System maintenance help"),
        ]
        
        print("📝 Demo Scenarios:")
        for i, (command, desc) in enumerate(scenarios, 1):
            print(f"  {i}. {desc}")
            
        print("\n" + "-"*60)
        
        for command, description in scenarios:
            print(f"\n🎬 Scenario: {description}")
            print("-" * 40)
            
            # Simulate wake word detection
            if "hey nix" in command.lower():
                print("👂 Wake word detected!")
                self.is_listening = True
                
            # Simulate voice input
            clean_command = self.simulate_voice_input(command)
            
            # Process command
            response = self.process_command(clean_command)
            
            # Simulate voice output
            self.simulate_voice_output(response)
            
            # Pause between scenarios
            time.sleep(1)
            
        print("\n" + "="*60)
        print("✨ Demo Complete!")
        print("\n📋 Current Status:")
        print("  ✅ Voice architecture designed")
        print("  ✅ WhisperPiper class created")
        print("  ✅ TUI voice widget ready")
        print("  🚧 Whisper integration pending")
        print("  🚧 Piper TTS setup needed")
        print("  🚧 Microphone access configuration")
        
        print("\n🎯 Next Steps:")
        print("  1. Install openai-whisper: poetry add openai-whisper")
        print("  2. Set up Piper TTS binary")
        print("  3. Configure audio device access")
        print("  4. Connect to TUI voice widget")
        print("  5. Test with real audio input/output")


def main():
    """Run the voice demo"""
    try:
        demo = VoiceInterfaceDemo()
        demo.run_demo()
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\n💡 Make sure to run with: poetry run python demo_voice_fixed.py")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Check that all dependencies are installed")


if __name__ == "__main__":
    main()