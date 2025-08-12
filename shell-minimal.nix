{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  name = "nix-for-humanity-minimal";
  
  buildInputs = with pkgs; [
    # Core essentials only
    python312
    poetry
    
    # Development tools
    black
    ruff
    
    # Basic utilities
    ripgrep
    fd
    bat
    jq
  ];
  
  shellHook = ''
    echo "🌟 Nix for Humanity - Minimal Dev Environment"
    echo "============================================="
    echo ""
    echo "✅ Core tools loaded:"
    echo "  • Python 3.12 with Poetry"
    echo "  • Black & Ruff for formatting"
    echo "  • Basic utilities"
    echo ""
    
    # Ensure we're in the project directory
    cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity
    
    # Set up environment
    export NIX_HUMANITY_PYTHON_BACKEND=true
    export PYTHONPATH="$PWD/src:$PYTHONPATH"
    
    # Install Python dependencies
    echo "📦 Installing Python dependencies..."
    poetry install --all-extras --quiet 2>/dev/null || true
    
    echo ""
    echo "🚀 Ready for development!"
    echo ""
  '';
}