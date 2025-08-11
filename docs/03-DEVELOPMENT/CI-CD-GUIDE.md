# 🚀 CI/CD Guide - Nix for Humanity

**Status**: ACTIVE
**Last Updated**: 2025-08-11
**Purpose**: Automated quality enforcement and release management

## 📋 Overview

Our CI/CD pipeline automatically enforces all project standards, ensuring consistent quality and smooth releases. Every commit is checked, every PR is validated, and every release is automated.

## 🔄 Continuous Integration Workflows

### 1. Standards Compliance Check (`standards-check.yml`)

**Triggers**: Every PR, push to main/develop
**Purpose**: Enforce all project standards automatically

#### What It Checks:

| Check | Description | Required to Pass |
|-------|-------------|------------------|
| **Black Formatting** | 88-character lines, consistent style | Yes |
| **Ruff Linting** | 700+ code quality rules | Yes |
| **Type Checking** | mypy strict mode | Yes |
| **Security Scan** | Bandit security analysis | Yes |
| **Pre-commit Hooks** | All hooks pass | Yes |
| **Documentation** | Required docs exist | Yes |
| **Commit Messages** | Conventional format | No (warning only) |
| **Test Coverage** | pytest with coverage | No (informational) |

#### How to Fix Failures:

```bash
# Fix formatting issues
poetry run black .

# Fix linting issues
poetry run ruff check --fix .

# Check type hints
poetry run mypy src/

# Run all pre-commit hooks
poetry run pre-commit run --all-files
```

### 2. Performance Testing (`performance-test.yml`)

**Triggers**: Weekly (Sunday 2 AM UTC), manual, performance-related PRs
**Purpose**: Prevent performance regressions

#### Performance Budgets:

| Operation | Target | Maximum |
|-----------|--------|---------|
| Cold Start | <1s | 3s |
| Warm Start | <500ms | 1s |
| Command Processing | <200ms | 1s |
| Memory (base) | <50MB | 100MB |
| Memory (after 100 commands) | <100MB | 200MB |

#### Running Locally:

```bash
# Run performance benchmarks
poetry run pytest tests/performance/ --benchmark-only

# Check memory usage
poetry run python scripts/performance_benchmark.py
```

### 3. Release Automation (`release.yml`)

**Triggers**: Git tags (v*.*.*), manual dispatch
**Purpose**: Automated, consistent releases

#### Release Process:

1. **Version Validation**: Semantic versioning check
2. **Test Suite**: Full test run with all personas
3. **Package Building**: Create wheel and sdist
4. **GitHub Release**: Auto-generated release notes
5. **PyPI Publishing**: For stable releases only
6. **Documentation Update**: CHANGELOG auto-update

#### Creating a Release:

```bash
# 1. Update version in pyproject.toml
poetry version minor  # or major/patch

# 2. Commit changes
git add pyproject.toml
git commit -m "chore: bump version to 1.2.0"

# 3. Create and push tag
git tag -a v1.2.0 -m "Release version 1.2.0"
git push origin main --tags

# GitHub Actions takes over from here!
```

### 4. Dependency Updates (`dependabot.yml`)

**Schedule**: Weekly (Monday 4 AM UTC)
**Purpose**: Keep dependencies secure and up-to-date

#### Configuration:

- Python packages: 5 PRs max
- GitHub Actions: 3 PRs max
- npm packages: 3 PRs max
- Major version updates: Ignored (manual review required)

## 📊 Status Badges

Add these to your README:

```markdown
![Standards](https://github.com/Luminous-Dynamics/nix-for-humanity/workflows/Standards%20Compliance%20Check/badge.svg)
![Performance](https://github.com/Luminous-Dynamics/nix-for-humanity/workflows/Performance%20Testing/badge.svg)
![Release](https://github.com/Luminous-Dynamics/nix-for-humanity/workflows/Release/badge.svg)
```

## 🔧 GitHub Secrets Required

Set these in Settings → Secrets and variables → Actions:

| Secret | Description | Required |
|--------|-------------|----------|
| `PYPI_API_TOKEN` | PyPI publishing token | For releases |
| `CODECOV_TOKEN` | Code coverage reporting | Optional |

## 🎯 Branch Protection Rules

Recommended settings for `main` branch:

- ✅ Require PR before merging
- ✅ Require status checks to pass:
  - `python-quality`
  - `pre-commit`
  - `documentation`
- ✅ Require branches to be up to date
- ✅ Require conversation resolution
- ✅ Require signed commits (optional)
- ✅ Include administrators

## 📈 Monitoring CI/CD Health

### Success Metrics:

| Metric | Target | Current |
|--------|--------|---------|
| Build Success Rate | >95% | Monitor in Actions tab |
| Average CI Time | <5 min | Check workflow runs |
| Performance Budget Compliance | 100% | Weekly reports |
| Dependency Updates | Weekly | Dependabot dashboard |

### Common Issues and Solutions:

#### 1. "Black formatting failed"
```bash
# Fix locally
poetry run black .
git add -u
git commit -m "style: apply Black formatting"
git push
```

#### 2. "Type checking failed"
```bash
# Add missing type hints
poetry run mypy src/ --show-error-codes
# Fix each error, focusing on public APIs first
```

#### 3. "Performance budget exceeded"
```bash
# Profile the slow operation
poetry run python -m cProfile -s cumtime script.py
# Optimize bottlenecks
```

#### 4. "Pre-commit hooks failed"
```bash
# Install and run locally
poetry run pre-commit install
poetry run pre-commit run --all-files
# Fix issues and commit
```

## 🚀 Advanced Features

### Manual Workflow Dispatch

Trigger workflows manually from GitHub:

1. Go to Actions tab
2. Select workflow
3. Click "Run workflow"
4. Fill in parameters (if any)
5. Click "Run workflow" button

### Workflow Artifacts

Downloads available for 90 days:
- Compliance reports (JSON)
- Performance reports (Markdown)
- Built packages (wheel, sdist)
- Test coverage reports

### Composite Actions

Reusable action components in `.github/actions/`:
- `setup-poetry`: Install Poetry and dependencies
- `run-tests`: Execute test suite with coverage
- `check-standards`: Run all quality checks

## 🔒 Security Considerations

### Automated Security Scanning:
- Bandit for Python code
- Dependabot for dependencies
- CodeQL analysis (optional)
- Secret scanning (automatic)

### Best Practices:
1. Never commit secrets or tokens
2. Use GitHub Secrets for sensitive data
3. Review Dependabot PRs carefully
4. Keep GitHub Actions up-to-date
5. Use specific version tags for actions

## 📝 Customizing Workflows

### Adding New Checks:

```yaml
# In .github/workflows/standards-check.yml
- name: 🆕 New Check
  run: |
    echo "Running custom check..."
    poetry run custom-check-script
  continue-on-error: false  # Set to true for warnings
```

### Modifying Performance Budgets:

Edit `performance-test.yml`:
```python
budgets = {
    'Cold Start': 3000,  # milliseconds
    'Warm Start': 1000,
    'Base Memory': 100,  # MB
}
```

### Changing Release Process:

Modify `release.yml` to:
- Add deployment steps
- Send notifications
- Update external services
- Trigger downstream builds

## 🎉 Summary

Our CI/CD pipeline ensures:
1. **Quality**: Every commit meets standards
2. **Performance**: No regressions slip through
3. **Security**: Dependencies stay updated
4. **Automation**: Releases are consistent
5. **Visibility**: Clear status for all checks

The Sacred Trinity development model is enforced automatically, maintaining our $200/month efficiency while ensuring $4.2M quality!

---

*"Automation liberates consciousness for creative work"* 🕉️
