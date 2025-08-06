#!/usr/bin/env bash
# Quick demo of REAL execution capabilities

echo "🚀 Nix for Humanity - Real Execution Demo"
echo "========================================="
echo

# 1. Show that we're NOT in dry-run mode
echo "1️⃣ Testing installation with --yes flag (skips confirmation):"
echo "   Command: ./bin/ask-nix-modern --bridge --yes 'install hello'"
echo
./bin/ask-nix-modern --bridge --yes "install hello"
echo

# 2. Verify installation
echo "2️⃣ Verifying installation:"
if command -v hello >/dev/null 2>&1; then
    echo "   ✅ Package installed successfully!"
    echo "   Running 'hello' command:"
    hello
else
    echo "   ❌ Package not found in PATH"
fi
echo

# 3. List packages
echo "3️⃣ Listing installed packages:"
./bin/ask-nix-modern "show installed packages" | grep -E "(hello|Installed packages:|💡 Tip:)"
echo

# 4. Test educational error
echo "4️⃣ Testing educational error messages:"
echo "   Trying to install non-existent package..."
./bin/ask-nix-modern --bridge --yes "install fakepkg999" || true
echo

# 5. Clean up
echo "5️⃣ Cleaning up (removing hello):"
./bin/ask-nix-modern --bridge --yes "remove hello"
echo

echo "✅ Demo complete! The system executes commands by default."
echo "   Use --dry-run flag if you want to preview without executing."