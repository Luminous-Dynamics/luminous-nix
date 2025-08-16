"""
Error handling decorators for Nix for Humanity.

Provides decorators for retry logic and error handling.
"""

import functools
import logging
import time
from typing import Any, Callable, Optional, Type, Union

from .error_handler import ErrorHandler, handle_error

logger = logging.getLogger(__name__)


def retry_on_error(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable[[Exception, int], None]] = None,
) -> Callable:
    """
    Decorator to retry a function on error.
    
    Args:
        max_attempts: Maximum number of attempts (default: 3)
        delay: Initial delay between retries in seconds (default: 1.0)
        backoff: Multiplier for delay after each retry (default: 2.0)
        exceptions: Tuple of exception types to catch (default: all)
        on_retry: Optional callback called on each retry with (exception, attempt_number)
    
    Returns:
        Decorated function that retries on specified errors
    
    Example:
        @retry_on_error(max_attempts=3, delay=1.0)
        def flaky_network_call():
            # This will be retried up to 3 times if it fails
            return requests.get("https://api.example.com")
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None
            current_delay = delay
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts:
                        # Last attempt failed, re-raise
                        logger.error(
                            f"Function {func.__name__} failed after {max_attempts} attempts: {e}"
                        )
                        raise
                    
                    # Log retry
                    logger.warning(
                        f"Function {func.__name__} failed (attempt {attempt}/{max_attempts}): {e}"
                        f" - Retrying in {current_delay:.1f}s..."
                    )
                    
                    # Call retry callback if provided
                    if on_retry:
                        try:
                            on_retry(e, attempt)
                        except Exception as callback_error:
                            logger.error(f"Retry callback failed: {callback_error}")
                    
                    # Wait before retry
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            # This should never be reached, but just in case
            if last_exception:
                raise last_exception
                
        return wrapper
    return decorator


def with_error_handling(
    operation: str = None,
    category: Any = None,  # ErrorCategory from error_handler
    default_return: Any = None,
    log_errors: bool = True,
    reraise: bool = True,  # Changed default to True to match test expectations
    error_handler: Optional[ErrorHandler] = None,
    user_friendly: bool = True,
) -> Callable:
    """
    Decorator to add comprehensive error handling to a function.
    
    Args:
        default_return: Value to return if an error occurs (default: None)
        log_errors: Whether to log errors (default: True)
        reraise: Whether to re-raise the exception after handling (default: False)
        error_handler: Optional ErrorHandler instance to use
        user_friendly: Whether to provide user-friendly error messages (default: True)
    
    Returns:
        Decorated function with error handling
    
    Example:
        @with_error_handling(default_return=[], log_errors=True)
        def get_packages():
            # If this fails, it will return [] and log the error
            return fetch_packages_from_api()
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Use provided error handler or create a new one
                handler = error_handler or ErrorHandler()
                
                # Build context
                context = {
                    "function": func.__name__,
                    "operation": operation or func.__name__,
                    "args": str(args)[:100],  # Truncate for logging
                    "kwargs": str(kwargs)[:100],
                }
                
                # Handle the error
                error_response = handle_error(
                    exception=e,
                    operation=operation or func.__name__,
                    user_input=str(args)[:100] if args else ""
                )
                
                # Attach nix_error to the exception for testing
                e.nix_error = error_response
                
                # Override category if specified
                if category is not None:
                    from .error_handler import ErrorCategory
                    if isinstance(category, ErrorCategory):
                        e.nix_error.category = category
                
                # Log if requested
                if log_errors:
                    logger.error(
                        f"Error in {operation or func.__name__}: {str(e)}",
                        exc_info=True if logger.isEnabledFor(logging.DEBUG) else False
                    )
                
                # Re-raise if requested
                if reraise:
                    raise
                
                # Return default value
                return default_return
                
        # Also create an async version if the function is async
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                # Use provided error handler or create a new one
                handler = error_handler or ErrorHandler()
                
                # Build context
                context = {
                    "function": func.__name__,
                    "operation": operation or func.__name__,
                    "args": str(args)[:100],
                    "kwargs": str(kwargs)[:100],
                }
                
                # Handle the error
                error_response = handle_error(
                    exception=e,
                    operation=operation or func.__name__,
                    user_input=str(args)[:100] if args else ""
                )
                
                # Attach nix_error to the exception for testing
                e.nix_error = error_response
                
                # Override category if specified
                if category is not None:
                    from .error_handler import ErrorCategory
                    if isinstance(category, ErrorCategory):
                        e.nix_error.category = category
                
                # Log if requested
                if log_errors:
                    logger.error(
                        f"Error in {operation or func.__name__}: {str(e)}",
                        exc_info=True if logger.isEnabledFor(logging.DEBUG) else False
                    )
                
                # Re-raise if requested
                if reraise:
                    raise
                
                # Return default value
                return default_return
        
        # Return async wrapper for async functions, regular wrapper otherwise
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return wrapper
    return decorator


def timeout(seconds: float) -> Callable:
    """
    Decorator to add a timeout to a function.
    
    Args:
        seconds: Maximum time allowed for function execution
    
    Returns:
        Decorated function that will timeout after specified seconds
    
    Note:
        This uses threading and may not work correctly with all types of operations.
        For CPU-bound operations, consider using multiprocessing instead.
    
    Example:
        @timeout(5.0)
        def slow_operation():
            # This will be terminated if it takes more than 5 seconds
            time.sleep(10)
    """
    import signal
    import threading
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = [None]
            exception = [None]
            
            def target():
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    exception[0] = e
            
            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()
            thread.join(seconds)
            
            if thread.is_alive():
                # Function is still running, timeout occurred
                # Note: We can't actually kill the thread in Python
                raise TimeoutError(
                    f"Function {func.__name__} timed out after {seconds} seconds"
                )
            
            if exception[0]:
                raise exception[0]
            
            return result[0]
            
        return wrapper
    return decorator


def validate_input(**validators: Callable[[Any], bool]) -> Callable:
    """
    Decorator to validate function inputs.
    
    Args:
        **validators: Keyword arguments mapping parameter names to validation functions
    
    Returns:
        Decorated function that validates inputs before execution
    
    Example:
        @validate_input(
            age=lambda x: x > 0,
            name=lambda x: len(x) > 0
        )
        def create_user(name: str, age: int):
            return {"name": name, "age": age}
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Get function signature
            import inspect
            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            
            # Validate each parameter
            for param_name, validator in validators.items():
                if param_name in bound.arguments:
                    value = bound.arguments[param_name]
                    if not validator(value):
                        raise ValueError(
                            f"Invalid value for parameter '{param_name}': {value}"
                        )
            
            return func(*args, **kwargs)
            
        return wrapper
    return decorator


def deprecated(message: str = "", version: str = "") -> Callable:
    """
    Decorator to mark a function as deprecated.
    
    Args:
        message: Optional deprecation message
        version: Optional version when the function will be removed
    
    Returns:
        Decorated function that logs a deprecation warning when called
    
    Example:
        @deprecated(message="Use new_function instead", version="2.0.0")
        def old_function():
            return "This still works but is deprecated"
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            warning_msg = f"Function '{func.__name__}' is deprecated"
            
            if message:
                warning_msg += f": {message}"
            
            if version:
                warning_msg += f" (will be removed in version {version})"
            
            logger.warning(warning_msg)
            
            return func(*args, **kwargs)
            
        return wrapper
    return decorator


# Export commonly used decorators at module level for convenience
__all__ = [
    "retry_on_error",
    "with_error_handling",
    "timeout",
    "validate_input",
    "deprecated",
]