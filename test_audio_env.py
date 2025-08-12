#!/usr/bin/env python3
"""
Test audio environment setup - verifies PortAudio is accessible
"""

import sys
import os

print("🎤 Audio Environment Test")
print("=" * 50)

# Check environment variables
print("\n📊 Environment Variables:")
print(f"LD_LIBRARY_PATH: {os.environ.get('LD_LIBRARY_PATH', 'Not set')[:100]}")
print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')[:100]}")

# Try different import methods
print("\n🔍 Testing Audio Libraries:")

# Test 1: sounddevice (preferred)
try:
    import sounddevice as sd
    print("✅ sounddevice imported successfully!")
    devices = sd.query_devices()
    print(f"   Found {len(devices)} audio devices")
    
    # Show first few devices
    for i, device in enumerate(devices[:3]):
        print(f"   {i}: {device['name'][:30]}")
    
    # Test recording capability
    print("\n🎤 Testing Recording:")
    try:
        # Record 0.1 seconds of silence to test
        recording = sd.rec(int(0.1 * 44100), samplerate=44100, channels=1, dtype='float32')
        sd.wait()
        print("✅ Recording capability confirmed!")
    except Exception as e:
        print(f"⚠️  Recording test failed: {e}")
        
except ImportError as e:
    print(f"❌ sounddevice import failed: {e}")
    print("   This is the main library we need to fix")

# Test 2: pyaudio (alternative)
try:
    import pyaudio
    print("\n✅ pyaudio imported successfully!")
    p = pyaudio.PyAudio()
    print(f"   Found {p.get_device_count()} devices via PyAudio")
    p.terminate()
except ImportError as e:
    print(f"\n⚠️  pyaudio not available: {e}")

# Test 3: Check if we can access PortAudio directly
print("\n🔍 Checking PortAudio library:")
try:
    import ctypes
    import ctypes.util
    
    # Try to find PortAudio library
    portaudio_lib = ctypes.util.find_library('portaudio')
    if portaudio_lib:
        print(f"✅ Found PortAudio library: {portaudio_lib}")
        # Try to load it
        lib = ctypes.CDLL(portaudio_lib)
        print("✅ Successfully loaded PortAudio library!")
    else:
        print("❌ Could not find PortAudio library via ctypes")
        
        # Try manual paths
        possible_paths = [
            "/nix/store/fhg78y7g4jikh01acs0bdb8qw9vvn1vm-portaudio-190700_20210406/lib/libportaudio.so",
            "/usr/lib/libportaudio.so",
            "/usr/local/lib/libportaudio.so",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                print(f"   Found at: {path}")
                try:
                    lib = ctypes.CDLL(path)
                    print(f"   ✅ Loaded from: {path}")
                    break
                except Exception as e:
                    print(f"   ❌ Failed to load: {e}")
                    
except Exception as e:
    print(f"❌ Error checking PortAudio: {e}")

print("\n" + "=" * 50)
print("📋 Summary:")

# Provide diagnosis
if 'sd' in locals():
    print("✅ Audio environment is WORKING!")
    print("   You can now use voice recording features")
else:
    print("❌ Audio environment needs configuration")
    print("\n📝 To fix:")
    print("1. Run: nix-shell shell-audio.nix")
    print("2. Or: export LD_LIBRARY_PATH=/path/to/portaudio/lib:$LD_LIBRARY_PATH")
    print("3. Then: poetry run python this_script.py")