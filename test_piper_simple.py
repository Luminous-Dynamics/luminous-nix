#!/usr/bin/env python3
"""
Simple Piper TTS test to verify it's working with downloaded models
"""

import subprocess
import tempfile
from pathlib import Path


def test_piper_basic():
    """Test basic Piper functionality"""
    
    print("🎤 Testing Piper TTS (Simple)")
    print("=" * 40)
    
    # Check if piper-tts is available
    result = subprocess.run(["which", "piper"], capture_output=True, text=True)
    if result.returncode != 0:
        print("❌ Piper not found in PATH")
        return False
    
    piper_path = result.stdout.strip()
    print(f"✅ Piper found at: {piper_path}")
    
    # Test with a simple text
    test_text = "Hello from Nix for Humanity. Testing voice synthesis."
    
    # Create temp output file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        output_file = tmp.name
    
    print(f"\n📝 Test text: '{test_text}'")
    print(f"📁 Output file: {output_file}")
    
    # Look for model
    model_dir = Path.home() / ".local" / "share" / "piper"
    model_file = model_dir / "en_US-amy-medium.onnx"
    
    if not model_file.exists():
        print(f"\n⚠️  Model not found at: {model_file}")
        print("   Run: ./install_piper_models.sh to download models")
        return False
    
    print(f"\n🎭 Using model: {model_file.name}")
    
    # Run Piper with the model
    try:
        process = subprocess.Popen(
            ["piper", "--model", str(model_file), "--output_file", output_file],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(input=test_text, timeout=10)
        
        if process.returncode == 0:
            # Check if file was created
            output_path = Path(output_file)
            if output_path.exists():
                file_size = output_path.stat().st_size
                print(f"\n✅ Success! Audio file created: {file_size:,} bytes")
                
                # Try to play it
                print("\n🔊 Attempting to play audio...")
                play_result = subprocess.run(
                    ["aplay", output_file],
                    capture_output=True,
                    timeout=5
                )
                if play_result.returncode == 0:
                    print("✅ Audio played successfully!")
                else:
                    print("⚠️  Could not play audio (aplay not available or no audio device)")
                
                return True
            else:
                print(f"❌ No output file created")
                if stderr:
                    print(f"   Error: {stderr[:200]}")
                return False
        else:
            print(f"❌ Piper failed with code: {process.returncode}")
            if stderr:
                print(f"   Error: {stderr[:200]}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏱️  Piper timed out (may need to download data)")
        return False
    except Exception as e:
        print(f"❌ Error running Piper: {e}")
        return False


def main():
    """Run the test"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║        🎭 Piper TTS Simple Test 🎭                          ║
║                                                              ║
║     Testing text-to-speech with downloaded models           ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    success = test_piper_basic()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 Piper TTS is working!")
        print("\nNext steps:")
        print("  1. Test with different voices")
        print("  2. Integrate with voice recording pipeline")
        print("  3. Connect to TUI")
    else:
        print("⚠️  Piper TTS needs attention")
        print("\nTroubleshooting:")
        print("  1. Check if piper-tts is installed (not piper)")
        print("  2. Run ./install_piper_models.sh to download models")
        print("  3. Check error messages above")
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())