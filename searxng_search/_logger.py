"""Logging utilities for the SearXNG Python SDK."""

import functools
import inspect
import logging

logging.getLogger("my_library").addHandler(logging.NullHandler())


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name."""

    return logging.getLogger(name)


def log_errors(logger: logging.Logger):
    """Decorator that logs exceptions with full stack trace before re-raising."""

    def decorator(func):
        _logger = logger or get_logger(func.__module__)

        if inspect.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                try:
                    return await func(*args, **kwargs)
                except Exception:
                    _logger.error("Exception in '%s'", func.__qualname__, exc_info=True)
                    raise

            return async_wrapper

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception:
                _logger.error("Exception in '%s'", func.__qualname__, exc_info=True)
                raise

        return wrapper

    return decorator
