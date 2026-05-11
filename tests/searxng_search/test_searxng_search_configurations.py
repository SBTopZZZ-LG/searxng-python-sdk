"""Tests for SearXNGBaseConfiguration and SearXNGSearchConfiguration dataclasses."""

import math

import pytest
from pydantic import ValidationError

from searxng_search.searxng_search import (
    Autocomplete,
    Category,
    Plugins,
    SafeSearch,
    SearXNGBaseConfiguration,
    SearXNGSearchConfiguration,
    Theme,
    TimeRange,
)

# ---------------------------------------------------------------------------
# SearXNGBaseConfiguration
# ---------------------------------------------------------------------------


def test_base_configuration_accepts_valid_url():
    """Test that SearXNGBaseConfiguration accepts a valid HTTP URL."""
    config = SearXNGBaseConfiguration(base_url="https://searxng.example.com")
    assert config.base_url == "https://searxng.example.com/"


def test_base_configuration_normalizes_protocol_relative_url():
    """Test that SearXNGBaseConfiguration normalizes protocol-relative URLs."""
    config = SearXNGBaseConfiguration(base_url="//searxng.example.com")
    assert config.base_url == "https://searxng.example.com/"


@pytest.mark.parametrize("url", ["not-a-url", "ftp://example.com", ""])
def test_base_configuration_rejects_invalid_url(url: str):
    """Test that SearXNGBaseConfiguration raises ValidationError for invalid URLs."""
    with pytest.raises(ValidationError):
        SearXNGBaseConfiguration(base_url=url)


def test_base_configuration_user_agent_defaults_to_none():
    """Test that user_agent defaults to None when not provided."""
    config = SearXNGBaseConfiguration(base_url="https://searxng.example.com")
    assert config.user_agent is None


def test_base_configuration_stores_all_fields():
    """Test that all fields are stored correctly when provided."""
    base_url = "https://searxng.example.com"
    user_agent = "TestAgent/1.0"

    config = SearXNGBaseConfiguration(
        base_url=base_url,
        user_agent=user_agent,
    )

    assert config.base_url == base_url + "/"
    assert config.user_agent == user_agent


def test_base_configuration_timeout_defaults_to_30():
    """Test that timeout defaults to 30.0 when not provided."""
    config = SearXNGBaseConfiguration(base_url="https://searxng.example.com")
    assert config.timeout is not None
    assert math.isclose(config.timeout, 30.0, rel_tol=1e-9)


def test_base_configuration_accepts_custom_timeout():
    """Test that a valid positive timeout value is accepted."""
    config = SearXNGBaseConfiguration(
        base_url="https://searxng.example.com", timeout=15.0
    )
    assert config.timeout is not None
    assert math.isclose(config.timeout, 15.0, rel_tol=1e-9)


def test_base_configuration_accepts_none_timeout():
    """Test that None is accepted for timeout (disables timeout)."""
    config = SearXNGBaseConfiguration(
        base_url="https://searxng.example.com", timeout=None
    )
    assert config.timeout is None


@pytest.mark.parametrize("timeout", [0.0, -1.0, -100.0])
def test_base_configuration_rejects_non_positive_timeout(timeout: float):
    """Test that a zero or negative timeout raises ValidationError."""
    with pytest.raises(ValidationError):
        SearXNGBaseConfiguration(
            base_url="https://searxng.example.com", timeout=timeout
        )


# ---------------------------------------------------------------------------
# SearXNGSearchConfiguration
# ---------------------------------------------------------------------------


def test_search_configuration_accepts_valid_query():
    """Test that SearXNGSearchConfiguration accepts a non-empty query."""
    config = SearXNGSearchConfiguration(query="python")
    assert config.query == "python"


def test_search_configuration_rejects_empty_query():
    """Test that SearXNGSearchConfiguration raises ValidationError for an empty query."""
    with pytest.raises(ValidationError):
        SearXNGSearchConfiguration(query="")


def test_search_configuration_all_optional_fields_default_to_none():
    """Test that all optional fields default to None."""
    config = SearXNGSearchConfiguration(query="python")
    assert config.custom_params is None
    assert config.custom_headers is None
    assert config.categories is None
    assert config.engines is None
    assert config.page_number is None
    assert config.time_range is None
    assert config.results_on_new_tab is None
    assert config.image_proxy is None
    assert config.autocomplete is None
    assert config.safe_search is None
    assert config.theme is None
    assert config.enabled_plugins is None
    assert config.disabled_plugins is None
    assert config.enabled_engines is None
    assert config.disabled_engines is None


def test_search_configuration_stores_all_fields():
    """Test that all fields are stored correctly when provided."""
    query = "python"
    custom_params = {"lang": "en"}
    custom_headers = {"X-Custom": "value"}
    categories: set[Category | str] = {Category.GENERAL, Category.NEWS}
    engines = {"google", "bing"}
    page_number = 2
    time_range = TimeRange.MONTH
    results_on_new_tab = True
    image_proxy = False
    autocomplete: set[Autocomplete | str] = {Autocomplete.GOOGLE}
    safe_search = SafeSearch.MODERATE
    theme: set[Theme | str] = {Theme.SIMPLE}
    enabled_plugins: set[Plugins | str] = {Plugins.HASH_PLUGIN}
    disabled_plugins: set[Plugins | str] = {Plugins.TOR_CHECK_PLUGIN}
    enabled_engines = {"brave"}
    disabled_engines = {"yahoo"}

    config = SearXNGSearchConfiguration(
        query=query,
        custom_params=custom_params,
        custom_headers=custom_headers,
        categories=categories,
        engines=engines,
        page_number=page_number,
        time_range=time_range,
        results_on_new_tab=results_on_new_tab,
        image_proxy=image_proxy,
        autocomplete=autocomplete,
        safe_search=safe_search,
        theme=theme,
        enabled_plugins=enabled_plugins,
        disabled_plugins=disabled_plugins,
        enabled_engines=enabled_engines,
        disabled_engines=disabled_engines,
    )

    assert config.query == query
    assert config.custom_params == custom_params
    assert config.custom_headers == custom_headers
    assert config.categories == categories
    assert config.engines == engines
    assert config.page_number == page_number
    assert config.time_range == time_range
    assert config.results_on_new_tab == results_on_new_tab
    assert config.image_proxy == image_proxy
    assert config.autocomplete == autocomplete
    assert config.safe_search == safe_search
    assert config.theme == theme
    assert config.enabled_plugins == enabled_plugins
    assert config.disabled_plugins == disabled_plugins
    assert config.enabled_engines == enabled_engines
    assert config.disabled_engines == disabled_engines
