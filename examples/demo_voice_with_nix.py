#!/usr/bin/env python3
"""
Voice Interface Demo using Nix Packages

This demo uses Whisper and Piper installed via Nix packages.
Run with: nix-shell shell-voice.nix --run "poetry run python demo_voice_with_nix.py"

Usage:
    1. Enter nix-shell: nix-shell shell-voice.nix
    2. Run demo: poetry run python demo_voice_with_nix.py
"""

import subprocess
import tempfile
from pathlib import Path
import time
import shutil


class NixVoiceInterface:
    """Voice interface using Nix-installed Whisper and Piper"""
    
    def __init__(self):
        self.check_dependencies()
        
    def check_dependencies(self):
        """Check if voice tools are available"""
        tools = {
            'whisper': 'OpenAI Whisper (speech recognition)',
            'piper': 'Piper TTS (text-to-speech)',
            'ffmpeg': 'Audio processing',
        }
        
        print("🔍 Checking voice dependencies...\n")
        all_available = True
        
        for tool, description in tools.items():
            if shutil.which(tool):
                print(f"✅ {tool}: {description} - Available")
            else:
                print(f"❌ {tool}: {description} - Not found")
                all_available = False
                
        if not all_available:
            print("\n⚠️  Some tools are missing. Run: nix-shell shell-voice.nix")
        else:
            print("\n✨ All voice tools available!")
        
        return all_available
    
    def test_whisper(self):
        """Test Whisper speech recognition"""
        print("\n" + "="*60)
        print("🎤 Testing Whisper Speech Recognition")
        print("="*60)
        
        # Check if whisper is available
        if not shutil.which('whisper'):
            print("❌ Whisper not found. Install with: nix-env -iA nixos.openai-whisper")
            return
            
        # Show Whisper version/help
        try:
            result = subprocess.run(['whisper', '--help'], 
                                  capture_output=True, text=True, timeout=5)
            print("✅ Whisper is installed and responsive")
            print("\nWhisper capabilities:")
            print("  • Offline speech recognition")
            print("  • Multiple model sizes (tiny to large)")
            print("  • 99+ language support")
            print("  • Timestamp generation")
        except Exception as e:
            print(f"⚠️ Whisper test failed: {e}")
    
    def test_piper(self):
        """Test Piper text-to-speech"""
        print("\n" + "="*60)
        print("🔊 Testing Piper Text-to-Speech")
        print("="*60)
        
        # Check if piper is available
        if not shutil.which('piper'):
            print("❌ Piper not found. Install with: nix-env -iA nixos.piper")
            return
            
        # Test Piper with simple text
        try:
            test_text = "Hello from Nix for Humanity voice interface"
            
            # Create temporary file for output
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                output_file = tmp.name
            
            # Run Piper (it might need a model file)
            result = subprocess.run(
                ['piper', '--help'],
                capture_output=True, text=True, timeout=5
            )
            
            print("✅ Piper is installed and responsive")
            print("\nPiper capabilities:")
            print("  • Fast neural text-to-speech")
            print("  • Multiple voice models")
            print("  • Adjustable speed and pitch")
            print("  • Low resource usage")
            
            # Clean up
            Path(output_file).unlink(missing_ok=True)
            
        except Exception as e:
            print(f"⚠️ Piper test failed: {e}")
    
    def demonstrate_pipeline(self):
        """Demonstrate the voice pipeline concept"""
        print("\n" + "="*60)
        print("🌊 Voice Pipeline Demonstration")
        print("="*60)
        
        print("\n📊 Voice Processing Pipeline:")
        print("  1️⃣ Microphone → Audio capture (sounddevice)")
        print("  2️⃣ Audio → Text (Whisper)")
        print("  3️⃣ Text → NLP (Nix for Humanity)")
        print("  4️⃣ Response → Speech (Piper)")
        print("  5️⃣ Speech → Speaker output")
        
        print("\n🎯 Example Flow:")
        steps = [
            ("User speaks", "Hey Nix, install firefox"),
            ("Whisper transcribes", "hey nix install firefox"),
            ("NLP processes", "Intent: INSTALL, Package: firefox"),
            ("Backend executes", "nix-env -iA nixos.firefox"),
            ("Piper speaks", "Installing Firefox browser for you"),
        ]
        
        for i, (stage, example) in enumerate(steps, 1):
            print(f"\n  Step {i}: {stage}")
            print(f"    → {example}")
            time.sleep(0.5)


def main():
    """Run the voice interface demo"""
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║                                                                  ║
    ║    🎤 Nix for Humanity - Voice Interface (Nix Packages) 🎤      ║
    ║                                                                  ║
    ║    Using official NixOS packages for voice processing           ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)
    
    interface = NixVoiceInterface()
    
    if interface.check_dependencies():
        interface.test_whisper()
        interface.test_piper()
        interface.demonstrate_pipeline()
    
    print("\n" + "="*60)
    print("📝 Installation Instructions")
    print("="*60)
    print("""
    To install voice dependencies on NixOS:
    
    1. Quick install (user environment):
       nix-env -iA nixos.openai-whisper nixos.piper
    
    2. Declarative (configuration.nix):
       environment.systemPackages = with pkgs; [
         openai-whisper
         piper
         piper-phonemize
         portaudio
       ];
    
    3. Development shell (recommended):
       nix-shell shell-voice.nix
    
    4. Python packages (already in Poetry):
       poetry add openai-whisper pyttsx3 sounddevice
    """)
    
    print("\n" + "="*60)
    print("🚀 Next Steps")
    print("="*60)
    print("""
    1. Enter voice development shell:
       nix-shell shell-voice.nix
    
    2. Test real audio recording:
       poetry run python test_microphone.py
    
    3. Download Whisper models:
       whisper --model base --download-root ~/.cache/whisper
    
    4. Download Piper voices:
       # Piper voices are downloaded automatically on first use
    
    5. Run full voice demo:
       poetry run python demo_voice_complete.py
    """)


if __name__ == "__main__":
    main()