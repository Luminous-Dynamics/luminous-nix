"""Structured logging configuration for Nix for Humanity."""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import structlog
from structlog.stdlib import BoundLogger


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
    json_logs: bool = False,
    add_timestamp: bool = True,
    colorize: bool = True,
) -> BoundLogger:
    """Configure structured logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
        json_logs: Whether to output JSON formatted logs
        add_timestamp: Whether to add timestamps to logs
        colorize: Whether to colorize console output (ignored if json_logs=True)
        
    Returns:
        Configured structlog logger
    """
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )

    # Processors for structlog
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
    ]

    if add_timestamp:
        processors.append(
            structlog.processors.TimeStamper(fmt="iso", utc=False)
        )

    # Add custom processors
    processors.extend([
        add_app_context,
        add_user_context,
        structlog.processors.format_exc_info,
    ])

    # Console rendering
    if json_logs:
        processors.append(structlog.processors.JSONRenderer())
    else:
        if colorize and sys.stdout.isatty():
            processors.append(
                structlog.dev.ConsoleRenderer(
                    columns=[
                        structlog.dev.Column(
                            "timestamp",
                            structlog.dev.KeyValueColumnFormatter(
                                key_style="dim",
                                value_style="blue",
                                reset_style="reset",
                                value_repr=str,
                            ),
                        ),
                        structlog.dev.Column(
                            "level",
                            structlog.dev.KeyValueColumnFormatter(
                                key_style="dim",
                                value_style="level",
                                reset_style="reset",
                                value_repr=str,
                            ),
                        ),
                        structlog.dev.Column(
                            "event",
                            structlog.dev.KeyValueColumnFormatter(
                                key_style="bright",
                                value_style="bright",
                                reset_style="reset",
                                value_repr=str,
                            ),
                        ),
                        structlog.dev.Column(
                            "",
                            structlog.dev.KeyValueColumnFormatter(
                                key_style="dim",
                                value_style="",
                                reset_style="reset",
                                value_repr=str,
                            ),
                        ),
                    ]
                )
            )
        else:
            processors.append(structlog.dev.ConsoleRenderer())

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Set up file logging if requested
    if log_file:
        setup_file_logging(log_file, log_level, json_logs)

    # Return a logger instance
    return structlog.get_logger()


def setup_file_logging(
    log_file: Path,
    log_level: str = "INFO",
    json_format: bool = False,
) -> None:
    """Set up file-based logging.
    
    Args:
        log_file: Path to log file
        log_level: Logging level
        json_format: Whether to use JSON format in file
    """
    # Ensure log directory exists
    log_file.parent.mkdir(parents=True, exist_ok=True)

    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(getattr(logging, log_level.upper()))

    # Set format
    if json_format:
        formatter = logging.Formatter('%(message)s')
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    file_handler.setFormatter(formatter)

    # Add to root logger
    logging.getLogger().addHandler(file_handler)


def add_app_context(
    logger: logging.Logger,
    method_name: str,
    event_dict: Dict[str, Any],
) -> Dict[str, Any]:
    """Add application context to log events.
    
    Args:
        logger: Logger instance
        method_name: Method being called
        event_dict: Event dictionary
        
    Returns:
        Updated event dictionary
    """
    event_dict["app"] = "nix-for-humanity"
    event_dict["version"] = "1.2.0"
    
    # Add environment info
    if os.getenv("NIX_HUMANITY_PYTHON_BACKEND"):
        event_dict["backend"] = "python"
    
    # Add process info
    event_dict["pid"] = os.getpid()
    
    return event_dict


def add_user_context(
    logger: logging.Logger,
    method_name: str,
    event_dict: Dict[str, Any],
) -> Dict[str, Any]:
    """Add user context to log events.
    
    Args:
        logger: Logger instance
        method_name: Method being called
        event_dict: Event dictionary
        
    Returns:
        Updated event dictionary
    """
    # Add user info if available
    user_id = os.getenv("USER") or os.getenv("USERNAME")
    if user_id:
        event_dict["user"] = user_id
    
    # Add session info if available
    session_id = os.getenv("NIX_HUMANITY_SESSION_ID")
    if session_id:
        event_dict["session_id"] = session_id
    
    return event_dict


