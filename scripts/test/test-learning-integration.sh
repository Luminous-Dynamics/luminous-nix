#!/usr/bin/env bash
# Test script to verify learning system integration

echo "🧪 Testing Learning System Integration"
echo "====================================="

# Check if learning is enabled
echo -e "\n1️⃣  Checking learning status..."
ask-nix --learning-status

# Enable learning if not already enabled
echo -e "\n2️⃣  Enabling learning..."
ask-nix --enable-learning

# Test with a dry-run command (won't actually install)
echo -e "\n3️⃣  Testing install command (dry-run)..."
ask-nix --dry-run "install firefox"

# Check insights
echo -e "\n4️⃣  Checking learning insights..."
ask-nix --show-insights

# Test with a search command
echo -e "\n5️⃣  Testing search command..."
ask-nix "search python"

# Check insights again
echo -e "\n6️⃣  Checking updated insights..."
ask-nix --show-insights

# Test error learning (intentionally bad package name)
echo -e "\n7️⃣  Testing error learning (bad package)..."
ask-nix --dry-run "install notarealpackage123"

# Final insights check
echo -e "\n8️⃣  Final insights check..."
ask-nix --show-insights

echo -e "\n✅ Integration test complete!"
echo "Check the output above to verify:"
echo "  - Commands are being tracked"
echo "  - Success/failure is recorded"
echo "  - Preferences are learned"
echo "  - Error solutions are suggested"
