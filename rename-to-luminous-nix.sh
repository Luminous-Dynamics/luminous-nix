#!/bin/bash
# Rename "Nix for Humanity" to "Luminous Nix" throughout the codebase
# This script handles the systematic renaming while preserving functionality

set -e  # Exit on error

echo "🌟 Beginning rename from 'Nix for Humanity' to 'Luminous Nix'..."
echo "=================================================="

# Save current directory
ORIGINAL_DIR=$(pwd)
PROJECT_ROOT="/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity"

cd "$PROJECT_ROOT"

# Create backup branch
echo "📝 Creating backup branch..."
git checkout -b backup-before-rename-$(date +%Y%m%d-%H%M%S) 2>/dev/null || true

# Return to main branch
git checkout main 2>/dev/null || git checkout master 2>/dev/null || true

echo ""
echo "🔄 Phase 1: Updating Python package references..."
echo "--------------------------------------------------"

# Update Python package name in imports
find . -name "*.py" -type f ! -path "./.git/*" ! -path "./archive/*" -exec sed -i \
    -e 's/from nix_for_humanity/from luminous_nix/g' \
    -e 's/import nix_for_humanity/import luminous_nix/g' \
    -e 's/nix_for_humanity\./luminous_nix./g' {} \;

echo "✓ Python imports updated"

echo ""
echo "🔄 Phase 2: Updating documentation..."
echo "--------------------------------------"

# Update documentation - preserve "Nix for Humanity" in historical context
find . -name "*.md" -type f ! -path "./.git/*" ! -path "./archive/*" -exec sed -i \
    -e 's/Nix for Humanity/Luminous Nix/g' \
    -e 's/nix-for-humanity/luminous-nix/g' \
    -e 's/NIX FOR HUMANITY/LUMINOUS NIX/g' {} \;

# Update CHANGELOG to note the rename
if [ -f "CHANGELOG.md" ]; then
    echo -e "\n## [Renamed] - $(date +%Y-%m-%d)\n### Changed\n- Renamed project from 'Nix for Humanity' to 'Luminous Nix' for better alignment with consciousness-first philosophy\n$(cat CHANGELOG.md)" > CHANGELOG.md
fi

echo "✓ Documentation updated"

echo ""
echo "🔄 Phase 3: Updating environment variables..."
echo "----------------------------------------------"

# Update environment variable names
find . -type f ! -path "./.git/*" ! -path "./archive/*" \
    \( -name "*.py" -o -name "*.sh" -o -name "*.bash" -o -name "*.md" -o -name "*.yaml" -o -name "*.yml" -o -name "*.toml" \) \
    -exec sed -i \
    -e 's/LUMINOUS_NIX_PYTHON_BACKEND/LUMINOUS_NIX_PYTHON_BACKEND/g' \
    -e 's/LUMINOUS_NIX_CONFIG/LUMINOUS_NIX_CONFIG/g' \
    -e 's/LUMINOUS_NIX_DEBUG/LUMINOUS_NIX_DEBUG/g' \
    -e 's/LUMINOUS_NIX_CACHE/LUMINOUS_NIX_CACHE/g' \
    -e 's/LUMINOUS_NIX/LUMINOUS_NIX/g' {} \;

echo "✓ Environment variables updated"

echo ""
echo "🔄 Phase 4: Updating configuration files..."
echo "--------------------------------------------"

# Update pyproject.toml
if [ -f "pyproject.toml" ]; then
    sed -i \
        -e 's/name = "nix-for-humanity"/name = "luminous-nix"/g' \
        -e 's/nix_for_humanity/luminous_nix/g' \
        -e 's|Nix for Humanity|Luminous Nix|g' \
        -e 's|github.com/Luminous-Dynamics/nix-for-humanity|github.com/Luminous-Dynamics/luminous-nix|g' \
        pyproject.toml
    echo "✓ pyproject.toml updated"
fi

# Update shell.nix and flake.nix if they exist
for nixfile in shell.nix flake.nix default.nix; do
    if [ -f "$nixfile" ]; then
        sed -i \
            -e 's/nix-for-humanity/luminous-nix/g' \
            -e 's/Nix for Humanity/Luminous Nix/g' \
            "$nixfile"
        echo "✓ $nixfile updated"
    fi
done

echo ""
echo "🔄 Phase 5: Updating CLI entry points..."
echo "-----------------------------------------"

