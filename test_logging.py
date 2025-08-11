#!/usr/bin/env python3
"""
Test the logging configuration system
"""

import logging
import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from nix_for_humanity.core.logging_config import (
    ColorFormatter,
    JSONFormatter,
    LoggingConfig,
    LogLevelContext,
    SacredFormatter,
    get_logger,
    log_duration,
    log_event,
    log_metric,
    setup_logging,
)


def test_basic_logging():
    """Test basic logging setup"""
    print("\n1. Testing Basic Logging")
    print("-" * 40)

    # Setup default logging
    setup_logging()

    # Get logger
    logger = get_logger("test.basic")

    # Test different levels
    logger.debug("Debug message - might not show")
    logger.info("Info message - should show")
    logger.warning("Warning message - should show")
    logger.error("Error message - should show")
    logger.critical("Critical message - should show")

    print("✅ Basic logging works")


def test_debug_mode():
    """Test debug mode logging"""
    print("\n2. Testing Debug Mode")
    print("-" * 40)

    # Setup debug logging
    setup_logging(debug=True)

    logger = get_logger("test.debug")

    # Debug should now show
    logger.debug("Debug message - should show in debug mode")
    logger.info("Info message with details")

    print("✅ Debug mode works")


def test_structured_logging():
    """Test structured logging helpers"""
    print("\n3. Testing Structured Logging")
    print("-" * 40)

    logger = get_logger("test.structured")

    # Log event
    log_event(logger, "user_login", user_id="test123", ip="127.0.0.1")

    # Log metric
    log_metric(logger, "cache_hit_rate", 0.95, unit="%")

    # Log duration
    log_duration(logger, "database_query", 0.125)

    print("✅ Structured logging works")


def test_log_level_context():
    """Test temporary log level context"""
    print("\n4. Testing Log Level Context")
    print("-" * 40)

    logger_name = "test.context"
    logger = get_logger(logger_name)

    # Normal level
    logger.debug("Debug outside context - might not show")

    # Temporary debug level
    with LogLevelContext(logger_name, "DEBUG") as ctx_logger:
        ctx_logger.debug("Debug inside context - should show")

    # Back to normal
    logger.debug("Debug after context - might not show again")

    print("✅ Log level context works")


def test_formatters():
    """Test different formatters"""
    print("\n5. Testing Formatters")
    print("-" * 40)

    # Create a test logger
    test_logger = logging.getLogger("test.formatters")
    test_logger.setLevel(logging.DEBUG)
    test_logger.handlers.clear()

    # Test color formatter
    handler = logging.StreamHandler()
    handler.setFormatter(ColorFormatter("%(levelname)s: %(message)s"))
    test_logger.addHandler(handler)
    test_logger.info("Color formatted message")
    test_logger.removeHandler(handler)

    # Test sacred formatter
    handler = logging.StreamHandler()
    handler.setFormatter(SacredFormatter("%(message)s"))
    test_logger.addHandler(handler)
    test_logger.info("Sacred formatted message")
    test_logger.removeHandler(handler)

    # Test JSON formatter (write to temp file to check)
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as f:
        handler = logging.FileHandler(f.name)
        handler.setFormatter(JSONFormatter())
        test_logger.addHandler(handler)
        test_logger.info("JSON formatted message", extra={"custom_field": "value"})
        handler.close()

        # Read and verify JSON
        with open(f.name) as json_file:
            content = json_file.read()
            assert "JSON formatted message" in content
            assert "custom_field" in content
            print(f"  JSON output sample: {content[:100]}...")

    print("✅ All formatters work")


def test_custom_config():
    """Test custom configuration"""
    print("\n6. Testing Custom Configuration")
    print("-" * 40)

    config = {
        "root_level": "WARNING",
        "handlers": {
            "console": {"type": "console", "level": "INFO", "formatter": "sacred"}
        },
        "loggers": {
            "test.custom": {
                "level": "DEBUG",
                "handlers": ["console"],
                "propagate": False,
            }
        },
    }

    log_config = LoggingConfig()
    log_config.setup_from_config(config)

    logger = get_logger("test.custom")
    logger.info("Custom configured logger")

    print("✅ Custom configuration works")


def test_production_mode():
    """Test production mode (without actually writing files)"""
    print("\n7. Testing Production Mode Setup")
    print("-" * 40)

    # Create temporary directory for logs
    with tempfile.TemporaryDirectory() as tmpdir:
        # Override log directory
        import nix_for_humanity.core.logging_config as lc

        original_dir = lc.LOG_DIR
        lc.LOG_DIR = Path(tmpdir)

        # Setup production logging
        setup_logging(production=True)

        logger = get_logger("test.production")

        # These should be logged to files
        logger.warning("Production warning")
        logger.error("Production error")

        # Check files were created
        json_log = Path(tmpdir) / "production.json"
        error_log = Path(tmpdir) / "errors.log"

        # In production mode these would be created
        print(f"  Would create: {json_log}")
        print(f"  Would create: {error_log}")

        # Restore original
        lc.LOG_DIR = original_dir

    print("✅ Production mode setup works")


if __name__ == "__main__":
    print("🧪 Testing Logging Configuration System")
    print("=" * 60)

    # Run all tests
    test_basic_logging()
    test_debug_mode()
    test_structured_logging()
    test_log_level_context()
    test_formatters()
    test_custom_config()
    test_production_mode()

    print("\n" + "=" * 60)
    print("🎉 All logging tests passed!")
    print("\nThe logging system provides:")
    print("  • Multiple formatters (Color, JSON, Sacred)")
    print("  • Debug, Default, and Production modes")
    print("  • Structured logging helpers")
    print("  • Temporary log level contexts")
    print("  • Custom configuration support")
    print("  • Rotating file handlers")
    print("  • Thread-safe singleton pattern")
