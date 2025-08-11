# Git Workflow Standards

## Branch Strategy

### Protected Branches
- `main` - Production-ready code only (protected)
- `develop` - Integration branch for features

### Working Branches
- `feature/*` - New features (e.g., `feature/whisper-voice`)
- `fix/*` - Bug fixes (e.g., `fix/voice-implementation`)
- `chore/*` - Cleanup tasks (e.g., `chore/remove-duplicates`)
- `docs/*` - Documentation updates (e.g., `docs/api-reference`)

### Branch Rules
- Create from `develop`, not `main`
- Delete after merging
- One feature per branch
- Descriptive names in kebab-case

## Commit Message Format

### Structure
```
type(scope): subject

[optional body]

[optional footer(s)]
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting, semicolons, etc)
- `refactor`: Code change that neither fixes nor adds
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements
- `build`: Build system changes
- `ci`: CI/CD changes

### Examples
```bash
feat(voice): add Whisper STT integration
fix(cli): handle empty input gracefully
docs(api): update REST endpoint documentation
chore: remove duplicate CLI scripts
```

### Commit Rules
- Use present tense ("add" not "added")
- Keep subject under 50 characters
- Capitalize first letter
- No period at end of subject
- Body explains what and why, not how

## Git Workflow

### Feature Development
```bash
# 1. Create feature branch
git checkout develop
git pull origin develop
git checkout -b feature/your-feature

# 2. Work and commit
git add .
git commit -m "feat(scope): description"

# 3. Keep updated with develop
git fetch origin
git rebase origin/develop

# 4. Push and create PR
git push origin feature/your-feature
# Create PR to develop branch
```

### Hotfix Process
```bash
# 1. Create from main
git checkout main
git checkout -b fix/critical-bug

# 2. Fix and test
git commit -m "fix: resolve critical issue"

# 3. Merge to both main and develop
git checkout main
git merge fix/critical-bug
git checkout develop
git merge fix/critical-bug
```

## What NOT to Commit

### Never Commit
- `.archive-*/` directories
- `__pycache__/`, `*.pyc`
- `.env` files with secrets
- Personal IDE configs (unless shared)
- Large binary files (>10MB)
- Generated documentation
- Build artifacts
- `node_modules/` (use package-lock.json)

### Use .gitignore
```gitignore
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so

# Archives
.archive-*/

# Environment
.env
.venv
venv/

# IDE
.vscode/*
!.vscode/settings.json
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

## Pull Request Standards

### PR Title
Follow commit message format: `type(scope): description`

### PR Description Template
```markdown
## Summary
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] All tests pass
- [ ] New tests added
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No duplicate files created
```

### Review Process
1. Self-review first
2. Run all tests locally
3. Update documentation
4. Request review
5. Address feedback
6. Squash commits if needed

## Version Tags

### Format
`v<MAJOR>.<MINOR>.<PATCH>`

### When to Version
- MAJOR: Breaking API changes
- MINOR: New features (backwards compatible)
- PATCH: Bug fixes

### Tagging Process
```bash
git checkout main
git pull origin main
git tag -a v1.0.1 -m "Release version 1.0.1"
git push origin v1.0.1
```

## Git Aliases (Recommended)

Add to `~/.gitconfig`:
```ini
[alias]
    co = checkout
    br = branch
    ci = commit
    st = status
    unstage = reset HEAD --
    last = log -1 HEAD
    visual = !gitk
    fl = log --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit
```
