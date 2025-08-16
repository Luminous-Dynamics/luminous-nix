# 📖 API Reference - Luminous Nix

> Complete API documentation for developers and integrators

## 🎯 Core API

### Main Entry Points

#### `ask_nix(query: str, *, execute: bool = False, context: Optional[Context] = None) -> QueryResult`

**Purpose:** Natural language interface to NixOS - the primary way to interact with the system.

**Parameters:**
- `query` (str): Natural language command or question
  - Examples: "install firefox", "find text editor", "update system"
- `execute` (bool, optional): Whether to execute the command or just preview
  - Default: `False` (safe mode - preview only)
- `context` (Optional[Context]): Stateful context for related commands
  - Allows follow-up commands like "install the first one"

**Returns:**
- `QueryResult`: Dictionary containing:
  - `success` (bool): Whether operation succeeded
  - `message` (str): Human-readable message
  - `data` (Any): Result data (packages, info, etc.)
  - `action` (str): What action was taken/would be taken
  - `suggestions` (List[str]): Alternative queries if unclear

**Examples:**
```python
# Safe preview mode
result = ask_nix("install firefox")
print(result["message"])  # "Would install: firefox-120.0"

# Actually execute
result = ask_nix("install firefox", execute=True)
print(result["message"])  # "Successfully installed: firefox-120.0"

# With context for follow-ups
ctx = Context()
ask_nix("search editor", context=ctx)
ask_nix("install the second one", context=ctx)  # Refers to search results
```

**Performance:** <100ms for queries, 1-3s for searches

**Thread Safety:** Fully thread-safe, supports concurrent calls

**Since:** v1.0.0

---

#### `search_packages(query: str, limit: int = 20) -> List[PackageInfo]`

**Purpose:** Search for packages by name or description.

**Parameters:**
- `query` (str): Search term (supports partial matches)
- `limit` (int): Maximum results to return (default: 20)

**Returns:**
- List of `PackageInfo` dictionaries with:
  - `name`: Package name
  - `version`: Version string
  - `description`: Package description

**Example:**
```python
packages = search_packages("editor")
for pkg in packages:
    print(f"{pkg['name']}: {pkg['description']}")
```

---

#### `install_package(name: str, *, version: Optional[str] = None) -> ExecutionResult`

**Purpose:** Install a specific package.

**Parameters:**
- `name` (str): Exact package name
- `version` (Optional[str]): Specific version (default: latest)

**Returns:**
- `ExecutionResult` with installation status

---

## 🎨 Backend API

### NixForHumanityBackend

```python
class NixForHumanityBackend:
    """
    Core backend for processing natural language queries.

    Handles intent parsing, command execution, and learning.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize with optional configuration."""

    async def execute(self, query: str, context: Context) -> ExecutionResult:
        """Execute a natural language query."""

    async def understand(self, query: str, context: Context) -> Intent:
        """Parse query into structured intent."""
```

**Key Methods:**

#### `execute(query: str, context: Context) -> ExecutionResult`

**Purpose:** Process and execute a natural language query.

**Parameters:**
- `query`: Natural language input
- `context`: Execution context with history and state

**Returns:** `ExecutionResult` with success status and output

#### `understand(query: str, context: Context) -> Intent`

**Purpose:** Parse natural language into structured intent.

**Returns:** `Intent` with:
- `action`: Identified action type
- `entities`: Extracted entities
- `confidence`: Confidence score (0-1)

---

## ⚙️ Configuration API

### ConfigManager

```python
class ConfigManager:
    """
    Manages user configuration and preferences.

    Handles aliases, preferences, history, and patterns.
    """

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""

    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""

    def add_alias(self, name: str, expansion: str) -> None:
        """Add command alias."""

    def expand_aliases(self, query: str) -> str:
        """Expand aliases in query."""
```

**Key Methods:**

#### `add_alias(name: str, expansion: str) -> None`

**Purpose:** Create a command shortcut.

**Example:**
```python
config.add_alias("i", "install")
config.add_alias("s", "search")
# Now "i firefox" expands to "install firefox"
```

#### `get_statistics() -> Dict[str, Any]`

**Purpose:** Get usage statistics.

**Returns:** Dictionary with:
- `total_commands`: Total commands executed
- `common_actions`: Most used actions
- `time_saved`: Estimated time saved

---

## 🚀 Async API

### AsyncCommandExecutor

```python
class AsyncCommandExecutor:
    """
    Async executor for concurrent operations.

    Provides parallel execution and streaming.
    """

    async def execute_parallel(
        self, commands: List[str]
    ) -> List[AsyncExecutionResult]:
        """Execute multiple commands in parallel."""

    async def stream_execution(
        self, commands: List[str]
    ) -> AsyncIterator[AsyncExecutionResult]:
        """Stream results as they complete."""
```

**Key Features:**
- 10x faster parallel execution
- Real-time progress streaming
- Automatic retry logic
- Resource pooling

