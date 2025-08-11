# Python Development Standards

## Project Setup

### Requirements
- Python 3.11+ required
- Poetry for dependency management
- Type hints for all public functions
- Google-style docstrings

### Project Structure
```
pyproject.toml          # Poetry configuration
poetry.lock            # Locked dependencies
src/
  nix_for_humanity/
    __init__.py       # Package initialization
    py.typed          # Marker for type hints
tests/
.flake8               # Linting configuration
mypy.ini              # Type checking configuration
```

## Code Style

### Import Organization
```python
"""Module docstring."""

# Standard library imports
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Third-party imports
import click
import pytest
from pydantic import BaseModel

# Local application imports
from nix_for_humanity.core import backend
from nix_for_humanity.utils import helpers
```

### Naming Conventions
```python
# Module names: lowercase with underscores
module_name.py

# Class names: PascalCase
class NixBackend:
    pass

# Function/variable names: snake_case
def process_query(user_input: str) -> str:
    response_text = ""
    return response_text

# Constants: UPPERCASE
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30

# Protected: single underscore prefix
_internal_state = {}

# Private: double underscore prefix (name mangling)
__private_method()
```

## Type Hints

### Basic Types
```python
from typing import Dict, List, Optional, Union, Any, Tuple
from pathlib import Path

def process_file(
    file_path: Path,
    encoding: str = "utf-8",
    max_size: Optional[int] = None
) -> Dict[str, Any]:
    """Process a file and return metadata."""
    pass
```

### Custom Types
```python
from typing import TypedDict, Literal, Protocol

class Config(TypedDict):
    """Configuration dictionary structure."""
    host: str
    port: int
    debug: bool

CommandType = Literal["install", "remove", "update"]

class Executor(Protocol):
    """Protocol for command executors."""
    def execute(self, command: str) -> bool:
        ...
```

### Generic Types
```python
from typing import TypeVar, Generic

T = TypeVar('T')

class Result(Generic[T]):
    """Generic result wrapper."""
    def __init__(self, value: T, success: bool):
        self.value = value
        self.success = success
```

## Documentation

### Module Documentation
```python
"""
Natural language processing for Nix commands.

This module provides NLP capabilities for translating natural
language queries into Nix commands. It uses a hybrid approach
combining rule-based and statistical methods.

Example:
    >>> from nix_for_humanity.nlp import process
    >>> result = process("install firefox")
    >>> print(result.command)
    'nix-env -iA nixpkgs.firefox'
"""
```

### Function Documentation
```python
def process_query(
    query: str,
    context: Optional[Dict[str, Any]] = None,
    timeout: float = 30.0
) -> Response:
    """
    Process a natural language query into a Nix command.
    
    Translates user intent into executable Nix commands using
    NLP techniques and pattern matching.
    
    Args:
        query: Natural language query from user.
        context: Optional session context for stateful processing.
        timeout: Maximum processing time in seconds.
        
    Returns:
        Response object containing:
            - command: The generated Nix command
            - explanation: Human-readable explanation
            - confidence: Confidence score (0-1)
            
    Raises:
        ValueError: If query is empty or invalid.
        TimeoutError: If processing exceeds timeout.
        
    Example:
        >>> response = process_query("install firefox")
        >>> print(response.command)
        'nix-env -iA nixpkgs.firefox'
    """
    if not query:
        raise ValueError("Query cannot be empty")
    
    # Implementation here
    return Response(command="", explanation="", confidence=0.0)
```

### Class Documentation
```python
class NixBackend:
    """
    Backend for processing Nix operations.
    
    This class provides the core logic for translating natural
    language queries into Nix commands and executing them safely.
    
    Attributes:
        config: Configuration dictionary
        executor: Command executor instance
        cache: Result cache for performance
        
    Example:
        >>> backend = NixBackend(config={'safe_mode': True})
        >>> result = backend.process("install firefox")
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the backend.
        
        Args:
            config: Optional configuration overrides.
        """
        self.config = config or {}
```

## Error Handling

### Exception Hierarchy
```python
class NixForHumanityError(Exception):
    """Base exception for all custom errors."""
    pass

class ValidationError(NixForHumanityError):
    """Raised when input validation fails."""
    pass

class ExecutionError(NixForHumanityError):
    """Raised when command execution fails."""
    pass
```

