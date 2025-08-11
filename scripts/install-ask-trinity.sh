#!/usr/bin/env bash
# Install ask-trinity command for easy access

echo "📦 Installing ask-trinity command..."

# Create a wrapper script in user's bin directory
mkdir -p ~/bin

cat > ~/bin/ask-trinity << 'EOF'
#!/usr/bin/env bash
exec /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/bin/ask-trinity "$@"
EOF

chmod +x ~/bin/ask-trinity

# Add to PATH if not already there
if ! echo $PATH | grep -q "$HOME/bin"; then
    echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
    echo 'export PATH="$HOME/bin:$PATH"' >> ~/.zshrc 2>/dev/null || true
    echo "📝 Added ~/bin to PATH in shell config"
    echo "   Please run: source ~/.bashrc"
    echo "   Or start a new terminal"
else
    echo "✅ ~/bin already in PATH"
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "You can now use:"
echo "  ask-trinity 'your nixos question'"
echo ""
echo "Examples:"
echo "  ask-trinity 'how do I install firefox?'"
echo "  ask-trinity 'explain flakes to a beginner'"
echo "  ask-trinity 'write a systemd service'"
