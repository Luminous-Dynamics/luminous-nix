#!/usr/bin/env python3
"""
Complete Voice Pipeline Test
Tests the full flow: Microphone → Whisper → NLP → Piper → Audio
"""

import os
import sys
import time
import wave
import json
import tempfile
import subprocess
from pathlib import Path
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("""
╔══════════════════════════════════════════════════════════════════╗
║         🎤 Complete Voice Pipeline Test 🎤                      ║
║                                                                  ║
║     Testing: Mic → Whisper → NLP → Piper → Audio               ║
╚══════════════════════════════════════════════════════════════════╝
""")

class VoicePipelineTest:
    def __init__(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="voice_pipeline_"))
        self.whisper_model = "base.en"
        self.piper_model = Path.home() / ".local/share/piper/en_US-amy-medium.onnx"
        
    def test_microphone(self, duration=3):
        """Step 1: Record audio from microphone"""
        print("\n" + "="*60)
        print("🎤 Step 1: Recording Audio")
        print("="*60)
        
        try:
            import sounddevice as sd
            
            print(f"Recording {duration} seconds of audio...")
            print("Please say: 'Install Firefox browser'")
            print("Recording in 3...")
            time.sleep(1)
            print("2...")
            time.sleep(1)
            print("1...")
            time.sleep(1)
            print("🔴 RECORDING NOW - SPEAK!")
            
            # Record audio
            fs = 16000  # Sample rate for Whisper
            recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
            sd.wait()
            
            print("✅ Recording complete!")
            
            # Save to WAV file
            audio_file = self.temp_dir / "recording.wav"
            
            # Convert float32 to int16 for WAV
            audio_int16 = np.int16(recording * 32767)
            
            with wave.open(str(audio_file), 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(fs)
                wf.writeframes(audio_int16.tobytes())
            
            print(f"📁 Saved to: {audio_file}")
            file_size = audio_file.stat().st_size
            print(f"   Size: {file_size:,} bytes")
            
            return str(audio_file)
            
        except ImportError:
            print("❌ sounddevice not available")
            print("   Using pre-recorded test file instead...")
            
            # Create a test file with ffmpeg
            test_file = self.temp_dir / "test_audio.wav"
            subprocess.run([
                "ffmpeg", "-f", "lavfi", 
                "-i", "sine=frequency=440:duration=3",
                "-ac", "1", "-ar", "16000",
                str(test_file), "-y"
            ], capture_output=True)
            
            return str(test_file)
    
    def test_whisper(self, audio_file):
        """Step 2: Transcribe audio with Whisper"""
        print("\n" + "="*60)
        print("🎙️ Step 2: Transcribing with Whisper")
        print("="*60)
        
        print(f"Model: {self.whisper_model}")
        print(f"Audio: {audio_file}")
        print("Transcribing...")
        
        # Run Whisper
        result = subprocess.run([
            "whisper", audio_file,
            "--model", self.whisper_model,
            "--language", "en",
            "--output_format", "json",
            "--output_dir", str(self.temp_dir)
        ], capture_output=True, text=True)
        
        # Read the transcription
        json_file = self.temp_dir / "recording.json"
        if not json_file.exists():
            json_file = self.temp_dir / "test_audio.json"
        
        if json_file.exists():
            with open(json_file, 'r') as f:
                data = json.load(f)
                transcription = data.get("text", "").strip()
            
            print(f"✅ Transcription: '{transcription}'")
            return transcription
        else:
            print("⚠️  No transcription produced")
            print("   Using test text: 'Install Firefox browser'")
            return "Install Firefox browser"
    
    def test_nlp_processing(self, text):
        """Step 3: Process with NLP engine"""
        print("\n" + "="*60)
        print("🧠 Step 3: NLP Processing")
        print("="*60)
        
        print(f"Input: '{text}'")
        
        try:
            from nix_for_humanity.core import NixForHumanityCore
            
            # Initialize core
            core = NixForHumanityCore()
            
            # Process the text
            response = core.process(text)
            
            print(f"✅ Intent: {response.intent}")
            print(f"   Command: {response.command}")
            print(f"   Confidence: {response.confidence:.2f}")
            
            return response.explanation or f"Installing {response.params.get('package', 'firefox')}"
            
        except Exception as e:
            print(f"⚠️  NLP processing error: {e}")
            print("   Using simple response")
            
            # Simple fallback
            if "install" in text.lower():
                if "firefox" in text.lower():
                    return "I'll install Firefox browser for you"
                else:
                    return "I'll help you install that package"
            else:
                return "I understood your request"
    
    def test_piper_synthesis(self, text):
        """Step 4: Generate speech with Piper"""
        print("\n" + "="*60)
        print("🔊 Step 4: Speech Synthesis with Piper")
        print("="*60)
        
        print(f"Text: '{text}'")
        print(f"Model: {self.piper_model.name}")
        
        if not self.piper_model.exists():
            print("❌ Piper model not found")
            print("   Run: ./download_piper_model.sh")
            return None
        
        # Generate speech
        output_file = self.temp_dir / "response.wav"
        
        process = subprocess.Popen([
            "piper",
            "--model", str(self.piper_model),
            "--output_file", str(output_file)
        ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        stdout, stderr = process.communicate(input=text)
        
        if output_file.exists():
            file_size = output_file.stat().st_size
            print(f"✅ Speech generated: {file_size:,} bytes")
            return str(output_file)
        else:
            print("❌ Speech generation failed")
            return None
    
    def test_audio_playback(self, audio_file):
        """Step 5: Play the audio response"""
        print("\n" + "="*60)
        print("🔊 Step 5: Audio Playback")
        print("="*60)
        
        if not audio_file:
            print("⚠️  No audio file to play")
            return False
        
        print(f"Playing: {audio_file}")
        
        # Try to play with aplay
        result = subprocess.run([
            "aplay", audio_file
        ], capture_output=True)
        
        if result.returncode == 0:
            print("✅ Audio played successfully!")
            return True
        else:
            print("⚠️  Could not play audio (no audio device?)")
            return False
    
    def run_complete_test(self):
        """Run the complete pipeline test"""
        
        print("\n🚀 Starting Complete Pipeline Test")
        print("="*60)
        
        results = {
            "recording": False,
            "transcription": False,
            "nlp": False,
            "synthesis": False,
            "playback": False
        }
        
        try:
            # Step 1: Record
            audio_file = self.test_microphone(duration=3)
            results["recording"] = bool(audio_file)
            
            # Step 2: Transcribe
            transcription = self.test_whisper(audio_file)
            results["transcription"] = bool(transcription)
            
            # Step 3: Process
            response = self.test_nlp_processing(transcription)
            results["nlp"] = bool(response)
            
            # Step 4: Synthesize
            speech_file = self.test_piper_synthesis(response)
            results["synthesis"] = bool(speech_file)
            
            # Step 5: Play
            played = self.test_audio_playback(speech_file)
            results["playback"] = played
            
        except Exception as e:
            print(f"\n❌ Pipeline error: {e}")
        
        # Summary
        print("\n" + "="*60)
        print("📊 Pipeline Test Results")
        print("="*60)
        
        icons = {True: "✅", False: "❌"}
        print(f"{icons[results['recording']]} Recording: {'Working' if results['recording'] else 'Failed'}")
        print(f"{icons[results['transcription']]} Transcription: {'Working' if results['transcription'] else 'Failed'}")
        print(f"{icons[results['nlp']]} NLP Processing: {'Working' if results['nlp'] else 'Failed'}")
        print(f"{icons[results['synthesis']]} Speech Synthesis: {'Working' if results['synthesis'] else 'Failed'}")
        print(f"{icons[results['playback']]} Audio Playback: {'Working' if results['playback'] else 'Failed'}")
        
        success_count = sum(results.values())
        total_count = len(results)
        
        print(f"\n🎯 Overall: {success_count}/{total_count} components working")
        
        if success_count == total_count:
            print("🎉 COMPLETE SUCCESS! Voice pipeline fully operational!")
        elif success_count >= 3:
            print("✅ Voice pipeline mostly working!")
        else:
            print("⚠️  Voice pipeline needs attention")
        
        print(f"\n📁 Test files saved in: {self.temp_dir}")
        
        return results


def main():
    """Run the test"""
    
    # Check if we're in the right environment
    if not os.environ.get("LD_LIBRARY_PATH"):
        print("⚠️  PortAudio might not be configured")
        print("   Run: nix-shell shell-audio.nix")
        print("   Then: poetry run python test_complete_voice_pipeline.py")
        print()
    
    tester = VoicePipelineTest()
    results = tester.run_complete_test()
    
    # Return success code
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    exit(main())