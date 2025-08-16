# Archive Log - 2025-08-10

## Purpose
This archive contains duplicate implementations and deprecated code discovered during architecture review.
These files were creating confusion and maintenance burden.

## Archive Structure
- `cli-variants/` - Duplicate CLI entry points (should only have one: bin/ask-nix)
- `implementations/` - Alternative implementation attempts
- `features/` - Versioned feature directories
- `old-archives/` - Previous archive directories
- `docs/` - Outdated documentation

## Files Archived

### CLI Variants (30+ duplicates)
These were all variations of the same CLI tool. We should only have `bin/ask-nix`.

- `bin/ask-nix-adaptive` - Duplicate CLI variant
- `bin/ask-nix-ai-aware` - Duplicate CLI variant
- `bin/ask-nix-ai-env` - Duplicate CLI variant
- `bin/ask-nix-config` - Duplicate CLI variant
- `bin/ask-nix-core` - Duplicate CLI variant
- `bin/ask-nix-enhanced` - Duplicate CLI variant
- `bin/ask-nix-hybrid` - Duplicate CLI variant
- `bin/ask-nix-hybrid-v2` - Duplicate CLI variant
- `bin/ask-nix-learning` - Duplicate CLI variant
- `bin/ask-nix-modern` - Duplicate CLI variant
- `bin/ask-nix-new` - Duplicate CLI variant
- `bin/ask-nix-python` - Duplicate CLI variant
- `bin/ask-nix-refactored` - Duplicate CLI variant
- `bin/ask-nix-v1` - Duplicate CLI variant
- `bin/ask-nix-v3` - Duplicate CLI variant
- `bin/ask-nix-xai` - Duplicate CLI variant
- `archive/` - Old archive directory
- `features/v1.0/` - Versioned feature directory
- `features/v2.0/` - Versioned feature directory
- `features/v3.0/` - Versioned feature directory

## Why These Were Archived

### CLI Variants
We had 30+ variants like `ask-nix-v2`, `ask-nix-enhanced`, etc. This created:
- Confusion about which to use
- Maintenance burden
- Inconsistent behavior
- Code duplication

**Solution**: Single entry point `bin/ask-nix` with all features integrated.

### Multiple Archives
Having multiple archive directories (`archive/`, `archive-old/`, etc.) nested within each other was:
- Confusing
- Taking up unnecessary space
- Making it hard to find things

**Solution**: Single `.archive-YYYY-MM-DD/` directory per consolidation.

### Versioned Features
Directories like `features/v1.0/`, `features/v2.0/` suggested we needed multiple versions simultaneously.

**Solution**: Use git branches/tags for versions, not directories.

### Alternative Implementations
Multiple attempts at the same functionality (`mvp_simplified`, `nodejs-mvp`, etc.) created confusion.

**Solution**: One canonical implementation in `src/nix_for_humanity/`.

## Recovery Instructions

If you need to recover any of these files:

1. They are safely stored in this archive
2. Review why they were archived first
3. If truly needed, copy (don't move) back to proper location
4. Update to match current architecture before using

## Lessons Learned

1. **Check before creating** - Always search for existing implementations
2. **Edit don't duplicate** - Modify existing code instead of creating new versions
3. **Use git for versions** - Let version control handle iterations
4. **One source of truth** - Single implementation per feature
5. **Clean as you go** - Don't let duplicates accumulate

---
*Archived by: Archive Consolidation Script*
*Date: 2025-08-10*
*Purpose: Clean up duplicate implementations discovered during architecture review*
