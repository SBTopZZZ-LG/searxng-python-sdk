"""Test for the _http_url module."""

from unittest.mock import MagicMock, patch

import pytest
from pydantic import TypeAdapter, ValidationError

from searxng_search._http_url import HttpUrl, _normalize_url


@pytest.fixture
def http_url_adapter() -> TypeAdapter:
    """Return a TypeAdapter for the HttpUrl type."""
    return TypeAdapter(HttpUrl)


def test_normalize_url_calls_validate_python():
    """Test that _normalize_url calls validate_python on the adapter."""

    mock__http_url_adapter = MagicMock()
    mock__http_url_adapter.validate_python.return_value = "https://example.com/"

    with patch("searxng_search._http_url._http_url_adapter", mock__http_url_adapter):
        _ = _normalize_url("https://example.com")

    mock__http_url_adapter.validate_python.assert_called_once_with(
        "https://example.com"
    )


def test_normalize_url_sets_https_prefix():
    """Test that _normalize_url adds https: prefix to protocol-relative URLs."""

    mock__http_url_adapter = MagicMock()
    mock__http_url_adapter.validate_python.return_value = "https://example.com/"

    with patch("searxng_search._http_url._http_url_adapter", mock__http_url_adapter):
        _ = _normalize_url("//example.com")

    mock__http_url_adapter.validate_python.assert_called_once_with(
        "https://example.com"
    )


@pytest.mark.parametrize(
    "url,expected",
    [
        ("https://example.com/", "https://example.com/"),
        ("https://example.com", "https://example.com/"),
        ("//example.com/", "https://example.com/"),
    ],
)
def test_httpurl_type_adapter_normalizes_urls(
    http_url_adapter: TypeAdapter, url: str, expected: str
):
    """Test that HttpUrl type adapter normalizes URLs correctly."""

    assert http_url_adapter.validate_python(url) == expected


@pytest.mark.parametrize(
    "url",
    [
        "not-a-url",
        "ftp://example.com",
        "",
    ],
)
def test_httpurl_type_adapter_raises_on_invalid_url(
    http_url_adapter: TypeAdapter, url: str
):
    """Test that HttpUrl type adapter raises ValidationError for invalid URLs."""

    with pytest.raises(ValidationError):
        http_url_adapter.validate_python(url)
