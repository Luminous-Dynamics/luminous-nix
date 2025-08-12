{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  name = "nix-for-humanity-complete";
  
  buildInputs = with pkgs; [
    # === Core Python Environment ===
    python312
    poetry
    
    # === Voice Interface Dependencies ===
    # Speech Recognition
    openai-whisper
    openai-whisper-cpp
    
    # Text-to-Speech
    piper
    piper-phonemize
    espeak-ng
    
    # Audio Processing
    portaudio
    sox
    ffmpeg
    alsa-utils
    
    # === Development Tools ===
    # Python Quality Tools
    black
    ruff
    mypy
    python312Packages.pytest
    python312Packages.pip
    python312Packages.virtualenv
    python312Packages.ipython
    
    # === AI/ML Dependencies ===
    # For Causal XAI (DoWhy)
    python312Packages.numpy
    python312Packages.pandas
    python312Packages.scikit-learn
    python312Packages.matplotlib
    
    # Local LLMs
    ollama
    
    # === System Integration ===
    # For NixOS operations
    nix-info
    nixpkgs-fmt
    nixfmt-rfc-style
    
    # === Database & Cache ===
    sqlite
    redis
    
    # === Web Development ===
    nodejs_20
    yarn
    
    # === Terminal Tools ===
    ripgrep
    fd
    bat
    eza
    fzf
    jq
    yq
    
    # === Documentation ===
    mdbook
    pandoc
    
    # === Testing Tools ===
    hyperfine  # Benchmarking
    httpie     # API testing
    
    # === Monitoring ===
    htop
    btop
    ncdu
  ];
  
  shellHook = ''
    echo "🌟 Nix for Humanity - Complete Development Environment"
    echo "======================================================"
    echo ""
    echo "✅ All dependencies loaded:"
    echo "  • Python 3.12 with Poetry"
    echo "  • Voice: Whisper & Piper"
    echo "  • AI/ML: NumPy, Pandas, scikit-learn"
    echo "  • Development: Black, Ruff, mypy, pytest"
    echo "  • System: NixOS tools"
    echo ""
    
    # Ensure we're in the project directory
    cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity
    
    # Set up environment variables
    export NIX_HUMANITY_DEV=true
    export NIX_HUMANITY_PYTHON_BACKEND=true
    export PYTHONPATH="$PWD/src:$PYTHONPATH"
    
    # Install Python dependencies via Poetry
    echo "📦 Installing Python dependencies..."
    poetry install --all-extras --quiet
    
    # Create convenient aliases
    alias ntest="poetry run pytest"
    alias nformat="poetry run black . && poetry run ruff check --fix ."
    alias ncheck="poetry run mypy . && poetry run ruff check ."
    alias nrun="poetry run python"
    alias ask="./bin/ask-nix"
    alias tui="./bin/nix-tui"
    
    echo ""
    echo "🚀 Quick Commands:"
    echo "  ntest    - Run tests"
    echo "  nformat  - Format code"
    echo "  ncheck   - Check code quality"
    echo "  nrun     - Run Python script"
    echo "  ask      - Use ask-nix CLI"
    echo "  tui      - Launch TUI"
    echo ""
    echo "💡 Tip: This shell includes EVERYTHING. No more dependency issues!"
    echo ""
  '';
  
  # Environment variables
  PYTHONPATH = "./src:$PYTHONPATH";
  LD_LIBRARY_PATH = "${pkgs.lib.makeLibraryPath [
    pkgs.portaudio
    pkgs.stdenv.cc.cc.lib
  ]}:$LD_LIBRARY_PATH";
  
  # Enable Poetry virtual environment
  POETRY_VIRTUALENVS_IN_PROJECT = "true";
  POETRY_VIRTUALENVS_CREATE = "true";
}