#!/usr/bin/env bash
# Test script for ask-nix-enhanced

echo "🧪 Testing ask-nix-enhanced tool..."
echo "=================================="

# Check if we're in nix-shell
if [ -z "$IN_NIX_SHELL" ]; then
    echo "⚠️  Not in nix-shell! Python 3 won't be available."
    echo "📦 Entering nix-shell automatically..."
    echo ""
    # Run this script again within nix-shell
    exec nix-shell --run "$0 $*"
fi

echo "✅ Running in nix-shell environment"
echo "🐍 Python version: $(python3 --version)"
echo ""

# Check if the tool exists and is executable
if [ ! -f "./bin/ask-nix-enhanced" ]; then
    echo "❌ ask-nix-enhanced not found in ./bin/"
    exit 1
fi

if [ ! -x "./bin/ask-nix-enhanced" ]; then
    echo "⚠️  Making ask-nix-enhanced executable..."
    chmod +x ./bin/ask-nix-enhanced
fi

echo "✅ Tool found and executable"
echo

# Test 1: Help output
echo "📋 Test 1: Help output"
echo "----------------------"
./bin/ask-nix-enhanced --help | head -20
echo

# Test 2: Dry run mode (default)
echo "📋 Test 2: Dry run query"
echo "------------------------"
./bin/ask-nix-enhanced "how do I install firefox" | head -30
echo

# Test 3: Different personalities
echo "📋 Test 3: Personality variations"
echo "---------------------------------"
echo "Minimal:"
./bin/ask-nix-enhanced --minimal "install git" | head -10
echo
echo "Technical:"
./bin/ask-nix-enhanced --technical "what is a generation" | head -15
echo

# Test 4: Check Python backend
echo "📋 Test 4: Python backend availability"
echo "--------------------------------------"
if python3 -c "import sys; sys.path.insert(0, 'backend/python'); import natural_language_executor" 2>/dev/null; then
    echo "✅ Python backend imports successfully"
else
    echo "❌ Python backend import failed"
    echo "   This might affect advanced features"
fi
echo

# Test 5: Knowledge engine
echo "📋 Test 5: Knowledge engine test"
echo "--------------------------------"
python3 scripts/nix-knowledge-engine.py 2>&1 | grep -q "NixOS Knowledge Engine Test" && echo "✅ Knowledge engine works" || echo "❌ Knowledge engine failed"

echo
echo "🎉 Basic tests complete!"
echo
echo "To test interactive mode, run:"
echo "  ./bin/ask-nix-enhanced"
echo
echo "To test live execution (be careful!):"
echo "  ./bin/ask-nix-enhanced --live 'show system generation'"
