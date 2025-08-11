{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  name = "nix-for-humanity-dev";
  
  buildInputs = with pkgs; [
    # Use Python 3.11 for compatibility
    python311
    python311Packages.pip
    python311Packages.virtualenv
    
    # Poetry for dependency management
    poetry
    
    # Required system libraries
    pkg-config
    openssl
    
    # For TUI
    ncurses
    
    # Development tools
    git
    curl
    jq
  ];
  
  shellHook = ''
    echo "🌟 Nix for Humanity Development Environment"
    echo "Python: $(python3 --version)"
    
    # Create venv if it doesn't exist
    if [ ! -d "venv" ]; then
      echo "Creating virtual environment..."
      python3 -m venv venv
    fi
    
    # Activate venv
    source venv/bin/activate
    
    # Install dependencies
    if [ ! -f "venv/.deps_installed" ]; then
      echo "Installing dependencies..."
      pip install --upgrade pip
      pip install -e .
      pip install textual rich blessed
      touch venv/.deps_installed
    fi
    
    # Set PYTHONPATH
    export PYTHONPATH="$PWD/src:$PWD/features/v3.0/xai:$PYTHONPATH"
    
    # Enable features
    export NIX_HUMANITY_PYTHON_BACKEND=true
    
    echo "✅ Environment ready!"
    echo "Run: ./bin/ask-nix 'help'"
  '';
}