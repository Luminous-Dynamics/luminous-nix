#!/usr/bin/env bash

# Archive Duplicates Script
# Purpose: Consolidate all duplicate implementations into a single archive
# Date: 2025-08-10

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create archive directory with timestamp
ARCHIVE_DIR=".archive-2025-08-10"
ARCHIVE_LOG="${ARCHIVE_DIR}/ARCHIVE_LOG.md"

echo -e "${BLUE}📦 Starting Archive Consolidation${NC}"
echo -e "${BLUE}Archive Directory: ${ARCHIVE_DIR}${NC}"
echo ""

# Create archive structure
mkdir -p "${ARCHIVE_DIR}/cli-variants"
mkdir -p "${ARCHIVE_DIR}/implementations"
mkdir -p "${ARCHIVE_DIR}/features"
mkdir -p "${ARCHIVE_DIR}/old-archives"
mkdir -p "${ARCHIVE_DIR}/docs"

# Initialize archive log
cat > "${ARCHIVE_LOG}" << 'EOF'
# Archive Log - 2025-08-10

## Purpose
This archive contains duplicate implementations and deprecated code discovered during architecture review.
These files were creating confusion and maintenance burden.

## Archive Structure
- `cli-variants/` - Duplicate CLI entry points (should only have one: bin/ask-nix)
- `implementations/` - Alternative implementation attempts
- `features/` - Versioned feature directories
- `old-archives/` - Previous archive directories
- `docs/` - Outdated documentation

## Files Archived

### CLI Variants (30+ duplicates)
These were all variations of the same CLI tool. We should only have `bin/ask-nix`.

EOF

# Archive CLI variants
echo -e "${YELLOW}📋 Archiving CLI variants...${NC}"
cd bin/ 2>/dev/null || { echo "bin/ directory not found"; exit 0; }

for script in ask-nix-*; do
    if [[ -f "$script" && "$script" != "ask-nix" ]]; then
        echo "  Moving: $script"
        mv "$script" "../${ARCHIVE_DIR}/cli-variants/" 2>/dev/null || true
        echo "- \`bin/$script\` - Duplicate CLI variant" >> "../${ARCHIVE_LOG}"
    fi
done

# Archive archive directories
echo -e "${YELLOW}📋 Consolidating old archive directories...${NC}"
cd ..
for dir in archive archive-*; do
    if [[ -d "$dir" && "$dir" != "${ARCHIVE_DIR}" ]]; then
        echo "  Moving: $dir/"
        mv "$dir" "${ARCHIVE_DIR}/old-archives/" 2>/dev/null || true
        echo "- \`$dir/\` - Old archive directory" >> "${ARCHIVE_LOG}"
    fi
done

# Archive versioned features
echo -e "${YELLOW}📋 Archiving versioned features...${NC}"
if [[ -d "features" ]]; then
    cd features/
    for dir in v1.0 v2.0 v3.0 v4.0; do
        if [[ -d "$dir" ]]; then
            echo "  Moving: features/$dir/"
            mv "$dir" "../${ARCHIVE_DIR}/features/" 2>/dev/null || true
            echo "- \`features/$dir/\` - Versioned feature directory" >> "../${ARCHIVE_LOG}"
        fi
    done
    cd ..
fi

# Archive duplicate implementations
echo -e "${YELLOW}📋 Archiving duplicate implementations...${NC}"

# Move mvp_simplified variants
if [[ -d "mvp_simplified" ]]; then
    echo "  Moving: mvp_simplified/"
    mv "mvp_simplified" "${ARCHIVE_DIR}/implementations/" 2>/dev/null || true
    echo "- \`mvp_simplified/\` - Alternative MVP implementation" >> "${ARCHIVE_LOG}"
fi

# Move nodejs-mvp if it exists
if [[ -d "implementations/nodejs-mvp" ]]; then
    echo "  Moving: implementations/nodejs-mvp/"
    mv "implementations/nodejs-mvp" "${ARCHIVE_DIR}/implementations/" 2>/dev/null || true
    echo "- \`implementations/nodejs-mvp/\` - Old Node.js implementation" >> "${ARCHIVE_LOG}"
fi

# Move web-based implementation (deprecated)
if [[ -d "implementations/web-based" ]]; then
    echo "  Moving: implementations/web-based/"
    mv "implementations/web-based" "${ARCHIVE_DIR}/implementations/" 2>/dev/null || true
    echo "- \`implementations/web-based/\` - Deprecated web implementation" >> "${ARCHIVE_LOG}"
fi

# Add summary to log
cat >> "${ARCHIVE_LOG}" << 'EOF'

## Why These Were Archived

### CLI Variants
We had 30+ variants like `ask-nix-v2`, `ask-nix-enhanced`, etc. This created:
- Confusion about which to use
- Maintenance burden
- Inconsistent behavior
- Code duplication

**Solution**: Single entry point `bin/ask-nix` with all features integrated.

### Multiple Archives
Having multiple archive directories (`archive/`, `archive-old/`, etc.) nested within each other was:
- Confusing
- Taking up unnecessary space
- Making it hard to find things

**Solution**: Single `.archive-YYYY-MM-DD/` directory per consolidation.

### Versioned Features
Directories like `features/v1.0/`, `features/v2.0/` suggested we needed multiple versions simultaneously.

**Solution**: Use git branches/tags for versions, not directories.

### Alternative Implementations
Multiple attempts at the same functionality (`mvp_simplified`, `nodejs-mvp`, etc.) created confusion.

**Solution**: One canonical implementation in `src/nix_for_humanity/`.

## Recovery Instructions

If you need to recover any of these files:

1. They are safely stored in this archive
2. Review why they were archived first
3. If truly needed, copy (don't move) back to proper location
4. Update to match current architecture before using

## Lessons Learned

1. **Check before creating** - Always search for existing implementations
2. **Edit don't duplicate** - Modify existing code instead of creating new versions
3. **Use git for versions** - Let version control handle iterations
4. **One source of truth** - Single implementation per feature
5. **Clean as you go** - Don't let duplicates accumulate

---
*Archived by: Archive Consolidation Script*
*Date: 2025-08-10*
*Purpose: Clean up duplicate implementations discovered during architecture review*
EOF

# Count what was archived
echo ""
echo -e "${GREEN}✅ Archive Complete!${NC}"
echo ""
echo "📊 Summary:"
echo "  - Archive location: ${ARCHIVE_DIR}/"
echo "  - Log file: ${ARCHIVE_LOG}"
echo ""
echo "📝 Next Steps:"
echo "  1. Review ${ARCHIVE_LOG} to understand what was archived"
echo "  2. Commit the archive to git for history"
echo "  3. Add ${ARCHIVE_DIR}/ to .gitignore if desired"
echo "  4. Focus on the canonical implementations in src/"
echo ""
echo -e "${BLUE}Remember: We now have ONE source of truth for each component!${NC}"
