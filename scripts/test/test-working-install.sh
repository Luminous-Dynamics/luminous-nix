#!/usr/bin/env bash
echo "🌟 Nix for Humanity - Live Installation Test"
echo "==========================================="
echo ""
echo "Let's install a small, useful package: 'jq' (JSON processor)"
echo ""

# Check if jq is already installed
if which jq > /dev/null 2>&1; then
    echo "⚠️  jq is already installed at: $(which jq)"
    echo "Let's try 'tree' instead..."
    PACKAGE="tree"
else
    PACKAGE="jq"
fi

# Check if tree is already installed
if [ "$PACKAGE" = "tree" ] && which tree > /dev/null 2>&1; then
    echo "⚠️  tree is also already installed at: $(which tree)"
    echo "Let's try 'bat' (better cat)..."
    PACKAGE="bat"
fi

echo ""
echo "📦 Installing $PACKAGE using natural language..."
echo ""
echo "Command: ./bin/nix-profile-do 'install $PACKAGE'"
echo ""

# First show dry run
echo "1️⃣ First, let's see what would happen (dry run):"
./bin/nix-profile-do "install $PACKAGE" --dry-run

echo ""
echo "2️⃣ Now let's actually install it (this may take 30+ seconds):"
echo "   Running in background to avoid timeout..."

# Run in background and capture PID
./bin/nix-profile-do "install $PACKAGE" > /tmp/nix-install.log 2>&1 &
PID=$!

# Monitor for 10 seconds
echo -n "   Installing"
for i in {1..10}; do
    sleep 1
    echo -n "."
    if ! ps -p $PID > /dev/null; then
        echo " Done!"
        break
    fi
done

# Check if still running
if ps -p $PID > /dev/null; then
    echo ""
    echo "   ⏳ Installation still in progress (downloading from cache)..."
    echo "   Check progress with: tail -f /tmp/nix-install.log"
    echo "   Process PID: $PID"
else
    # Show result
    echo ""
    echo "3️⃣ Installation result:"
    tail -5 /tmp/nix-install.log
fi

echo ""
echo "✅ To verify installation later:"
echo "   which $PACKAGE"
echo ""
echo "📝 This demonstrates that Nix for Humanity can:"
echo "   - Understand 'install $PACKAGE' in natural language"
echo "   - Convert to proper 'nix profile install' command"
echo "   - Actually execute the installation"
