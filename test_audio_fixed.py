#!/usr/bin/env python3
"""Test that PortAudio is now accessible"""

import os
import sys

print("🎤 Testing PortAudio Access")
print("=" * 40)

# Check environment
ld_path = os.environ.get('LD_LIBRARY_PATH', 'Not set')
print(f"LD_LIBRARY_PATH: {ld_path[:100]}...")

try:
    import sounddevice as sd
    print("✅ sounddevice imported successfully!")
    
    # List audio devices
    print("\n📊 Available Audio Devices:")
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        kind = "Input" if device['max_input_channels'] > 0 else "Output"
        print(f"  {i}: {device['name']} ({kind})")
    
    # Test recording capability
    print("\n🎤 Testing recording capability...")
    try:
        # Try to record 1 second of audio
        duration = 1
        fs = 44100
        print(f"  Recording {duration} second of audio...")
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
        sd.wait()
        print("✅ Recording successful!")
        print(f"  Shape: {recording.shape}")
        print(f"  Max amplitude: {abs(recording).max():.4f}")
    except Exception as e:
        print(f"⚠️  Recording failed: {e}")
        print("  This might be normal if no microphone is connected")
    
except ImportError as e:
    print(f"❌ Failed to import sounddevice: {e}")
    print("\nMake sure to install it with:")
    print("  poetry add sounddevice")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 40)
print("Test complete!")
