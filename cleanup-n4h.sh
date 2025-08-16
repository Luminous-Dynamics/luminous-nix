#!/usr/bin/env bash
# 🧹 Nix for Humanity (N4H) Cleanup Script
# Purpose: Clean up code sprawl, consolidate duplicates, and organize the project

set -e  # Exit on error

echo "🧹 Starting Nix for Humanity (N4H) Cleanup..."
echo "============================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track changes
CHANGES_MADE=0

# Function to log actions
log_action() {
    echo -e "${GREEN}✓${NC} $1"
    ((CHANGES_MADE++))
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

# 1. Check current sprawl score
echo -e "\n📊 Checking current sprawl score..."
if command -v python3 &> /dev/null && [ -f scripts/detect-sprawl.py ]; then
    python3 scripts/detect-sprawl.py || true
fi

# 2. Create archive directory with timestamp
ARCHIVE_DIR=".archive-$(date +%Y%m%d-%H%M%S)"
echo -e "\n📁 Creating archive directory: $ARCHIVE_DIR"
mkdir -p "$ARCHIVE_DIR"
mkdir -p "$ARCHIVE_DIR/docs"
mkdir -p "$ARCHIVE_DIR/tests"
mkdir -p "$ARCHIVE_DIR/old-scripts"

# 3. Archive phantom test features (already identified)
echo -e "\n🧪 Archiving phantom test features..."
if [ -d "tests/archive/phantom-features-2025-08-12" ]; then
    if [ "$(ls -A tests/archive/phantom-features-2025-08-12)" ]; then
        cp -r tests/archive/phantom-features-2025-08-12 "$ARCHIVE_DIR/tests/"
        log_action "Archived phantom test features"
    fi
fi

# 4. Consolidate duplicate backend implementations
echo -e "\n🔧 Consolidating backend implementations..."
if [ -f "src/nix_for_humanity/nix/native_backend.py" ] && [ -f "src/nix_for_humanity/core/backend.py" ]; then
    log_warning "Found duplicate backends - manual consolidation needed:"
    echo "  - src/nix_for_humanity/nix/native_backend.py"
    echo "  - src/nix_for_humanity/core/backend.py"
    echo "  Recommendation: Merge into src/nix_for_humanity/core/backend.py"
fi

# 5. Archive old documentation that's been superseded
echo -e "\n📚 Archiving superseded documentation..."
SUPERSEDED_DOCS=(
    "docs/ARCHIVE/superseded"
    "docs/ARCHIVE/old-status"
    "docs/ARCHIVE/old-releases"
    "docs/ARCHIVE/old-implementations"
)

for doc_dir in "${SUPERSEDED_DOCS[@]}"; do
    if [ -d "$doc_dir" ]; then
        cp -r "$doc_dir" "$ARCHIVE_DIR/docs/" 2>/dev/null && \
            log_action "Archived $(basename $doc_dir)" || true
    fi
done

# 6. Clean up old refactoring artifacts
echo -e "\n🗑️ Cleaning up old refactoring artifacts..."
OLD_ARTIFACTS=(
    "archive/backend-refactor-20250811"
    "archive/ui-cleanup-20250811"
    "archive/voice-cleanup-20250811"
    "archive/2025-08-12-reorganization"
)

for artifact in "${OLD_ARTIFACTS[@]}"; do
    if [ -d "$artifact" ]; then
        cp -r "$artifact" "$ARCHIVE_DIR/" 2>/dev/null && \
            log_action "Archived $(basename $artifact)" || true
    fi
done

# 7. Remove empty directories
echo -e "\n🧹 Removing empty directories..."
find . -type d -empty -not -path "./.git/*" -not -path "./__pycache__/*" -delete 2>/dev/null && \
    log_action "Removed empty directories" || true

# 8. Create N4H abbreviation helper
echo -e "\n✨ Creating N4H abbreviation helpers..."
cat > "N4H_ALIASES.md" << 'EOF'
# N4H (Nix for Humanity) Abbreviation Guide

## When to Use N4H vs Full Name

### Use "N4H" in:
- Internal code comments
- Variable names (e.g., `N4H_CONFIG_PATH`)
- Log messages
- Development documentation
- Scripts and tooling

### Use "Nix for Humanity" in:
- User-facing messages
- Public documentation
- README files
- Marketing materials
- Error messages shown to users

## Common Abbreviations:
- N4H = Nix for Humanity
- N4H-TUI = Nix for Humanity Terminal UI
- N4H-API = Nix for Humanity API
- N4H-CLI = Nix for Humanity CLI

## Environment Variables:
```bash
export N4H_HOME=/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity
export N4H_PYTHON_BACKEND=true
export N4H_DEBUG=false
```
EOF
log_action "Created N4H abbreviation guide"

# 9. Update gitignore to prevent future sprawl
echo -e "\n📝 Updating .gitignore..."
if ! grep -q "^\\.archive-\*" .gitignore 2>/dev/null; then
    echo -e "\n# Archive directories" >> .gitignore
    echo ".archive-*" >> .gitignore
    log_action "Updated .gitignore for archive directories"
fi

# 10. Generate cleanup report
echo -e "\n📊 Generating cleanup report..."
cat > "CLEANUP_REPORT_$(date +%Y%m%d).md" << EOF
# N4H Cleanup Report - $(date +%Y-%m-%d)

## Summary
- Changes made: $CHANGES_MADE
- Archive directory: $ARCHIVE_DIR
- Current file count: $(find . -type f -not -path "./.git/*" | wc -l)
- Python files: $(find . -name "*.py" -not -path "./.git/*" | wc -l)
- Documentation files: $(find . -name "*.md" -not -path "./.git/*" | wc -l)

## Actions Taken
1. Created archive directory: $ARCHIVE_DIR
2. Archived phantom test features
3. Identified duplicate backends for consolidation
4. Archived superseded documentation
5. Cleaned up old refactoring artifacts
6. Removed empty directories
7. Created N4H abbreviation guide
8. Updated .gitignore

## Manual Actions Needed
1. Consolidate duplicate backend implementations:
   - Merge src/nix_for_humanity/nix/native_backend.py into src/nix_for_humanity/core/backend.py
   - Update all imports accordingly

2. Review and potentially archive:
   - Old session summaries (SESSION_*.md files)
   - Completed task reports (*_COMPLETE.md files)
   - Old test results

3. Consider using N4H abbreviation in:
   - Internal documentation
   - Code comments
   - Script names

## Sprawl Prevention Reminders
- Run \`python scripts/detect-sprawl.py\` before each session
- Never create *_enhanced.py, *_v2.py variants
- Use git branches for experiments
- One implementation per feature
EOF

log_action "Generated cleanup report"

# 11. Show disk space saved
echo -e "\n💾 Disk space analysis:"
if command -v du &> /dev/null; then
    echo "Archive size: $(du -sh $ARCHIVE_DIR 2>/dev/null | cut -f1)"
    echo "Project size: $(du -sh . 2>/dev/null | cut -f1)"
fi

# Final summary
echo -e "\n✨ ${GREEN}Cleanup Complete!${NC}"
echo "============================================="
echo "Total changes made: $CHANGES_MADE"
echo "Archive created at: $ARCHIVE_DIR"
echo ""
echo "📋 Next steps:"
echo "1. Review CLEANUP_REPORT_$(date +%Y%m%d).md"
echo "2. Manually consolidate the duplicate backends"
echo "3. Review N4H_ALIASES.md for abbreviation guidelines"
echo "4. Consider removing the archive after review"
echo "5. Run 'python scripts/detect-sprawl.py' to verify improvements"