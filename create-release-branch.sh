#!/bin/bash
# Create a release branch without full history

echo "Creating lightweight release branch..."

# Create a new orphan branch
git checkout --orphan release-v1.0.0

# Add all files
git add .

# Commit
git commit -m "release: v1.0.0 - Natural language interface for NixOS

This is a squashed release commit containing the full v1.0.0 codebase.
For full history, see the main branch.

Features:
- Natural Language CLI
- Configuration Generation
- Smart Package Discovery
- Flake Management
- Generation Management
- Home Manager Integration
- Error Intelligence

Built with the Sacred Trinity development model."

# Create tag
git tag -f v1.0.0-release

echo "Release branch created. You can push this lightweight branch:"
echo "git push origin release-v1.0.0"
echo "git push origin v1.0.0-release"