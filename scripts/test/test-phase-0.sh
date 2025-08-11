#!/usr/bin/env bash
# Test script for Phase 0 implementation

echo "🧪 Testing Phase 0: Command Execution"
echo "===================================="
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please wait for NixOS rebuild to complete."
    echo "   Or run: nix-shell -p python313"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo

# Test 1: Basic query (no execution)
echo "Test 1: Basic query without execution"
echo "-------------------------------------"
./bin/ask-nix-hybrid-v2 "How do I install Firefox?"
echo

# Test 2: Query with dry-run execution
echo "Test 2: Install with dry-run (default)"
echo "--------------------------------------"
./bin/ask-nix-hybrid-v2 --execute "install firefox"
echo

# Test 3: Search functionality
echo "Test 3: Search packages"
echo "-----------------------"
./bin/ask-nix-hybrid-v2 --execute "search browser"
echo

# Test 4: System update (dry-run)
echo "Test 4: System update (dry-run)"
echo "-------------------------------"
./bin/ask-nix-hybrid-v2 --execute "update my system"
echo

# Test 5: Different personalities
echo "Test 5: Testing personalities"
echo "-----------------------------"
echo "Minimal:"
./bin/ask-nix-hybrid-v2 --minimal "install python"
echo
echo "Encouraging:"
./bin/ask-nix-hybrid-v2 --encouraging "install python"
echo

echo "🎉 Phase 0 tests complete!"
echo
echo "To test REAL execution (not dry-run):"
echo "  ./bin/ask-nix-hybrid-v2 --execute --no-dry-run 'install firefox'"
echo
echo "⚠️  WARNING: Real execution will actually install packages!"
