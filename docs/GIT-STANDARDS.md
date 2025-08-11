# 🔀 Git Standards - Nix for Humanity

*Consistent version control for consciousness-first development*

## 📋 Quick Reference

```bash
# Commit format
feat(nlp): add fuzzy matching for package names

# Branch format
feature/add-voice-interface
bugfix/fix-memory-leak
docs/update-api-reference

# Tag format
v1.0.0
v1.1.0-beta.1
```

## 🎯 Commit Message Standards

### Format: Conventional Commits

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types (Required)
- **feat**: New feature for users
- **fix**: Bug fix for users
- **docs**: Documentation changes
- **style**: Code style (formatting, semicolons, etc)
- **refactor**: Code change that neither fixes nor adds feature
- **perf**: Performance improvement
- **test**: Adding or correcting tests
- **chore**: Maintenance tasks (updating dependencies, etc)
- **ci**: CI/CD configuration changes
- **build**: Build system or external dependency changes

### Scope (Optional but Recommended)
- **nlp**: Natural language processing
- **cli**: Command-line interface
- **tui**: Terminal user interface
- **voice**: Voice interface
- **api**: Backend API
- **docs**: Documentation
- **tests**: Test suite
- **deps**: Dependencies

### Subject (Required)
- Use imperative, present tense: "add" not "added" nor "adds"
- Don't capitalize first letter
- No period at the end
- Maximum 50 characters

### Body (Optional)
- Use imperative, present tense
- Include motivation for change
- Contrast with previous behavior
- Wrap at 72 characters

### Footer (Optional)
- Reference issues: `Fixes #123`
- Breaking changes: `BREAKING CHANGE: description`
- Co-authors: `Co-authored-by: Name <email>`

### Examples

#### Simple Commit
```
feat(nlp): add fuzzy matching for package names
```

#### Detailed Commit
```
fix(cli): prevent timeout on slow network connections

The previous implementation had a hard-coded 5-second timeout
which was too short for users on slow connections. This change
makes the timeout configurable with a sensible default of 30s.

Fixes #456
```

#### Breaking Change
```
refactor(api)!: change response format to JSON

BREAKING CHANGE: API now returns JSON instead of plain text.
Clients need to update their parsing logic.

Migration guide: docs/migration/v2.md
```

## 🌿 Branch Naming Standards

### Format
```
<type>/<description>
```

