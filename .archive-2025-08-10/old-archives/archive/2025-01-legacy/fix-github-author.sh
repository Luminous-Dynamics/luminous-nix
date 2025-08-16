#!/bin/bash
# Fix GitHub author configuration

echo "🔧 Fixing GitHub author configuration..."

# Set the correct email to match GitHub account
git config user.email "tristan.stoltz@evolvingresonantcocreationism.com"
git config user.name "Tristan Stoltz"

echo "✅ Git configuration updated:"
echo "   Name: $(git config user.name)"
echo "   Email: $(git config user.email)"

echo ""
echo "📝 To fix existing commits on GitHub:"
echo "1. Add tristan.stoltz@gmail.com to your GitHub account:"
echo "   https://github.com/settings/emails"
echo ""
echo "2. Or rewrite history to use the correct email:"
echo "   git filter-branch --env-filter '"
echo "   export GIT_AUTHOR_EMAIL=\"tristan.stoltz@evolvingresonantcocreationism.com\""
echo "   export GIT_COMMITTER_EMAIL=\"tristan.stoltz@evolvingresonantcocreationism.com\""
echo "   ' --tag-name-filter cat -- --branches --tags"
echo ""
echo "3. Force push (⚠️ only if you're sure!):"
echo "   git push --force origin main"