#!/bin/bash
# Push v1.0.0 release to GitHub

echo "🚀 Pushing Nix for Humanity v1.0.0 to GitHub..."

# Push main branch
echo "Pushing main branch..."
git push origin main

# Push tag
echo "Pushing v1.0.0 tag..."
git push origin v1.0.0

echo "✅ Push complete! Now create the release at:"
echo "https://github.com/Luminous-Dynamics/nix-for-humanity/releases/new"