class LoggerAdapter:
    """Adapter for integrating structured logging with existing code."""
    
    def __init__(self, logger: BoundLogger):
        """Initialize adapter with a structlog logger.
        
        Args:
            logger: Structlog BoundLogger instance
        """
        self.logger = logger
    
    def debug(self, msg: str, **kwargs) -> None:
        """Log debug message."""
        self.logger.debug(msg, **kwargs)
    
    def info(self, msg: str, **kwargs) -> None:
        """Log info message."""
        self.logger.info(msg, **kwargs)
    
    def warning(self, msg: str, **kwargs) -> None:
        """Log warning message."""
        self.logger.warning(msg, **kwargs)
    
    def error(self, msg: str, **kwargs) -> None:
        """Log error message."""
        self.logger.error(msg, **kwargs)
    
    def critical(self, msg: str, **kwargs) -> None:
        """Log critical message."""
        self.logger.critical(msg, **kwargs)
    
    def exception(self, msg: str, **kwargs) -> None:
        """Log exception with traceback."""
        self.logger.exception(msg, **kwargs)
    
    def bind(self, **kwargs) -> BoundLogger:
        """Bind context variables to logger.
        
        Args:
            **kwargs: Context variables to bind
            
        Returns:
            New logger with bound context
        """
        return self.logger.bind(**kwargs)
    
    def unbind(self, *keys) -> BoundLogger:
        """Unbind context variables from logger.
        
        Args:
            *keys: Keys to unbind
            
        Returns:
            New logger with unbound context
        """
        return self.logger.unbind(*keys)


# Performance logging utilities
class PerformanceLogger:
    """Logger for performance metrics."""
    
    def __init__(self, logger: BoundLogger):
        """Initialize performance logger.
        
        Args:
            logger: Structlog logger instance
        """
        self.logger = logger
        self.timers: Dict[str, datetime] = {}
    
    def start_timer(self, operation: str) -> None:
        """Start timing an operation.
        
        Args:
            operation: Name of the operation
        """
        self.timers[operation] = datetime.now()
        self.logger.debug(f"Started {operation}")
    
    def end_timer(self, operation: str, **context) -> float:
        """End timing an operation and log the duration.
        
        Args:
            operation: Name of the operation
            **context: Additional context to log
            
        Returns:
            Duration in seconds
        """
        if operation not in self.timers:
            self.logger.warning(f"No timer found for {operation}")
            return 0.0
        
        start_time = self.timers.pop(operation)
        duration = (datetime.now() - start_time).total_seconds()
        
        self.logger.info(
            f"Completed {operation}",
            duration_seconds=duration,
            duration_ms=duration * 1000,
            **context
        )
        
        return duration
    
    def log_metrics(self, metrics: Dict[str, Any]) -> None:
        """Log performance metrics.
        
        Args:
            metrics: Dictionary of metrics to log
        """
        self.logger.info("Performance metrics", **metrics)


# Security logging utilities
class SecurityLogger:
    """Logger for security events."""
    
    def __init__(self, logger: BoundLogger):
        """Initialize security logger.
        
        Args:
            logger: Structlog logger instance
        """
        self.logger = logger.bind(category="security")
    
    def log_auth_attempt(
        self,
        success: bool,
        user: Optional[str] = None,
        method: Optional[str] = None,
        **context
    ) -> None:
        """Log authentication attempt.
        
        Args:
            success: Whether authentication succeeded
            user: Username attempting auth
            method: Authentication method used
            **context: Additional context
        """
        event = "auth_success" if success else "auth_failure"
        self.logger.info(
            event,
            user=user,
            method=method,
            **context
        )
    
    def log_access(
        self,
        resource: str,
        action: str,
        allowed: bool,
        user: Optional[str] = None,
        **context
    ) -> None:
        """Log access control decision.
        
        Args:
            resource: Resource being accessed
            action: Action being performed
            allowed: Whether access was allowed
            user: User requesting access
            **context: Additional context
        """
        event = "access_granted" if allowed else "access_denied"
        self.logger.info(
            event,
            resource=resource,
            action=action,
            user=user,
            **context
        )
    
    def log_security_event(
        self,
        event_type: str,
        severity: str,
        description: str,
        **context
    ) -> None:
        """Log general security event.
        
        Args:
            event_type: Type of security event
            severity: Severity level (low, medium, high, critical)
            description: Event description
            **context: Additional context
        """
        log_func = getattr(self.logger, severity, self.logger.info)
        log_func(
            "security_event",
            event_type=event_type,
            description=description,
            **context
        )


# Global logger instance
logger: Optional[BoundLogger] = None


def get_logger() -> BoundLogger:
    """Get or create the global logger instance.
    
    Returns:
        Configured logger instance
    """
    global logger
    if logger is None:
        logger = setup_logging(
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            json_logs=os.getenv("JSON_LOGS", "false").lower() == "true",
            colorize=os.getenv("NO_COLOR") is None,
        )
    return logger