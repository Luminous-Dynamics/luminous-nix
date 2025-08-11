#!/usr/bin/env bash

# Documentation Standards Checker
# Enforces documentation standards to prevent sprawl

echo "📋 Documentation Standards Check"
echo "================================"

DOCS_DIR="${1:-.}"
ISSUES_FOUND=0

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check 1: File count
echo -e "\n📊 Checking file count..."
FILE_COUNT=$(find "$DOCS_DIR" -name "*.md" -type f | grep -v -E '(archive|backup)' | wc -l)
if [ "$FILE_COUNT" -gt 100 ]; then
    echo -e "${RED}❌ Too many docs: $FILE_COUNT files (max: 100)${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    echo -e "${GREEN}✅ File count OK: $FILE_COUNT files${NC}"
fi

# Check 2: Duplicate topics
echo -e "\n🔍 Checking for duplicate topics..."
DUPLICATES=$(find "$DOCS_DIR" -name "*.md" -type f | grep -v -E '(archive|backup)' | xargs -I {} basename {} 2>/dev/null | sort | uniq -d)
if [ -n "$DUPLICATES" ]; then
    echo -e "${RED}❌ Duplicate filenames found:${NC}"
    echo "$DUPLICATES"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    echo -e "${GREEN}✅ No duplicate filenames${NC}"
fi

# Check 3: File naming conventions
echo -e "\n📝 Checking file naming..."
BAD_NAMES=$(find "$DOCS_DIR" -name "*_COMPLETE*.md" -o -name "*_FINAL*.md" -o -name "*_V[0-9]*.md" | grep -v -E '(archive|backup)')
if [ -n "$BAD_NAMES" ]; then
    echo -e "${RED}❌ Bad file naming conventions:${NC}"
    echo "$BAD_NAMES"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    echo -e "${GREEN}✅ File naming OK${NC}"
fi

# Check 4: File size
echo -e "\n📏 Checking file sizes..."
LARGE_FILES=$(find "$DOCS_DIR" -name "*.md" -type f | grep -v -E '(archive|backup)' | xargs wc -l 2>/dev/null | awk '$1 > 1000 {print $2 " (" $1 " lines)"}')
if [ -n "$LARGE_FILES" ]; then
    echo -e "${YELLOW}⚠️  Large files found (>1000 lines):${NC}"
    echo "$LARGE_FILES"
fi

# Check 5: Required files exist
echo -e "\n✅ Checking required files..."
REQUIRED_FILES=(
    "START-HERE.md"
    "TROUBLESHOOTING.md"
    "README.md"
    "DOCUMENTATION-STANDARDS.md"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$DOCS_DIR/$file" ]; then
        echo -e "${RED}❌ Missing required file: $file${NC}"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    else
        echo -e "${GREEN}✅ Found: $file${NC}"
    fi
done

# Check 6: Directory structure
echo -e "\n📁 Checking directory structure..."
EXPECTED_DIRS=(
    "01-VISION"
    "02-ARCHITECTURE"
    "03-DEVELOPMENT"
    "04-OPERATIONS"
    "05-REFERENCE"
    "06-TUTORIALS"
)

for dir in "${EXPECTED_DIRS[@]}"; do
    if [ ! -d "$DOCS_DIR/$dir" ]; then
        echo -e "${RED}❌ Missing directory: $dir${NC}"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    else
        # Check for INDEX.md in each directory
        if [ ! -f "$DOCS_DIR/$dir/INDEX.md" ]; then
            echo -e "${YELLOW}⚠️  Missing INDEX.md in $dir${NC}"
        else
            echo -e "${GREEN}✅ $dir/INDEX.md exists${NC}"
        fi
    fi
done

# Check 7: Look for outdated markers
echo -e "\n🕰️  Checking for outdated content markers..."
OUTDATED=$(grep -r "TODO\|FIXME\|DEPRECATED\|Coming Soon\|Will be\|Future version" "$DOCS_DIR" --include="*.md" 2>/dev/null | grep -v -E '(archive|backup)' | grep -v "Coming Soon (v1.1)" | head -10)
if [ -n "$OUTDATED" ]; then
    echo -e "${YELLOW}⚠️  Possible outdated content:${NC}"
    echo "$OUTDATED" | head -5
    echo "..."
fi

# Check 8: Mystical language in technical docs
echo -e "\n🔮 Checking for mystical language in technical docs..."
MYSTICAL=$(grep -r "sacred\|consciousness\|transcendent\|mystical\|divine" "$DOCS_DIR/02-ARCHITECTURE" "$DOCS_DIR/05-REFERENCE" "$DOCS_DIR/04-OPERATIONS" --include="*.md" 2>/dev/null | head -10)
if [ -n "$MYSTICAL" ]; then
    echo -e "${YELLOW}⚠️  Mystical language in technical docs:${NC}"
    echo "$MYSTICAL" | head -3
    echo "..."
fi

# Check 9: Working examples
echo -e "\n💻 Checking for code examples..."
for file in "$DOCS_DIR/06-TUTORIALS"/*.md; do
    if [ -f "$file" ]; then
        HAS_CODE=$(grep -c '```' "$file" || true)
        if [ "$HAS_CODE" -eq 0 ]; then
            echo -e "${YELLOW}⚠️  No code examples in tutorial: $(basename "$file")${NC}"
        fi
    fi
done

# Summary
echo -e "\n================================"
echo "📊 Summary"
echo "================================"

if [ $ISSUES_FOUND -eq 0 ]; then
    echo -e "${GREEN}✅ All documentation standards met!${NC}"
    exit 0
else
    echo -e "${RED}❌ Found $ISSUES_FOUND issues that need fixing${NC}"
    echo -e "\nRefer to DOCUMENTATION-STANDARDS.md for guidelines"
    exit 1
fi