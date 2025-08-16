# Luminous Nix Test Suite

## Current Test Status

### Real Coverage: 8%
After archiving 955 broken tests that were testing non-existent features, we now have accurate coverage metrics.

### Working Tests (9 passing)
- `test_cli_real_commands.py` - Tests actual CLI commands that exist
- `test_nlp_intent_recognition.py` - Tests intent recognition (5 passing, 5 failing)
- `test_native_backend.py` - Tests the native backend functionality
- `test_flake_simple.py` - Tests flake functionality

### Tests with Issues (19 with collection errors)
Many tests have import errors because they try to import modules that don't exist or have been renamed.

## Test Structure

```
tests/
├── unit/           # Unit tests for individual components
├── integration/    # Integration tests for combined functionality
├── e2e/           # End-to-end tests for full workflows
├── performance/   # Performance benchmarks
├── security/      # Security-specific tests
└── tui/           # Terminal UI tests
```

## Running Tests

### Run all working tests
```bash
poetry run pytest tests/ -k "not error"
```

### Run with coverage
```bash
poetry run pytest --cov=nix_for_humanity --cov-report=term
```

### Run specific test file
```bash
poetry run pytest tests/test_cli_real_commands.py -v
```

## Test Philosophy

Following the golden rule from CLAUDE.md:
> **"Test what IS, build what WILL BE, document what WAS"**

We only test features that actually exist. Tests for aspirational features create false confidence and maintenance burden.

## Archived Tests

In `.archive-2025-08-12/`, we've archived 955 tests that were testing phantom features:
- Tests for 5 backends when only 1 exists
- Tests for advanced learning system that wasn't built
- Tests for symbiotic intelligence features not implemented
- Tests for research modules that don't exist

## Next Steps

1. Fix import errors in remaining tests
2. Write tests for actual features that exist
3. Achieve real 30% coverage with meaningful tests
4. Update tests as features are actually implemented

## Test Guidelines

1. **Never test non-existent features** - Only test what's actually built
2. **Use Poetry for all testing** - Never use pip or venv directly
3. **Import from correct modules** - Check that modules exist before importing
4. **Be honest about coverage** - 8% real coverage is better than 95% fake coverage
5. **Archive broken tests** - Don't delete, but move to archive with explanation

## Common Test Patterns

### Testing CLI Commands
```python
from nix_for_humanity.core.backend import NixForHumanityBackend
from nix_for_humanity.api.schema import Request, Response

backend = NixForHumanityBackend()
request = Request(
    query="install firefox",
    context={"dry_run": True}
)
response = backend.process(request)
```

### Testing Intent Recognition
```python
from nix_for_humanity.core.intents import IntentRecognizer, IntentType

recognizer = IntentRecognizer()
intent = recognizer.recognize("install firefox")
assert intent.type == IntentType.INSTALL_PACKAGE
```

## Coverage Goals

Current: 8% (real, honest coverage)
Goal: 30% (meaningful tests for actual features)
Not Goal: 95% (fake coverage from phantom tests)

Remember: Quality over quantity. One real test is worth more than 100 phantom tests.