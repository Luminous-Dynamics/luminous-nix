{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  name = "nix-for-humanity-tui";
  
  buildInputs = with pkgs; [
    # Python with TUI packages
    (python311.withPackages (ps: with ps; [
      # Core TUI framework
      textual
      textual-dev
      rich
      
      # Additional dependencies from requirements-tui.txt
      blessed
      pyperclip
      colorama
      
      # Async support
      # asyncio is built-in to Python 3.11+
      
      # Testing tools
      pytest
      pytest-asyncio
      
      # Type checking
      mypy
      
      # Code quality
      black
      ruff
      
      # Documentation
      mkdocs
      mkdocs-material
      
      # Backend dependencies
      flask
      gunicorn
      pyjwt
      pyopenssl
      websockets
      python-socketio
      flask-socketio
      requests
      pytest-cov
      python-dotenv
      watchdog
      cryptography
      click
      
      # Core dependencies for backend
      # sqlite3 is included with Python
      pyyaml
    ]))
    
    # System tools
    git
    jq
    curl
    sqlite
    
    # Development tools
    neovim
    ripgrep
    fd
  ];
  
  shellHook = ''
    echo "🌟 Nix for Humanity TUI Development Environment"
    echo "=============================================="
    echo "Python: $(python3 --version)"
    echo ""
    echo "Available commands:"
    echo "  python3 src/tui/app.py          - Run the basic TUI"
    echo "  python3 src/tui/enhanced_app.py - Run the enhanced TUI"
    echo "  python3 -m textual run src/tui/app.py - Run with Textual CLI"
    echo ""
    echo "TUI Features:"
    echo "  - Beautiful Textual-based interface"
    echo "  - Natural language processing"
    echo "  - Real-time system feedback"
    echo "  - Accessibility-first design"
    echo ""
    echo "🎨 Ready to create beautiful terminal interfaces!"
    
    # Set Python path
    export PYTHONPATH="$PWD:$PWD/scripts:$PWD/backend:$PYTHONPATH"
    
    # Create necessary directories
    mkdir -p logs data test/results
  '';
  
  # Environment variables
  NODE_ENV = "development";
  PYTHONPATH = "$PWD";
}