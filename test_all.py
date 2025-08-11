#!/usr/bin/env python3
"""
Simple test suite for Nix for Humanity

Runs tests without requiring pytest.
"""

import asyncio
import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Track test results
tests_passed = 0
tests_failed = 0
failures = []


def test(name):
    """Decorator for test functions"""

    def decorator(func):
        def wrapper():
            global tests_passed, tests_failed
            try:
                print(f"  Testing {name}...", end=" ")
                if asyncio.iscoroutinefunction(func):
                    asyncio.run(func())
                else:
                    func()
                print("✅")
                tests_passed += 1
            except Exception as e:
                print("❌")
                print(f"    Error: {e}")
                tests_failed += 1
                failures.append((name, str(e)))

        return wrapper

    return decorator


print("🧪 Running Nix for Humanity Test Suite")
print("=" * 60)

# Test 1: Backend initialization
print("\n1. Testing Unified Backend")
print("-" * 40)


@test("Backend initialization")
def test_backend_init():
    from nix_for_humanity.core.unified_backend import NixForHumanityBackend

    backend = NixForHumanityBackend({"dry_run": True})
    assert backend is not None
    assert backend.config["dry_run"] == True


@test("Intent parsing")
async def test_intent_parsing():
    from nix_for_humanity.core.unified_backend import Context, NixForHumanityBackend

    backend = NixForHumanityBackend()
    intent = await backend.understand("install firefox", Context())
    assert intent.type.value == "install"
    assert intent.parameters.get("package") == "firefox"


@test("Query execution")
async def test_query_execution():
    from nix_for_humanity.core.unified_backend import NixForHumanityBackend

    backend = NixForHumanityBackend({"dry_run": True})
    result = await backend.execute("search firefox")  # Use a recognized intent
    assert result.execution_time is not None
    assert result.execution_time < 1.0
    # Note: success depends on implementation, just check it runs


test_backend_init()
test_intent_parsing()
test_query_execution()

# Test 2: Caching
print("\n2. Testing Cache System")
print("-" * 40)


@test("Cache get/set")
def test_cache_operations():
    from nix_for_humanity.core.cache import SimpleCache

    with tempfile.TemporaryDirectory() as tmpdir:
        cache = SimpleCache(cache_dir=Path(tmpdir))

        # Test miss
        assert cache.get("test_key") is None

        # Test set and hit
        cache.set("test_key", {"data": "value"})
        assert cache.get("test_key")["data"] == "value"


@test("Smart cache decisions")
def test_smart_cache():
    from nix_for_humanity.core.cache import SmartCache

    cache = SmartCache()

    assert cache.should_cache("search") == True
    assert cache.should_cache("install") == False
    assert cache.should_cache("generate_config") == True


test_cache_operations()
test_smart_cache()

# Test 3: Async patterns
print("\n3. Testing Async Executor")
print("-" * 40)


@test("Async execution")
async def test_async_execution():
    from nix_for_humanity.core.async_executor import AsyncCommandExecutor

    executor = AsyncCommandExecutor()
    result = await executor.execute("test command")
    assert result.success == True
    assert result.duration is not None


@test("Parallel execution")
async def test_parallel():
    from nix_for_humanity.core.async_executor import AsyncCommandExecutor

    executor = AsyncCommandExecutor()
    results = await executor.execute_parallel(["cmd1", "cmd2", "cmd3"])
    assert len(results) == 3
    assert all(r.success for r in results)


test_async_execution()
test_parallel()

# Test 4: Error handling
print("\n4. Testing Intelligent Errors")
print("-" * 40)


@test("Error pattern matching")
def test_error_patterns():
    from nix_for_humanity.errors import ErrorContext, IntelligentErrorHandler

    handler = IntelligentErrorHandler()

    error = "attribute 'firofox' not found"
    context = ErrorContext("package_error", error, package="firofox")
    result = handler.explain_error(error, context)

    assert "not found" in result["explanation"]
    assert len(result["suggestions"]) > 0


