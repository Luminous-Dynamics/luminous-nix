#!/usr/bin/env bash
# 🕉️ Sacred Development Aliases for Nix for Humanity
# Source this file to get convenient development shortcuts

# Navigate to project root
export NIX_HUMANITY_ROOT="/srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity"
alias nhroot='cd $NIX_HUMANITY_ROOT'

# Poetry shortcuts
alias pi='poetry install'
alias piall='poetry install --all-extras'
alias pr='poetry run'
alias psh='poetry shell'
alias pa='poetry add'
alias pdev='poetry add --group dev'
alias prm='poetry remove'
alias pup='poetry update'
alias pshow='poetry show'
alias ptree='poetry show --tree'
alias pcheck='poetry check'
alias plock='poetry lock'
alias pbuild='poetry build'

# Testing shortcuts
alias pt='poetry run pytest'
alias ptc='poetry run pytest --cov=nix_for_humanity'
alias ptv='poetry run pytest -vv'
alias ptvs='poetry run pytest -vvs'  # verbose with stdout
alias ptf='poetry run pytest --failed-first'  # run failed tests first
alias ptx='poetry run pytest -x'  # stop on first failure

# Code quality shortcuts
alias fmt='poetry run black .'
alias fmtc='poetry run black --check .'  # check only
alias lint='poetry run ruff check .'
alias lintf='poetry run ruff check --fix .'  # auto-fix
alias type='poetry run mypy .'
alias sec='poetry run bandit -r src/'

# Pre-commit shortcuts
alias pc='poetry run pre-commit'
alias pcr='poetry run pre-commit run'
alias pca='poetry run pre-commit run --all-files'
alias pci='poetry run pre-commit install'
alias pcu='poetry run pre-commit autoupdate'

# Application shortcuts
alias ask='poetry run ask-nix'
alias tui='poetry run nix-tui'
alias server='poetry run nix-humanity-server'

# Combined quality checks (Sacred Trinity workflow)
alias qa='fmt && lintf && type'  # Quick quality check
alias qafull='pca && pt'  # Full quality with tests

# Development workflow shortcuts
alias dev='poetry install --all-extras && poetry shell'
alias clean='find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null'
alias deps='poetry show --latest'  # check for outdated deps

# Sacred Trinity helpers
trinity-check() {
    echo "🕉️ Sacred Trinity Code Quality Check"
    echo "====================================="
    echo "📝 Formatting with Black (88 chars)..."
    poetry run black --check . && echo "✅ Formatting OK" || echo "❌ Needs formatting"
    echo ""
    echo "🔍 Linting with Ruff..."
    poetry run ruff check . && echo "✅ Linting OK" || echo "❌ Linting issues"
    echo ""
    echo "🎯 Type checking with mypy..."
    poetry run mypy . && echo "✅ Types OK" || echo "❌ Type issues"
    echo ""
    echo "🧪 Running tests..."
    poetry run pytest -q && echo "✅ Tests passing" || echo "❌ Test failures"
}

trinity-fix() {
    echo "🕉️ Sacred Trinity Auto-Fix"
    echo "=========================="
    echo "📝 Formatting code..."
    poetry run black .
    echo "🔍 Fixing linting issues..."
    poetry run ruff check --fix .
    echo "✅ Done! Now run 'trinity-check' to verify"
}

# Git helpers with Poetry
commit-ready() {
    echo "🔍 Checking if ready to commit..."
    poetry run pre-commit run --all-files
    if [ $? -eq 0 ]; then
        echo "✅ Ready to commit!"
    else
        echo "❌ Fix issues before committing"
    fi
}

# Help function
nh-help() {
    echo "🕉️ Nix for Humanity Development Aliases"
    echo "========================================"
    echo ""
    echo "Navigation:"
    echo "  nhroot     - Go to project root"
    echo ""
    echo "Poetry Management:"
    echo "  pi/piall   - Install dependencies (all extras)"
    echo "  pr         - Run command in Poetry environment"
    echo "  psh        - Enter Poetry shell"
    echo "  pa/pdev    - Add dependency (production/dev)"
    echo ""
    echo "Testing:"
    echo "  pt         - Run tests"
    echo "  ptc        - Run tests with coverage"
    echo "  ptv/ptvs   - Verbose test output"
    echo ""
    echo "Code Quality:"
    echo "  fmt        - Format code with Black"
    echo "  lint/lintf - Check/fix with Ruff"
    echo "  type       - Type check with mypy"
    echo "  qa         - Quick quality check"
    echo "  qafull     - Full quality with tests"
    echo ""
    echo "Sacred Trinity:"
    echo "  trinity-check - Full quality check"
    echo "  trinity-fix   - Auto-fix issues"
    echo "  commit-ready  - Pre-commit check"
    echo ""
    echo "Application:"
    echo "  ask        - Run ask-nix CLI"
    echo "  tui        - Run TUI interface"
    echo "  server     - Run web server"
}

echo "🌟 Nix for Humanity development aliases loaded!"
echo "Type 'nh-help' for a list of commands"
