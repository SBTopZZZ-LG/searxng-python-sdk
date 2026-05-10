"""Test for the _logger module."""

import logging
from unittest.mock import MagicMock, patch

import pytest

from searxng_search._logger import log_errors


@pytest.fixture
def make_logger():
    """Return a factory function that creates loggers with the specified name."""

    def _factory(name: str) -> logging.Logger:
        return logging.getLogger(name)

    return _factory


@pytest.mark.parametrize(
    "logger_name",
    [
        "test_logger",
        "another_test_logger",
    ],
)
def test_get_logger_returns_logger_with_specified_name(make_logger, logger_name: str):
    """Test that get_logger returns a logger with the specified name."""

    mock_logging = MagicMock()

    test_logger = make_logger(logger_name)
    mock_logging.getLogger.return_value = test_logger

    with patch("searxng_search._logger.logging", mock_logging):
        from searxng_search._logger import get_logger

        logger = get_logger(logger_name)

    mock_logging.getLogger.assert_called_once_with(logger_name)
    assert logger is test_logger


def test_log_errors_returns_func_result():
    """Test that the decorated function's return value is propagated."""

    mock_logger = MagicMock()

    @log_errors(mock_logger)
    def my_func():
        return 42

    assert my_func() == 42


def test_log_errors_passes_args_and_kwargs_to_func():
    """Test that positional and keyword arguments are forwarded to the decorated function."""

    mock_logger = MagicMock()

    @log_errors(mock_logger)
    def my_func(a, b, *, c):
        return (a, b, c)

    assert my_func(1, 2, c=3) == (1, 2, 3)


def test_log_errors_logs_and_reraises_on_exception():
    """Test that exceptions are logged with exc_info=True and then re-raised."""

    mock_logger = MagicMock()
    error = ValueError("oops")

    @log_errors(mock_logger)
    def my_func():
        raise error

    with pytest.raises(ValueError, match="oops"):
        my_func()

    mock_logger.error.assert_called_once_with(
        "Exception in '%s'", my_func.__qualname__, exc_info=True
    )


def test_log_errors_uses_provided_logger():
    """Test that get_logger is not called when a logger is explicitly provided."""

    mock_logger = MagicMock()

    with patch("searxng_search._logger.get_logger") as mock_get_logger:

        @log_errors(mock_logger)
        def my_func():
            return 42

    mock_get_logger.assert_not_called()


def test_log_errors_falls_back_to_get_logger_when_none():
    """Test that get_logger is called with func.__module__ when logger is None."""

    mock_logger = MagicMock()

    with patch(
        "searxng_search._logger.get_logger", return_value=mock_logger
    ) as mock_get_logger:

        @log_errors(None)  # type: ignore
        def my_func():
            return 42

    mock_get_logger.assert_called_once_with(my_func.__module__)


def test_log_errors_preserves_func_metadata():
    """Test that functools.wraps preserves __name__ and __qualname__ on the wrapper."""

    mock_logger = MagicMock()

    @log_errors(mock_logger)
    def my_func():
        """A test function to check metadata preservation."""

    assert my_func.__name__ == "my_func"
    assert "my_func" in my_func.__qualname__
