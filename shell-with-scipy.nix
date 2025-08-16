{ pkgs ? import <nixpkgs> {} }:

let
  # Create a Python environment with scipy and all dependencies properly linked
  pythonWithScipy = pkgs.python313.withPackages (ps: with ps; [
    # Core scientific computing
    numpy
    scipy
    pandas
    matplotlib
    scikit-learn
    
    # Other essentials
    pip
    virtualenv
    flask
    gunicorn
    requests
    pytest
    pytest-asyncio
    pytest-cov
    pytest-mock
    pyyaml
    rich
    textual
    blessed
    pyperclip
    psutil
    
    # System integration
    dbus-python  # D-Bus integration for system monitoring
    pygobject3   # GObject introspection for D-Bus
    
    # Monitoring and caching
    prometheus-client
    diskcache
    watchdog
    
    # Additional scientific libraries
    statsmodels
    sympy
    networkx
  ]);

in
pkgs.mkShell {
  name = "luminous-nix-with-scipy";

  buildInputs = with pkgs; [
    # Python with scipy
    pythonWithScipy
    
    # Essential C/C++ libraries that scipy needs
    gcc
    stdenv.cc.cc.lib  # This provides libstdc++.so.6
    glibc
    gfortran          # Fortran compiler for scipy
    blas              # Basic Linear Algebra Subprograms
    lapack            # Linear Algebra PACKage
    
    # Build tools
    gnumake
    cmake
    pkg-config
    ninja  # Required for dbus-python
    meson  # Required for dbus-python
    
    # Poetry for package management
    poetry
    
    # Other development tools
    nodejs_20
    nodePackages.npm
    git
    curl
    jq
    
    # System monitoring tools
    htop
    sqlite
    redis
    
    # D-Bus and GObject development
    dbus
    dbus.dev
    glib
    gobject-introspection
    gtk3
    
    # Nix tools
    nix-prefetch-git
    nixfmt
    nil
  ];

  shellHook = ''
    echo "🔬 Luminous Nix Development Environment (with scipy)"
    echo "===================================================="
    echo ""
    
    # Set up library paths for scipy
    export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib}/lib:${pkgs.glibc}/lib:$LD_LIBRARY_PATH"
    export LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib}/lib:${pkgs.glibc}/lib:$LIBRARY_PATH"
    
    # Set up Python paths
    export PYTHONPATH="$PWD/src:$PYTHONPATH"
    export PATH="$PWD/bin:$PATH"
    
    # Test scipy installation
    echo "Testing scipy installation..."
    python -c "import scipy; print(f'✅ scipy {scipy.__version__} loaded successfully!')" 2>/dev/null || echo "❌ scipy failed to load"
    
    echo ""
    echo "🐍 Python: $(python --version)"
    echo "📦 Poetry: $(poetry --version 2>/dev/null || echo 'Run: nix-shell -p poetry')"
    echo ""
    echo "Available commands:"
    echo "  python            - Python with scipy ready"
    echo "  poetry install    - Install project dependencies"
    echo "  poetry run pytest - Run tests"
    echo ""
    
    # Create necessary directories
    mkdir -p logs data cache .local/share/luminous-nix
    
    echo "🌊 Ready to compute with scipy!"
  '';

  # Environment variables
  NIX_CFLAGS_COMPILE = "-I${pkgs.glibc.dev}/include";
  NIX_CFLAGS_LINK = "-L${pkgs.glibc}/lib -L${pkgs.stdenv.cc.cc.lib}/lib";
  
  # Ensure we can find shared libraries
  LD_LIBRARY_PATH = "${pkgs.stdenv.cc.cc.lib}/lib";
}