### Error Handling Patterns
```python
# Good: Specific exception handling
try:
    result = execute_command(cmd)
except subprocess.TimeoutExpired:
    logger.error(f"Command timed out: {cmd}")
    raise ExecutionError(f"Command timed out after {timeout}s")
except subprocess.CalledProcessError as e:
    logger.error(f"Command failed: {e.stderr}")
    raise ExecutionError(f"Command failed: {e.stderr}")

# Bad: Bare except
try:
    result = execute_command(cmd)
except:  # Never do this!
    pass
```

### Context Managers
```python
from contextlib import contextmanager

@contextmanager
def temporary_config(config: Dict):
    """Temporarily override configuration."""
    old_config = current_config.copy()
    try:
        current_config.update(config)
        yield current_config
    finally:
        current_config.clear()
        current_config.update(old_config)
```

## Logging

### Setup
```python
import logging
from pathlib import Path

# Configure at module level
logger = logging.getLogger(__name__)

def setup_logging(level: str = "INFO"):
    """Configure application logging."""
    logging.basicConfig(
        level=getattr(logging, level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('app.log')
        ]
    )
```

### Usage
```python
# Use appropriate levels
logger.debug(f"Processing query: {query}")
logger.info(f"Command executed successfully: {cmd}")
logger.warning(f"Deprecated function called: {func_name}")
logger.error(f"Failed to execute command: {error}")
logger.critical(f"System configuration corrupted")

# Include context
logger.error(
    "Command execution failed",
    extra={
        'command': cmd,
        'user': user_id,
        'error': str(error)
    }
)
```

## Performance

### Profiling
```python
import cProfile
import pstats
from functools import wraps
import time

def profile(func):
    """Decorator for profiling functions."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        result = func(*args, **kwargs)
        profiler.disable()
        
        stats = pstats.Stats(profiler)
        stats.sort_stats('cumulative')
        stats.print_stats(10)
        
        return result
    return wrapper

def timeit(func):
    """Decorator for timing functions."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        logger.debug(f"{func.__name__} took {end - start:.4f}s")
        return result
    return wrapper
```

### Optimization Guidelines
- Profile before optimizing
- Use generators for large datasets
- Cache expensive computations
- Prefer list comprehensions over loops
- Use `__slots__` for classes with many instances

## Security

### Input Validation
```python
import re
from pathlib import Path

def validate_path(path_str: str) -> Path:
    """Validate and sanitize file path."""
    # Remove any path traversal attempts
    path_str = re.sub(r'\.\.+', '', path_str)
    
    path = Path(path_str).resolve()
    
    # Ensure path is within allowed directory
    if not path.is_relative_to(ALLOWED_DIR):
        raise ValidationError(f"Path outside allowed directory: {path}")
    
    return path
```

### Command Execution
```python
import subprocess
import shlex

# Good: Use subprocess with list arguments
def safe_execute(cmd: List[str]) -> str:
    """Safely execute command."""
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True,
        timeout=30
    )
    return result.stdout

# Bad: Shell injection vulnerable
def unsafe_execute(cmd: str) -> str:
    # NEVER do this with user input!
    return subprocess.run(cmd, shell=True, capture_output=True).stdout
```

## Common Anti-Patterns to Avoid

### ❌ DON'T Do This
```python
# Mutable default arguments
def bad_function(items=[]):  # BUG!
    items.append(1)
    return items

# Global state
global_cache = {}  # Avoid global mutable state

# Circular imports
from .module_a import func_a  # If module_a imports this module

# Using assert for validation
assert user_input, "Input required"  # Assertions can be disabled

# Hardcoded paths
config_file = "/home/user/config.json"  # Use Path and env vars
```

### ✅ DO This Instead
```python
# Immutable defaults
def good_function(items=None):
    if items is None:
        items = []
    items.append(1)
    return items

# Dependency injection
class Service:
    def __init__(self, cache):
        self.cache = cache

# Proper validation
if not user_input:
    raise ValueError("Input required")

# Configurable paths
config_file = Path(os.environ.get('CONFIG_PATH', './config.json'))
```

## Testing Your Code

### Testability Patterns
```python
# Dependency injection for testability
class Service:
    def __init__(self, executor=None):
        self.executor = executor or DefaultExecutor()
    
    def process(self, query: str) -> str:
        # Now executor can be mocked in tests
        return self.executor.execute(query)
```

### Type Checking
```bash
# Run mypy for type checking
mypy src/

# Strict mode
mypy --strict src/
```

### Linting
```bash
# Flake8 for style
flake8 src/

# Black for formatting
black src/

# isort for imports
isort src/
```