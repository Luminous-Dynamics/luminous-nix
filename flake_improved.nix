{
  description = "Luminous Nix - Natural Language Interface for NixOS";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          config.allowUnfree = true;  # For some ML models
        };

        poetry2nix-lib = poetry2nix.lib.mkPoetry2Nix { inherit pkgs; };
        
        # Python environment for development
        pythonEnv = pkgs.python313.withPackages (ps: with ps; [
          # Core dependencies
          pip
          setuptools
          wheel
          virtualenv
          
          # Web framework
          flask
          gunicorn
          requests
          aiohttp
          websockets
          
          # CLI and TUI
          click
          rich
          textual
          blessed
          colorama
          python-dotenv
          pyperclip
          
          # Data processing
          numpy
          scipy  # Now included!
          pandas
          matplotlib
          scikit-learn
          
          # ML/AI (for learning system)
          torch
          transformers
          sentence-transformers
          
          # System monitoring
          psutil
          py-cpuinfo
          
          # Database
          sqlalchemy
          aiosqlite
          
          # Testing
          pytest
          pytest-asyncio
          pytest-cov
          pytest-mock
          hypothesis  # Property-based testing
          
          # Code quality
          black
          ruff
          mypy
          pylint
          
          # Documentation
          sphinx
          sphinx-rtd-theme
          
          # Utilities
          pyyaml
          toml
          jsonschema
          python-dateutil
          humanize
          tqdm
          
          # Voice interface (if available)
          # sounddevice
          # pyaudio
        ]);

        # Development tools
        devTools = with pkgs; [
          # Version control
          git
          gh
          pre-commit
          
          # Build tools
          gcc
          gnumake
          cmake
          pkg-config
          
          # Nix tools
          nil  # Nix LSP
          nixfmt-rfc-style
          nix-prefetch-git
          nix-tree
          nix-diff
          cachix
          
          # System tools
          htop
          btop
          ncdu
          duf
          ripgrep
          fd
          bat
          eza
          zoxide
          fzf
          
          # Network tools
          curl
          wget
          httpie
          jq
          yq
          
          # Documentation
          mdbook
          pandoc
          graphviz
          plantuml
          
          # Demo creation
          asciinema
          termtosvg
          vhs
          
          # Database tools
          sqlite
          litecli
          
          # Container tools (optional)
          podman
          docker-compose
          
          # Monitoring
          prometheus
          grafana-loki
          
          # Security scanning
          trivy
          grype
          
          # Performance profiling
          hyperfine
          flamegraph
        ];

        # Voice/Audio dependencies
        audioTools = with pkgs; [
          portaudio
          libsndfile
          ffmpeg-full
          sox
          espeak-ng
          piper-tts
        ];

        # Create the main binary wrapper
        askNix = pkgs.writeShellScriptBin "ask-nix" ''
          #!/usr/bin/env bash
          exec ${pythonEnv}/bin/python -m luminous_nix.cli "$@"
        '';

        # TUI launcher
        nixTui = pkgs.writeShellScriptBin "nix-tui" ''
          #!/usr/bin/env bash
          exec ${pythonEnv}/bin/python -m luminous_nix.interfaces.tui "$@"
        '';

        # Voice interface launcher
        nixVoice = pkgs.writeShellScriptBin "nix-voice" ''
          #!/usr/bin/env bash
          exec ${pythonEnv}/bin/python -m luminous_nix.interfaces.voice "$@"
        '';

      in
      {
        # Development shell with everything
        devShells.default = pkgs.mkShell {
          buildInputs = [
            pythonEnv
            askNix
            nixTui
            nixVoice
          ] ++ devTools ++ audioTools ++ (with pkgs; [
            # Node.js for any web UI
            nodejs_20
            nodePackages.npm
            nodePackages.pnpm
            
            # Poetry for Python package management
            poetry
            
            # Local LLM support
            ollama
            
            # ActivityWatch for behavior tracking
            activitywatch
          ]);

          shellHook = ''
            echo "✨ Welcome to Luminous Nix Development Environment! ✨"
            echo "======================================================"
            echo ""
            echo "🐍 Python: $(python --version)"
            echo "📦 Poetry: $(poetry --version 2>/dev/null || echo 'Not in PATH - use nix shell')"
            echo "🦀 Rust: $(rustc --version 2>/dev/null || echo 'Not installed')"
            echo "🟢 Node.js: $(node --version)"
            echo ""
            echo "🎯 Main Commands:"
            echo "  ask-nix          - Natural language NixOS interface"
            echo "  nix-tui          - Terminal UI interface"
            echo "  nix-voice        - Voice interface (experimental)"
            echo ""
            echo "🛠️ Development:"
            echo "  poetry install   - Install Python dependencies"
            echo "  poetry run pytest - Run tests"
            echo "  poetry run black . - Format code"
            echo "  pre-commit run --all-files - Run all checks"
            echo ""
            echo "📊 System Monitoring:"
            echo "  btop            - Beautiful system monitor"
            echo "  sacred-monitor  - Luminous Nix health monitor"
            echo ""
            echo "🤖 AI Tools:"
            echo "  ollama serve    - Start local LLM server"
            echo "  aw-qt           - ActivityWatch GUI"
            echo ""
            echo "💡 Tips:"
            echo "  - scipy is now available: python -c 'import scipy; print(scipy.__version__)'
            echo "  - Use 'nix flake update' to update dependencies"
            echo "  - Run 'pre-commit install' to set up git hooks"
            echo ""
            
            # Set up environment
            export LUMINOUS_NIX_ROOT="$PWD"
            export PYTHONPATH="$PWD/src:$PYTHONPATH"
            export PATH="$PWD/bin:$PATH"
            
            # Create necessary directories
            mkdir -p logs data cache .local/share/luminous-nix
            
            # Python development mode
            if [ -f pyproject.toml ]; then
              echo "📦 Installing in development mode..."
              poetry install --quiet 2>/dev/null || pip install -e . --quiet 2>/dev/null
            fi
            
            echo "🌊 Ready to flow with natural language NixOS!"
          '';

          # Environment variables
          LUMINOUS_NIX_DEV = "1";
          NIXPKGS_ALLOW_UNFREE = "1";  # For ML models
          
          # Performance
          PYTHON_OPTIMIZE = "1";
          NODE_OPTIONS = "--max-old-space-size=4096";
        };

        # Minimal shell for running only
        devShells.minimal = pkgs.mkShell {
          buildInputs = [
            pythonEnv
            askNix
          ];
          
          shellHook = ''
            echo "🚀 Luminous Nix - Minimal Environment"
            echo "Run: ask-nix 'your command here'"
          '';
        };

        # Package definition
        packages = {
          default = self.packages.${system}.luminous-nix;
          
          luminous-nix = poetry2nix-lib.mkPoetryApplication {
            projectDir = ./.;
            python = pkgs.python313;
            
            # Override specific packages if needed
            overrides = poetry2nix-lib.overrides.withDefaults (self: super: {
              # Fix packages that don't build correctly
              scipy = super.scipy.override {
                preferWheel = true;
              };
            });
          };
          
          # Standalone binaries
          ask-nix = askNix;
          nix-tui = nixTui;
          nix-voice = nixVoice;
        };

        # Apps for direct execution
        apps = {
          default = flake-utils.lib.mkApp {
            drv = askNix;
          };
          
          tui = flake-utils.lib.mkApp {
            drv = nixTui;
          };
          
          voice = flake-utils.lib.mkApp {
            drv = nixVoice;
          };
        };
      }
    ) // {
      # NixOS module for system-wide installation
      nixosModules.default = { config, lib, pkgs, ... }: with lib; {
        options.programs.luminous-nix = {
          enable = mkEnableOption "Luminous Nix - Natural Language NixOS Interface";
          
          enableVoice = mkOption {
            type = types.bool;
            default = false;
            description = "Enable voice interface support";
          };
          
          enableSelfHealing = mkOption {
            type = types.bool;
            default = false;
            description = "Enable self-healing system (experimental)";
          };
        };

        config = mkIf config.programs.luminous-nix.enable {
          environment.systemPackages = [
            self.packages.${pkgs.system}.luminous-nix
          ] ++ (lib.optionals config.programs.luminous-nix.enableVoice [
            pkgs.portaudio
            pkgs.piper-tts
          ]);
          
          # Create system service for self-healing if enabled
          systemd.services.luminous-nix-healing = mkIf config.programs.luminous-nix.enableSelfHealing {
            description = "Luminous Nix Self-Healing Service";
            wantedBy = [ "multi-user.target" ];
            after = [ "network.target" ];
            
            serviceConfig = {
              Type = "simple";
              ExecStart = "${self.packages.${pkgs.system}.luminous-nix}/bin/luminous-nix-healing";
              Restart = "on-failure";
              RestartSec = "30s";
              
              # Security hardening
              PrivateTmp = true;
              ProtectSystem = "strict";
              ProtectHome = true;
              NoNewPrivileges = true;
            };
          };
        };
      };

      # Home Manager module
      homeManagerModules.default = { config, lib, pkgs, ... }: with lib; {
        options.programs.luminous-nix = {
          enable = mkEnableOption "Luminous Nix";
          
          settings = mkOption {
            type = types.attrs;
            default = {};
            description = "Luminous Nix configuration";
          };
        };

        config = mkIf config.programs.luminous-nix.enable {
          home.packages = [ self.packages.${pkgs.system}.luminous-nix ];
          
          xdg.configFile."luminous-nix/config.yaml".text = 
            builtins.toJSON config.programs.luminous-nix.settings;
        };
      };

      # Overlay for adding to nixpkgs
      overlays.default = final: prev: {
        luminous-nix = self.packages.${prev.system}.luminous-nix;
      };
    };
}