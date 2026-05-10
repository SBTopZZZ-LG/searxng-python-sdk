"""Test for the _http_url module."""

from unittest.mock import MagicMock, patch

import pytest
from pydantic import TypeAdapter, ValidationError


def test_normalize_url_calls_validate_python():
    """Test that _normalize_url calls validate_python on the adapter."""

    mock_adapter = MagicMock()
    mock_adapter.validate_python.return_value = "https://example.com/"

    with patch("searxng_search._http_url._http_url_adapter", mock_adapter):
        from searxng_search._http_url import _normalize_url

        _ = _normalize_url("https://example.com")

    mock_adapter.validate_python.assert_called_once_with("https://example.com")


def test_normalize_url_sets_https_prefix():
    """Test that _normalize_url adds https: prefix to protocol-relative URLs."""

    mock_adapter = MagicMock()
    mock_adapter.validate_python.return_value = "https://example.com/"

    with patch("searxng_search._http_url._http_url_adapter", mock_adapter):
        from searxng_search._http_url import _normalize_url

        _ = _normalize_url("//example.com")

    mock_adapter.validate_python.assert_called_once_with("https://example.com")


def test_httpurl_type_adapter_normalizes_urls():
    """Test that HttpUrl type adapter normalizes URLs correctly."""

    from searxng_search._http_url import HttpUrl

    adapter = TypeAdapter(HttpUrl)

    result = adapter.validate_python("https://example.com/")
    assert result == "https://example.com/"

    result = adapter.validate_python("https://example.com")
    assert result == "https://example.com/"

    result = adapter.validate_python("//example.com/")
    assert result == "https://example.com/"


def test_httpurl_type_adapter_raises_on_invalid_url():
    """Test that HttpUrl type adapter raises ValidationError for invalid URLs."""

    from searxng_search._http_url import HttpUrl

    adapter = TypeAdapter(HttpUrl)

    with pytest.raises(ValidationError):
        adapter.validate_python("not-a-url")

    with pytest.raises(ValidationError):
        adapter.validate_python("ftp://example.com")

    with pytest.raises(ValidationError):
        adapter.validate_python("")

    result = adapter.validate_python("//example.com")
    assert result == "https://example.com/"
