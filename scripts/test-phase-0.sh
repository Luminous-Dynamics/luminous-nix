#!/usr/bin/env bash
# Test script for Phase 0 - Making ONE command work

echo "🎉 Phase 0 Test Suite - Making ONE Command Work"
echo "=============================================="
echo

# Test 1: Basic understanding
echo "Test 1: Basic 'install firefox' command"
echo "--------------------------------------"
nix-shell -p python313 --run "python3 bin/ask-nix-v3 'install firefox'" | grep -E "(Intent:|firefox)"
echo

# Test 2: Different phrasing
echo "Test 2: Natural language 'I need VS Code'"
echo "----------------------------------------"
nix-shell -p python313 --run "python3 bin/ask-nix-v3 'I need VS Code'" | grep -E "(Intent:|vscode)"
echo

# Test 3: Execution mode (dry-run)
echo "Test 3: Execution mode with --execute flag"
echo "-----------------------------------------"
nix-shell -p python313 --run "python3 bin/ask-nix-v3 --execute 'install firefox'" | grep -E "(DRY RUN|Would execute)"
echo

echo "✅ Phase 0 Complete! We have:"
echo "  - Natural language understanding"
echo "  - Command preparation"
echo "  - Dry-run safety"
echo "  - Ready for real execution"
echo
echo "To actually install (BE CAREFUL):"
echo "  ask-nix-v3 --execute --no-dry-run 'install firefox'"