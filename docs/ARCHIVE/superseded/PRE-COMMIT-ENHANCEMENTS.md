# Pre-commit Hook Enhancements 🚀

## Overview
Enhanced the pre-commit hooks configuration with advanced features for better code quality, security, and developer experience.

## New Features Added

### 1. **Enhanced Python Quality Checks**
- **docformatter**: Automatically formats Python docstrings to PEP 257
- **mypy**: Type checking (local hook, runs with poetry)
- **Quick pytest**: Runs fast unit tests on push (not every commit)

### 2. **Security Scanning**
- **bandit**: Scans Python code for security vulnerabilities
- **detect-secrets**: Prevents accidental commit of secrets/tokens
  - Configured with `.secrets.baseline` for known safe patterns
  - Excludes package-lock.json

### 3. **Commit Quality**
- **gitlint**: Enforces conventional commit message format
  - Requires types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert
  - Title max 72 chars, body max 80 chars per line
  - Blocks WIP/TODO/FIXME in commit titles

### 4. **Developer Experience**
- **Quick Config** (`.pre-commit-config-quick.yaml`):
  - Runs in ~2 seconds vs ~10+ seconds for full config
  - Only essential checks for rapid feedback
  - Use: `./scripts/hooks.sh quick`

- **Helper Script** (`scripts/hooks.sh`):
  ```bash
  ./scripts/hooks.sh quick    # Fast checks (~2s)
  ./scripts/hooks.sh full     # All checks (~10s)
  ./scripts/hooks.sh fix      # Auto-fix formatting
  ./scripts/hooks.sh install  # Setup all hooks
  ./scripts/hooks.sh skip     # Emergency commit without checks
  ./scripts/hooks.sh status   # Show installation status
  ```

### 5. **Smart Staging**
- Type checking only on changed files
- Tests only run on push (not every commit)
- Security scans exclude test directories
- Docstring formatting excludes tests

## Configuration Files

### Main Config (`.pre-commit-config.yaml`)
Full suite of checks including:
- File hygiene (whitespace, EOF, line endings)
- Python formatting (Black, isort, docformatter)
- Security (bandit, detect-secrets)
- Documentation (markdownlint)
- Shell scripts (shellcheck - errors only)
- Type checking (mypy)
- Commit messages (gitlint)

### Quick Config (`.pre-commit-config-quick.yaml`)
Minimal checks for fast feedback:
- Essential file hygiene
- Black formatting (check only)
- isort (check only)
- Runs in ~2 seconds

### Gitlint Config (`.gitlint`)
Enforces:
- Conventional commit format
- Proper line lengths
- No WIP commits to main

## Usage Patterns

### During Development
```bash
# Quick feedback while coding
./scripts/hooks.sh quick

# Auto-fix before committing
./scripts/hooks.sh fix

# Full check before pushing
./scripts/hooks.sh full
```

### Initial Setup
```bash
# Install all hooks (commit, commit-msg, pre-push)
./scripts/hooks.sh install

# Update hook versions
poetry run pre-commit autoupdate
```

### Emergency Situations
```bash
# Skip hooks for emergency fix
./scripts/hooks.sh skip -m "fix: emergency production issue"

# Or directly
git commit --no-verify -m "fix: critical bug"
```

## Performance Optimization

### Staged Execution
- **On every commit**: Basic hygiene, formatting
- **On commit message**: Validate format
- **On push**: Run tests, type checking

### Parallel Execution
- Most hooks run in parallel
- Only mypy runs serially (requires full context)

### Caching
- Pre-commit caches environments
- Clear with: `./scripts/hooks.sh clean`

## Best Practices

1. **Use quick checks frequently** during development
2. **Run full checks** before creating PRs
3. **Auto-fix** formatting issues instead of manual fixes
4. **Don't skip hooks** unless truly necessary
5. **Keep `.secrets.baseline` updated** when adding test data

## Troubleshooting

### If hooks are slow
```bash
# Use quick config
./scripts/hooks.sh quick

# Clear cache if needed
./scripts/hooks.sh clean
```

### If hooks fail unexpectedly
```bash
# Check what's installed
./scripts/hooks.sh status

# Reinstall
./scripts/hooks.sh install

# Update versions
poetry run pre-commit autoupdate
```

### If you need to bypass
```bash
# Skip once
git commit --no-verify

# Or use helper
./scripts/hooks.sh skip -m "your message"
```

## Benefits

1. **Consistent Code Quality**: Automated formatting and linting
2. **Security**: Catches vulnerabilities and secrets before commit
3. **Type Safety**: Optional type checking catches bugs early
4. **Fast Feedback**: Quick mode gives results in seconds
5. **Flexible**: Different configs for different needs
6. **Educational**: Teaches best practices through enforcement

## Metrics

- **Quick checks**: ~2 seconds
- **Full checks**: ~10-15 seconds
- **Auto-fix**: ~5 seconds
- **Coverage**: 13+ different quality checks
- **Security**: 2 dedicated security scanners

---

This enhancement makes the development workflow smoother while maintaining high code quality standards. The flexibility between quick and full checks allows developers to choose the right balance of speed vs thoroughness for their current task.