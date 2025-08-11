#!/bin/bash
# Quick Poetry installation for Nix for Humanity
# This bypasses heavy ML dependencies for faster setup

echo "🚀 Quick Poetry Installation (TUI + CLI only)"
echo "==========================================="

# Set project-local virtualenv
export POETRY_VIRTUALENVS_IN_PROJECT=true
export POETRY_VIRTUALENVS_CREATE=true

# Create .venv if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate it
source .venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install poetry in the venv
echo "📦 Installing Poetry..."
pip install poetry

# Install core + TUI dependencies only (skip ML deps)
echo "🎨 Installing core and TUI dependencies..."
poetry install --only main -E tui --no-interaction

# Create simple launcher
cat > run-tui.sh << 'EOF'
#!/bin/bash
source .venv/bin/activate
export PYTHONPATH="${PWD}/src:$PYTHONPATH"
python -m nix_humanity.ui.main_app "$@"
EOF
chmod +x run-tui.sh

cat > run-cli.sh << 'EOF'
#!/bin/bash
source .venv/bin/activate
export PYTHONPATH="${PWD}/src:$PYTHONPATH"
python -m nix_humanity.interfaces.cli "$@"
EOF
chmod +x run-cli.sh

echo ""
echo "✅ Quick installation complete!"
echo ""
echo "🎯 Test commands:"
echo "  ./run-cli.sh help          # Test CLI"
echo "  ./run-tui.sh               # Launch TUI"
echo ""
echo "💡 For full features (voice, ML):"
echo "  poetry install -E voice -E ml"