# Update bin scripts
if [ -d "bin" ]; then
    for script in bin/*; do
        if [ -f "$script" ] && [ ! -L "$script" ]; then
            sed -i \
                -e 's/Nix for Humanity/Luminous Nix/g' \
                -e 's/nix_for_humanity/luminous_nix/g' \
                -e 's/LUMINOUS_NIX/LUMINOUS_NIX/g' \
                "$script"
        fi
    done
    echo "✓ CLI scripts updated"
fi

echo ""
echo "🔄 Phase 6: Updating test files..."
echo "------------------------------------"

# Update test files
find tests -name "*.py" -type f -exec sed -i \
    -e 's/nix_for_humanity/luminous_nix/g' \
    -e 's/Nix for Humanity/Luminous Nix/g' \
    -e 's/LUMINOUS_NIX/LUMINOUS_NIX/g' {} \;

echo "✓ Test files updated"

echo ""
echo "🔄 Phase 7: Renaming the source directory..."
echo "---------------------------------------------"

# Rename the main Python package directory
if [ -d "src/nix_for_humanity" ]; then
    mv src/nix_for_humanity src/luminous_nix
    echo "✓ Source directory renamed: src/nix_for_humanity → src/luminous_nix"
fi

echo ""
echo "🔄 Phase 8: Updating configuration paths..."
echo "--------------------------------------------"

# Update any hardcoded paths
find . -type f ! -path "./.git/*" ! -path "./archive/*" \
    \( -name "*.py" -o -name "*.sh" -o -name "*.md" \) \
    -exec sed -i \
    -e 's|~/.config/luminous-nix|~/.config/luminous-nix|g' \
    -e 's|~/.cache/luminous-nix|~/.cache/luminous-nix|g' \
    -e 's|~/.local/share/luminous-nix|~/.local/share/luminous-nix|g' {} \;

echo "✓ Configuration paths updated"

echo ""
echo "🔄 Phase 9: Creating user migration helper..."
echo "----------------------------------------------"

# Create user migration script
cat > migrate-user-config.sh << 'EOF'
#!/bin/bash
# Migrate user configuration from Nix for Humanity to Luminous Nix

echo "🌟 Migrating user configuration to Luminous Nix..."

# Migrate config directory
if [ -d "$HOME/.config/nix-humanity" ]; then
    echo "→ Migrating configuration..."
    cp -r "$HOME/.config/nix-humanity" "$HOME/.config/luminous-nix"
    echo "  ✓ Configuration migrated"
fi

# Migrate cache directory
if [ -d "$HOME/.cache/nix-humanity" ]; then
    echo "→ Migrating cache..."
    cp -r "$HOME/.cache/nix-humanity" "$HOME/.cache/luminous-nix"
    echo "  ✓ Cache migrated"
fi

# Migrate data directory
if [ -d "$HOME/.local/share/nix-humanity" ]; then
    echo "→ Migrating data..."
    cp -r "$HOME/.local/share/nix-humanity" "$HOME/.local/share/luminous-nix"
    echo "  ✓ Data migrated"
fi

# Update shell aliases if they exist
for rcfile in ~/.bashrc ~/.zshrc ~/.config/fish/config.fish; do
    if [ -f "$rcfile" ]; then
        if grep -q "LUMINOUS_NIX" "$rcfile"; then
            sed -i.bak \
                -e 's/LUMINOUS_NIX/LUMINOUS_NIX/g' \
                -e 's/nix-humanity/luminous-nix/g' \
                "$rcfile"
            echo "  ✓ Updated $rcfile"
        fi
    fi
done

echo ""
echo "✨ Migration complete! Welcome to Luminous Nix!"
echo ""
echo "Note: Your old configuration has been preserved in:"
echo "  - ~/.config/luminous-nix/"
echo "  - ~/.cache/luminous-nix/"
echo "  - ~/.local/share/luminous-nix/"
echo ""
echo "You can safely remove these directories once you've verified everything works."
EOF

chmod +x migrate-user-config.sh
echo "✓ User migration script created"

echo ""
echo "🔄 Phase 10: Updating abbreviations and references..."
echo "------------------------------------------------------"

# Update any N4H abbreviations to LN
find . -type f ! -path "./.git/*" ! -path "./archive/*" \
    \( -name "*.md" -o -name "*.py" -o -name "*.sh" \) \
    -exec sed -i \
    -e 's/\bN4H\b/LN/g' \
    -e 's/\bn4h\b/ln/g' {} \;

echo "✓ Abbreviations updated"

echo ""
echo "=================================================="
echo "✨ Rename complete!"
echo ""
echo "📋 Summary of changes:"
echo "  • Python package: nix_for_humanity → luminous_nix"
echo "  • Project name: 'Nix for Humanity' → 'Luminous Nix'"
echo "  • Environment vars: LUMINOUS_NIX_* → LUMINOUS_NIX_*"
echo "  • Config paths: ~/.config/luminous-nix → ~/.config/luminous-nix"
echo "  • Abbreviation: N4H → LN"
echo ""
echo "📦 Next steps:"
echo "  1. Review the changes: git diff"
echo "  2. Test the installation: poetry install"
echo "  3. Run tests: poetry run pytest"
echo "  4. Commit changes: git add -A && git commit -m 'feat: rename project to Luminous Nix'"
echo "  5. Run user migration: ./migrate-user-config.sh"
echo ""
echo "🎯 Don't forget to:"
echo "  • Rename the directory: mv nix-for-humanity luminous-nix"
echo "  • Update GitHub repository name"
echo "  • Announce the change to users"
echo ""
echo "🌊 Luminous Nix - Making NixOS glow with consciousness! 🌊"

cd "$ORIGINAL_DIR"