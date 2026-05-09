"""Logging utilities for the SearXNG Python SDK."""

import functools
import logging

logging.getLogger("my_library").addHandler(logging.NullHandler())


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name."""

    return logging.getLogger(name)


def log_errors(logger: logging.Logger):
    """Decorator that logs exceptions with full stack trace before re-raising."""

    def decorator(func):
        _logger = logger or get_logger(func.__module__)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception:
                _logger.error("Exception in '%s'", func.__qualname__, exc_info=True)
                raise

        return wrapper

    return decorator
