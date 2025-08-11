# 📝 Documentation Standards

**Stop documentation sprawl before it starts.** Follow these rules for all documentation.

## 🎯 Core Principles

1. **One Source of Truth** - Each topic has exactly ONE document
2. **Document Reality** - What works NOW, not future dreams
3. **User First** - Write for users, not to impress developers
4. **Examples > Explanations** - Show, don't tell
5. **Maintain > Create** - Update existing docs before creating new ones

## 📁 Where Documentation Goes

```
docs/
├── START-HERE.md          # NEVER change this entry point
├── TROUBLESHOOTING.md     # All problems and solutions
├── ARCHITECTURE-VISUAL.md # System diagrams only
├── README.md              # Brief overview only
│
├── 01-VISION/            # Why (philosophy, roadmap)
├── 02-ARCHITECTURE/      # How (technical design)
├── 03-DEVELOPMENT/       # Contributing (dev guides)
├── 04-OPERATIONS/        # Running (deployment, config)
├── 05-REFERENCE/         # What (APIs, commands)
├── 06-TUTORIALS/         # Learning (step-by-step)
│
└── archive/              # Old docs go here to die
```

### Decision Tree: Where Does My Doc Go?

```
Is it about WHY we built this?
  → 01-VISION/

Is it about HOW it's built?
  → 02-ARCHITECTURE/

Is it about CONTRIBUTING?
  → 03-DEVELOPMENT/

Is it about DEPLOYING/RUNNING?
  → 04-OPERATIONS/

Is it a REFERENCE (API, commands)?
  → 05-REFERENCE/

Is it a TUTORIAL/GUIDE?
  → 06-TUTORIALS/

Is it outdated?
  → archive/

Not sure?
  → DON'T CREATE IT. Update existing doc instead.
```

## 📋 Document Template

Every document MUST follow this structure:

```markdown
# [Emoji] Title

**One-line description.** What this document provides.

## What Works

What actually functions RIGHT NOW.

## What's Coming (v1.1)

🚧 Features in active development

## What's Planned (Future)

📅 Future ideas (minimize this section)

## Quick Example

\```bash
# Actual working command
ask-nix "install firefox"
\```

## Details

[Main content here - keep it practical]

## Troubleshooting

Common issues and solutions.

## See Also

- [Related Doc 1](link)
- [Related Doc 2](link)
```

## ✅ Good Documentation

### Example: Good Title
```markdown
# 🔧 Installing Nix for Humanity
```
- Clear emoji
- Active verb
- Specific topic

### Example: Good Description
```markdown
**Install and configure Nix for Humanity in 5 minutes.** Step-by-step guide for all platforms.
```
- Time estimate
- Clear outcome
- Target audience

### Example: Good Code Block
```bash
# Install via pip (works on all systems)
pip install nix-for-humanity

# Verify installation
ask-nix --version
# Output: nix-for-humanity 1.0.0
```
- Comments explain purpose
- Shows expected output
- Actually works

## ❌ Bad Documentation

### Example: Bad Title
```markdown
# Sacred Consciousness Integration Manifestation Guide
```
- Too mystical
- Unclear purpose
- No emoji indicator

### Example: Bad Description
```markdown
This document explores the transcendent possibilities of human-AI consciousness co-evolution through the lens of sacred technology...
```
- Too philosophical
- No practical value
- No clear outcome

### Example: Bad Code Block
```bash
# This will work in v2.0
ask-nix --consciousness-mode --sacred-trinity --transcendent
```
- Doesn't actually work
- No explanation
- Aspirational features

## 📏 Documentation Rules

### File Naming
```
✅ GOOD                     ❌ BAD
installation-guide.md       INSTALLATION_GUIDE_V2_FINAL.md
troubleshooting.md         troubleshooting-enhanced-v3.md
api-reference.md           API_REFERENCE_COMPLETE_FINAL_2.md
```

### File Size
- **Target**: 100-500 lines
- **Maximum**: 1000 lines
- **Too big?** Split into logical sections
- **Too small?** Merge with related doc

### Update Frequency
- **Features change**: Update immediately
- **Errors found**: Fix within 24 hours
- **Monthly review**: Check all docs for accuracy

## 🚫 What NOT to Document

### Don't Document
- Future features that don't exist
- Internal implementation details users don't need
- Philosophy in technical docs
- Duplicate information
- Obvious things ("click the button to click the button")

### Don't Create New Docs For
- Version updates (use CHANGELOG.md)
- Status reports (use GitHub issues)
- Planning (use GitHub projects)
- Research (separate research repo)

## 🔄 Documentation Lifecycle

### 1. Before Creating
```bash
# Check if topic already exists
grep -r "your topic" docs/

# Found something? UPDATE IT
# Nothing found? Continue to step 2
```

### 2. Creating
- Use the template above
- Put in correct directory
- One topic per document
- Focus on user value

### 3. Reviewing
Before commit, ask:
- [ ] Does this work TODAY?
- [ ] Is this the ONLY doc about this topic?
- [ ] Would a new user understand this?
- [ ] Are all examples tested and working?

### 4. Maintaining
- Review monthly
- Update immediately when features change
- Archive when obsolete

### 5. Archiving
```bash
# Move to archive with date
mv old-doc.md archive/cleanup-$(date +%Y%m%d)/

# Add to archive log
echo "- old-doc.md: Reason for archival" >> archive/cleanup-$(date +%Y%m%d)/ARCHIVE_LOG.md
```

## 📊 Quality Checklist

Before committing any documentation:

### Content
- [ ] Documents WORKING features only
- [ ] Examples are tested and work
- [ ] No duplicate information
- [ ] Clear target audience
- [ ] Practical, not philosophical

### Structure
- [ ] Follows template
- [ ] In correct directory
- [ ] Proper markdown formatting
- [ ] Includes examples
- [ ] Has troubleshooting section

### Style
- [ ] Clear, simple language
- [ ] Active voice
- [ ] Present tense for current features
- [ ] Future tense for planned features
- [ ] No mystical language in technical docs

## 🎯 The Golden Rule

**When in doubt, DON'T create new documentation.**

Instead:
1. Update existing docs
2. Improve examples
3. Fix broken links
4. Add troubleshooting
5. Simplify complex sections

## 📈 Success Metrics

Good documentation has:
- **Low file count** - Fewer, better docs
- **High accuracy** - Everything documented works
- **Quick answers** - Users find solutions fast
- **Low maintenance** - Doesn't need constant updates
- **Clear navigation** - Users know where to look

## 🚨 Red Flags

Your documentation is failing if:
- Multiple files cover the same topic
- Users can't find what they need
- Examples don't work
- Philosophy mixed with technical content
- More than 100 files in docs/
- Frequent "where is X documented?" questions

---

## Summary

**Remember**: The best documentation is documentation that doesn't need to exist because the system is intuitive. The second best is documentation that's so clear it's read once and understood forever.

**Every new document is a future maintenance burden. Create wisely.**

---
*Last updated: 2025-08-10*  
*Next review: Monthly*