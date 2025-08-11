#!/bin/bash
# Archive unnecessary files to clean up the project

echo "🗄️ Archiving chaos to focus on what matters..."
echo "============================================"

# Create archive directory with timestamp
ARCHIVE_DIR="archive/2025-01-legacy"
mkdir -p "$ARCHIVE_DIR"

# Archive future features we don't need yet
echo "📦 Archiving future features..."
mv features/v4.0 "$ARCHIVE_DIR/" 2>/dev/null || echo "  v4.0 already archived"
mv features/v1.5 "$ARCHIVE_DIR/" 2>/dev/null || echo "  v1.5 already archived"
mv features/v2.0/personas/advanced "$ARCHIVE_DIR/" 2>/dev/null || echo "  advanced personas already archived"
mv features/v2.0/multi-modal "$ARCHIVE_DIR/" 2>/dev/null || echo "  multi-modal already archived"
mv features/research "$ARCHIVE_DIR/" 2>/dev/null || echo "  research already archived"

# Archive consciousness/sacred stuff we don't need
echo "📦 Archiving consciousness features..."
mv features/v3.0/intelligence "$ARCHIVE_DIR/" 2>/dev/null || echo "  intelligence already archived"
mv features/v3.0/advanced-learning "$ARCHIVE_DIR/" 2>/dev/null || echo "  advanced-learning already archived"

# Archive old demos
echo "📦 Archiving old demos..."
mv demos "$ARCHIVE_DIR/" 2>/dev/null || echo "  demos already archived"

# Archive multiple virtual environments
echo "📦 Archiving redundant virtual environments..."
mv venv_tui "$ARCHIVE_DIR/" 2>/dev/null || echo "  venv_tui already archived"
mv venv_test "$ARCHIVE_DIR/" 2>/dev/null || echo "  venv_test already archived"
mv venv_quick "$ARCHIVE_DIR/" 2>/dev/null || echo "  venv_quick already archived"

# Archive old documentation
echo "📦 Archiving obsolete documentation..."
mv docs/archive "$ARCHIVE_DIR/docs-archive" 2>/dev/null || echo "  docs/archive already archived"
mv docs/01-VISION/research "$ARCHIVE_DIR/vision-research" 2>/dev/null || echo "  vision research already archived"

# Archive experiment files
echo "📦 Archiving experiments..."
mv experiments "$ARCHIVE_DIR/" 2>/dev/null || echo "  experiments already archived"

# Archive training data
echo "📦 Archiving training data..."
mv training-data "$ARCHIVE_DIR/" 2>/dev/null || echo "  training-data already archived"
mv models "$ARCHIVE_DIR/" 2>/dev/null || echo "  models already archived"

# Archive test models
echo "📦 Archiving test models..."
mv test_models "$ARCHIVE_DIR/" 2>/dev/null || echo "  test_models already archived"
mv test_data "$ARCHIVE_DIR/" 2>/dev/null || echo "  test_data already archived"

# Archive frontends we're not using
echo "📦 Archiving unused frontends..."
mv frontends "$ARCHIVE_DIR/" 2>/dev/null || echo "  frontends already archived"

# Archive old release files
echo "📦 Archiving old releases..."
mv release/v1.0.0 "$ARCHIVE_DIR/" 2>/dev/null || echo "  v1.0.0 release already archived"
mv release/v1.1 "$ARCHIVE_DIR/" 2>/dev/null || echo "  v1.1 release already archived"

# Archive standalone test files in root
echo "📦 Archiving standalone test files..."
mv test_*.py "$ARCHIVE_DIR/" 2>/dev/null || echo "  test files already archived"
mv simple_*.py "$ARCHIVE_DIR/" 2>/dev/null || echo "  simple files already archived"
mv launch_*.py "$ARCHIVE_DIR/" 2>/dev/null || echo "  launch files already archived"
mv realistic_*.py "$ARCHIVE_DIR/" 2>/dev/null || echo "  realistic files already archived"

# Archive misc scripts we don't need
echo "📦 Archiving misc scripts..."
mv create-release-branch.sh "$ARCHIVE_DIR/" 2>/dev/null || echo "  release scripts already archived"
mv push-release.sh "$ARCHIVE_DIR/" 2>/dev/null || echo "  push scripts already archived"
mv fix-github-author.sh "$ARCHIVE_DIR/" 2>/dev/null || echo "  github scripts already archived"

# Archive old run scripts
echo "📦 Archiving old run scripts..."
mv run_tui*.sh "$ARCHIVE_DIR/" 2>/dev/null || echo "  run_tui scripts already archived"

