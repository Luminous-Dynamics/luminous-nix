# Simplicity-First RFC Template

**RFC Number**: [auto-assigned]  
**Title**: [Feature Name]  
**Author**: [Your Name]  
**Status**: Draft | Review | Accepted | Rejected  
**Created**: [Date]

## Executive Summary
[One paragraph explaining what and why - suitable for Grandma Rose]

## The Litmus Test Pre-Check

Before writing any code, this feature MUST pass all tests:

### 1️⃣ The Explainability Test
**Can I explain this feature's purpose in under 60 seconds?**
- [ ] Yes, here's my 60-second explanation:
```
[Your explanation here]
```

### 2️⃣ The Composition Test  
**Will this feature do ONE thing well with a clean interface?**
- [ ] Yes, the single responsibility is:
```
[Define the ONE thing]
```

### 3️⃣ The "Grandma Rose" Test
**Can I explain the benefit without technical jargon?**
- [ ] Yes, Grandma Rose would understand:
```
[Your jargon-free explanation]
```

### 4️⃣ The Deletion Test
**If removed, would the impact be clear and contained?**
- [ ] Yes, removing this would only affect:
```
[List specific, contained impacts]
```

### 5️⃣ The "Magic vs. Tutorial" Test
**Will the outcome feel magical but the code read like a tutorial?**
- [ ] Yes, because:
```
User experience: [Describe the "magic"]
Code simplicity: [Why it's tutorial-simple]
```

### 6️⃣ The Teachability Test 🆕
**Does this teach users something that eventually makes the feature unnecessary?**
- [ ] Yes, it teaches:
```
[What skill/knowledge the user gains]
[How this leads to not needing the feature]
```

## The Embarrassingly Simple Version

**What's the simplest version we can ship in ONE DAY to get feedback?**

```
Day 1 Implementation:
[Describe the absolute minimum viable version]

What we learn from this:
[What feedback/data this provides]

What we DON'T build yet:
[List all the complexity we're deferring]
```

## Complexity Budget

**Estimated Complexity Cost**: 
- New lines of code: ~[number]
- New dependencies: [list or "none"]
- New concepts introduced: [list]
- **Total complexity units**: [score]

**If this exceeds our budget, what can we DELETE to offset it?**
```
Simplification opportunity:
[What existing code can be removed/simplified]
Expected reduction: [lines/complexity]
```

## User Simplification Factor

**Does this add internal complexity to radically simplify the user experience?**

Internal complexity added:
```
[Be honest about what complexity this adds]
```

User simplification achieved:
```
[Quantify how much simpler the user's life becomes]
```

**10x Rule Check**: Does this create 10x more simplification for users than complexity for us?
- [ ] Yes, because: [explanation]

## Architecture Impact

### Which Layer? (Check ONE)
- [ ] Layer 1: Principled Foundation (research/philosophy)
- [ ] Layer 2: Simple Components (single-purpose code)
- [ ] Layer 3: Elegant Composition (how parts connect)
- [ ] Layer 4: Sophisticated Outcome (user experience)

### Integration Points
```
Existing components used:
[List what we're composing with]

New interfaces needed:
[Define clean boundaries]
```

## Success Metrics

**Primary KPI Impact**:
- Expected Friction Score change: [before] → [after]
- How we'll measure: [specific method]

**Secondary metrics**:
- [ ] Code reduction achieved
- [ ] User learning time reduced
- [ ] Support requests prevented
- [ ] Other: [specify]

## The Three Examples Rule

**Have we seen this pattern THREE times?**
- [ ] No → Don't generalize yet
- [ ] Yes → Here are the three examples:
  1. [First occurrence]
  2. [Second occurrence]
  3. [Third occurrence]

## Decision

**Verdict**: [ ] Approved | [ ] Rejected | [ ] Needs Simplification

**If rejected, why?**
```
[Which Litmus Test failed?]
[Path to approval?]
```

**If approved, implementation plan:**
1. Day 1: Ship embarrassingly simple version
2. Day 2-7: Gather feedback
3. Week 2: Iterate based on learning
4. Week 3-4: Only add complexity if proven necessary

## Appendix: Deep Thinking

[This section can be longer - put your PhD-level analysis here if needed, but the above MUST be simple and clear]

---

## Review Checklist for Reviewers

- [ ] Can you explain this to a new team member in 60 seconds?
- [ ] Is this the simplest possible solution?
- [ ] Does it make the user's life radically simpler?
- [ ] Can we ship something useful in one day?
- [ ] Will users eventually not need this feature?
- [ ] Is the complexity budget justified?

**Remember**: "The strategic thinking proves you COULD build complexity. The simple code proves you CHOSE not to."