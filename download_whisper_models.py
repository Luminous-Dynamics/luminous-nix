#!/usr/bin/env python3
"""
Download Whisper Models
Pre-downloads models for offline use
"""

import subprocess
import os
from pathlib import Path


def download_model(model_name):
    """Download a specific Whisper model"""
    print(f"\n📥 Downloading '{model_name}' model...")
    
    cache_dir = Path.home() / ".cache" / "whisper"
    model_file = cache_dir / f"{model_name}.pt"
    
    if model_file.exists():
        size_mb = model_file.stat().st_size / (1024 * 1024)
        print(f"✅ Already downloaded: {model_file} ({size_mb:.1f} MB)")
        return True
    
    print(f"  This will download to: {cache_dir}")
    print("  Please wait...")
    
    try:
        # Try using whisper CLI
        result = subprocess.run(
            ['whisper', '--model', model_name, '--language', 'en', '--help'],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        # Also try Python API
        try:
            import whisper
            print(f"  Loading model via Python API...")
            model = whisper.load_model(model_name)
            print(f"✅ Model '{model_name}' downloaded successfully!")
            return True
        except ImportError:
            print("  Python whisper module not available, using CLI only")
            
        # Check if file was created
        if model_file.exists():
            size_mb = model_file.stat().st_size / (1024 * 1024)
            print(f"✅ Downloaded: {model_file} ({size_mb:.1f} MB)")
            return True
        else:
            print(f"⚠️  Model file not found after download attempt")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⚠️  Download timeout - model may be very large or connection is slow")
        return False
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False


def main():
    """Download recommended Whisper models"""
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║                                                                  ║
    ║        📥 Whisper Model Downloader 📥                           ║
    ║                                                                  ║
    ║     Pre-download models for offline voice recognition           ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)
    
    # Model information
    models = {
        "tiny": "39 MB - Fastest, least accurate",
        "base": "74 MB - Good balance (RECOMMENDED)",
        "small": "244 MB - Better accuracy",
        "medium": "769 MB - High accuracy",
        "large": "1550 MB - Best accuracy (slow)"
    }
    
    print("\n📊 Available Models:")
    for name, info in models.items():
        print(f"  • {name}: {info}")
    
    print("\n🎯 Recommended for testing: 'base' model")
    print("   Good balance of speed and accuracy")
    
    # Check cache directory
    cache_dir = Path.home() / ".cache" / "whisper"
    cache_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n📁 Models will be saved to: {cache_dir}")
    
    # Check what's already downloaded
    existing = []
    for model_name in models.keys():
        model_file = cache_dir / f"{model_name}.pt"
        if model_file.exists():
            existing.append(model_name)
    
    if existing:
        print(f"\n✅ Already downloaded: {', '.join(existing)}")
    
    # Download selection
    print("\n" + "="*60)
    choice = input("Which model to download? (base/tiny/small/medium/large/all): ").strip().lower()
    
    if choice == "all":
        to_download = list(models.keys())
    elif choice in models:
        to_download = [choice]
    else:
        print("Invalid choice, downloading 'base' model")
        to_download = ["base"]
    
    # Download models
    success = []
    failed = []
    
    for model_name in to_download:
        if download_model(model_name):
            success.append(model_name)
        else:
            failed.append(model_name)
    
    # Summary
    print("\n" + "="*60)
    print("📊 Download Summary")
    print("="*60)
    
    if success:
        print(f"✅ Successfully downloaded: {', '.join(success)}")
    if failed:
        print(f"❌ Failed to download: {', '.join(failed)}")
    
    # Test command
    if success:
        test_model = success[0]
        print(f"\n🎯 Test with:")
        print(f"  echo 'test audio' | whisper --model {test_model} -")
        print(f"\nOr run the full voice test:")
        print(f"  poetry run python test_voice_recording.py")


if __name__ == "__main__":
    main()