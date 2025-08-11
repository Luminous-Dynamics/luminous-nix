#!/bin/bash
# Simple documentation consistency checker

echo "🔍 Documentation Consistency Check"
echo "=================================="
echo

VERSION="1.2.0"
PHASE="3"
PHASE_NAME="The Humane Interface"
PHASE_STATUS="in_progress"

echo "📊 Source of Truth (from PROJECT_STATUS.yaml):"
echo "   Version: $VERSION"
echo "   Phase: $PHASE - $PHASE_NAME"  
echo "   Status: $PHASE_STATUS"
echo

ISSUES=0

# Check README.md
echo "Checking README.md..."
if grep -q "Phase 4.*CURRENT\|Phase 4.*current" README.md 2>/dev/null; then
    echo "  ❌ README claims Phase 4 is current (should be Phase 3)"
    ((ISSUES++))
fi
if grep -q "v1.3\|1.3.0" README.md 2>/dev/null; then
    echo "  ❌ README mentions version 1.3+ (current is $VERSION)"
    ((ISSUES++))
fi

# Check Current Status Dashboard
echo "Checking Current Status Dashboard..."
STATUS_FILE="docs/04-OPERATIONS/CURRENT_STATUS_DASHBOARD.md"
if [ -f "$STATUS_FILE" ]; then
    DASHBOARD_VERSION=$(grep -oP 'Version.*?v?\K\d+\.\d+\.\d+' "$STATUS_FILE" | head -1)
    if [ "$DASHBOARD_VERSION" != "$VERSION" ]; then
        echo "  ❌ Dashboard shows version $DASHBOARD_VERSION (should be $VERSION)"
        ((ISSUES++))
    fi
fi

# Check Roadmap
echo "Checking Roadmap..."
ROADMAP="docs/01-VISION/02-ROADMAP.md"
if [ -f "$ROADMAP" ]; then
    if grep -q "Phase 3.*✅ COMPLETE" "$ROADMAP" 2>/dev/null; then
        echo "  ❌ Roadmap claims Phase 3 is complete (it's $PHASE_STATUS)"
        ((ISSUES++))
    fi
    if grep -q "Phase 4.*Current.*Months 10-12" "$ROADMAP" 2>/dev/null; then
        echo "  ❌ Roadmap claims Phase 4 is current (should be Phase 3)"
        ((ISSUES++))
    fi
fi

# Check for files claiming features are complete when they're not
echo "Checking for false completion claims..."
for file in $(find . -name "*.md" -type f 2>/dev/null | head -20); do
    if grep -q "Voice.*✅.*COMPLETE\|Voice.*interface.*complete" "$file" 2>/dev/null; then
        if [[ ! "$file" =~ "CHANGELOG" ]] && [[ ! "$file" =~ "PROJECT_STATUS" ]]; then
            echo "  ⚠️  $file claims voice is complete (needs verification)"
        fi
    fi
done

echo
echo "=================================="
if [ $ISSUES -eq 0 ]; then
    echo "✅ No major inconsistencies found!"
else
    echo "❌ Found $ISSUES documentation inconsistencies"
    echo "   Please update docs to match PROJECT_STATUS.yaml"
fi