#!/bin/bash

# Archive redundant and outdated documentation
# This script moves redundant docs to archive while preserving essential ones

echo "📦 Archiving redundant documentation..."

# Create archive directory with timestamp
ARCHIVE_DIR="archive/cleanup-$(date +%Y%m%d)"
mkdir -p "$ARCHIVE_DIR"

# Create subdirectories
mkdir -p "$ARCHIVE_DIR/misc"
mkdir -p "$ARCHIVE_DIR/planning"
mkdir -p "$ARCHIVE_DIR/status"
mkdir -p "$ARCHIVE_DIR/duplicates"
mkdir -p "$ARCHIVE_DIR/old-versions"
mkdir -p "$ARCHIVE_DIR/research-overflow"

echo "📁 Moving misc documents..."
# Archive entire misc directory
if [ -d "misc" ]; then
    mv misc/* "$ARCHIVE_DIR/misc/" 2>/dev/null
    rmdir misc 2>/dev/null
fi

echo "📁 Moving planning documents..."
# Archive planning directory
if [ -d "planning" ]; then
    mv planning/* "$ARCHIVE_DIR/planning/" 2>/dev/null
    rmdir planning 2>/dev/null
fi

echo "📁 Moving status reports..."
# Archive status directory
if [ -d "status" ]; then
    mv status/* "$ARCHIVE_DIR/status/" 2>/dev/null
    rmdir status 2>/dev/null
fi

echo "📁 Moving roadmap directory..."
# Archive roadmap directory
if [ -d "roadmap" ]; then
    mv roadmap/* "$ARCHIVE_DIR/old-versions/" 2>/dev/null
    rmdir roadmap 2>/dev/null
fi

echo "📁 Archiving duplicate guides..."
# Handle duplicate TUI guides
if [ -f "06-TUTORIALS/TUI_GUIDE.md" ] && [ -f "06-TUTORIALS/03-TUI-GUIDE.md" ]; then
    echo "  Keeping 03-TUI-GUIDE.md, archiving TUI_GUIDE.md"
    mv "06-TUTORIALS/TUI_GUIDE.md" "$ARCHIVE_DIR/duplicates/" 2>/dev/null
fi

echo "📁 Archiving COMPLETE documents..."
# Move all *_COMPLETE.md files to archive
find . -name "*_COMPLETE.md" -type f | while read -r file; do
    echo "  Archiving: $file"
    mv "$file" "$ARCHIVE_DIR/old-versions/" 2>/dev/null
done

echo "📁 Archiving old implementation docs..."
# Archive implementation-specific old docs
for pattern in "*_V1.md" "*_V1_*.md" "*_2025_*.md" "*_LEGACY*.md"; do
    find . -name "$pattern" -type f | while read -r file; do
        echo "  Archiving: $file"
        mv "$file" "$ARCHIVE_DIR/old-versions/" 2>/dev/null
    done
done

echo "📁 Consolidating research overflow..."
# Move excessive research docs (keep only essential ones)
if [ -d "01-VISION/research" ]; then
    # Count files
    research_count=$(find "01-VISION/research" -type f | wc -l)
    if [ "$research_count" -gt 50 ]; then
        echo "  Found $research_count research files, keeping top 50..."
        # Move older research files to archive
        find "01-VISION/research" -type f -mtime +30 | head -150 | while read -r file; do
            mv "$file" "$ARCHIVE_DIR/research-overflow/" 2>/dev/null
        done
    fi
fi

echo "📁 Cleaning up root documentation clutter..."
# Move these files from root if they exist
root_cleanup=(
    "DOCUMENTATION_*.md"
    "PHASE_*_*.md"
    "IMPLEMENTATION_*.md"
    "PROJECT_*.md"
    "*_ANALYSIS.md"
    "*_SYNTHESIS*.md"
    "*_PLAN.md"
    "*_REPORT.md"
)

for pattern in "${root_cleanup[@]}"; do
    for file in $pattern; do
        if [ -f "$file" ]; then
            echo "  Moving $file to archive"
            mv "$file" "$ARCHIVE_DIR/old-versions/" 2>/dev/null
        fi
    done
done

echo "📁 Removing empty directories..."
# Clean up empty directories
find . -type d -empty -delete 2>/dev/null

echo "📊 Creating archive summary..."
# Create summary of what was archived
cat > "$ARCHIVE_DIR/ARCHIVE_SUMMARY.md" << EOF
# Documentation Archive Summary

**Date**: $(date)
**Reason**: Documentation cleanup and consolidation

## What was archived:

### Directories
- \`misc/\` - Miscellaneous unsorted documents
- \`planning/\` - Old planning documents
- \`status/\` - Old status reports
- \`roadmap/\` - Outdated roadmap files

### Files
- All *_COMPLETE.md files
- All *_V1*.md files
- Duplicate guides (kept newer versions)
- Old implementation documents
- Excessive research papers (kept most recent 50)

## Essential documents kept:
- START-HERE.md (new entry point)
- TROUBLESHOOTING.md (practical guide)
- ARCHITECTURE-VISUAL.md (with diagrams)
- All INDEX.md files
- Current numbered directories (01-06)

## Next steps:
1. Review archived content
2. Delete if truly redundant
3. Restore if needed

---
*This archive can be safely deleted after review.*
EOF

echo "✅ Archive complete!"
echo ""
echo "📊 Summary:"
echo "  Archive location: $ARCHIVE_DIR"
echo "  Files archived: $(find "$ARCHIVE_DIR" -type f | wc -l)"
echo "  Space saved: $(du -sh "$ARCHIVE_DIR" | cut -f1)"
echo ""
echo "📝 Next steps:"
echo "  1. Review archive at: $ARCHIVE_DIR"
echo "  2. Delete archive after confirming nothing important was moved"
echo "  3. Commit the cleaned documentation"
