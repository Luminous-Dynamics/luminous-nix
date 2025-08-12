#!/usr/bin/env python3
"""
Simple Microphone Test
Verifies audio recording works before full pipeline test
"""

import sounddevice as sd
import numpy as np
import sys


def list_audio_devices():
    """List all available audio devices"""
    print("🎧 Available Audio Devices")
    print("="*50)
    
    devices = sd.query_devices()
    
    print("\n📥 Input Devices (Microphones):")
    for i, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            default = "🔷 DEFAULT" if i == sd.default.device[0] else ""
            print(f"  [{i}] {device['name']} ({device['max_input_channels']} ch) {default}")
    
    print("\n📤 Output Devices (Speakers):")
    for i, device in enumerate(devices):
        if device['max_output_channels'] > 0:
            default = "🔷 DEFAULT" if i == sd.default.device[1] else ""
            print(f"  [{i}] {device['name']} ({device['max_output_channels']} ch) {default}")
    
    # Show current defaults
    try:
        input_device = sd.query_devices(kind='input')
        output_device = sd.query_devices(kind='output')
        print(f"\n🎤 Default Input: {input_device['name']}")
        print(f"🔊 Default Output: {output_device['name']}")
    except:
        print("\n⚠️  Could not determine default devices")


def test_recording(duration=3):
    """Test recording from default microphone"""
    print("\n🎤 Microphone Test")
    print("="*50)
    
    sample_rate = 16000
    channels = 1
    
    print(f"Recording for {duration} seconds...")
    print("Say something clearly!")
    print("\n🔴 Recording NOW...")
    
    try:
        # Record
        recording = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=channels,
            dtype='float32'
        )
        sd.wait()
        
        print("✅ Recording complete!")
        
        # Analyze audio
        max_level = np.max(np.abs(recording))
        mean_level = np.mean(np.abs(recording))
        
        print(f"\n📊 Audio Analysis:")
        print(f"  Max level: {max_level:.4f} ({max_level*100:.1f}%)")
        print(f"  Mean level: {mean_level:.4f} ({mean_level*100:.1f}%)")
        print(f"  Samples: {len(recording)}")
        print(f"  Duration: {len(recording)/sample_rate:.2f}s")
        
        # Check if audio was captured
        if max_level < 0.001:
            print("\n❌ No audio detected!")
            print("Possible issues:")
            print("  • Microphone is muted")
            print("  • Wrong input device selected")
            print("  • Microphone permissions denied")
            print("  • Hardware not connected")
            return False
        elif max_level < 0.01:
            print("\n⚠️  Very quiet audio detected")
            print("Try:")
            print("  • Speaking louder")
            print("  • Moving closer to microphone")
            print("  • Increasing microphone volume")
            return True
        else:
            print("\n✅ Good audio level detected!")
            
            # Optional: Play back the recording
            print("\n🔊 Playing back recording...")
            try:
                sd.play(recording, sample_rate)
                sd.wait()
                print("✅ Playback complete")
            except Exception as e:
                print(f"⚠️  Could not play audio: {e}")
            
            return True
            
    except Exception as e:
        print(f"\n❌ Recording failed: {e}")
        print("\nPossible solutions:")
        print("  • Check if microphone is connected")
        print("  • Grant microphone permissions")
        print("  • Try: sudo usermod -a -G audio $USER")
        print("  • Logout and login again")
        return False


def test_realtime_monitor(duration=5):
    """Monitor microphone levels in real-time"""
    print("\n📊 Real-time Audio Monitor")
    print("="*50)
    print(f"Monitoring for {duration} seconds...")
    print("Speak to see audio levels:")
    print("")
    
    sample_rate = 16000
    block_size = 1024
    
    def audio_callback(indata, frames, time, status):
        """Called for each audio block"""
        if status:
            print(f"⚠️  {status}")
        
        level = np.sqrt(np.mean(indata**2))  # RMS level
        bars = int(level * 100)
        bar_display = "█" * min(bars, 50)
        sys.stdout.write(f"\r🎤 Level: {bar_display:<50} {level*100:.1f}%  ")
        sys.stdout.flush()
    
    try:
        with sd.InputStream(
            callback=audio_callback,
            channels=1,
            samplerate=sample_rate,
            blocksize=block_size
        ):
            sd.sleep(duration * 1000)
        
        print("\n✅ Monitoring complete")
        return True
        
    except Exception as e:
        print(f"\n❌ Monitoring failed: {e}")
        return False


def main():
    """Run microphone tests"""
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║                                                                  ║
    ║            🎤 Microphone Test Utility 🎤                        ║
    ║                                                                  ║
    ║     Verify your microphone works before voice testing           ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)
    
    # List devices
    list_audio_devices()
    
    # Test recording
    print("\n" + "="*50)
    input("Press ENTER to test recording...")
    recording_ok = test_recording(3)
    
    # Test real-time monitoring
    if recording_ok:
        print("\n" + "="*50)
        input("Press ENTER to test real-time monitoring...")
        monitoring_ok = test_realtime_monitor(5)
    else:
        monitoring_ok = False
    
    # Summary
    print("\n" + "="*50)
    print("📊 Test Summary")
    print("="*50)
    
    if recording_ok and monitoring_ok:
        print("✅ Microphone is working perfectly!")
        print("\nYou're ready to test the full voice pipeline:")
        print("  poetry run python test_voice_recording.py")
    elif recording_ok:
        print("⚠️  Basic recording works but monitoring failed")
        print("You can still proceed with voice testing")
    else:
        print("❌ Microphone is not working properly")
        print("\nTroubleshooting steps:")
        print("  1. Check physical connections")
        print("  2. Check system audio settings")
        print("  3. Verify user is in 'audio' group:")
        print("     groups | grep audio")
        print("  4. If not, add user to audio group:")
        print("     sudo usermod -a -G audio $USER")
        print("  5. Logout and login again")


if __name__ == "__main__":
    main()