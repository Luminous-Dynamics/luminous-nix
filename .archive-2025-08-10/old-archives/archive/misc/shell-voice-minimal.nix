{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  name = "nix-for-humanity-voice-minimal";
  
  buildInputs = with pkgs; [
    # Core Python for voice interface
    python311
    python311Packages.pip
    python311Packages.virtualenv
    
    # Essential voice dependencies only
    portaudio       # Audio I/O (small)
    espeak-ng       # TTS fallback (small)
    ffmpeg-headless # Audio processing without GUI deps (smaller than ffmpeg-full)
    sox             # Sound processing (small)
    
    # Core development tools
    nodejs_20       # For the CLI
    git
    curl
    jq
  ];
  
  shellHook = ''
    echo "🎤 Nix for Humanity - Minimal Voice Environment"
    echo "=============================================="
    echo "This is a lightweight environment for quick voice testing."
    echo ""
    echo "⚠️  Note: This minimal shell does NOT include:"
    echo "  - Whisper (use pip in venv if needed)"
    echo "  - Piper TTS (use pip in venv if needed)"
    echo "  - Heavy ML dependencies"
    echo ""
    echo "For full voice support, use: nix develop"
    echo ""
    echo "Quick start:"
    echo "  1. python3 -m venv .venv-voice"
    echo "  2. source .venv-voice/bin/activate"
    echo "  3. pip install openai-whisper piper-tts sounddevice"
    echo ""
    echo "Or use mock mode: NIX_VOICE_MOCK=true ./bin/nix-voice"
    echo ""
    
    # Set up minimal environment
    export NIX_HUMANITY_MINIMAL=true
    export PYTHONPATH="$PWD:$PYTHONPATH"
    export PATH="$PWD/bin:$PATH"
  '';
}