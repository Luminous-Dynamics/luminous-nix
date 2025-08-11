#!/usr/bin/env bash
# Helper script to run commands within nix-shell

# If we're already in nix-shell, just run the command
if [ -n "$IN_NIX_SHELL" ]; then
    exec "$@"
fi

# Otherwise, enter nix-shell and run the command
echo "📦 Entering nix-shell to access Python 3..."
exec nix-shell --run "$*"
