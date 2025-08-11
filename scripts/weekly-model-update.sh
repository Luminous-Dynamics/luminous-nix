#!/usr/bin/env bash
# Weekly Sacred Trinity Model Update
# Run this every Friday to incorporate new knowledge

set -e

echo "🌊 Sacred Trinity Weekly Model Update"
echo "===================================="
echo ""

# Set sacred intention
echo "🙏 Setting intention for model evolution..."
echo "   May these models serve users with wisdom and compassion"
sleep 2

# Check if we're in the right directory
cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/scripts

# Run the update
echo ""
echo "📚 Checking for new knowledge..."
python3 sacred-trinity-trainer-v2.py

# Create backup of current model list
echo ""
echo "📸 Creating model snapshot..."
ollama list | grep "nix-" > ../models/snapshot_$(date +%Y%m%d).txt

# Show current models
echo ""
echo "📊 Current Sacred Trinity Models:"
echo "--------------------------------"
for model in empathy expert coder quick; do
    current_file="../models/current_${model}.txt"
    if [ -f "$current_file" ]; then
        current=$(cat "$current_file")
        size=$(ollama show "$current" --modelfile 2>/dev/null | wc -c)
        echo "✓ $model: $current ($(numfmt --to=iec $size))"
    else
        echo "✗ $model: not trained yet"
    fi
done

# Test the unified interface
echo ""
echo "🧪 Testing unified interface..."
echo "Question: 'How do I install Firefox?'"
../bin/ask-trinity "How do I install Firefox?" | head -10

echo ""
echo "✅ Weekly update complete!"
echo ""
echo "📝 Next steps:"
echo "1. Test with real user questions"
echo "2. Note any improvements needed"
echo "3. Continue collecting Q&A pairs"
echo ""
echo "🔄 Next automatic update: $(date -d 'next Friday' '+%A, %B %d')"
