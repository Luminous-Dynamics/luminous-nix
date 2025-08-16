#!/usr/bin/env bash

# Archive outdated documentation for Nix for Humanity
# This script moves obsolete docs to archive directories
# while preserving references that might still be needed

set -e

echo "📦 Starting documentation archival process..."

# Create archive directories
mkdir -p docs/ARCHIVE/old-releases
mkdir -p docs/ARCHIVE/old-status
mkdir -p docs/ARCHIVE/old-implementations
mkdir -p docs/ARCHIVE/superseded

# Function to archive a file
archive_file() {
    local file="$1"
    local target_dir="$2"
    
    if [ -f "$file" ]; then
        echo "  Archiving: $file"
        mv "$file" "$target_dir/" 2>/dev/null || true
    fi
}

# Archive old release notes (keeping v1.3.0 as current)
echo "\n📝 Archiving old release documentation..."
archive_file "RELEASE-v0.1.0-alpha.md" "docs/ARCHIVE/old-releases"
archive_file "RELEASE-v0.1.0-alpha-HONEST.md" "docs/ARCHIVE/old-releases"
archive_file "RELEASE-v1.0.1.md" "docs/ARCHIVE/old-releases"
archive_file "RELEASE_v1.0.md" "docs/ARCHIVE/old-releases"
archive_file "RELEASE-v1.1.0.md" "docs/ARCHIVE/old-releases"
archive_file "RELEASE_v1.2.0.md" "docs/ARCHIVE/old-releases"
archive_file "V1.1.0_PROGRESS.md" "docs/ARCHIVE/old-releases"

# Archive old status reports
echo "\n📊 Archiving old status reports..."
for file in docs/status/*.md; do
    if [ -f "$file" ]; then
        archive_file "$file" "docs/ARCHIVE/old-status"
    fi
done

# Archive superseded documentation
echo "\n🔄 Archiving superseded documentation..."
archive_file "README-HONEST.md" "docs/ARCHIVE/superseded"
archive_file "README-COMPARISON.md" "docs/ARCHIVE/superseded"
archive_file "README-NEW.md" "docs/ARCHIVE/superseded"
archive_file "CLAUDE_SETUP_INSTRUCTIONS.md" "docs/ARCHIVE/superseded"  # Now in CLAUDE.md
archive_file "TEST-RESULTS-BEFORE-PROMOTION.md" "docs/ARCHIVE/superseded"
archive_file "FIX_ENVIRONMENT_PROPERLY.md" "docs/ARCHIVE/superseded"
archive_file "PATTERN-FIX-COMPLETE.md" "docs/ARCHIVE/superseded"
archive_file "CLI-FIXES-COMPLETE.md" "docs/ARCHIVE/superseded"
archive_file "PRE-COMMIT-FIXES-COMPLETE.md" "docs/ARCHIVE/superseded"
archive_file "PRE-COMMIT-ENHANCEMENTS.md" "docs/ARCHIVE/superseded"
archive_file "VOICE_PIPELINE_SUCCESS.md" "docs/ARCHIVE/superseded"
archive_file "VOICE_SETUP_PROGRESS.md" "docs/ARCHIVE/superseded"
archive_file "DEMO-SUITE-COMPLETE.md" "docs/ARCHIVE/superseded"

# Archive old implementation plans
echo "\n🏗️ Archiving old implementation plans..."
archive_file "IMPLEMENTATION_ROADMAP.md" "docs/ARCHIVE/old-implementations"
archive_file "IMPLEMENTATION_PRIORITY_LIST.md" "docs/ARCHIVE/old-implementations"
archive_file "IMPROVEMENT_ROADMAP.md" "docs/ARCHIVE/old-implementations"
archive_file "TEST_FIX_PROGRESS.md" "docs/ARCHIVE/old-implementations"
archive_file "TEST_STRATEGY.md" "docs/ARCHIVE/old-implementations"
archive_file "REFACTORING_ASSESSMENT.md" "docs/ARCHIVE/old-implementations"

# Archive completed/outdated docs from docs/ directory
echo "\n📚 Archiving outdated docs/ content..."
archive_file "docs/V1.1_BETA_TESTING_GUIDE.md" "docs/ARCHIVE/old-releases"
archive_file "docs/V1.1_FEATURE_SHOWCASE.md" "docs/ARCHIVE/old-releases"
archive_file "docs/V1.1_ANNOUNCEMENT_BLOG.md" "docs/ARCHIVE/old-releases"
archive_file "docs/V1.1_TROUBLESHOOTING.md" "docs/ARCHIVE/old-releases"
archive_file "docs/TESTING_INFRASTRUCTURE_v1.1.md" "docs/ARCHIVE/old-releases"
archive_file "docs/V1_REALITY_CHECK.md" "docs/ARCHIVE/old-releases"

# Clean up empty status directory if all files moved
if [ -d "docs/status" ] && [ -z "$(ls -A docs/status)" ]; then
    echo "\n🗑️ Removing empty docs/status directory..."
    rmdir docs/status
fi

# Count remaining markdown files
echo "\n📊 Documentation cleanup summary:"
echo "  Total .md files before: $(find . -name '*.md' -type f | wc -l)"
echo "  Archived files: $(find docs/ARCHIVE -name '*.md' -type f 2>/dev/null | wc -l)"
echo "  Active documentation: $(find docs -name '*.md' -type f | grep -v ARCHIVE | wc -l)"

# Create an index of archived files
echo "\n📝 Creating archive index..."
cat > docs/ARCHIVE/INDEX.md << 'EOF'
# 📦 Documentation Archive

This directory contains outdated and superseded documentation that has been archived
to reduce clutter while preserving historical context.

## Archive Structure

### old-releases/
Documentation from previous releases (v0.1.0 through v1.2.0)

### old-status/
Historical status reports and session summaries

### old-implementations/
Superseded implementation plans and roadmaps

### superseded/
Documents that have been replaced by newer versions

## Why Archive?

- Reduces cognitive load when browsing active documentation
- Preserves historical context for reference
- Keeps working directory clean and focused
- Makes it easier to find current, relevant information

## Still Need Something?

If you need to reference archived documentation:
1. Check the appropriate subdirectory
2. Use `git log` to see the history
3. Restore if truly needed with `git restore`

---
*Archived on: $(date +"%Y-%m-%d")*
EOF

echo "\n✅ Documentation archival complete!"
echo "   Active docs are now more focused and maintainable."
echo "   Historical docs preserved in docs/ARCHIVE/"
