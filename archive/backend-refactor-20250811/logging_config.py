"""
Logging Configuration System for Nix for Humanity

Provides flexible, structured logging with consciousness-first principles.
"""

import json
import logging
import logging.handlers
import sys
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

# Default directories
LOG_DIR = Path.home() / ".local" / "share" / "nix-humanity" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


class LogLevel(str, Enum):
    """Logging levels"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ColorFormatter(logging.Formatter):
    """
    Colored formatter for terminal output

    Uses ANSI color codes for different log levels.
    """

    # Color codes
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }

    RESET = "\033[0m"

    def __init__(self, fmt: str | None = None, use_colors: bool = True):
        """
        Initialize color formatter

        Args:
            fmt: Format string
            use_colors: Whether to use colors
        """
        super().__init__(fmt)
        self.use_colors = use_colors and sys.stderr.isatty()

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors"""
        if self.use_colors:
            levelname = record.levelname
            if levelname in self.COLORS:
                record.levelname = f"{self.COLORS[levelname]}{levelname}{self.RESET}"
                record.msg = f"{self.COLORS[levelname]}{record.msg}{self.RESET}"

        result = super().format(record)

        # Reset for next use
        record.levelname = (
            record.levelname.replace(self.RESET, "")
            .replace("\033[36m", "")
            .replace("\033[32m", "")
            .replace("\033[33m", "")
            .replace("\033[31m", "")
            .replace("\033[35m", "")
        )
        record.msg = (
            record.msg.replace(self.RESET, "")
            .replace("\033[36m", "")
            .replace("\033[32m", "")
            .replace("\033[33m", "")
            .replace("\033[31m", "")
            .replace("\033[35m", "")
        )

        return result


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging

    Outputs logs as JSON for easy parsing and analysis.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in [
                "name",
                "msg",
                "args",
                "created",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "thread",
                "threadName",
                "exc_info",
                "exc_text",
                "stack_info",
                "getMessage",
            ]:
                log_obj[key] = value

        return json.dumps(log_obj)


