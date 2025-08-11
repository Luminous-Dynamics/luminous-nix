#!/bin/bash
# Real-time standards monitoring for Nix for Humanity
# Part of the Sacred Trinity development model

# Colors for beautiful output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Configuration
REFRESH_INTERVAL=${1:-60}  # Default 60 seconds, or pass as first argument
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Navigate to project root
cd "$PROJECT_ROOT" || exit 1

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python standards
check_python() {
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${WHITE}🐍 Python Standards${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    # Black formatting
    echo -n "  Black Formatting: "
    if poetry run black --check src/ tests/ scripts/ >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Formatted${NC}"
    else
        UNFORMATTED=$(poetry run black --check src/ tests/ scripts/ 2>&1 | grep -c "would be reformatted")
        echo -e "${YELLOW}⚠️  $UNFORMATTED files need formatting${NC}"
    fi

    # Ruff linting
    echo -n "  Ruff Linting: "
    RUFF_OUTPUT=$(poetry run ruff check src/ tests/ scripts/ 2>&1)
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ No issues${NC}"
    else
        ISSUES=$(echo "$RUFF_OUTPUT" | grep -E "^\w" | wc -l)
        echo -e "${YELLOW}⚠️  $ISSUES issues found${NC}"
    fi

    # Type checking
    echo -n "  Type Checking: "
    if poetry run mypy src/ --strict >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Types complete${NC}"
    else
        ERRORS=$(poetry run mypy src/ --strict 2>&1 | grep -c ": error:")
        echo -e "${YELLOW}⚠️  $ERRORS type errors${NC}"
    fi

    # Import sorting
    echo -n "  Import Sorting: "
    if poetry run isort --check-only src/ tests/ scripts/ >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Imports sorted${NC}"
    else
        echo -e "${YELLOW}⚠️  Imports need sorting${NC}"
    fi
}

# Function to check test coverage
check_tests() {
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${WHITE}🧪 Test Coverage${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    if command_exists pytest; then
        # Quick coverage check (not running full tests for speed)
        echo -n "  Coverage Status: "
        if [ -f "coverage.json" ]; then
            COVERAGE=$(python3 -c "import json; print(json.load(open('coverage.json'))['totals']['percent_covered'])" 2>/dev/null)
            if [ ! -z "$COVERAGE" ]; then
                COVERAGE_INT=${COVERAGE%.*}
                if [ "$COVERAGE_INT" -ge 90 ]; then
                    echo -e "${GREEN}✅ ${COVERAGE}%${NC}"
                elif [ "$COVERAGE_INT" -ge 80 ]; then
                    echo -e "${YELLOW}⚠️  ${COVERAGE}%${NC}"
                else
                    echo -e "${RED}❌ ${COVERAGE}%${NC}"
                fi
            else
                echo -e "${BLUE}ℹ️  Run tests to update${NC}"
            fi
        else
            echo -e "${BLUE}ℹ️  No coverage data${NC}"
        fi
    else
        echo -e "  ${YELLOW}⚠️  pytest not available${NC}"
    fi
}

# Function to check documentation
check_docs() {
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${WHITE}📚 Documentation${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    REQUIRED_DOCS=(
        "README.md"
        "CHANGELOG.md"
        "LICENSE"
        "docs/README.md"
        "CLAUDE.md"
    )

    MISSING=0
    for doc in "${REQUIRED_DOCS[@]}"; do
        if [ ! -f "$doc" ]; then
            MISSING=$((MISSING + 1))
        fi
    done

    echo -n "  Required Files: "
    if [ $MISSING -eq 0 ]; then
        echo -e "${GREEN}✅ All present${NC}"
    else
        echo -e "${YELLOW}⚠️  $MISSING missing${NC}"
    fi

    # Check for TODO items in docs
    echo -n "  TODO Items: "
    TODO_COUNT=$(grep -r "TODO" docs/ 2>/dev/null | wc -l)
    if [ $TODO_COUNT -eq 0 ]; then
        echo -e "${GREEN}✅ None${NC}"
    else
        echo -e "${BLUE}ℹ️  $TODO_COUNT found${NC}"
    fi
}

# Function to check Git status
check_git() {
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${WHITE}📊 Git Status${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    # Uncommitted changes
    echo -n "  Working Tree: "
    if git diff --quiet && git diff --cached --quiet; then
        echo -e "${GREEN}✅ Clean${NC}"
    else
        CHANGED=$(git status --porcelain | wc -l)
        echo -e "${YELLOW}⚠️  $CHANGED changes${NC}"
    fi

    # Branch info
    BRANCH=$(git branch --show-current)
    echo "  Current Branch: $BRANCH"

    # Commits ahead/behind
    if [ "$BRANCH" != "main" ]; then
        AHEAD=$(git rev-list --count origin/main..$BRANCH 2>/dev/null || echo "0")
        BEHIND=$(git rev-list --count $BRANCH..origin/main 2>/dev/null || echo "0")
        echo "  Commits: ↑$AHEAD ↓$BEHIND"
    fi
}

# Function to check performance
check_performance() {
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${WHITE}⚡ Performance${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    # Simple startup time check
    echo -n "  Startup Time: "
    START=$(date +%s%N)
    python3 -c "from nix_for_humanity import initialize; initialize()" 2>/dev/null
    END=$(date +%s%N)
    ELAPSED=$((($END - $START) / 1000000))

    if [ $ELAPSED -lt 3000 ]; then
        echo -e "${GREEN}✅ ${ELAPSED}ms${NC}"
    else
        echo -e "${RED}❌ ${ELAPSED}ms (>3000ms)${NC}"
    fi

    # Check if performance benchmarks exist
    if [ -f "metrics/raw/latest_performance.json" ]; then
        echo "  Latest Benchmark: $(date -r metrics/raw/latest_performance.json '+%Y-%m-%d %H:%M')"
    else
        echo -e "  ${BLUE}ℹ️  No benchmarks available${NC}"
    fi
}

# Function to show summary
show_summary() {
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${WHITE}📈 Standards Summary${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    # Calculate overall health
    HEALTH_SCORE=100
    ISSUES=""

    # Check various conditions and adjust score
    if ! poetry run black --check src/ tests/ scripts/ >/dev/null 2>&1; then
        HEALTH_SCORE=$((HEALTH_SCORE - 10))
        ISSUES="${ISSUES}  - Run: poetry run black .\n"
    fi

    if ! poetry run ruff check src/ tests/ scripts/ >/dev/null 2>&1; then
        HEALTH_SCORE=$((HEALTH_SCORE - 15))
        ISSUES="${ISSUES}  - Run: poetry run ruff check --fix .\n"
    fi

    if ! poetry run mypy src/ --strict >/dev/null 2>&1; then
        HEALTH_SCORE=$((HEALTH_SCORE - 20))
        ISSUES="${ISSUES}  - Fix type hints\n"
    fi

    # Display health score with color
    echo -n "  Overall Health: "
    if [ $HEALTH_SCORE -ge 90 ]; then
        echo -e "${GREEN}${HEALTH_SCORE}% 🌟${NC}"
    elif [ $HEALTH_SCORE -ge 70 ]; then
        echo -e "${YELLOW}${HEALTH_SCORE}% ⚠️${NC}"
    else
        echo -e "${RED}${HEALTH_SCORE}% ❌${NC}"
    fi

    if [ ! -z "$ISSUES" ]; then
        echo -e "\n  ${WHITE}Quick Fixes:${NC}"
        echo -e "$ISSUES"
    fi
}

# Function to display header
show_header() {
    clear
    echo -e "${MAGENTA}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${MAGENTA}║${NC}  ${WHITE}📊 Nix for Humanity - Real-time Standards Monitor${NC}         ${MAGENTA}║${NC}"
    echo -e "${MAGENTA}║${NC}  ${BLUE}Sacred Trinity Development Model${NC}                          ${MAGENTA}║${NC}"
    echo -e "${MAGENTA}║${NC}  $(date '+%Y-%m-%d %H:%M:%S')                                   ${MAGENTA}║${NC}"
    echo -e "${MAGENTA}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo
}

# Function to display footer
show_footer() {
    echo
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${WHITE}Commands:${NC}"
    echo -e "  ${GREEN}r${NC} - Refresh now    ${GREEN}q${NC} - Quit    ${GREEN}d${NC} - Generate dashboard"
    echo -e "  ${BLUE}Refreshing every ${REFRESH_INTERVAL} seconds...${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Function to handle user input
handle_input() {
    read -t 1 -n 1 key
    case $key in
        q|Q)
            echo -e "\n${GREEN}✨ Exiting standards monitor...${NC}"
            exit 0
            ;;
        r|R)
            return 0  # Trigger refresh
            ;;
        d|D)
            echo -e "\n${BLUE}📊 Generating dashboard...${NC}"
            python scripts/metrics_dashboard.py
            echo -e "${GREEN}✅ Dashboard generated!${NC}"
            sleep 2
            return 0
            ;;
    esac
    return 1  # No action needed
}

# Main monitoring loop
main() {
    # Check dependencies
    if ! command_exists poetry; then
        echo -e "${RED}❌ Poetry not found. Please install Poetry first.${NC}"
        exit 1
    fi

    echo -e "${GREEN}🚀 Starting Nix for Humanity Standards Monitor...${NC}"
    echo -e "${BLUE}📁 Project root: $PROJECT_ROOT${NC}"
    echo

    # Main loop
    while true; do
        show_header

        check_python
        echo
        check_tests
        echo
        check_docs
        echo
        check_git
        echo
        check_performance
        echo
        show_summary

        show_footer

        # Wait for refresh interval or user input
        for ((i=0; i<$REFRESH_INTERVAL; i++)); do
            if handle_input; then
                break  # User requested action
            fi
        done
    done
}

# Trap Ctrl+C for clean exit
trap 'echo -e "\n${GREEN}✨ Standards monitor stopped gracefully.${NC}"; exit 0' INT

# Run main function
main "$@"
