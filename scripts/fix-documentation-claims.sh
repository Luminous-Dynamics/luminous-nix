#!/bin/bash

echo "🔧 Fixing false documentation claims to match PROJECT_STATUS.yaml reality..."
echo "=================================================="

# Fix CHANGELOG.md
echo "Fixing CHANGELOG.md..."
sed -i 's/Voice Interface with Whisper & Piper.*- Complete/Voice Interface with Whisper \& Piper - In Development/g' CHANGELOG.md

# Fix voice-related files
echo "Fixing voice status files..."
sed -i 's/Voice Interface Setup Complete!/Voice Interface Setup - In Development/g' VOICE_SETUP_COMPLETE.md
sed -i 's/Voice Interface Installation Complete/Voice Interface Installation - Partial/g' VOICE_INSTALLATION_COMPLETE.md
sed -i 's/Voice Interface.*✅.*Architecture only/Voice Interface | 🚧 | Architecture only/g' V1_1_RELEASE_STATUS.md

# Fix Phase 2 Completion Report
echo "Fixing Phase 2 Completion Report..."
sed -i 's/Advanced Causal XAI.*DoWhy integration complete/Advanced Causal XAI - DoWhy integration planned/g' docs/04-OPERATIONS/PHASE_2_COMPLETION_REPORT.md

# Fix Research Navigation Guide
echo "Fixing Research Navigation Guide..."
sed -i 's/Causal XAI papers.*→ DoWhy integration ✅/Causal XAI papers → DoWhy integration 🚧/g' docs/01-VISION/RESEARCH_NAVIGATION_GUIDE.md
sed -i 's/Implement DoWhy for causal XAI ✅/Implement DoWhy for causal XAI 🚧/g' docs/01-VISION/RESEARCH_NAVIGATION_GUIDE.md

# Fix Architecture docs
echo "Fixing Architecture docs..."
sed -i 's/Federated Learning.*Privacy-preserving aggregation methodology complete/Federated Learning: Privacy-preserving aggregation methodology planned/g' docs/02-ARCHITECTURE/00-RESEARCH-SYNTHESIS.md

# Fix README claims about voice
echo "Fixing main README..."
sed -i 's/Now with revolutionary voice interface! 🎤//g' README.md

# Update version references that are wrong
echo "Fixing version references..."
for file in $(grep -l "v1.3.0\|v1.4.0\|v1.5.0" docs/*.md 2>/dev/null); do
    echo "  Fixing future version references in $file"
    sed -i 's/v1.3.0/v1.3.0 (planned)/g' "$file"
    sed -i 's/v1.4.0/v1.4.0 (future)/g' "$file"
    sed -i 's/v1.5.0/v1.5.0 (vision)/g' "$file"
done

# Count remaining issues
echo ""
echo "📊 Checking for remaining false claims..."
echo "------------------------------------------"

echo -n "Files claiming voice is complete: "
grep -l "voice.*complete\|voice.*enabled" *.md 2>/dev/null | wc -l

echo -n "Files claiming Phase 3 complete: "
grep -l "Phase 3.*COMPLETE\|Phase 3.*✅" docs/**/*.md 2>/dev/null | wc -l

echo -n "Files claiming Phase 4 current: "
grep -l "Phase 4.*Current\|Living System.*Current" docs/**/*.md 2>/dev/null | wc -l

echo ""
echo "✅ Documentation claims fixed to match reality!"
echo "Remember: PROJECT_STATUS.yaml is the single source of truth"