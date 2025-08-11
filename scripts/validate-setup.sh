#!/usr/bin/env bash
# Validate that Nix for Humanity is properly set up

echo "🔍 Validating Nix for Humanity Setup"
echo "===================================="
echo

# Check for required files
echo "📁 Checking required files..."
REQUIRED_FILES=(
    "bin/ask-nix-modern"
    "bin/execution-bridge.js"
    "bin/nix-do"
    "bin/nix-profile-do"
    "scripts/nix-knowledge-engine-modern.py"
    "scripts/nix-knowledge-engine.py"
)

ALL_GOOD=true
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ Missing: $file"
        ALL_GOOD=false
    fi
done

echo
echo "🔧 Checking executability..."
EXECUTABLES=(
    "bin/ask-nix-modern"
    "bin/execution-bridge.js"
    "bin/nix-do"
    "bin/nix-profile-do"
)

for exe in "${EXECUTABLES[@]}"; do
    if [ -x "$exe" ]; then
        echo "✅ $exe is executable"
    else
        echo "❌ $exe is not executable"
        chmod +x "$exe"
        echo "   Fixed: made executable"
    fi
done

echo
echo "🐍 Checking Python dependencies..."
if python3 -c "import sys; sys.path.insert(0, 'scripts'); import nix_knowledge_engine" 2>/dev/null; then
    echo "✅ Python knowledge engine loads correctly"
else
    echo "❌ Python knowledge engine failed to load"
    ALL_GOOD=false
fi

echo
echo "📦 Checking Node.js..."
if command -v node >/dev/null 2>&1; then
    echo "✅ Node.js is available"
else
    echo "❌ Node.js not found (needed for execution bridge)"
    ALL_GOOD=false
fi

echo
echo "🌉 Testing execution bridge..."
if node bin/execution-bridge.js '{"action": "list_packages"}' >/dev/null 2>&1; then
    echo "✅ Execution bridge works"
else
    echo "❌ Execution bridge failed"
    ALL_GOOD=false
fi

echo
echo "💡 Quick functionality test..."
if ./bin/ask-nix-modern --minimal "what is nix" >/dev/null 2>&1; then
    echo "✅ Basic query works"
else
    echo "❌ Basic query failed"
    ALL_GOOD=false
fi

echo
echo "=================================="
if [ "$ALL_GOOD" = true ]; then
    echo "✅ All checks passed! Nix for Humanity is ready to use."
    echo
    echo "Try these commands:"
    echo "  ./bin/ask-nix-modern 'install htop'"
    echo "  ./bin/ask-nix-modern 'search for editors'"
    echo "  ./bin/ask-nix-modern 'list my packages'"
else
    echo "❌ Some checks failed. Please fix the issues above."
    exit 1
fi
