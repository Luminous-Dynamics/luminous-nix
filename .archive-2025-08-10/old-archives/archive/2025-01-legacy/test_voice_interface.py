#!/usr/bin/env python3
"""
Test Voice Interface Components for Phase 3
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


def test_voice_components():
    """Test Phase 3 Voice Interface components"""
    print("🎤 Testing Phase 3 Voice Interface Components...")
    print("=" * 60)

    # Check what voice files we have
    voice_dir = Path("features/v2.0/voice")
    if voice_dir.exists():
        print(f"\n📁 Voice components preserved in: {voice_dir}")
        voice_files = list(voice_dir.glob("*.py"))
        print(f"   Found {len(voice_files)} Python files")

        # List key components
        key_files = [
            "voice_interface.py",
            "voice_interface_enhanced.py",
            "voice_connection.py",
            "voice_websocket_server.py",
            "voice_nlp_integration.py",
            "voice_input_grandma_rose.py",
        ]

        print("\n📋 Key Components Status:")
        for file in key_files:
            file_path = voice_dir / file
            if file_path.exists():
                print(f"   ✅ {file}")
            else:
                print(f"   ❌ {file} (missing)")
    else:
        print("❌ Voice directory not found")

    # Check if voice interface is in main src
    print("\n🔍 Checking main source tree...")
    try:
        from luminous_nix.interfaces.voice import main as voice_main

        print("   ✅ Voice interface integrated in main source")
    except ImportError:
        print("   ℹ️  Voice interface not yet integrated (expected for v2.0)")

    # Check for voice dependencies
    print("\n📦 Voice Dependencies Check:")
    try:
        import whisper

        print("   ✅ Whisper (speech-to-text) available")
    except ImportError:
        print("   ⏳ Whisper not installed (will be added in v2.0)")

    try:
        import piper

        print("   ✅ Piper (text-to-speech) available")
    except ImportError:
        print("   ⏳ Piper not installed (will be added in v2.0)")

    try:
        import pipecat

        print("   ✅ Pipecat (low-latency processing) available")
    except ImportError:
        print("   ⏳ Pipecat not installed (will be added in v2.0)")

    # Phase 3 Priorities Summary
    print("\n📊 Phase 3 Voice Interface Status:")
    print("   • Components: Preserved for v2.0 implementation")
    print("   • Architecture: WebSocket-based real-time processing")
    print("   • Personas: Grandma Rose adaptation ready")
    print("   • Integration: Planned for v2.0 release")

    print("\n💡 Next Steps for Voice Interface:")
    print("   1. Install voice dependencies (whisper, piper, pipecat)")
    print("   2. Integrate voice components into main source")
    print("   3. Test with all 10 personas")
    print("   4. Implement wake word detection")
    print("   5. Add flow state protection features")

    return True


if __name__ == "__main__":
    test_voice_components()
