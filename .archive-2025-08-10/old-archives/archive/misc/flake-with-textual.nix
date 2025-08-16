# Alternative flake.nix that adds textual to pythonMainEnv
# This avoids the poetry2nix circular dependency issue

{
  description = "Nix for Humanity - Natural Language Interface for NixOS";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        
        # Python environment with TUI dependencies
        pythonEnv = pkgs.python311.withPackages (ps: with ps; [
          # Core dependencies
          pip
          requests
          click
          colorama
          python-dotenv
          pyyaml
          
          # TUI dependencies
          textual
          rich
          blessed
          
          # Testing
          pytest
          pytest-asyncio
          pytest-cov
          pytest-mock
          
          # Other useful packages
          flask
          gunicorn
          numpy
          pandas
        ]);
        
        # TUI runner script
        runTuiApp = pkgs.writeShellScriptBin "run-tui-app" ''
          #!/usr/bin/env bash
          set -e
          
          echo "🌟 Launching Nix for Humanity TUI..."
          echo ""
          
          cd ${toString ./.}
          export PYTHONPATH="${toString ./.}:$PYTHONPATH"
          
          exec ${pythonEnv}/bin/python -m nix_humanity.interfaces.tui "$@"
        '';
        
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            pythonEnv
            runTuiApp
            
            # Development tools
            nodePackages.npm
            git
            ripgrep
            fd
            curl
            jq
          ];
          
          shellHook = ''
            echo "🌟 Nix for Humanity Development Environment!"
            echo "==========================================="
            echo "Python: $(python --version)"
            echo ""
            echo "✅ Textual TUI framework is available!"
            echo ""
            echo "Available commands:"
            echo "  run-tui-app       - Launch the TUI"
            echo "  python test_tui_components.py - Test components"
            echo ""
            echo "Try: python -c 'import textual; print(textual.__version__)'"
            echo ""
            
            export NIX_FOR_HUMANITY_ROOT="$PWD"
          '';
        };
      }
    );
}