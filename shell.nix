{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  name = "nixos-gui-dev";

  buildInputs = with pkgs; [
    # Core development tools
    nodejs_20
    nodePackages.npm
    nodePackages.pnpm
    nodePackages.yarn

    # Build tools
    gnumake
    gcc
    pkg-config

    # SSL/TLS support
    openssl

    # Testing tools
    curl
    jq
    httpie

    # Security tools
    nmap

    # Database tools (if needed)
    sqlite
    redis

    # Python for Sacred Trinity and NixOS integration
    # Primary Python (3.13) for main application
    python313
    python313Packages.pip
    python313Packages.virtualenv
    python313Packages.flask
    python313Packages.gunicorn
    python313Packages.requests     # For API calls
    python313Packages.pytest       # For testing
    python313Packages.pytest-asyncio  # For async testing
    python313Packages.pytest-cov      # For coverage reports
    python313Packages.pytest-mock      # For mocking in tests
    # sqlite3 is included in Python by default
    python313Packages.pyyaml       # For configuration
    python313Packages.rich         # For beautiful terminal output
    python313Packages.textual      # For TUI interface
    python313Packages.blessed      # Terminal capabilities
    python313Packages.pyperclip    # Clipboard support

    # Secondary Python (3.11) for research components that need DoWhy
    python311
    python311Packages.pip
    python311Packages.virtualenv

    # Embodied AI Avatar dependencies
    python313Packages.pygame      # For quick 2D prototype
    python313Packages.numpy       # Numerical computations
    python313Packages.pillow      # Image processing
    # Note: Taichi and Genesis need pip install in venv

    # For Sacred Trinity workflow
    ollama                         # Local LLM (Mistral-7B)

    # ActivityWatch for user behavior monitoring
    activitywatch                  # Privacy-first activity tracking

    # System utilities
    htop
    lsof
    netcat

    # Git and version control
    git
    gh  # GitHub CLI

    # Documentation
    pandoc

    # Container tools (optional)
    podman
    docker-compose

    # Monitoring tools
    prometheus
    grafana

    # Load testing tools
    apacheHttpd  # for ab (Apache Bench)
    siege

    # Certificate generation
    mkcert

    # Process management
    # supervisor is not available as a package name
    tmux

    # Editor support
    neovim
    ripgrep
    fd
  ];

  shellHook = ''
    echo "🗣️ Nix for Humanity Development Environment"
    echo "=========================================="
    echo "Node.js: $(node --version)"
    echo "npm: $(npm --version)"
    echo "Python 3.13 (main): $(python3 --version)"
    echo "Python 3.11 (research): $(python3.11 --version)"
    echo "SQLite: $(sqlite3 --version | head -1)"
    echo ""
    echo "Available commands:"
    echo "  ask-nix-hybrid    - Our hybrid NixOS assistant"
    echo "  nix-do           - Execute NixOS commands (Python)"
    echo "  npm start        - Start development servers"
    echo "  npm test         - Run test suite"
    echo ""
    echo "ActivityWatch Integration:"
    echo "  aw-qt            - Start ActivityWatch GUI"
    echo "  aw-server        - Start headless server"
    echo "  Web UI: http://localhost:5600"
    echo ""
    echo "Sacred Trinity workflow:"
    echo "  Human: Define natural language patterns"
    echo "  Claude: Implement architecture"
    echo "  LLM: ask-nix-guru 'NixOS question here'"
    echo ""
    echo "🌊 We flow with Python integration!"

    # Set up environment variables
    export NODE_ENV=development
    export JWT_SECRET=$(openssl rand -hex 32)
    export SESSION_SECRET=$(openssl rand -hex 32)
    export NIXOS_GUI_PORT=8080
    export NIXOS_GUI_HTTPS_PORT=8443

    # Create SSL certificates if they don't exist
    if [ ! -f ssl/cert.pem ]; then
      echo "Generating SSL certificates..."
      mkdir -p ssl
      mkcert -install
      mkcert -cert-file ssl/cert.pem -key-file ssl/key.pem localhost 127.0.0.1 ::1
    fi

    # Set up Python virtual environment for fallback
    if [ ! -d .venv ]; then
      echo "Setting up Python virtual environment..."
      python3 -m venv .venv
    fi

    # Source Python venv
    source .venv/bin/activate

    # Install Python dependencies if requirements.txt exists
    if [ -f requirements.txt ]; then
      pip install -r requirements.txt
    fi

    # Create necessary directories
    mkdir -p logs
    mkdir -p data
    mkdir -p test/results

    # Add project scripts and bins to PATH
    export PATH=$PWD/scripts:$PWD/bin:$PATH

    # Set Python path for our modules
    export PYTHONPATH="$PWD/scripts:$PYTHONPATH"

    # Alias for quick commands
    alias nix-gui-start="npm start"
    alias nix-gui-test="npm test"
    alias nix-gui-build="npm run build"
    alias nix-gui-secure="npm run start:secure"

    # Python version aliases
    alias python-main="python3"
    alias python-research="python3.11"
    alias pip-main="python3 -m pip"
    alias pip-research="python3.11 -m pip"

    # Function to check all services
    check-services() {
      echo "Checking services..."
      lsof -i :8080 >/dev/null 2>&1 && echo "✅ HTTP server on :8080" || echo "❌ HTTP server not running"
      lsof -i :8443 >/dev/null 2>&1 && echo "✅ HTTPS server on :8443" || echo "❌ HTTPS server not running"
      lsof -i :6379 >/dev/null 2>&1 && echo "✅ Redis on :6379" || echo "❌ Redis not running"
    }

    echo ""
    echo "💡 Tips:"
    echo "  - Run 'nix-shell' to enter this environment"
    echo "  - Run 'check-services' to verify running services"
    echo "  - SSL certificates are in the ssl/ directory"
    echo "  - Logs are written to the logs/ directory"
    echo ""
    echo "🐍 Python Versions:"
    echo "  - python3 (3.13) - Main application development"
    echo "  - python3.11 - Research components (DoWhy, etc.)"
    echo "  - Use 'python-research' alias for research work"
    echo ""
  '';

  # Environment variables
  NIXOS_GUI_DEV = "1";
  NODE_OPTIONS = "--max-old-space-size=4096";

  # Prevent npm from accessing system directories
  NPM_CONFIG_PREFIX = "$PWD/.npm-global";

  # Python settings
  PYTHONPATH = "$PWD";

  # SSL settings
  NODE_TLS_REJECT_UNAUTHORIZED = "0"; # For development only
}
