# 📚 Documentation Standards for Nix for Humanity

> Comprehensive guide for documenting code, APIs, and functionality

## 🎯 Overview

This document establishes documentation standards to ensure:
- **Consistency** across all code and documentation
- **Clarity** for users and developers
- **Completeness** of API documentation
- **Maintainability** through clear examples
- **Accessibility** for all skill levels

## 📝 Documentation Levels

### 1. Code-Level Documentation (Docstrings)

Every public function, class, and module MUST have comprehensive docstrings.

#### Module Docstrings

```python
"""
Module Name - Brief one-line description.

Detailed description of what this module does, its purpose,
and how it fits into the larger system.

Key Features:
    - Feature 1: Description
    - Feature 2: Description
    - Feature 3: Description

Usage Example:
    >>> from nix_for_humanity import ModuleName
    >>> result = ModuleName.do_something()
    >>> print(result)

Dependencies:
    - Required: package1, package2
    - Optional: package3 (for feature X)

Note:
    Any important notes, warnings, or considerations.

Since: v1.0.0
"""
```

#### Class Docstrings

```python
class ExampleClass:
    """
    Brief one-line description of the class.

    Detailed description of the class purpose, responsibilities,
    and usage patterns. Explain the problem it solves.

    Attributes:
        attribute1 (Type): Description of attribute1
        attribute2 (Type): Description of attribute2
        _private_attr (Type): Description (if relevant)

    Class Variables:
        CLASS_CONSTANT (Type): Description of constant

    Example:
        >>> obj = ExampleClass(param1="value")
        >>> result = obj.method()
        >>> print(result)
        "expected output"

    Note:
        Important considerations or warnings.

    Since: v1.0.0
    See Also:
        RelatedClass: For similar functionality
        other_module: For integration details
    """
```

#### Function/Method Docstrings

```python
def example_function(param1: str, param2: int = 10, **kwargs) -> Dict[str, Any]:
    """
    Brief one-line description of what the function does.

    Detailed explanation of the function's behavior, algorithm,
    or approach. Include any important implementation details.

    Args:
        param1: Description of param1. Include constraints,
            valid values, or examples if helpful.
        param2: Description of param2. Mention default value
            and when you might want to change it.
        **kwargs: Additional keyword arguments:
            - option1 (bool): Description (default: False)
            - option2 (str): Description (default: "value")

    Returns:
        Description of the return value. Include structure
        for complex types:
        {
            "success": bool,
            "data": Any,
            "error": Optional[str]
        }

    Raises:
        ValueError: When param1 is empty or invalid
        TypeError: When param2 is not an integer
        NetworkError: When external service is unavailable

    Example:
        >>> result = example_function("test", param2=20)
        >>> print(result["success"])
        True

        >>> # Using with kwargs
        >>> result = example_function(
        ...     "test",
        ...     option1=True,
        ...     option2="custom"
        ... )

    Performance:
        Time Complexity: O(n) where n is length of param1
        Space Complexity: O(1)
        Typical execution: <1ms for standard inputs

    Note:
        This function is thread-safe and can be called
        concurrently. Caches results for 5 minutes.

    Since: v1.0.0
    Deprecated: Use new_function() for better performance (v1.2.0)
    See Also:
        related_function: For similar operations
        helper_function: Used internally
    """
```

#### Async Function Docstrings

```python
async def async_operation(data: List[str]) -> AsyncIterator[str]:
    """
    Asynchronously process data and yield results.

    Processes items in parallel with backpressure handling.
    Automatically retries failed items up to 3 times.

    Args:
        data: List of items to process. Maximum 1000 items.

    Yields:
        Processed items as they complete. Order not guaranteed.

    Raises:
        asyncio.TimeoutError: If processing exceeds 30 seconds
        ProcessingError: If all retries fail for an item

    Example:
        >>> async for result in async_operation(["a", "b"]):
        ...     print(result)
        "processed: a"
        "processed: b"

    Concurrency:
        Maximum 10 concurrent operations.
        Uses connection pooling for efficiency.

    Since: v1.1.0
    """
```

## 🏷️ Type Hints Documentation

### Complex Type Definitions

```python
from typing import TypedDict, Literal, Union, Optional

class QueryResult(TypedDict):
    """
    Result of a natural language query.

    Attributes:
        intent: The parsed intent type
        confidence: Confidence score (0.0-1.0)
        entities: Extracted entities from the query
        suggestions: Alternative interpretations
    """
    intent: Literal["install", "search", "remove", "update"]
    confidence: float
    entities: Dict[str, str]
    suggestions: Optional[List[str]]

# Document type aliases
PackageName = str
"""A valid Nix package name (e.g., 'firefox', 'python311')."""

Version = Union[str, Literal["latest"]]
"""Package version string or 'latest' for newest."""
```