class SacredFormatter(logging.Formatter):
    """
    Sacred formatter with consciousness-first symbols

    Uses sacred symbols to indicate log levels.
    """

    SYMBOLS = {
        "DEBUG": "🔍",
        "INFO": "✨",
        "WARNING": "⚠️",
        "ERROR": "❌",
        "CRITICAL": "🔥",
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format with sacred symbols"""
        symbol = self.SYMBOLS.get(record.levelname, "📝")
        record.msg = f"{symbol} {record.msg}"
        return super().format(record)


class LoggingConfig:
    """
    Centralized logging configuration

    Provides flexible logging setup with multiple handlers and formatters.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """
        Initialize logging configuration

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.handlers: dict[str, logging.Handler] = {}
        self.loggers: dict[str, logging.Logger] = {}

    def setup_default(self) -> None:
        """Setup default logging configuration"""
        # Root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.WARNING)

        # Console handler with color
        console_handler = self._create_console_handler()
        root_logger.addHandler(console_handler)

        # File handler for errors
        error_handler = self._create_file_handler(
            LOG_DIR / "errors.log", level=logging.ERROR
        )
        root_logger.addHandler(error_handler)

        # Application logger
        app_logger = logging.getLogger("nix_for_humanity")
        app_logger.setLevel(logging.INFO)
        app_logger.propagate = False

        # Application handlers
        app_console = self._create_console_handler(sacred=True)
        app_logger.addHandler(app_console)

        app_file = self._create_file_handler(
            LOG_DIR / "nix-humanity.log", level=logging.DEBUG
        )
        app_logger.addHandler(app_file)

    def setup_from_config(self, config: dict[str, Any]) -> None:
        """
        Setup logging from configuration dictionary

        Args:
            config: Configuration dictionary
        """
        # Set root level
        root_level = config.get("root_level", "WARNING")
        logging.getLogger().setLevel(getattr(logging, root_level))

        # Setup handlers
        handlers_config = config.get("handlers", {})
        for name, handler_config in handlers_config.items():
            handler = self._create_handler_from_config(handler_config)
            self.handlers[name] = handler

        # Setup loggers
        loggers_config = config.get("loggers", {})
        for name, logger_config in loggers_config.items():
            logger = logging.getLogger(name)
            logger.setLevel(getattr(logging, logger_config.get("level", "INFO")))

            # Add handlers
            for handler_name in logger_config.get("handlers", []):
                if handler_name in self.handlers:
                    logger.addHandler(self.handlers[handler_name])

            # Set propagate
            logger.propagate = logger_config.get("propagate", True)

            self.loggers[name] = logger

    def setup_debug(self) -> None:
        """Setup debug logging configuration"""
        # Set all loggers to DEBUG
        logging.getLogger().setLevel(logging.DEBUG)

        # Verbose console output
        console = self._create_console_handler(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
        )
        logging.getLogger().addHandler(console)

        # Debug file
        debug_file = self._create_file_handler(
            LOG_DIR / f"debug-{datetime.now():%Y%m%d-%H%M%S}.log",
            level=logging.DEBUG,
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s",
        )
        logging.getLogger().addHandler(debug_file)

    def setup_production(self) -> None:
        """Setup production logging configuration"""
        # Root logger - only warnings and above
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.WARNING)

        # JSON file handler for structured logs
        json_handler = logging.handlers.RotatingFileHandler(
            LOG_DIR / "production.json",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
        )
        json_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(json_handler)

        # Error file handler
        error_handler = logging.handlers.RotatingFileHandler(
            LOG_DIR / "errors.log", maxBytes=5 * 1024 * 1024, backupCount=3  # 5MB
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        root_logger.addHandler(error_handler)

        # Syslog handler if available
        try:
            syslog = logging.handlers.SysLogHandler(address="/dev/log")
            syslog.setLevel(logging.WARNING)
            root_logger.addHandler(syslog)
        except Exception:
            pass  # Syslog not available

    def _create_console_handler(
        self, level: int = logging.INFO, fmt: str | None = None, sacred: bool = False
    ) -> logging.StreamHandler:
        """Create console handler"""
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(level)

        if fmt is None:
            fmt = "%(levelname)s: %(message)s"

        if sacred:
            handler.setFormatter(SacredFormatter(fmt))
        else:
            handler.setFormatter(ColorFormatter(fmt))

        return handler

    def _create_file_handler(
        self,
        filepath: Path,
        level: int = logging.DEBUG,
        fmt: str | None = None,
        max_bytes: int = 10 * 1024 * 1024,
        backup_count: int = 5,
    ) -> logging.handlers.RotatingFileHandler:
        """Create rotating file handler"""
        handler = logging.handlers.RotatingFileHandler(
            filepath, maxBytes=max_bytes, backupCount=backup_count
        )
        handler.setLevel(level)

        if fmt is None:
            fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

        handler.setFormatter(logging.Formatter(fmt))
        return handler

    def _create_handler_from_config(self, config: dict[str, Any]) -> logging.Handler:
        """Create handler from configuration"""
        handler_type = config.get("type", "console")

        if handler_type == "console":
            handler = logging.StreamHandler()
        elif handler_type == "file":
            handler = logging.FileHandler(config.get("filename", "app.log"))
        elif handler_type == "rotating_file":
            handler = logging.handlers.RotatingFileHandler(
                config.get("filename", "app.log"),
                maxBytes=config.get("max_bytes", 10 * 1024 * 1024),
                backupCount=config.get("backup_count", 5),
            )
        else:
            raise ValueError(f"Unknown handler type: {handler_type}")

        # Set level
        handler.setLevel(getattr(logging, config.get("level", "INFO")))

        # Set formatter
        formatter_type = config.get("formatter", "default")
        if formatter_type == "json":
            handler.setFormatter(JSONFormatter())
        elif formatter_type == "color":
            handler.setFormatter(ColorFormatter(config.get("format")))
        elif formatter_type == "sacred":
            handler.setFormatter(SacredFormatter(config.get("format")))
        else:
            handler.setFormatter(
                logging.Formatter(config.get("format", logging.BASIC_FORMAT))
            )

        return handler

    def get_logger(self, name: str) -> logging.Logger:
        """Get or create a logger"""
        if name in self.loggers:
            return self.loggers[name]

        logger = logging.getLogger(name)
        self.loggers[name] = logger
        return logger

    def set_level(self, logger_name: str, level: str | int) -> None:
        """Set logger level"""
        logger = logging.getLogger(logger_name)
        if isinstance(level, str):
            level = getattr(logging, level.upper())
        logger.setLevel(level)

    def add_handler(self, logger_name: str, handler: logging.Handler) -> None:
        """Add handler to logger"""
        logger = logging.getLogger(logger_name)
        logger.addHandler(handler)

    def remove_handler(self, logger_name: str, handler: logging.Handler) -> None:
        """Remove handler from logger"""
        logger = logging.getLogger(logger_name)
        logger.removeHandler(handler)

    def clear_handlers(self, logger_name: str) -> None:
        """Clear all handlers from logger"""
        logger = logging.getLogger(logger_name)
        logger.handlers.clear()


# Singleton instance
_config: LoggingConfig | None = None


def get_logging_config() -> LoggingConfig:
    """Get singleton logging configuration"""
    global _config
    if _config is None:
        _config = LoggingConfig()
        _config.setup_default()
    return _config


def setup_logging(
    level: str | None = None,
    debug: bool = False,
    production: bool = False,
    config: dict[str, Any] | None = None,
) -> None:
    """
    Convenience function to setup logging

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        debug: Enable debug mode
        production: Enable production mode
        config: Custom configuration dictionary
    """
    log_config = get_logging_config()

    if debug:
        log_config.setup_debug()
    elif production:
        log_config.setup_production()
    elif config:
        log_config.setup_from_config(config)
    else:
        log_config.setup_default()

    # Override level if specified
    if level:
        logging.getLogger().setLevel(getattr(logging, level.upper()))


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the given name

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return get_logging_config().get_logger(name)


# Context manager for temporary log level
class LogLevelContext:
    """Context manager for temporary log level changes"""

    def __init__(self, logger_name: str, level: str | int):
        self.logger_name = logger_name
        self.new_level = (
            level if isinstance(level, int) else getattr(logging, level.upper())
        )
        self.old_level = None
        self.logger = None

    def __enter__(self):
        self.logger = logging.getLogger(self.logger_name)
        self.old_level = self.logger.level
        self.logger.setLevel(self.new_level)
        return self.logger

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.logger and self.old_level is not None:
            self.logger.setLevel(self.old_level)


# Structured logging helpers
def log_event(
    logger: logging.Logger, event: str, level: int = logging.INFO, **kwargs
) -> None:
    """
    Log a structured event

    Args:
        logger: Logger instance
        event: Event name
        level: Log level
        **kwargs: Additional fields
    """
    extra = {"event": event, **kwargs}
    logger.log(level, f"Event: {event}", extra=extra)


def log_metric(
    logger: logging.Logger,
    metric: str,
    value: int | float,
    unit: str | None = None,
    **kwargs,
) -> None:
    """
    Log a metric

    Args:
        logger: Logger instance
        metric: Metric name
        value: Metric value
        unit: Optional unit
        **kwargs: Additional fields
    """
    extra = {"metric": metric, "value": value, "unit": unit, **kwargs}
    logger.info(f"Metric: {metric}={value}{unit or ''}", extra=extra)


def log_duration(
    logger: logging.Logger, operation: str, duration: float, **kwargs
) -> None:
    """
    Log operation duration

    Args:
        logger: Logger instance
        operation: Operation name
        duration: Duration in seconds
        **kwargs: Additional fields
    """
    extra = {"operation": operation, "duration_ms": duration * 1000, **kwargs}
    logger.info(f"Operation '{operation}' took {duration:.3f}s", extra=extra)