### Types
- **feature/**: New features
- **bugfix/**: Bug fixes
- **hotfix/**: Urgent production fixes
- **docs/**: Documentation updates
- **refactor/**: Code refactoring
- **test/**: Test additions/fixes
- **chore/**: Maintenance tasks

### Rules
- Use lowercase
- Use hyphens, not underscores
- Be descriptive but concise
- Include issue number if applicable

### Examples
```bash
feature/add-voice-interface
bugfix/fix-memory-leak-in-nlp
hotfix/critical-security-patch
docs/update-api-reference
refactor/consolidate-error-handling
test/add-integration-tests
chore/update-dependencies
```

## 🏷️ Tag & Release Standards

### Version Format: Semantic Versioning
```
v<major>.<minor>.<patch>[-<prerelease>][+<metadata>]
```

### Version Increments
- **Major**: Breaking API changes
- **Minor**: New features (backward compatible)
- **Patch**: Bug fixes (backward compatible)

### Prerelease Tags
- **alpha**: Early development
- **beta**: Feature complete, testing
- **rc**: Release candidate

### Examples
```bash
v1.0.0          # First stable release
v1.1.0          # New features added
v1.1.1          # Bug fixes
v2.0.0-alpha.1  # Alpha version of v2
v2.0.0-beta.1   # Beta version
v2.0.0-rc.1     # Release candidate
```

## 🔄 Git Workflow

### Main Branches
- **main**: Production-ready code
- **develop**: Integration branch (optional)

### Feature Development
```bash
# 1. Create feature branch from main
git checkout -b feature/new-feature main

# 2. Make changes and commit
git add .
git commit -m "feat(scope): add new feature"

# 3. Push to remote
git push -u origin feature/new-feature

# 4. Create pull request
# 5. After review, merge to main
```

### Hotfix Process
```bash
# 1. Create hotfix from main
git checkout -b hotfix/critical-fix main

# 2. Fix and commit
git commit -m "fix(scope): critical security fix"

# 3. Push and create PR
git push -u origin hotfix/critical-fix

# 4. Merge to main AND develop (if exists)
```

## 📝 Pull Request Standards

### PR Title Format
Same as commit message format:
```
feat(nlp): add fuzzy matching for package names
```

### PR Description Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project standards
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No console.log statements
- [ ] Performance impact considered

## Screenshots (if applicable)
Add screenshots for UI changes

## Related Issues
Fixes #123
```

## 🪝 Git Hooks (Recommended)

### Pre-commit Hook
```bash
#!/usr/bin/env bash
# .git/hooks/pre-commit

# Check commit message format
commit_regex='^(feat|fix|docs|style|refactor|perf|test|chore|ci|build)(\(.+\))?: .{1,50}'
if ! grep -qE "$commit_regex" "$1"; then
    echo "Invalid commit message format!"
    exit 1
fi

# Run tests
npm test || exit 1

# Check for console.log
if grep -r "console\.log" src/; then
    echo "Remove console.log statements"
    exit 1
fi
```

### Commit-msg Hook
```bash
#!/usr/bin/env bash
# .git/hooks/commit-msg

# Validate commit message format
npx commitlint --edit $1
```

## 🚫 What NOT to Commit

### Never Commit
- Passwords, API keys, tokens
- `.env` files with secrets
- `node_modules/` directory
- Build artifacts (`dist/`, `build/`)
- Personal IDE settings
- OS-specific files (`.DS_Store`, `Thumbs.db`)
- Large binary files (use Git LFS if needed)

### Use .gitignore
```gitignore
# Dependencies
node_modules/
venv/
.env

# Build artifacts
dist/
build/
*.pyc
__pycache__/

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Logs
*.log
npm-debug.log*
```

## 📊 Git Best Practices

### Commit Practices
1. **Atomic commits**: One logical change per commit
2. **Commit often**: Small, frequent commits
3. **Test before commit**: Ensure code works
4. **Write meaningful messages**: Future you will thank you
5. **Don't commit commented code**: Delete it

### Branch Practices
1. **Keep branches short-lived**: Merge within days, not weeks
2. **Delete merged branches**: Keep repository clean
3. **Rebase feature branches**: Keep history clean
4. **Never force push to main**: Protect shared branches

### Collaboration Practices
1. **Pull before push**: Avoid conflicts
2. **Communicate in commits**: Explain the why
3. **Review your own PR first**: Self-review
4. **Respond to feedback promptly**: Keep PRs moving
5. **Squash commits when merging**: Clean history

## 🤝 Sacred Trinity Git Workflow

### Human Commits
```bash
# Clear, intentional commits
git commit -m "feat(ui): add user preference panel

Implemented based on user feedback from beta testing.
Makes the system more accessible for Grandma Rose persona."
```

### AI-Assisted Commits
```bash
# AI helps write commit messages
git commit -m "refactor(nlp): optimize intent recognition pipeline

Claude Code Max: Refactored to reduce complexity from O(n²) to O(n log n).
Maintains same accuracy with 10x performance improvement.

Co-authored-by: Claude <claude@anthropic.com>"
```

### Local LLM Reviews
```bash
# Local LLM validates commits
git commit -m "fix(nix): correct package dependency resolution

Local Mistral: Verified against NixOS 25.11 standards.
Fixes edge case with circular dependencies.

Reviewed-by: Mistral-7B"
```

## 🔧 Git Configuration

### Recommended Settings
```bash
# Set your identity
git config --global user.name "Your Name"
git config --global user.email "you@example.com"

# Helpful aliases
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.st status
git config --global alias.last 'log -1 HEAD'
git config --global alias.visual '!gitk'

# Better diffs
git config --global diff.algorithm histogram
git config --global merge.conflictstyle diff3

# Auto-cleanup
git config --global fetch.prune true
```

## 📈 Metrics & Monitoring

### Commit Quality Metrics
- Commit message compliance: >95%
- Average commits per PR: 3-7
- Time from branch to merge: <3 days
- Breaking changes per release: <1

### Repository Health
```bash
# Check commit message compliance
git log --oneline | grep -E '^[a-f0-9]+ (feat|fix|docs|style|refactor|perf|test|chore|ci|build)'

# Find large files
git rev-list --objects --all | grep "$(git verify-pack -v .git/objects/pack/*.idx | sort -k 3 -n | tail -10 | awk '{print$1}')"

# Clean up repository
git gc --prune=now --aggressive
```

## 🚀 Migration Guide

### For Existing Repositories
1. Create `.gitmessage` template
2. Set up commit hooks
3. Update CONTRIBUTING.md
4. Train team on standards
5. Gradually enforce via CI

### Enforcement Timeline
- **Week 1**: Documentation and training
- **Week 2**: Soft enforcement (warnings)
- **Week 3**: Hard enforcement (CI blocks)
- **Week 4**: Full compliance

---

*"Every commit tells a story. Make yours worth reading."*

**Remember**: Good Git hygiene makes collaboration joyful and debugging possible. These standards support both human understanding and AI parsing, essential for our Sacred Trinity workflow.