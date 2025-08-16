# 🎯 Refactoring Priorities - Quick Action Plan

## 🔴 CRITICAL (Do This Week)

### 1. Backend Consolidation
**Problem**: 5 different backend files (2,697 lines total)
**Solution**: Merge into single `core/backend.py`
**Script**: Run `./scripts/refactor-consolidate-backends.sh`

```bash
# Quick consolidation
cd /srv/luminous-dynamics/11-meta-consciousness/luminous-nix
./scripts/refactor-consolidate-backends.sh
```

### 2. Remove Duplicate UI Files
**Problem**: 11 UI files with overlapping functionality
**Solution**: Keep only `ui/app.py` and `ui/widgets/`

```bash
# Archive duplicates
mkdir -p archive/ui-cleanup
mv src/nix_for_humanity/ui/enhanced_* archive/ui-cleanup/
mv src/nix_for_humanity/ui/consolidated_ui.py archive/ui-cleanup/
```

## 🟡 HIGH (Next Week)

### 3. Fix 20 TODOs
**Locations**:
- `websocket/realtime.py` - 4 TODOs (auth, streaming)
- `voice/recognition.py` - 2 TODOs (Whisper, Vosk)
- `config/loader.py` - 3 TODOs (error handling)
- Others in `ai/nlp.py`, `nix/native_backend.py`

### 4. Voice Module Cleanup
**Problem**: 4 different voice interface files
**Solution**: Single `voice/pipeline.py`

## 🟢 MEDIUM (Next Month)

### 5. Import Standardization
- Remove all `unified_` and `consolidated_` prefixes
- Single import path per module
- Fix circular dependencies

### 6. Type Hints Completion
- Add to ~30% of functions missing them
- Especially in `core/` and `cli/` modules

## 🔵 LOW (When Time Permits)

### 7. Test Consolidation
- Remove `test_*_simple.py` duplicates
- Consolidate test utilities

### 8. Documentation Updates
- Update architecture diagrams
- Remove references to deleted files

---

## 🚀 Quick Win Commands

```bash
# 1. Find and remove all .bak files
find . -name "*.bak" -delete

# 2. Archive old migration scripts
mkdir -p archive/old-scripts
mv fix_*.py archive/old-scripts/

# 3. Standardize imports
find src/ -type f -name "*.py" -exec sed -i \
  's/from.*unified_backend/from .core.backend/g' {} +

# 4. Run tests to verify
poetry run pytest --tb=short
```

---

**Estimated Time**: 2 weeks total
**Risk**: Low (95% test coverage)
**Impact**: 20% reduction in code, much cleaner architecture
