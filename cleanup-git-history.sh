#!/bin/bash
# Script to remove large archive folders from git history

echo "🧹 Git History Cleanup Script"
echo "============================="
echo
echo "Current repository size:"
du -sh .git
echo
echo "This will remove .archive-2025-08-10 from git history"
echo "⚠️  WARNING: This rewrites history and requires force push!"
echo
read -p "Continue? (y/n) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Removing archive from history..."
    
    # Use BFG or filter-branch
    git filter-branch --force --index-filter \
        'git rm -r --cached --ignore-unmatch .archive-2025-08-10' \
        --prune-empty --tag-name-filter cat -- --all
    
    # Cleanup
    rm -rf .git/refs/original/
    git reflog expire --expire=now --all
    git gc --prune=now --aggressive
    
    echo
    echo "✅ Complete! New repository size:"
    du -sh .git
    echo
    echo "Next steps:"
    echo "1. git push --force --all"
    echo "2. git push --force --tags"
    echo "3. Tell collaborators to re-clone"
fi