#!/bin/bash
# Sacred Standards Review Script
# Automates our weekly and monthly review process

# Colors for sacred output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REVIEW_TYPE="${1:-weekly}"  # weekly, monthly, or quick

# Navigate to project root
cd "$PROJECT_ROOT" || exit 1

# Sacred header
show_header() {
    echo -e "${MAGENTA}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${MAGENTA}║${NC}  ${WHITE}🕉️  Sacred Standards Review - $REVIEW_TYPE${NC}                  ${MAGENTA}║${NC}"
    echo -e "${MAGENTA}║${NC}  ${BLUE}Sacred Trinity Development Model${NC}                          ${MAGENTA}║${NC}"
    echo -e "${MAGENTA}║${NC}  $(date '+%Y-%m-%d %H:%M:%S')                                   ${MAGENTA}║${NC}"
    echo -e "${MAGENTA}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo
}

# Quick review (for session starts)
quick_review() {
    echo -e "${CYAN}━━━ Quick Standards Check ━━━${NC}"
    echo
    
    # Check for CI/CD failures
    echo -e "${YELLOW}Recent Commits:${NC}"
    git log --oneline -5
    echo
    
    # Quick standards check
    echo -e "${YELLOW}Standards Status:${NC}"
    
    # Black
    echo -n "  Black: "
    if poetry run black --check src/ tests/ scripts/ >/dev/null 2>&1; then
        echo -e "${GREEN}✅${NC}"
    else
        COUNT=$(poetry run black --check src/ tests/ scripts/ 2>&1 | grep -c "would be reformatted")
        echo -e "${YELLOW}$COUNT files need formatting${NC}"
    fi
    
    # Ruff
    echo -n "  Ruff: "
    if poetry run ruff check src/ tests/ scripts/ >/dev/null 2>&1; then
        echo -e "${GREEN}✅${NC}"
    else
        COUNT=$(poetry run ruff check src/ tests/ scripts/ 2>&1 | grep -E "^\w" | wc -l)
        echo -e "${YELLOW}$COUNT issues${NC}"
    fi
    
    # Type checking
    echo -n "  Types: "
    if poetry run mypy src/ --strict >/dev/null 2>&1; then
        echo -e "${GREEN}✅${NC}"
    else
        echo -e "${YELLOW}Issues present${NC}"
    fi
    
    echo
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Weekly review
weekly_review() {
    echo -e "${CYAN}📊 Generating Weekly Report...${NC}"
    echo
    
    # Generate reports
    python scripts/generate_weekly_report.py
    python scripts/metrics_dashboard.py
    
    echo
    echo -e "${GREEN}✅ Reports generated:${NC}"
    echo "  - Weekly report: metrics/reports/weekly_report_*.md"
    echo "  - Dashboard: dashboard.html"
    echo
    
    # Show summary from report
    if [ -f "dashboard.html" ]; then
        echo -e "${YELLOW}Opening dashboard in browser...${NC}"
        xdg-open dashboard.html 2>/dev/null || open dashboard.html 2>/dev/null || echo "  Please open dashboard.html manually"
    fi
    
    echo
    echo -e "${CYAN}━━━ Action Items ━━━${NC}"
    echo
    
    # Extract action items from latest report
    LATEST_REPORT=$(ls -t metrics/reports/weekly_report_*.md 2>/dev/null | head -1)
    if [ -f "$LATEST_REPORT" ]; then
        sed -n '/## 🎯 Action Items/,/## 💡 Recommendations/p' "$LATEST_REPORT" | head -n -1
    fi
    
    echo
    echo -e "${CYAN}━━━ Set This Week's Focus ━━━${NC}"
    echo
    echo "Top 3 standards improvements for this week:"
    echo "1. ________________________________"
    echo "2. ________________________________"
    echo "3. ________________________________"
    echo
    
    # Update session notes
    echo -e "${YELLOW}Updating session notes...${NC}"
    echo "" >> .claude/session-notes.md
    echo "## $(date '+%Y-%m-%d') - Weekly Review" >> .claude/session-notes.md
    echo "**Review Type**: Weekly" >> .claude/session-notes.md
    echo "**Report Generated**: $(date '+%H:%M:%S')" >> .claude/session-notes.md
    echo "" >> .claude/session-notes.md
}

# Monthly review
monthly_review() {
    echo -e "${CYAN}🌊 Monthly Deep Dive${NC}"
    echo
    
    # First run weekly review
    weekly_review
    
    echo
    echo -e "${CYAN}━━━ Trends Analysis ━━━${NC}"
    echo
    
    # Count reports from past month
    REPORT_COUNT=$(find metrics/reports -name "*.md" -mtime -30 | wc -l)
    echo "Reports generated in past 30 days: $REPORT_COUNT"
    
    # Check if standards evolved
    echo
    echo -e "${YELLOW}Standards Evolution Check:${NC}"
    echo "Recent changes to standards docs:"
    git log --oneline --since="1 month ago" -- docs/*STANDARDS*.md docs/*Standards*.md | head -5
    
    echo
    echo -e "${CYAN}━━━ Sacred Trinity Reflection ━━━${NC}"
    echo
    echo "1. Is our \$200/month model delivering value? [Y/n]"
    echo "2. Any friction in Human-AI collaboration? [y/N]"
    echo "3. New patterns to document? [y/N]"
    echo
    
    # Update monthly notes
    echo "" >> .claude/session-notes.md
    echo "## $(date '+%Y-%m-%d') - Monthly Deep Dive" >> .claude/session-notes.md
    echo "**Reports Generated**: $REPORT_COUNT in past month" >> .claude/session-notes.md
    echo "" >> .claude/session-notes.md
}

# Interactive menu
interactive_menu() {
    echo -e "${CYAN}Select Review Type:${NC}"
    echo "  1) Quick Review (session start)"
    echo "  2) Weekly Review"
    echo "  3) Monthly Deep Dive"
    echo "  4) Generate Dashboard Only"
    echo "  5) Open Real-time Monitor"
    echo "  q) Quit"
    echo
    read -p "Choice: " choice
    
    case $choice in
        1) quick_review ;;
        2) weekly_review ;;
        3) monthly_review ;;
        4) 
            python scripts/metrics_dashboard.py
            echo -e "${GREEN}✅ Dashboard generated${NC}"
            ;;
        5) 
            ./scripts/monitor_standards.sh
            ;;
        q|Q) 
            echo -e "${GREEN}✨ Exiting sacred review${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid choice${NC}"
            ;;
    esac
}

# Main execution
main() {
    show_header
    
    case "$REVIEW_TYPE" in
        quick)
            quick_review
            ;;
        weekly)
            weekly_review
            ;;
        monthly)
            monthly_review
            ;;
        menu|interactive|"")
            interactive_menu
            ;;
        *)
            echo -e "${YELLOW}Usage: $0 [quick|weekly|monthly|menu]${NC}"
            echo "  quick   - Quick check for session start"
            echo "  weekly  - Full weekly review"
            echo "  monthly - Deep monthly analysis"
            echo "  menu    - Interactive menu"
            exit 1
            ;;
    esac
    
    echo
    echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${WHITE}✨ Sacred Review Complete ✨${NC}"
    echo -e "${BLUE}Remember: Standards serve consciousness, not the other way around${NC}"
    echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════${NC}"
}

# Run main
main