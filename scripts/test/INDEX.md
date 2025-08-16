# Test

*This directory contains all test scripts for the Luminous Nix project.*

## 📚 Contents

- [PERSONA_TESTING_README](PERSONA_TESTING_README.md)

### 📁 Subdirectories

- [__pycache__/](__pycache__/) - 0 documents

---

## Original Documentation


This directory contains all test scripts for the Luminous Nix project.

## Categories

### Core Testing
- **test-all-commands.sh** - Test all supported commands
- **test-all-core-commands.sh** - Test core command set
- **test-execute-commands.sh** - Test --execute flag functionality

### Feature Testing
- **test-personas.py** - Test against all 10 personas
- **test-personas.js** - JavaScript persona tests
- **test-nlp-integration.js** - NLP system integration tests
- **test-learning-integration.sh** - Learning system tests

### Execution Testing
- **test-real-execution.sh** - Test actual command execution
- **test-safe-execution.js** - Test safe execution modes
- **test-dry-run.js** - Test dry-run functionality
- **test_execution.py** - Python execution tests

### Installation Testing
- **test-working-install.sh** - Test package installation
- **test-search-command.sh** - Test search functionality

### Integration Testing
- **test-unified-ask-nix.sh** - Test unified CLI
- **test-enhanced-tool.sh** - Test enhanced features
- **test-demo-build.sh** - Test demo build process

## Running Tests

```bash
# Run all tests
./run-all-tests.sh

# Run specific test category
./test-personas.py

# Run with coverage
npm test -- --coverage
```

## Adding New Tests

1. Create test script in appropriate category
2. Make it executable: `chmod +x test-name.sh`
3. Add to test suite in `run-all-tests.sh`
4. Document expected behavior
