{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  name = "nix-humanity-audio-env";
  
  buildInputs = with pkgs; [
    # Python and package management
    python311
    poetry
    
    # Audio libraries
    portaudio
    alsa-lib
    pulseaudio
    
    # Audio tools
    sox
    ffmpeg
    
    # Speech processing
    openai-whisper
    piper-tts
    
    # Python packages that need C libraries
    (python311.withPackages (ps: with ps; [
      numpy
      sounddevice
      pyaudio
      scipy
    ]))
  ];
  
  shellHook = ''
    echo "🎤 Audio Development Environment"
    echo "================================"
    echo ""
    echo "✅ PortAudio configured"
    echo "✅ Python audio packages available"
    echo "✅ Speech tools ready"
    echo ""
    
    # Ensure PortAudio can be found
    export LD_LIBRARY_PATH="${pkgs.portaudio}/lib:$LD_LIBRARY_PATH"
    
    # Set up Python path
    export PYTHONPATH="$PWD/src:$PYTHONPATH"
    
    # Verify audio access
    python3 -c "import sounddevice; print('✅ sounddevice working!')" 2>/dev/null || echo "⚠️ sounddevice needs configuration"
    
    echo ""
    echo "Usage:"
    echo "  python test_microphone.py"
    echo "  python test_voice_recording.py"
    echo ""
  '';
}