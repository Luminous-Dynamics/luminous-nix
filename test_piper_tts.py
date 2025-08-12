#!/usr/bin/env python3
"""
Professional Piper TTS Test Suite
Validates text-to-speech functionality after installation
"""

import subprocess
import tempfile
import wave
import json
from pathlib import Path
from datetime import datetime


class PiperTTSValidator:
    """Professional validation of Piper TTS installation and functionality"""
    
    def __init__(self):
        self.piper_cmd = "piper"
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "overall_status": "pending"
        }
        self.temp_dir = Path(tempfile.mkdtemp(prefix="piper_test_"))
    
    def check_installation(self):
        """Verify Piper TTS is installed correctly"""
        print("\n" + "="*60)
        print("🔍 Installation Check")
        print("="*60)
        
        try:
            # Check if piper command exists
            result = subprocess.run(
                ["which", self.piper_cmd],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                piper_path = result.stdout.strip()
                print(f"✅ Piper found at: {piper_path}")
                
                # Get version
                version_result = subprocess.run(
                    [self.piper_cmd, "--version"],
                    capture_output=True,
                    text=True
                )
                
                version = version_result.stdout.strip() or version_result.stderr.strip()
                print(f"📌 Version: {version}")
                
                self.test_results["tests"]["installation"] = {
                    "status": "passed",
                    "path": piper_path,
                    "version": version
                }
                return True
            else:
                print("❌ Piper command not found in PATH")
                self.test_results["tests"]["installation"] = {
                    "status": "failed",
                    "error": "Command not found"
                }
                return False
                
        except Exception as e:
            print(f"❌ Installation check failed: {e}")
            self.test_results["tests"]["installation"] = {
                "status": "error",
                "error": str(e)
            }
            return False
    
    def check_models(self):
        """Check for available voice models"""
        print("\n" + "="*60)
        print("🎭 Voice Models Check")
        print("="*60)
        
        # Piper needs models to be downloaded separately
        # Check common model locations
        model_dirs = [
            Path.home() / ".local" / "share" / "piper",
            Path("/usr/share/piper-voices"),
            Path("/var/lib/piper-voices"),
            self.temp_dir / "models"
        ]
        
        found_models = []
        for model_dir in model_dirs:
            if model_dir.exists():
                onnx_files = list(model_dir.glob("**/*.onnx"))
                if onnx_files:
                    print(f"📁 Found models in: {model_dir}")
                    for model in onnx_files[:3]:  # Show first 3
                        print(f"   • {model.name}")
                        found_models.append(str(model))
        
        if not found_models:
            print("⚠️  No voice models found locally")
            print("\n📥 To download models:")
            print("   1. Visit: https://github.com/rhasspy/piper/releases")
            print("   2. Download a voice model (e.g., en_US-amy-medium.onnx)")
            print("   3. Save to: ~/.local/share/piper/")
            
            self.test_results["tests"]["models"] = {
                "status": "warning",
                "message": "No models found, download required"
            }
            return False
        else:
            print(f"\n✅ Found {len(found_models)} voice model(s)")
            self.test_results["tests"]["models"] = {
                "status": "passed",
                "count": len(found_models),
                "models": found_models[:5]  # First 5 for report
            }
            return True
    
    def test_basic_synthesis(self):
        """Test basic text-to-speech synthesis"""
        print("\n" + "="*60)
        print("🔊 Basic Synthesis Test")
        print("="*60)
        
        test_text = "Hello from Nix for Humanity. Voice interface is operational."
        output_file = self.temp_dir / "test_output.wav"
        
        print(f"📝 Test text: '{test_text}'")
        print(f"📁 Output: {output_file}")
        
        # Since we might not have models, test with stdin/stdout
        try:
            # Test basic command structure
            process = subprocess.Popen(
                [self.piper_cmd, "-f", str(output_file)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input=test_text, timeout=5)
            
            if "Error" in stderr or "model" in stderr.lower():
                print("⚠️  No model available for synthesis")
                print(f"   Error: {stderr[:200]}")
                
                self.test_results["tests"]["synthesis"] = {
                    "status": "skipped",
                    "reason": "No model available"
                }
                return False
            
            if output_file.exists():
                # Analyze the WAV file
                file_size = output_file.stat().st_size
                print(f"✅ Audio file created: {file_size} bytes")
                
                # Try to get WAV properties
                try:
                    with wave.open(str(output_file), 'rb') as wav:
                        frames = wav.getnframes()
                        rate = wav.getframerate()
                        duration = frames / float(rate)
                        print(f"📊 Duration: {duration:.2f} seconds")
                        print(f"   Sample rate: {rate} Hz")
                        print(f"   Frames: {frames}")
                
                    self.test_results["tests"]["synthesis"] = {
                        "status": "passed",
                        "file_size": file_size,
                        "duration": duration
                    }
                    return True
                except Exception as e:
                    print(f"⚠️  Could not analyze WAV file: {e}")
                    
            else:
                print("❌ No audio file generated")
                self.test_results["tests"]["synthesis"] = {
                    "status": "failed",
                    "error": "No output file created"
                }
                return False
                
        except subprocess.TimeoutExpired:
            print("⚠️  Synthesis timeout - model download may be needed")
            self.test_results["tests"]["synthesis"] = {
                "status": "timeout",
                "error": "Process timeout"
            }
            return False
        except Exception as e:
            print(f"❌ Synthesis test failed: {e}")
            self.test_results["tests"]["synthesis"] = {
                "status": "error",
                "error": str(e)
            }
            return False
    
    def test_streaming_output(self):
        """Test streaming raw audio output"""
        print("\n" + "="*60)
        print("🌊 Streaming Output Test")
        print("="*60)
        
        test_text = "Testing streaming output"
        
        try:
            # Test --output_raw flag
            process = subprocess.Popen(
                [self.piper_cmd, "--output_raw"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=False  # Binary mode for raw audio
            )
            
            # Send text as bytes
            stdout, stderr = process.communicate(
                input=test_text.encode('utf-8'),
                timeout=3
            )
            
            if stdout:
                audio_size = len(stdout)
                print(f"✅ Received {audio_size} bytes of raw audio")
                self.test_results["tests"]["streaming"] = {
                    "status": "passed",
                    "bytes_received": audio_size
                }
                return True
            else:
                stderr_text = stderr.decode('utf-8', errors='ignore')
                if "model" in stderr_text.lower():
                    print("⚠️  Streaming test skipped - no model")
                    self.test_results["tests"]["streaming"] = {
                        "status": "skipped",
                        "reason": "No model available"
                    }
                else:
                    print("❌ No audio data received")
                    self.test_results["tests"]["streaming"] = {
                        "status": "failed",
                        "error": "No output received"
                    }
                return False
                
        except Exception as e:
            print(f"⚠️  Streaming test error: {e}")
            self.test_results["tests"]["streaming"] = {
                "status": "error",
                "error": str(e)
            }
            return False
    
    def generate_report(self):
        """Generate professional test report"""
        print("\n" + "="*60)
        print("📊 Test Report")
        print("="*60)
        
        # Calculate overall status
        statuses = [test["status"] for test in self.test_results["tests"].values()]
        
        if all(s == "passed" for s in statuses):
            self.test_results["overall_status"] = "PASSED"
            overall_icon = "✅"
        elif any(s in ["failed", "error"] for s in statuses):
            self.test_results["overall_status"] = "FAILED"
            overall_icon = "❌"
        elif any(s == "warning" for s in statuses):
            self.test_results["overall_status"] = "WARNING"
            overall_icon = "⚠️"
        else:
            self.test_results["overall_status"] = "PARTIAL"
            overall_icon = "⚠️"
        
        print(f"\n{overall_icon} Overall Status: {self.test_results['overall_status']}")
        
        print("\n📋 Test Results:")
        for test_name, result in self.test_results["tests"].items():
            status = result["status"]
            icon = {
                "passed": "✅",
                "failed": "❌",
                "warning": "⚠️",
                "skipped": "⏭️",
                "error": "❌",
                "timeout": "⏱️"
            }.get(status, "❓")
            
            print(f"  {icon} {test_name}: {status}")
            if "error" in result:
                print(f"     Error: {result['error'][:100]}")
            if "reason" in result:
                print(f"     Reason: {result['reason']}")
        
        # Save JSON report
        report_file = self.temp_dir / "piper_test_report.json"
        with open(report_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n📁 Full report saved to: {report_file}")
        
        return self.test_results["overall_status"]
    
    def cleanup(self):
        """Clean up test files"""
        try:
            import shutil
            # Keep files for debugging
            print(f"\n🗂️  Test files preserved in: {self.temp_dir}")
            # shutil.rmtree(self.temp_dir)
        except:
            pass


def main():
    """Run comprehensive Piper TTS validation"""
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║                                                                  ║
    ║        🎤 Piper TTS Professional Validation Suite 🎤            ║
    ║                                                                  ║
    ║     Comprehensive testing of text-to-speech installation        ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)
    
    validator = PiperTTSValidator()
    
    # Run tests
    tests_passed = []
    
    if validator.check_installation():
        tests_passed.append("installation")
    
    if validator.check_models():
        tests_passed.append("models")
    
    if validator.test_basic_synthesis():
        tests_passed.append("synthesis")
    
    if validator.test_streaming_output():
        tests_passed.append("streaming")
    
    # Generate report
    overall_status = validator.generate_report()
    
    # Recommendations
    print("\n" + "="*60)
    print("💡 Recommendations")
    print("="*60)
    
    if overall_status == "PASSED":
        print("✅ Piper TTS is fully operational!")
        print("\nNext steps:")
        print("  1. Test with voice recording pipeline")
        print("  2. Integrate with TUI")
        print("  3. Configure for different personas")
    else:
        print("⚠️  Piper TTS needs configuration")
        print("\nRequired actions:")
        
        if "models" not in tests_passed:
            print("  1. Download voice models:")
            print("     wget https://github.com/rhasspy/piper/releases/download/v1.2.0/en_US-amy-medium.onnx")
            print("     wget https://github.com/rhasspy/piper/releases/download/v1.2.0/en_US-amy-medium.onnx.json")
            print("     mkdir -p ~/.local/share/piper")
            print("     mv *.onnx* ~/.local/share/piper/")
        
        if "installation" not in tests_passed:
            print("  1. Reinstall piper-tts:")
            print("     nix profile install nixpkgs#piper-tts")
        
        print("\n  2. Run this test again after fixes")
    
    # Don't cleanup to preserve test files
    # validator.cleanup()
    
    return overall_status == "PASSED"


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)