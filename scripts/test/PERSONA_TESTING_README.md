# 🎭 Persona Testing Framework

## Quick Start

Run comprehensive persona testing:
```bash
cd /srv/luminous-dynamics/11-meta-consciousness/luminous-nix
./scripts/test-persona-feedback.sh
```

## What It Does

The Persona Feedback Testing Framework validates that Luminous Nix works well for all 10 core personas:

1. **Grandma Rose** (75) - Non-technical, voice-first
2. **Maya** (16, ADHD) - Needs speed and focus
3. **David** (42) - Tired parent, needs reliability
4. **Dr. Sarah** (35) - Researcher, needs precision
5. **Alex** (28) - Blind developer, needs accessibility
6. **Carlos** (52) - Learning NixOS, needs education
7. **Priya** (34) - Busy mom, needs context-awareness
8. **Jamie** (19) - Privacy advocate, needs transparency
9. **Viktor** (67) - ESL, needs simple language
10. **Luna** (14) - Autistic, needs predictability

## Key Features

- **Real Testing**: Uses actual `ask-nix` command, not mocks
- **Persona-Specific Metrics**: Each persona has unique success criteria
- **Actionable Insights**: Generates specific improvement recommendations
- **Comprehensive Reports**: Both JSON (for analysis) and Markdown (for humans)

## Test Scenarios

Each persona is tested with realistic scenarios:
- Grandma Rose: "I want to look at pictures of my grandchildren"
- Maya: "firefox now" (needs instant response)
- Dr. Sarah: "install tensorflow with cuda support"
- Carlos: "what is a package manager"

## Success Metrics

The framework measures:
- **Response Time**: Against persona-specific thresholds
- **Language Complexity**: Technical terms, word count
- **Accessibility**: Screen reader compatibility
- **User Needs**: Does it actually help?

## Output

After testing, you'll find in `test-results/persona-feedback/`:
- `persona-feedback-[timestamp].json` - Complete data
- `persona-feedback-[timestamp].md` - Human-readable report

## Example Report Extract

```markdown
### Key Insights
- ⚠️ Grandma Rose: Critical issues - only 50% success rate
- 🐌 Viktor: Slow responses (3.2s average)
- ✅ Dr. Sarah: Excellent performance (95% success)

### Actionable Improvements
[CRITICAL] Accessibility: Ensure all output is screen-reader compatible
[HIGH] Language Simplification: Implement automatic technical term translation
[MEDIUM] Speed Optimization: Implement instant response mode
```

## Integration

Add to your development workflow:
1. Run before major releases
2. Track success rates over time
3. Focus on underserved personas
4. Use insights to guide development

## Philosophy

> "Every failed test represents a real person we're not serving well enough."

The goal isn't 100% success for technical users - it's adequate success for ALL users, especially the most vulnerable.

---

**Remember**: These aren't just test cases. They're real people who deserve technology that understands them.
