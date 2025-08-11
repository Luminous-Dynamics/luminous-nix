#!/usr/bin/env python3
"""
Quick microphone test script.

Tests if microphone is accessible and working.
"""

import sys
import numpy as np

try:
    import sounddevice as sd
    print("✅ sounddevice imported successfully")
except ImportError as e:
    print(f"❌ Failed to import sounddevice: {e}")
    print("   Install with: poetry add sounddevice")
    sys.exit(1)

def test_microphone():
    """Test microphone availability and functionality."""
    print("\n🎤 Testing Microphone Access")
    print("-" * 40)
    
    # List devices
    print("\nAvailable audio devices:")
    devices = sd.query_devices()
    input_devices = []
    
    for i, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            input_devices.append(i)
            is_default = " (DEFAULT)" if i == sd.default.device[0] else ""
            print(f"  [{i}] {device['name']}{is_default}")
            print(f"      Channels: {device['max_input_channels']}")
    
    if not input_devices:
        print("\n❌ No input devices found!")
        return False
    
    print(f"\nFound {len(input_devices)} input device(s)")
    
    # Test recording
    print("\n📊 Recording 2 seconds of audio...")
    duration = 2  # seconds
    sample_rate = 16000
    
    try:
        recording = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype=np.float32
        )
        sd.wait()  # Wait for recording to complete
        
        # Analyze audio
        rms = np.sqrt(np.mean(recording**2))
        max_val = np.max(np.abs(recording))
        
        print(f"\n✅ Recording complete!")
        print(f"   RMS Level: {rms:.4f}")
        print(f"   Max Level: {max_val:.4f}")
        
        if max_val < 0.001:
            print("\n⚠️  No audio detected - microphone may be muted or disconnected")
            return False
        elif rms < 0.01:
            print("\n⚠️  Very low audio level - speak louder or adjust gain")
            return True
        else:
            print("\n✅ Microphone working properly!")
            return True
            
    except Exception as e:
        print(f"\n❌ Recording failed: {e}")
        return False

if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║              🎤 Microphone Test for Voice Interface           ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
    """)
    
    success = test_microphone()
    
    if success:
        print("\n🎉 Microphone test passed! Ready for voice interface.")
    else:
        print("\n❌ Microphone test failed. Please check:")
        print("   1. Microphone is connected")
        print("   2. Microphone permissions are granted")
        print("   3. Audio input is not muted")
    
    sys.exit(0 if success else 1)