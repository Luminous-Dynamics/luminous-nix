#!/bin/sh
# Finish renaming Nix for Humanity to Luminous Nix

echo "🔄 Updating environment variables..."

# Update all environment variable references
find . -type f \( -name "*.py" -o -name "*.sh" -o -name "*.md" \) ! -path "./.git/*" ! -path "./archive/*" -exec sed -i \
    -e 's/LUMINOUS_NIX_PYTHON_BACKEND/LUMINOUS_NIX_PYTHON_BACKEND/g' \
    -e 's/LUMINOUS_NIX_CONFIG/LUMINOUS_NIX_CONFIG/g' \
    -e 's/LUMINOUS_NIX_DEBUG/LUMINOUS_NIX_DEBUG/g' \
    -e 's/LUMINOUS_NIX_CACHE/LUMINOUS_NIX_CACHE/g' \
    -e 's/LUMINOUS_NIX/LUMINOUS_NIX/g' {} \; 2>/dev/null

echo "✓ Environment variables updated"

echo "🔄 Updating configuration paths..."

# Update config paths
find . -type f \( -name "*.py" -o -name "*.sh" -o -name "*.md" \) ! -path "./.git/*" ! -path "./archive/*" -exec sed -i \
    -e 's|~/.config/luminous-nix|~/.config/luminous-nix|g' \
    -e 's|~/.cache/luminous-nix|~/.cache/luminous-nix|g' \
    -e 's|~/.local/share/luminous-nix|~/.local/share/luminous-nix|g' {} \; 2>/dev/null

echo "✓ Configuration paths updated"

echo "🔄 Updating test files..."

# Update test imports
find tests -name "*.py" -exec sed -i \
    -e 's/from nix_for_humanity/from luminous_nix/g' \
    -e 's/import nix_for_humanity/import luminous_nix/g' \
    -e 's/nix_for_humanity\./luminous_nix./g' {} \; 2>/dev/null

echo "✓ Test files updated"

echo "🔄 Updating abbreviations..."

# Update N4H abbreviations
find . -type f \( -name "*.md" -o -name "*.py" \) ! -path "./.git/*" ! -path "./archive/*" -exec sed -i \
    -e 's/\bN4H\b/LN/g' \
    -e 's/\bn4h\b/ln/g' {} \; 2>/dev/null

echo "✓ Abbreviations updated"

echo ""
echo "✨ Rename complete! Key changes:"
echo "  • Python package: nix_for_humanity → luminous_nix"  
echo "  • Environment vars: LUMINOUS_NIX_* → LUMINOUS_NIX_*"
echo "  • Config paths: ~/.config/luminous-nix → ~/.config/luminous-nix"
echo ""
echo "📋 Next steps:"
echo "  1. Run: poetry install"
echo "  2. Test: poetry run pytest"
echo "  3. Rename directory: cd ../.. && mv nix-for-humanity luminous-nix"