# Archive marketing/presentation files
echo "📦 Archiving presentation files..."
mv share-*.md "$ARCHIVE_DIR/" 2>/dev/null || echo "  share files already archived"
mv v1.1_achievement_demo.md "$ARCHIVE_DIR/" 2>/dev/null || echo "  achievement demo already archived"
mv SESSION_ACHIEVEMENTS.md "$ARCHIVE_DIR/" 2>/dev/null || echo "  session achievements already archived"
mv SACRED_TRINITY_SUCCESS.md "$ARCHIVE_DIR/" 2>/dev/null || echo "  sacred trinity already archived"

# Archive project management files
echo "📦 Archiving old project management files..."
mv PROJECT_PROGRESS_REVIEW.md "$ARCHIVE_DIR/" 2>/dev/null || echo "  progress review already archived"
mv PHASE_3_STATUS_REPORT.md "$ARCHIVE_DIR/" 2>/dev/null || echo "  phase 3 report already archived"
mv DEPENDENCY_FIX_SUMMARY.md "$ARCHIVE_DIR/" 2>/dev/null || echo "  dependency summary already archived"
mv CONSOLIDATION_SUMMARY.md "$ARCHIVE_DIR/" 2>/dev/null || echo "  consolidation already archived"
mv STRUCTURE_CONSOLIDATION_PLAN.md "$ARCHIVE_DIR/" 2>/dev/null || echo "  structure plan already archived"
mv SRC_ORGANIZATION_STATUS.md "$ARCHIVE_DIR/" 2>/dev/null || echo "  src status already archived"
mv README_CONSOLIDATION_REPORT.md "$ARCHIVE_DIR/" 2>/dev/null || echo "  readme report already archived"
mv TEST_COVERAGE_*.md "$ARCHIVE_DIR/" 2>/dev/null || echo "  test coverage plans already archived"

# Archive changelog files (keep main one)
echo "📦 Archiving old changelogs..."
mv CHANGELOG_v1.1_preview.md "$ARCHIVE_DIR/" 2>/dev/null || echo "  v1.1 changelog already archived"

# Archive duplicate readmes
echo "📦 Archiving duplicate documentation..."
mv MVP_README.md "$ARCHIVE_DIR/" 2>/dev/null || echo "  MVP readme already archived"
mv CONFIG_FEATURE.md "$ARCHIVE_DIR/" 2>/dev/null || echo "  config feature already archived"
mv ENHANCED_COMMANDS.md "$ARCHIVE_DIR/" 2>/dev/null || echo "  enhanced commands already archived"

# Clean up data directories
echo "📦 Archiving data directories..."
mv data/databases "$ARCHIVE_DIR/" 2>/dev/null || echo "  databases already archived"
mv data/feedback "$ARCHIVE_DIR/" 2>/dev/null || echo "  feedback already archived"
mv data/preferences "$ARCHIVE_DIR/" 2>/dev/null || echo "  preferences already archived"

# Archive metrics and results
echo "📦 Archiving metrics..."
mv metrics "$ARCHIVE_DIR/" 2>/dev/null || echo "  metrics already archived"
mv results "$ARCHIVE_DIR/" 2>/dev/null || echo "  results already archived"

# Archive learning data
echo "📦 Archiving learning data..."
mv learning "$ARCHIVE_DIR/" 2>/dev/null || echo "  learning already archived"

# Archive SSL certificates (can regenerate)
echo "📦 Archiving SSL certificates..."
mv ssl "$ARCHIVE_DIR/" 2>/dev/null || echo "  ssl already archived"

# Archive node modules if any
echo "📦 Archiving node modules..."
mv node_modules "$ARCHIVE_DIR/" 2>/dev/null || echo "  node_modules already archived"

# Archive tui standalone directory
echo "📦 Archiving standalone tui..."
mv tui "$ARCHIVE_DIR/" 2>/dev/null || echo "  tui already archived"

# Archive benchmarks
echo "📦 Archiving benchmarks..."
mv benchmarks "$ARCHIVE_DIR/" 2>/dev/null || echo "  benchmarks already archived"
mv benchmark_*.py "$ARCHIVE_DIR/" 2>/dev/null || echo "  benchmark files already archived"

# Archive plugins
echo "📦 Archiving plugins..."
mv plugins "$ARCHIVE_DIR/" 2>/dev/null || echo "  plugins already archived"

echo ""
echo "✅ Archiving complete!"
echo ""
echo "📊 What's left (the essentials):"
echo "  - src/           Core source code"
echo "  - tests/         Test suite"
echo "  - docs/          Documentation"
echo "  - bin/           Entry points"
echo "  - scripts/       Utility scripts"
echo "  - features/v3.0/xai/  Working XAI integration"
echo "  - features/v2.0/voice/  Voice interface (keep for later)"
echo "  - pyproject.toml Poetry configuration"
echo "  - flake.nix      Nix configuration"
echo "  - README.md      Main documentation"
echo ""
echo "📦 Everything else has been archived to: $ARCHIVE_DIR"
echo ""
echo "Next step: Fix the CLI imports!"