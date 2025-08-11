#!/usr/bin/env bash
# Pre-commit hook helper commands

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

case "${1:-help}" in
    quick)
        echo -e "${GREEN}Running quick pre-commit checks...${NC}"
        poetry run pre-commit run --config .pre-commit-config-quick.yaml --all-files
        ;;
    
    full)
        echo -e "${GREEN}Running full pre-commit checks...${NC}"
        poetry run pre-commit run --all-files
        ;;
    
    install)
        echo -e "${GREEN}Installing pre-commit hooks...${NC}"
        poetry run pre-commit install
        poetry run pre-commit install --hook-type commit-msg
        poetry run pre-commit install --hook-type pre-push
        echo -e "${GREEN}✓ Hooks installed for commit, commit-msg, and pre-push${NC}"
        ;;
    
    update)
        echo -e "${GREEN}Updating pre-commit hooks to latest versions...${NC}"
        poetry run pre-commit autoupdate
        echo -e "${GREEN}✓ Hook versions updated${NC}"
        ;;
    
    skip)
        echo -e "${YELLOW}Committing with --no-verify (skipping hooks)...${NC}"
        shift
        git commit --no-verify "$@"
        ;;
    
    fix)
        echo -e "${GREEN}Auto-fixing what we can...${NC}"
        poetry run black .
        poetry run isort .
        poetry run docformatter --in-place -r src/
        echo -e "${GREEN}✓ Auto-fixes applied${NC}"
        ;;
    
    clean)
        echo -e "${GREEN}Cleaning pre-commit cache...${NC}"
        poetry run pre-commit clean
        poetry run pre-commit gc
        echo -e "${GREEN}✓ Cache cleaned${NC}"
        ;;
    
    status)
        echo -e "${GREEN}Pre-commit status:${NC}"
        echo -e "Config: .pre-commit-config.yaml"
        echo -e "Installed hooks:"
        ls -la .git/hooks/ | grep -E "(pre-commit|commit-msg|pre-push)" || echo "None installed"
        echo
        echo -e "Available configs:"
        ls -la .pre-commit-config*.yaml
        ;;
    
    help|--help|-h|*)
        echo "Pre-commit Hook Helper"
        echo
        echo "Usage: $0 [command]"
        echo
        echo "Commands:"
        echo "  quick    - Run quick checks only (~2 seconds)"
        echo "  full     - Run all checks (~10+ seconds)"
        echo "  install  - Install git hooks"
        echo "  update   - Update hook versions"
        echo "  skip     - Commit without checks (git commit --no-verify)"
        echo "  fix      - Auto-fix formatting issues"
        echo "  clean    - Clean pre-commit cache"
        echo "  status   - Show hook installation status"
        echo "  help     - Show this help"
        echo
        echo "Examples:"
        echo "  $0 quick           # Fast feedback during development"
        echo "  $0 fix             # Auto-fix before committing"
        echo "  $0 skip -m 'WIP'   # Emergency commit without checks"
        ;;
esac