**Example:**
```python
executor = AsyncCommandExecutor(max_workers=4)

# Parallel execution
results = await executor.execute_parallel([
    "install firefox",
    "install vim",
    "install git"
])

# Streaming results
async for result in executor.stream_execution(commands):
    print(f"Completed: {result.output}")
```

---

## 📝 Type Definitions

### Core Types

```python
class QueryResult(TypedDict):
    success: bool
    message: str
    data: Any
    action: str
    suggestions: List[str]

class ExecutionResult(TypedDict):
    success: bool
    output: str
    error: Optional[str]
    data: Optional[Any]

class Intent(TypedDict):
    action: str
    entities: Dict[str, Any]
    confidence: float

class PackageInfo(TypedDict):
    name: str
    version: Optional[str]
    description: Optional[str]
    homepage: Optional[str]
```

### Context Types

```python
class Context:
    """Execution context for stateful operations."""
    history: List[str]
    results: List[Any]
    state: Dict[str, Any]
```

---

## 🔌 Plugin API

### Creating Plugins

```python
from nix_for_humanity.plugins import Plugin, hook

class MyPlugin(Plugin):
    """Custom plugin example."""

    @hook("pre_execute")
    async def before_execute(self, query: str) -> str:
        """Modify query before execution."""
        return query.replace("please", "")

    @hook("post_execute")
    async def after_execute(self, result: ExecutionResult) -> None:
        """Process results after execution."""
        logger.info(f"Executed: {result}")
```

**Available Hooks:**
- `pre_execute`: Before query execution
- `post_execute`: After execution
- `on_error`: When errors occur
- `on_learn`: When patterns detected

---

## 🏷️ Environment Variables

### Configuration

- `LUMINOUS_NIX_BACKEND`: Backend type (`"python"` or `"subprocess"`)
- `LUMINOUS_NIX_CACHE_DIR`: Cache directory path
- `LUMINOUS_NIX_CONFIG_DIR`: Configuration directory
- `LUMINOUS_NIX_LOG_LEVEL`: Logging level (`DEBUG`, `INFO`, `WARNING`)
- `LUMINOUS_NIX_DRY_RUN`: Default dry-run mode (`true`/`false`)
- `LUMINOUS_NIX_PYTHON_BACKEND`: Enable native Python API (`true`/`false`)

### Example:
```bash
export LUMINOUS_NIX_PYTHON_BACKEND=true
export LUMINOUS_NIX_LOG_LEVEL=DEBUG
ask-nix "install firefox"
```

---

## 🔧 Utility Functions

### Cache Management

```python
from nix_for_humanity.core.cache import clear_cache, get_cache_size

# Clear all caches
clear_cache()

# Get cache size in bytes
size = get_cache_size()
print(f"Cache size: {size / 1024 / 1024:.2f} MB")
```

### Logging

```python
from nix_for_humanity.core.logging_config import get_logger, configure_logging

# Get module logger
logger = get_logger(__name__)

# Configure logging
configure_logging(
    level="DEBUG",
    format="detailed",
    color=True
)
```

---

## 📊 Error Handling

### Exception Types

```python
class QueryError(Exception):
    """Query parsing failed."""
    query: str
    reason: str
    suggestions: List[str]

class ExecutionError(Exception):
    """Command execution failed."""
    command: str
    exit_code: int
    stderr: str

class ConfigError(Exception):
    """Configuration error."""
    key: str
    issue: str
```

### Error Handling Example

```python
from nix_for_humanity import ask_nix, QueryError

try:
    result = ask_nix("invalid query xyz")
except QueryError as e:
    print(f"Could not understand: {e.reason}")
    print(f"Did you mean: {', '.join(e.suggestions)}?")
```

---

## 🎯 Performance Guarantees

### Response Times

| Operation | Guarantee | Typical |
|-----------|-----------|----------|
| Query parsing | <10ms | 2ms |
| Package search | <3s | 1s |
| Cache lookup | <1ms | 0.1ms |
| Parallel ops | Linear scaling | 10x speedup |

### Resource Usage

- Memory: <100MB baseline
- CPU: <5% idle, scales with operations
- Disk: <50MB cache (configurable)

---

## 🔄 Migration from Traditional NixOS

### Command Mapping

| Traditional | Luminous Nix |
|-------------|------------------|
| `nix-env -iA nixos.firefox` | `ask_nix("install firefox")` |
| `nix-env -qaP \| grep editor` | `search_packages("editor")` |
| `nix-env -e firefox` | `ask_nix("remove firefox")` |
| `nixos-rebuild switch` | `ask_nix("update system")` |

---

## 📚 Further Reading

- [Quick Start Guide](../03-DEVELOPMENT/03-QUICK-START.md)
- [Documentation Standards](../03-DEVELOPMENT/06-DOCUMENTATION-STANDARDS.md)
- [Backend Architecture](../02-ARCHITECTURE/02-BACKEND-ARCHITECTURE.md)
- [Type Definitions](../../src/nix_for_humanity/types.py)

---

*This API is stable and follows semantic versioning. Breaking changes will only occur in major version updates.*

**Version:** v1.0.0 | **Last Updated:** 2024
