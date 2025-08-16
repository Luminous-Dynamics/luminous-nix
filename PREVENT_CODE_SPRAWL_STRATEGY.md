# 🛡️ Preventing Code Sprawl - Systematic Solutions

*Breaking the cycle of duplicate implementations*

---

## 🔍 Root Cause Analysis

### Why This Keeps Happening

1. **"Enhanced" Pattern Addiction**
   - `main_app.py` → `enhanced_main_app.py` → `enhanced_main_app_with_demo.py`
   - Each "enhancement" creates a new file instead of improving existing
   - Fear of breaking working code leads to duplication

2. **"Unified/Consolidated" Anti-Pattern**
   - Attempts to fix sprawl CREATE MORE SPRAWL
   - `backend.py` → `unified_backend.py` → `consolidated_backend.py`
   - The "consolidation" becomes another variant!

3. **Sacred Trinity Speed Trap**
   - Rapid AI-assisted development
   - "Just create a new file" is faster than refactoring
   - Technical debt compounds exponentially

4. **Missing Architectural Boundaries**
   - No clear "this goes here" rules
   - Multiple ways to implement same feature
   - No single source of truth enforcement

## 🚦 Prevention Strategy

### 1. STRICT File Creation Rules

```python
# .claude/FILE_CREATION_RULES.md

## ❌ NEVER Create These Files:
- *_enhanced.py
- *_unified.py  
- *_consolidated.py
- *_improved.py
- *_v2.py, *_v3.py
- *_new.py
- *_refactored.py

## ✅ ALWAYS Do This Instead:
1. CHECK if functionality exists: grep -r "function_name" src/
2. IMPROVE existing file (add feature flags if needed)
3. USE git branches for experiments
4. DELETE old code when replacing
```

### 2. Automated Sprawl Detection

```python
# scripts/detect-sprawl.py
#!/usr/bin/env python3
"""Pre-commit hook to detect code sprawl patterns."""

import sys
import re
from pathlib import Path

# Forbidden patterns
SPRAWL_PATTERNS = [
    r'.*_enhanced\.(py|js)$',
    r'.*_unified\.(py|js)$',
    r'.*_consolidated\.(py|js)$',
    r'.*_v\d+\.(py|js)$',
    r'.*_new\.(py|js)$',
    r'.*_improved\.(py|js)$',
]

def check_sprawl():
    violations = []
    for pattern in SPRAWL_PATTERNS:
        for path in Path('src').rglob('*'):
            if re.match(pattern, path.name):
                violations.append(str(path))
    
    if violations:
        print("🚨 SPRAWL DETECTED! These files violate naming rules:")
        for v in violations:
            print(f"  ❌ {v}")
        print("\nInstead: Modify the original file or use feature branches!")
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(check_sprawl())
```

### 3. Pre-commit Hooks Configuration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: prevent-sprawl
        name: Prevent Code Sprawl
        entry: python scripts/detect-sprawl.py
        language: system
        pass_filenames: false
        
      - id: no-duplicate-classes
        name: No Duplicate Classes
        entry: python scripts/detect-duplicate-classes.py
        language: system
        types: [python]
        
      - id: single-backend-check
        name: Single Backend Check
        entry: bash -c 'if [ $(find src -name "*backend*.py" | wc -l) -gt 1 ]; then echo "Multiple backend files detected!"; exit 1; fi'
        language: system
        pass_filenames: false
```

### 4. Architectural Decision Records (ADRs)

```markdown
# docs/adr/001-single-implementation-rule.md

## Decision: One Implementation Per Feature

### Status: ACCEPTED

### Context
We keep creating multiple versions of the same functionality.

### Decision
- ONE backend: `core/backend.py`
- ONE TUI app: `ui/app.py`
- ONE CLI entry: `cli/main.py`
- ONE voice pipeline: `voice/pipeline.py`

### Consequences
- Use feature flags for variants
- Use dependency injection for flexibility
- Delete old when replacing
```

### 5. Claude Code Session Rules

```markdown
# .claude/SESSION_RULES.md

## 🚨 MANDATORY Before Every Session:

1. Run sprawl check:
   ```bash
   ./scripts/detect-sprawl.py
   find . -name "*_enhanced*" -o -name "*_unified*" | head -20
   ```

2. Check for duplicates:
   ```bash
   # List all backends
   find src -name "*backend*.py" -type f
   
   # List all UI apps  
   find src -name "*app*.py" -path "*/ui/*"
   ```

3. Read prevention rules:
   ```bash
   cat PREVENT_CODE_SPRAWL_STRATEGY.md | head -50
   ```

## 🛑 NEVER:
- Create "enhanced" versions
- Create "unified" versions
- Create "v2" versions
- Keep old code "just in case"

## ✅ ALWAYS:
- Modify existing files
- Use git branches for experiments
- Delete replaced code immediately
- Check if feature already exists
```

### 6. Continuous Monitoring

```python
# scripts/sprawl-monitor.py
#!/usr/bin/env python3
"""Weekly sprawl report generator."""

import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict

