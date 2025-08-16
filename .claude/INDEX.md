# .Claude

*This directory contains essential context files for Claude to understand and work effectively on the Luminous Nix project.*

## 📚 Contents

- [ACCESSIBILITY_REQUIREMENTS](ACCESSIBILITY_REQUIREMENTS.md)
- [CLAUDE_PROJECT_CONTEXT](CLAUDE_PROJECT_CONTEXT.md)
- [CLOUD_AI_CONSIDERATIONS](CLOUD_AI_CONSIDERATIONS.md)
- [CLOUD_AI_STRATEGY](CLOUD_AI_STRATEGY.md)
- [CONTEXT](CONTEXT.md)
- [DEVELOPMENT_PHILOSOPHY](DEVELOPMENT_PHILOSOPHY.md)
- [DOCUMENTATION_UPDATE_SUMMARY](DOCUMENTATION_UPDATE_SUMMARY.md)
- [IMPLEMENTATION_PRIORITIES](IMPLEMENTATION_PRIORITIES.md)
- [LAYERED_REALITY_POLICY](LAYERED_REALITY_POLICY.md)
- [MEMORY_UPDATE_2025_07_23](MEMORY_UPDATE_2025_07_23.md)
- [NATURAL_LANGUAGE_FIRST_CLARIFICATION](NATURAL_LANGUAGE_FIRST_CLARIFICATION.md)
- [NATURAL_LANGUAGE_FIRST_PRINCIPLE](NATURAL_LANGUAGE_FIRST_PRINCIPLE.md)
- [NIXOS_INTEGRATION_PATTERNS](NIXOS_INTEGRATION_PATTERNS.md)
- [NIX_DEVELOPMENT_RULES](NIX_DEVELOPMENT_RULES.md)
- [NLP_INTENT_PATTERNS](NLP_INTENT_PATTERNS.md)
- [OPERATIONAL_INTELLIGENCE](OPERATIONAL_INTELLIGENCE.md)
- [PROJECT_CONTEXT](PROJECT_CONTEXT.md)
- [PROJECT_STATUS](PROJECT_STATUS.md)
- [SERVICE_PORTS_REGISTRY](SERVICE_PORTS_REGISTRY.md)
- [TAURI_IMPLEMENTATION_APPROACH](TAURI_IMPLEMENTATION_APPROACH.md)
- [TECHNICAL_DECISIONS](TECHNICAL_DECISIONS.md)
- [TECH_STACK_DECISION](TECH_STACK_DECISION.md)
- [TEXT_FOUNDATION_UPDATE_SUMMARY](TEXT_FOUNDATION_UPDATE_SUMMARY.md)
- [VISION_ALIGNMENT](VISION_ALIGNMENT.md)
- [VISUAL_ELEMENTS_PHILOSOPHY](VISUAL_ELEMENTS_PHILOSOPHY.md)

---

## Original Documentation


This directory contains essential context files for Claude to understand and work effectively on the Luminous Nix project.

## Memory File Structure

### Core Context Files

1. **CLAUDE.md** (in project root)
   - Main project context and status
   - Current development state
   - Quick reference commands
   - Primary memory file - always check this first

2. **PROJECT_CONTEXT.md**
   - Detailed project identity
   - Technical stack decisions
   - Development approach
   - The "what" and "how" of the project

3. **VISION_ALIGNMENT.md**
   - Core vision and philosophy
   - What this IS and IS NOT
   - Three-stage journey
   - Alignment checkpoints
   - The "why" of the project

### Technical Reference Files

4. **NIXOS_INTEGRATION_PATTERNS.md**
   - NixOS best practices
   - Safe command patterns
   - Common operations
   - Error handling
   - Critical for NixOS integration work

5. **NLP_INTENT_PATTERNS.md**
   - Core intent recognition patterns
   - Natural language variations
   - Multi-turn conversation flows
   - Ambiguity resolution
   - Foundation for NLP implementation

6. **TECHNICAL_DECISIONS.md**
   - Architecture decisions log
   - Technology choices with rationale
   - Rejected alternatives
   - Performance targets
   - Reference for technical choices

7. **ACCESSIBILITY_REQUIREMENTS.md**
   - Non-negotiable accessibility standards
   - Testing requirements
   - Persona-specific needs
   - Legal compliance
   - Must read before any UI work

8. **SERVICE_PORTS_REGISTRY.md**
   - Port allocations (3456-3459)
   - Integration with ecosystem
   - Conflict resolution
   - Main registry location

9. **DEVELOPMENT_PHILOSOPHY.md**
   - $200/month development model
   - Ship weekly approach
   - Pragmatic over perfect
   - Claude Code Max workflow
   - What really matters

## How to Use These Files

### For New Sessions
1. Read CLAUDE.md (root) first - current state
2. Review VISION_ALIGNMENT.md - understand the goal
3. Check relevant technical files for specific work

### When Making Decisions
- Technical choices → TECHNICAL_DECISIONS.md
- NixOS operations → NIXOS_INTEGRATION_PATTERNS.md
- UI/UX changes → ACCESSIBILITY_REQUIREMENTS.md
- NLP patterns → NLP_INTENT_PATTERNS.md

### For Context Loading
These files should be referenced (with @) in the root CLAUDE.md to ensure they're loaded in new sessions:
```
@.claude/VISION_ALIGNMENT.md
@.claude/NIXOS_INTEGRATION_PATTERNS.md
@.claude/TECHNICAL_DECISIONS.md
```

## Maintenance

### When to Update
- Major decisions made → Update TECHNICAL_DECISIONS.md
- New patterns discovered → Update NLP_INTENT_PATTERNS.md
- Vision clarification → Update VISION_ALIGNMENT.md
- Architecture changes → Update PROJECT_CONTEXT.md

### Update Process
1. Make changes in appropriate file
2. Update root CLAUDE.md if needed
3. Commit with clear message
4. Test in fresh Claude session

## Critical Reminders

### Always Remember
- **NLP is primary** - GUI only for learning
- **Local-first** - No cloud processing
- **Accessibility-first** - If Alex can't use it, it's broken
- **Privacy sacred** - No telemetry, no tracking
- **$200/month model** - Pragmatic over perfect

### The Test
Before any feature, ask:
1. Can Grandma Rose use it with voice only?
2. Can Alex use it with screen reader only?
3. Does it work offline?
4. Will it eventually disappear?

If any answer is "no", reconsider.

---

*These memory files are the accumulated wisdom of the project. Treat them as living documents that grow with our understanding.*
