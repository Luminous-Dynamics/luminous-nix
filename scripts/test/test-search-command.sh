#!/usr/bin/env bash
# Test script to verify the search command works

echo "Testing nix search directly..."
echo "Command: nix search nixpkgs firefox | head -20"
echo "=================================================="

# Run the actual command with limited output
nix search nixpkgs firefox 2>&1 | head -20

echo
echo "Exit code: $?"
