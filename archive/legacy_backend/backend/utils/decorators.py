#!/usr/bin/env python3
"""
from typing import Optional
Decorators for Nix for Humanity
Provides useful decorators for error handling, logging, and performance monitoring
"""

import functools
import time
import logging
from typing import Callable, Any, Optional
from ..core.error_handler import error_handler, ErrorContext, ErrorCategory

logger = logging.getLogger(__name__)


def with_error_handling(operation: str, category: Optional[ErrorCategory] = None):
    """
    Decorator to add comprehensive error handling to functions
    
    Args:
        operation: Name of the operation for error context
        category: Optional error category hint
        
    Example:
        @with_error_handling("install_package", ErrorCategory.NIXOS)
        def install_package(package: str):
            # function code
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Build context from function arguments
                context = ErrorContext(
                    operation=operation,
                    metadata={
                        "function": func.__name__,
                        "args": str(args)[:200],  # Truncate for safety
                        "kwargs": str(kwargs)[:200]
                    }
                )
                
                # Handle error
                nix_error = error_handler.handle_error(e, context, category)
                
                # Re-raise with error attached
                e.nix_error = nix_error
                raise
                
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                # Build context from function arguments
                context = ErrorContext(
                    operation=operation,
                    metadata={
                        "function": func.__name__,
                        "args": str(args)[:200],
                        "kwargs": str(kwargs)[:200]
                    }
                )
                
                # Handle error
                nix_error = error_handler.handle_error(e, context, category)
                
                # Re-raise with error attached
                e.nix_error = nix_error
                raise
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return wrapper
            
    return decorator


def with_timing(name: Optional[str] = None):
    """
    Decorator to measure function execution time
    
    Args:
        name: Optional name for the timing log
        
    Example:
        @with_timing("package_installation")
        def install_package(package: str):
            # function code
    """
    def decorator(func: Callable) -> Callable:
        operation_name = name or func.__name__
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.debug(f"{operation_name} completed in {duration:.3f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.debug(f"{operation_name} failed after {duration:.3f}s")
                raise
                
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                logger.debug(f"{operation_name} completed in {duration:.3f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.debug(f"{operation_name} failed after {duration:.3f}s")
                raise
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return wrapper
            
    return decorator


def retry_on_error(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Decorator to retry function on failure with exponential backoff
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Backoff multiplier for each retry
        
    Example:
        @retry_on_error(max_attempts=3, delay=1.0)
        def fetch_package_info(package: str):
            # function code that might fail
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            current_delay = delay
            
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    if attempt >= max_attempts:
                        logger.error(f"{func.__name__} failed after {max_attempts} attempts")
                        raise
                    
                    logger.warning(f"{func.__name__} failed (attempt {attempt}/{max_attempts}), retrying in {current_delay}s")
                    time.sleep(current_delay)
                    current_delay *= backoff
                    
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            attempt = 0
            current_delay = delay
            
            while attempt < max_attempts:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    if attempt >= max_attempts:
                        logger.error(f"{func.__name__} failed after {max_attempts} attempts")
                        raise
                    
                    logger.warning(f"{func.__name__} failed (attempt {attempt}/{max_attempts}), retrying in {current_delay}s")
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return wrapper
            
    return decorator


def deprecated(replacement: Optional[str] = None):
    """
    Decorator to mark functions as deprecated
    
    Args:
        replacement: Optional name of replacement function
        
    Example:
        @deprecated("use_new_function")
        def old_function():
            # legacy code
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            msg = f"{func.__name__} is deprecated"
            if replacement:
                msg += f", use {replacement} instead"
            logger.warning(msg)
            return func(*args, **kwargs)
            
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            msg = f"{func.__name__} is deprecated"
            if replacement:
                msg += f", use {replacement} instead"
            logger.warning(msg)
            return await func(*args, **kwargs)
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return wrapper
            
    return decorator


# Import asyncio for async detection
import asyncio