## 📖 API Documentation

### API Module Documentation

```python
# src/nix_for_humanity/api/__init__.py
"""
Nix for Humanity Public API.

This module provides the stable, public API for interacting with
Nix for Humanity. All public functions are available at the module level.

Quick Start:
    >>> from nix_for_humanity import ask_nix
    >>> result = ask_nix("install firefox")
    >>> print(result.success)
    True

Main Functions:
    - ask_nix(): Natural language interface
    - search_packages(): Find packages
    - install_package(): Install software
    - get_config(): Configuration access

Configuration:
    Set environment variables:
    - NIX_HUMANITY_BACKEND: Backend type ("python" or "subprocess")
    - NIX_HUMANITY_CACHE_DIR: Cache directory path
    - NIX_HUMANITY_LOG_LEVEL: Logging level

Stability:
    This API follows semantic versioning. Functions marked as
    stable will not change signatures in minor releases.

Since: v1.0.0
"""
```

### API Function Documentation

```python
def ask_nix(
    query: str,
    *,
    execute: bool = False,
    context: Optional[Context] = None,
    timeout: float = 30.0
) -> QueryResult:
    """
    Natural language interface to NixOS.

    Main entry point for natural language queries. Understands
    commands like "install firefox", "find text editor", etc.

    Args:
        query: Natural language command or question.
            Examples:
            - "install firefox"
            - "find markdown editor"
            - "update system"
            - "remove package vim"

        execute: If True, execute the command. If False,
            only show what would be done (dry run).
            Default: False for safety.

        context: Optional context for stateful operations.
            Pass the same context for related commands.

        timeout: Maximum time in seconds to wait for response.
            Default: 30.0 seconds.

    Returns:
        QueryResult with:
        - success (bool): Whether operation succeeded
        - action (str): What action was taken/would be taken
        - data (Any): Result data (packages, info, etc.)
        - message (str): Human-readable message
        - suggestions (List[str]): Alternative queries if unclear

    Raises:
        QueryError: If query cannot be parsed
        TimeoutError: If operation exceeds timeout
        PermissionError: If operation requires sudo

    Examples:
        >>> # Dry run (safe)
        >>> result = ask_nix("install firefox")
        >>> print(result.message)
        "Would install: firefox-120.0"

        >>> # Actually execute
        >>> result = ask_nix("install firefox", execute=True)
        >>> print(result.message)
        "Successfully installed: firefox-120.0"

        >>> # With context for follow-up
        >>> ctx = Context()
        >>> ask_nix("find editor", context=ctx)
        >>> ask_nix("install the first one", context=ctx)

    Performance:
        - Typical response: <100ms for queries
        - Package search: 1-3 seconds
        - Installation: Depends on package size

    Thread Safety:
        This function is thread-safe. Multiple threads can
        call it concurrently with different contexts.

    Since: v1.0.0
    Stability: Stable
    See Also:
        - search_packages(): For specific package searches
        - install_package(): For direct installation
        - NixForHumanityBackend: For lower-level access
    """
```

## 🎨 Documentation Style Guide

### Language and Tone

1. **Be Clear and Concise**
   - Use simple, direct language
   - Avoid jargon unless necessary
   - Define technical terms on first use

2. **Be Complete**
   - Document all parameters
   - Include all possible exceptions
   - Provide real examples

3. **Be Helpful**
   - Explain "why" not just "what"
   - Include common use cases
   - Provide troubleshooting hints

### Formatting Standards

1. **Docstring Format**: Use Google-style with enhancements
2. **Line Length**: Maximum 72 characters for docstrings
3. **Indentation**: 4 spaces for docstring content
4. **Blank Lines**: One between sections

### Required Sections by Type

#### For Classes
- Description (required)
- Attributes (required if any)
- Example (required)
- Note (if applicable)
- Since (required)

#### For Functions
- Description (required)
- Args (required if any)
- Returns (required if not None)
- Raises (required if any)
- Example (required)
- Since (required)

#### For Modules
- Description (required)
- Key Features (recommended)
- Usage Example (required)
- Since (required)

## 📐 Documentation Templates

### Template: Data Processing Function

