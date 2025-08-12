{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  name = "nix-for-humanity-voice-dev";
  
  buildInputs = with pkgs; [
    # Python environment
    python312
    poetry
    
    # Voice recognition (Whisper)
    openai-whisper          # OpenAI Whisper for speech recognition
    openai-whisper-cpp      # C++ version for faster inference
    
    # Text-to-speech (Piper)
    piper                   # Piper TTS
    piper-phonemize        # Phonemization for Piper
    
    # Audio processing
    portaudio              # Audio I/O library
    sox                    # Sound processing
    ffmpeg                 # Audio/video processing
    
    # Additional tools
    espeak-ng              # Fallback TTS
    alsa-utils             # Audio utilities
  ];
  
  shellHook = ''
    echo "🎤 Voice Development Environment"
    echo "================================"
    echo ""
    echo "Available tools:"
    echo "  • Whisper: Speech recognition (whisper command)"
    echo "  • Piper: Text-to-speech (piper command)"
    echo "  • Python: With Poetry for dependencies"
    echo ""
    echo "Quick test commands:"
    echo "  Test Whisper: echo 'test' | whisper --help"
    echo "  Test Piper: echo 'Hello world' | piper --help"
    echo ""
    echo "To test voice features:"
    echo "  poetry run python demo_voice_with_nix.py"
    echo ""
    
    # Ensure we're in the project directory
    cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity
    
    # Activate Poetry environment
    poetry install --all-extras
  '';
  
  # Environment variables
  PYTHONPATH = "${pkgs.python312.sitePackages}:$PYTHONPATH";
  LD_LIBRARY_PATH = "${pkgs.lib.makeLibraryPath [
    pkgs.portaudio
    pkgs.stdenv.cc.cc.lib
  ]}:$LD_LIBRARY_PATH";
}