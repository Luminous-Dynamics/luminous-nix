#!/usr/bin/env bash
# Test script for Phase 1: Real Execution

echo "🧪 Testing Nix for Humanity - Phase 1: Real Execution"
echo "====================================================="
echo

cd "$(dirname "$0")"

echo "1️⃣ Testing search functionality..."
echo "Command: ask-nix 'search tree'"
echo "---"
./bin/ask-nix "search tree"
echo
echo "✅ Search test complete"
echo

echo "2️⃣ Testing install with dry-run..."
echo "Command: ask-nix --dry-run 'install tree'"
echo "---"
./bin/ask-nix --dry-run "install tree"
echo
echo "✅ Dry-run test complete"
echo

echo "3️⃣ Testing package validation..."
echo "Command: ask-nix --dry-run 'install nonexistentpackage123'"
echo "---"
./bin/ask-nix --dry-run "install nonexistentpackage123"
echo
echo "✅ Validation test complete"
echo

echo "4️⃣ Testing different personalities..."
echo "Command: ask-nix --minimal 'install vim'"
echo "---"
./bin/ask-nix --minimal --dry-run "install vim"
echo
echo "✅ Personality test complete"
echo

echo "🎉 All tests complete!"
echo
echo "To test REAL installation (will ask for confirmation):"
echo "  ./bin/ask-nix 'install tree'"
echo
echo "To skip confirmation:"
echo "  ./bin/ask-nix --yes 'install tree'"