def generate_sprawl_report():
    report = {
        "date": datetime.now().isoformat(),
        "duplicates": defaultdict(list),
        "sprawl_score": 0,
    }
    
    # Check for duplicate functionality
    patterns = {
        "backends": "*backend*.py",
        "ui_apps": "*/ui/*app*.py",
        "voice": "*voice*.py",
        "cli": "*/cli/*.py",
    }
    
    for category, pattern in patterns.items():
        files = list(Path('src').rglob(pattern))
        if len(files) > 1:
            report["duplicates"][category] = [str(f) for f in files]
            report["sprawl_score"] += len(files) - 1
    
    # Save report
    report_path = Path(f"metrics/sprawl/sprawl_{datetime.now():%Y%m%d}.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2))
    
    # Alert if sprawl is growing
    if report["sprawl_score"] > 5:
        print(f"🚨 HIGH SPRAWL ALERT: Score {report['sprawl_score']}")
        print("Duplicates found:")
        for category, files in report["duplicates"].items():
            print(f"  {category}: {len(files)} files")
        return 1
    return 0

if __name__ == "__main__":
    exit(generate_sprawl_report())
```

### 7. Git Workflow Enforcement

```bash
# .githooks/pre-commit
#!/bin/bash

# Check for sprawl patterns in staged files
STAGED=$(git diff --cached --name-only)

for file in $STAGED; do
    if echo "$file" | grep -E "(_enhanced|_unified|_consolidated|_v[0-9]+)\.(py|js)$"; then
        echo "❌ BLOCKED: $file matches sprawl pattern!"
        echo "Please modify the original file instead."
        exit 1
    fi
done

# Check for multiple backends
BACKEND_COUNT=$(find src -name "*backend*.py" -type f | wc -l)
if [ $BACKEND_COUNT -gt 1 ]; then
    echo "❌ Multiple backend files detected!"
    echo "Consolidate to single src/nix_for_humanity/core/backend.py"
    exit 1
fi

echo "✅ No sprawl patterns detected"
```

## 📊 Success Metrics

### Weekly Sprawl Score
```python
# Target metrics
METRICS = {
    "max_backends": 1,
    "max_ui_apps": 1,
    "max_voice_modules": 1,
    "max_file_versions": 1,  # No _v2, _v3 files
    "duplicate_threshold": 10,  # Max 10% code duplication
}
```

### Dashboard Integration

```markdown
## 🛡️ Anti-Sprawl Metrics

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Backend Files | 5 | 1 | ❌ VIOLATION |
| UI App Files | 11 | 1 | ❌ VIOLATION |
| Voice Modules | 4 | 1 | ⚠️ WARNING |
| "Enhanced" Files | 8 | 0 | ❌ VIOLATION |
| Sprawl Score | 15 | <3 | ❌ CRITICAL |
```

## 🔄 Cultural Change Required

### From: "Just Make It Work"
- Create new file
- Keep old "for safety"
- "Enhanced" versions
- Never delete anything

### To: "Keep It Clean"
- Improve existing code
- Trust version control
- Feature flags for variants
- Delete immediately when replacing

## 🎯 Implementation Plan

### Week 1: Setup Prevention
```bash
# 1. Install pre-commit hooks
poetry add --dev pre-commit
pre-commit install

# 2. Add sprawl detection
cp scripts/detect-sprawl.py scripts/
chmod +x scripts/detect-sprawl.py

# 3. Configure git hooks
cp .githooks/pre-commit .git/hooks/
chmod +x .git/hooks/pre-commit
```

### Week 2: Clean Existing Sprawl
```bash
# Run consolidation
./scripts/refactor-consolidate-backends.sh

# Archive enhanced versions
mkdir -p archive/sprawl-cleanup
mv src/**/*_enhanced*.py archive/sprawl-cleanup/
mv src/**/*_unified*.py archive/sprawl-cleanup/
```

### Week 3: Monitor & Enforce
```bash
# Weekly sprawl check
crontab -e
# Add: 0 9 * * MON /path/to/scripts/sprawl-monitor.py

# CI/CD integration
# Add to .github/workflows/ci.yml:
- name: Check for sprawl
  run: python scripts/detect-sprawl.py
```

## 🚨 Red Flags to Watch For

### In Code Reviews
- Files ending in `_enhanced`, `_new`, `_v2`
- Multiple files with similar names
- "Temporary" implementations
- Commented out old code
- TODO: merge with X

### In Commit Messages
- "Adding improved version"
- "New implementation of X"
- "Better version of Y"
- "Keeping old for reference"

## 💡 Alternative Patterns (Use These Instead)

### Feature Flags
```python
# Instead of enhanced_app.py
class App:
    def __init__(self, features=None):
        self.features = features or {}
        
    def render(self):
        if self.features.get('enhanced_ui'):
            return self.render_enhanced()
        return self.render_standard()
```

### Strategy Pattern
```python
# Instead of multiple backends
class Backend:
    def __init__(self, strategy='native'):
        self.strategy = self._load_strategy(strategy)
    
    def execute(self, command):
        return self.strategy.execute(command)
```

### Composition Over Duplication
```python
# Instead of consolidated_voice.py
class VoicePipeline:
    def __init__(self, recognizer=None, synthesizer=None):
        self.recognizer = recognizer or DefaultRecognizer()
        self.synthesizer = synthesizer or DefaultSynthesizer()
```

---

## ✅ Success Criteria

**After 30 days:**
- [ ] Zero "enhanced" files
- [ ] Single backend implementation
- [ ] Single UI app
- [ ] Sprawl score < 3
- [ ] All tests passing
- [ ] No new duplicates

**After 90 days:**
- [ ] Sprawl prevention automatic
- [ ] Team follows patterns naturally
- [ ] Code reviews catch violations
- [ ] Metrics show improvement

---

*"The best code is no code. The second best is code that replaces old code."*

**Remember**: Every "enhanced" version is technical debt. Every "unified" attempt creates more sprawl. The solution is discipline, not more code.