@test("Error education")
def test_error_education():
    from nix_for_humanity.errors import ErrorContext, ErrorEducator

    educator = ErrorEducator()

    error = "permission denied"
    context = ErrorContext("permission_error", error)
    educated = educator.educate(error, context)

    assert "❌" in educated
    assert "💡" in educated
    assert len(educated) > 100  # Should be detailed


test_error_patterns()
test_error_education()

# Test 5: Security
print("\n5. Testing Security")
print("-" * 40)


@test("Input validation")
def test_input_validation():
    from nix_for_humanity.security.validator import InputValidator

    validator = InputValidator()

    # Valid input
    result = validator.validate_input("firefox", "package")
    assert result["valid"] == True

    # Dangerous input
    result = validator.validate_input("firefox; rm -rf /", "package")
    assert result["valid"] == False


@test("Command validation")
def test_command_validation():
    from nix_for_humanity.security.validator import InputValidator

    validator = InputValidator()

    # Safe command
    valid, _ = validator.validate_command(["nix", "search", "firefox"])
    assert valid == True

    # Dangerous command
    valid, reason = validator.validate_command(["rm", "-rf", "/"])
    assert valid == False


test_input_validation()
test_command_validation()

# Test 6: Progress indicators
print("\n6. Testing Progress Indicators")
print("-" * 40)


@test("Spinner lifecycle")
def test_spinner():
    from nix_for_humanity.ui.progress import Spinner

    spinner = Spinner("Test")

    spinner.start()
    assert spinner.running == True

    spinner.stop()
    assert spinner.running == False


@test("Progress bar")
def test_progress_bar():
    from nix_for_humanity.ui.progress import ProgressBar

    bar = ProgressBar(10, "Test")

    for _ in range(10):
        bar.update()

    assert bar.current == 10


test_spinner()
test_progress_bar()

# Test 7: Type hints
print("\n7. Testing Type System")
print("-" * 40)


@test("Type definitions")
def test_types():
    from nix_for_humanity.types import ExecutionContext, PackageInfo

    # Test TypedDict
    pkg: PackageInfo = {"name": "firefox"}
    assert pkg["name"] == "firefox"

    # Test dataclass
    ctx = ExecutionContext(user_id="test")
    assert ctx.user_id == "test"
    assert ctx.timeout == 30


test_types()

# Test 8: Performance
print("\n8. Testing Performance")
print("-" * 40)


@test("Startup performance")
def test_startup_performance():
    import time

    start = time.perf_counter()

    from nix_for_humanity.core.unified_backend import NixForHumanityBackend

    backend = NixForHumanityBackend()

    elapsed = time.perf_counter() - start
    assert elapsed < 0.5  # Should be fast with lazy loading


@test("Cache performance")
def test_cache_performance():
    import time

    from nix_for_humanity.core.cache import SimpleCache

    with tempfile.TemporaryDirectory() as tmpdir:
        cache = SimpleCache(cache_dir=Path(tmpdir))

        # Write
        start = time.perf_counter()
        cache.set("key", {"data": "value"})
        write_time = time.perf_counter() - start

        # Read
        start = time.perf_counter()
        cache.get("key")
        read_time = time.perf_counter() - start

        assert write_time < 0.01
        assert read_time < 0.001  # Memory cache is instant


test_startup_performance()
test_cache_performance()

# Summary
print("\n" + "=" * 60)
print("Test Summary")
print("-" * 40)
print(f"✅ Passed: {tests_passed}")
print(f"❌ Failed: {tests_failed}")

if failures:
    print("\nFailed tests:")
    for name, error in failures:
        print(f"  • {name}: {error}")

print("\n" + "=" * 60)

if tests_failed == 0:
    print("🎉 All tests passed!")
    sys.exit(0)
else:
    print(f"😞 {tests_failed} test(s) failed")
    sys.exit(1)
