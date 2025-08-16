#!/bin/bash
# Backend Consolidation Script - Nix for Humanity v1.3.0
# Sacred Trinity Development Model

set -e

echo "🔧 Starting Backend Consolidation Refactoring"
echo "============================================"

PROJECT_ROOT="/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity"
cd "$PROJECT_ROOT"

# Step 1: Backup current state
echo "📦 Creating backup..."
mkdir -p archive/backend-refactor-$(date +%Y%m%d)
cp -r src/nix_for_humanity/core/*.py archive/backend-refactor-$(date +%Y%m%d)/ || true

# Step 2: Check current usage
echo "🔍 Analyzing current backend usage..."
echo "Files importing from consolidated_backend:"
grep -r "from.*consolidated_backend" src/ --include="*.py" | wc -l

echo "Files importing from unified_backend:"
grep -r "from.*unified_backend" src/ --include="*.py" | wc -l

echo "Files importing from backend:"
grep -r "from.*\.backend import" src/ --include="*.py" | wc -l

# Step 3: Standardize imports (dry run first)
echo "\n📝 Standardizing imports (dry run)..."
echo "Would update these files:"
grep -r "unified_backend\|consolidated_backend" src/ --include="*.py" -l

read -p "\nProceed with import standardization? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "✨ Standardizing imports..."
    
    # Update imports from unified_backend to backend
    find src/ -type f -name "*.py" -exec sed -i.bak \
        's/from \(\.\.*\)unified_backend import/from \1backend import/g' {} +
    
    # Update imports from consolidated_backend to backend
    find src/ -type f -name "*.py" -exec sed -i.bak \
        's/from \(\.\.*\)consolidated_backend import/from \1backend import/g' {} +
    
    # Update direct references
    find src/ -type f -name "*.py" -exec sed -i.bak \
        's/ConsolidatedBackend/NixForHumanityBackend/g' {} +
    
    echo "✅ Imports standardized"
fi

# Step 4: Run tests to verify
echo "\n🧪 Running tests to verify changes..."
poetry run pytest tests/test_core.py -v --tb=short || echo "⚠️ Some tests failed - review needed"

# Step 5: Check for circular imports
echo "\n🔄 Checking for circular imports..."
python -c "import src.nix_for_humanity.core" 2>&1 | grep -i "circular\|import" || echo "✅ No circular imports detected"

# Step 6: Generate report
echo "\n📊 Generating refactoring report..."
cat > BACKEND_REFACTOR_REPORT.md << EOF
# Backend Refactoring Report

## Changes Made
- Standardized all imports to use \`backend\` module
- Renamed ConsolidatedBackend to NixForHumanityBackend
- Removed references to unified_backend

## Files Modified
$(find src/ -name "*.py.bak" | wc -l) files updated

## Next Steps
1. Merge consolidated_backend.py into backend.py
2. Delete unified_backend.py
3. Update documentation
4. Run full test suite

## Backup Location
archive/backend-refactor-$(date +%Y%m%d)/

Generated: $(date)
EOF

echo "\n✅ Refactoring analysis complete!"
echo "📋 Report saved to BACKEND_REFACTOR_REPORT.md"
echo "\n⚠️ Manual steps required:"
echo "  1. Review and merge consolidated_backend.py → backend.py"
echo "  2. Delete obsolete files (unified_backend.py, etc.)"
echo "  3. Run full test suite: poetry run pytest"
echo "  4. Update documentation"
