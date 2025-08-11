# Testing Standards

## Testing Requirements

### Coverage Goals
- Overall: >80% coverage
- Core modules: >90% coverage
- New features: 100% coverage
- Critical paths: 100% coverage

### Before ANY Merge
- All existing tests must pass
- No decrease in coverage
- New features have tests
- Integration tests for API changes

## Test Organization

### Directory Structure
```
tests/
├── unit/              # Fast, isolated tests
├── integration/       # Component interaction tests
├── e2e/              # End-to-end user journeys
├── fixtures/         # Shared test data
├── conftest.py       # Pytest configuration
└── utils/            # Test helpers
```

### File Naming
- Test files: `test_<module>.py`
- Match source structure: `src/module.py` → `tests/unit/test_module.py`
- NO versioned test files (`test_module_v2.py`)
- Use git for test versions

## Writing Tests

### Test Structure
```python
"""Test module for [component name]."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from nix_for_humanity.core import backend


class TestBackend:
    """Test suite for Backend class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.backend = backend.Backend()

    def teardown_method(self):
        """Clean up after tests."""
        # Clean up any created files/resources
        pass

    def test_should_process_valid_query(self):
        """Test that valid queries are processed correctly."""
        # Arrange
        query = "install firefox"
        expected = "nix-env -iA nixpkgs.firefox"

        # Act
        result = self.backend.process(query)

        # Assert
        assert result.command == expected
        assert result.success is True

    def test_should_reject_invalid_query(self):
        """Test that invalid queries are rejected."""
        with pytest.raises(ValueError):
            self.backend.process("")
```

### Test Naming
- Use descriptive names: `test_should_<action>_when_<condition>`
- Group related tests in classes
- One assertion focus per test

### Fixtures
```python
# conftest.py
import pytest

@pytest.fixture
def mock_nix_store():
    """Provide mock Nix store for testing."""
    return {
        "firefox": "firefox-120.0",
        "chromium": "chromium-119.0"
    }

@pytest.fixture
def temp_config(tmp_path):
    """Provide temporary config directory."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    return config_dir
```

## Test Categories

### Unit Tests
- Fast (<100ms per test)
- No external dependencies
- No file I/O (use tmp_path)
- No network calls
- Mock all dependencies

### Integration Tests
```python
@pytest.mark.integration
class TestCLIIntegration:
    """Test CLI integration with backend."""

    def test_cli_executes_command(self):
        """Test full CLI flow."""
        # Tests actual integration
        pass
```

### End-to-End Tests
```python
@pytest.mark.e2e
@pytest.mark.slow
class TestUserJourney:
    """Test complete user workflows."""

    def test_new_user_installs_package(self):
        """Test new user package installation flow."""
        # Simulates real user interaction
        pass
```

## Testing Commands

### Running Tests
```bash
# All tests
pytest

# Specific category
pytest tests/unit/
pytest -m "not slow"

# With coverage
pytest --cov=nix_for_humanity --cov-report=html

# Specific test
pytest tests/unit/test_backend.py::TestBackend::test_should_process_valid_query

# Verbose output
pytest -vv

# Stop on first failure
pytest -x

# Run last failed
pytest --lf
```

### Test Markers
```python
# Mark slow tests
@pytest.mark.slow
def test_large_dataset():
    pass

# Mark tests requiring network
@pytest.mark.network
def test_api_call():
    pass

# Skip conditionally
@pytest.mark.skipif(not HAS_WHISPER, reason="Whisper not installed")
def test_voice_recognition():
    pass
```

## Mocking Guidelines

### What to Mock
- External services
- File system operations
- Network calls
- Time-dependent code
- Random operations

### Mocking Patterns
```python
# Mock external service
@patch('nix_for_humanity.core.executor.subprocess.run')
def test_command_execution(mock_run):
    mock_run.return_value.returncode = 0
    # Test code

# Mock file operations
@patch('pathlib.Path.exists')
def test_file_check(mock_exists):
    mock_exists.return_value = True
    # Test code

# Mock with context manager
def test_with_temp_file():
    with patch('builtins.open', mock_open(read_data='data')):
        # Test code
```

## Test Data

### Fixtures Directory
```
tests/fixtures/
├── sample_configs.py
├── mock_responses.py
└── test_data.json
```

### Using Test Data
```python
from tests.fixtures import sample_configs

def test_config_parsing():
    config = sample_configs.VALID_CONFIG
    result = parse_config(config)
    assert result.is_valid
```

## Performance Testing

### Benchmarking
```python
import pytest

@pytest.mark.benchmark
def test_performance(benchmark):
    """Test operation performance."""
    result = benchmark(expensive_operation)
    assert result
```

### Load Testing
```python
@pytest.mark.slow
def test_concurrent_requests():
    """Test system under load."""
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request) for _ in range(100)]
        results = [f.result() for f in futures]
        assert all(r.success for r in results)
```

## Continuous Integration

### Pre-commit Checks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: tests
        name: tests
        entry: pytest tests/unit/ -x
        language: system
        pass_filenames: false
        always_run: true
```

### CI Pipeline
```yaml
# .github/workflows/test.yml
test:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v2
    - name: Run tests
      run: |
        pytest --cov --cov-report=xml
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

## Test Quality Checklist

Before submitting:
- [ ] Tests are readable and self-documenting
- [ ] Each test has a single responsibility
- [ ] Test names clearly describe what they test
- [ ] No hardcoded paths or magic numbers
- [ ] Proper cleanup in teardown
- [ ] Appropriate use of mocks
- [ ] Tests run in isolation
- [ ] Tests are deterministic
- [ ] Edge cases covered
- [ ] Error cases tested
