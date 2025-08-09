# Nix shell for Grandma Rose Voice Interface
{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  name = "grandma-rose-voice-env";
  
  buildInputs = with pkgs; [
    # Python and package management
    python311
    python311Packages.pip
    python311Packages.virtualenv
    
    # Audio system dependencies
    portaudio
    espeak-ng       # For pyttsx3 on Linux
    alsa-lib
    pulseaudio
    
    # Python packages from nixpkgs (faster than pip)
    python311Packages.numpy
    python311Packages.pyaudio
    
    # Build dependencies for Python packages
    gcc
    stdenv.cc.cc.lib
    
    # Optional: for GUI development
    python311Packages.tkinter
    
    # Helpful tools
    sox  # For audio file manipulation
    ffmpeg  # Required by Whisper
  ];
  
  shellHook = ''
    echo "🎤 Grandma Rose Voice Interface Development Environment"
    echo "===================================================="
    echo ""
    echo "This shell provides all system dependencies for the voice interface."
    echo ""
    echo "To set up Python packages:"
    echo "  python -m venv venv"
    echo "  source venv/bin/activate" 
    echo "  pip install -r voice_requirements.txt"
    echo ""
    echo "To run the demo:"
    echo "  python voice_demo_simple.py  # No audio hardware needed"
    echo "  python voice_input_grandma_rose.py  # Full version"
    echo ""
    echo "Audio might need: export PULSE_LATENCY_MSEC=30"
    echo ""
    
    # Set up audio environment
    export AUDIODEV=default
    export AUDIODRIVER=pulse
  '';
  
  # Ensure audio libraries are found
  LD_LIBRARY_PATH = "${pkgs.portaudio}/lib:${pkgs.stdenv.cc.cc.lib}/lib";
}