```python
def process_data(input_data: List[Dict], options: ProcessOptions) -> ProcessResult:
    """
    Process input data according to specified options.

    Applies transformations, validations, and enrichments
    to the input data based on the provided options.

    Args:
        input_data: List of dictionaries containing:
            - "id" (str): Unique identifier
            - "value" (Any): Data to process
            - "metadata" (dict): Optional metadata

        options: Processing options:
            - validate (bool): Enable validation
            - transform (bool): Apply transformations
            - enrich (bool): Add enrichments

    Returns:
        ProcessResult containing:
            - processed_items (List[Dict]): Processed data
            - errors (List[Error]): Any errors encountered
            - statistics (Stats): Processing statistics

    Example:
        >>> data = [{"id": "1", "value": "test"}]
        >>> options = ProcessOptions(validate=True)
        >>> result = process_data(data, options)
        >>> print(len(result.processed_items))
        1

    Since: v1.0.0
    """
```

### Template: Configuration Class

```python
class Configuration:
    """
    Application configuration management.

    Handles loading, validation, and access to configuration
    values from multiple sources (files, env vars, defaults).

    Attributes:
        backend (str): Backend type ("python" or "subprocess")
        cache_dir (Path): Cache directory location
        log_level (str): Logging level
        timeout (float): Default timeout in seconds

    Example:
        >>> config = Configuration()
        >>> config.backend
        "python"
        >>> config.update(backend="subprocess")
        >>> config.save()

    Since: v1.0.0
    """
```

### Template: Error Classes

```python
class QueryError(Exception):
    """
    Raised when a natural language query cannot be parsed.

    Attributes:
        query (str): The original query
        reason (str): Why parsing failed
        suggestions (List[str]): Alternative queries

    Example:
        >>> raise QueryError(
        ...     "instal firefox",
        ...     "Unknown command 'instal'",
        ...     ["install firefox", "install Firefox"]
        ... )

    Since: v1.0.0
    """
```

## 🔍 Documentation Validation

### Automated Checks

```python
# tools/check_docstrings.py
"""
Validate docstring completeness and format.

Checks:
- All public functions have docstrings
- Required sections are present
- Examples are executable
- Types match signatures
"""

def validate_docstrings(module_path: str) -> List[Issue]:
    """Validate all docstrings in a module."""
    # Implementation
```

### Documentation Coverage Metrics

```python
# Minimum required coverage
DOC_COVERAGE_THRESHOLD = 90  # 90% of public APIs documented

# Check with:
# python tools/check_docstrings.py --coverage
```

## 📋 Documentation Checklist

### For New Functions

- [ ] Has one-line summary
- [ ] Has detailed description
- [ ] All parameters documented
- [ ] Return value documented
- [ ] Exceptions documented
- [ ] Has usage example
- [ ] Has "Since" version
- [ ] Type hints complete

### For New Classes

- [ ] Has class-level docstring
- [ ] Attributes documented
- [ ] Constructor documented
- [ ] All public methods documented
- [ ] Has usage example
- [ ] Inheritance documented

### For New Modules

- [ ] Has module-level docstring
- [ ] Lists main functionality
- [ ] Has quick start example
- [ ] Dependencies noted
- [ ] Exports documented

## 🚀 Best Practices

### 1. Document As You Code
- Write docstrings immediately after function signature
- Update docs when changing functionality
- Review docs in PR alongside code

### 2. Focus on User Needs
- What problem does this solve?
- When would I use this?
- What are common pitfalls?

### 3. Provide Real Examples
- Use realistic data
- Show expected output
- Include error cases

### 4. Keep Updated
- Mark deprecated features
- Note version changes
- Update examples for new APIs

### 5. Cross-Reference
- Link related functions
- Reference documentation
- Point to examples

## 📊 Documentation Metrics

Track documentation quality:

```python
# Metrics to monitor
metrics = {
    "coverage": "% of public APIs with docstrings",
    "completeness": "% with all required sections",
    "examples": "% with executable examples",
    "currency": "% updated in last release",
    "clarity": "Readability score (Flesch)",
}
```

## 🔄 Maintenance

### Regular Reviews

1. **Weekly**: Check new code for docs
2. **Monthly**: Update examples
3. **Release**: Verify all public APIs documented
4. **Quarterly**: Review and improve clarity

### Documentation Debt

Track and prioritize:
- Missing docstrings
- Incomplete documentation
- Outdated examples
- Unclear descriptions

## 🎯 Summary

Good documentation:
1. **Explains** what and why
2. **Shows** how with examples
3. **Warns** about pitfalls
4. **Guides** to related resources
5. **Evolves** with the code

Remember: Documentation is not an afterthought—it's an integral part of quality code that respects both current and future developers.

---

*"Code tells you how; comments tell you why; documentation tells you what, why, how, and when."*
