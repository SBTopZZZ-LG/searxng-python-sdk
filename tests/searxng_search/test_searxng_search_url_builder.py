"""Tests for SearXNG URL builder methods."""

import pytest

from searxng_search.searxng_search import (
    Autocomplete,
    Category,
    Plugins,
    SafeSearch,
    SearXNG,
    SearXNGBaseConfiguration,
    SearXNGSearchConfiguration,
    Theme,
    TimeRange,
)


@pytest.fixture
def searxng_client() -> SearXNG:
    """Return a SearXNG client with a default base configuration."""
    return SearXNG(
        base_configuration=SearXNGBaseConfiguration(
            base_url="https://searxng.example.com"
        )
    )


# ---------------------------------------------------------------------------
# SearXNG.__init__
# ---------------------------------------------------------------------------


def test_searxng_stores_base_configuration():
    """Test that SearXNG stores the provided base_configuration."""
    base_configuration = SearXNGBaseConfiguration(
        base_url="https://searxng.example.com"
    )

    client = SearXNG(base_configuration=base_configuration)

    assert client.base_configuration is base_configuration


# ---------------------------------------------------------------------------
# SearXNG._urlencode_set
# ---------------------------------------------------------------------------


def test_urlencode_set_returns_empty_string_for_none(searxng_client: SearXNG):
    """Test that _urlencode_set returns '' for None."""
    assert searxng_client._urlencode_set(None) == ""  # type: ignore # pylint: disable=protected-access


def test_urlencode_set_returns_empty_string_for_empty_set(searxng_client: SearXNG):
    """Test that _urlencode_set returns '' for an empty set."""
    assert searxng_client._urlencode_set(set()) == ""  # pylint: disable=protected-access


def test_urlencode_set_returns_single_item(searxng_client: SearXNG):
    """Test that _urlencode_set returns the single item as-is when no encoding is needed."""
    assert searxng_client._urlencode_set({"general"}) == "general"  # pylint: disable=protected-access


def test_urlencode_set_url_encodes_special_characters(searxng_client: SearXNG):
    """Test that _urlencode_set percent-encodes special characters."""
    assert searxng_client._urlencode_set({"social-media"}) == "social-media"  # pylint: disable=protected-access
    assert searxng_client._urlencode_set({"hello world"}) == "hello%20world"  # pylint: disable=protected-access


def test_urlencode_set_returns_comma_separated_items(searxng_client: SearXNG):
    """Test that _urlencode_set joins multiple items with commas."""
    result = searxng_client._urlencode_set({"general", "news"})  # pylint: disable=protected-access

    assert set(result.split(",")) == {"general", "news"}


def test_urlencode_set_encodes_enum_values(searxng_client: SearXNG):
    """Test that _urlencode_set uses the string value of StrEnum members."""
    result = searxng_client._urlencode_set({Category.GENERAL, Category.NEWS})  # pylint: disable=protected-access

    assert set(result.split(",")) == {"general", "news"}


# ---------------------------------------------------------------------------
# SearXNG._urlencode_custom_params
# ---------------------------------------------------------------------------


def test_urlencode_custom_params_returns_empty_string_for_none(searxng_client: SearXNG):
    """Test that _urlencode_custom_params returns '' for None."""
    assert searxng_client._urlencode_custom_params(None) == ""  # type: ignore # pylint: disable=protected-access


def test_urlencode_custom_params_returns_empty_string_for_empty_dict(
    searxng_client: SearXNG,
):
    """Test that _urlencode_custom_params returns '' for an empty dict."""
    assert searxng_client._urlencode_custom_params({}) == ""  # pylint: disable=protected-access


def test_urlencode_custom_params_returns_single_param(searxng_client: SearXNG):
    """Test that _urlencode_custom_params encodes a single key-value pair correctly."""
    assert searxng_client._urlencode_custom_params({"lang": "en"}) == "lang=en"  # pylint: disable=protected-access


def test_urlencode_custom_params_url_encodes_keys_and_values(searxng_client: SearXNG):
    """Test that _urlencode_custom_params percent-encodes special characters in keys and values."""
    result = searxng_client._urlencode_custom_params({"my key": "hello world"})  # pylint: disable=protected-access

    assert result == "my%20key=hello%20world"


def test_urlencode_custom_params_joins_multiple_params_with_ampersand(
    searxng_client: SearXNG,
):
    """Test that _urlencode_custom_params joins multiple pairs with '&'."""
    result = searxng_client._urlencode_custom_params({"lang": "en", "page": "2"})  # pylint: disable=protected-access

    assert set(result.split("&")) == {"lang=en", "page=2"}


# ---------------------------------------------------------------------------
# SearXNG._urlencode_boolean
# ---------------------------------------------------------------------------


def test_urlencode_boolean_returns_mapping_for_true(searxng_client: SearXNG):
    """Test that _urlencode_boolean returns mapping_for_true when is_true is True."""
    assert searxng_client._urlencode_boolean(True, "on", "off") == "on"  # pylint: disable=protected-access


def test_urlencode_boolean_returns_mapping_for_false(searxng_client: SearXNG):
    """Test that _urlencode_boolean returns mapping_for_false when is_true is False."""
    assert searxng_client._urlencode_boolean(False, "on", "off") == "off"  # pylint: disable=protected-access


def test_urlencode_boolean_works_with_custom_mappings(searxng_client: SearXNG):
    """Test that _urlencode_boolean works with arbitrary mapping strings."""
    true_mapping = "1"
    false_mapping = "0"

    assert (
        searxng_client._urlencode_boolean(True, true_mapping, false_mapping)  # pylint: disable=protected-access
        == true_mapping
    )
    assert (
        searxng_client._urlencode_boolean(False, true_mapping, false_mapping)  # pylint: disable=protected-access
        == false_mapping
    )


# ---------------------------------------------------------------------------
# SearXNG._build_search_url
# ---------------------------------------------------------------------------


def test_build_search_url_minimal(searxng_client: SearXNG):
    """Test that _build_search_url produces the correct base URL with only a query."""
    config = SearXNGSearchConfiguration(query="python")
    result = searxng_client._build_search_url(config)  # pylint: disable=protected-access

    assert result == "https://searxng.example.com/search?format=html&q=python"


def test_build_search_url_strips_trailing_slash():
    """Test that _build_search_url strips a trailing slash from the base URL."""
    client = SearXNG(
        base_configuration=SearXNGBaseConfiguration(
            base_url="https://searxng.example.com/"
        )
    )
    config = SearXNGSearchConfiguration(query="python")
    result = client._build_search_url(config)  # pylint: disable=protected-access

    assert result == "https://searxng.example.com/search?format=html&q=python"


def test_build_search_url_encodes_query(searxng_client: SearXNG):
    """Test that _build_search_url percent-encodes special characters in the query."""
    config = SearXNGSearchConfiguration(query="hello world")
    result = searxng_client._build_search_url(config)  # pylint: disable=protected-access

    assert result == "https://searxng.example.com/search?format=html&q=hello%20world"


def test_build_search_url_appends_custom_params(searxng_client: SearXNG):
    """Test that _build_search_url appends custom_params when provided."""
    config = SearXNGSearchConfiguration(query="python", custom_params={"lang": "en"})
    result = searxng_client._build_search_url(config)  # pylint: disable=protected-access

    assert result == "https://searxng.example.com/search?format=html&q=python&lang=en"


def test_build_search_url_appends_categories(searxng_client: SearXNG):
    """Test that _build_search_url appends categories when provided."""
    config = SearXNGSearchConfiguration(query="python", categories={Category.GENERAL})
    result = searxng_client._build_search_url(config)  # pylint: disable=protected-access

    assert (
        result
        == "https://searxng.example.com/search?format=html&q=python&categories=general"
    )


def test_build_search_url_appends_engines(searxng_client: SearXNG):
    """Test that _build_search_url appends engines when provided."""
    config = SearXNGSearchConfiguration(query="python", engines={"google"})
    result = searxng_client._build_search_url(config)  # pylint: disable=protected-access

    assert (
        result
        == "https://searxng.example.com/search?format=html&q=python&engines=google"
    )


def test_build_search_url_appends_page_number(searxng_client: SearXNG):
    """Test that _build_search_url appends page when provided."""
    config = SearXNGSearchConfiguration(query="python", page_number=3)
    result = searxng_client._build_search_url(config)  # pylint: disable=protected-access

    assert result == "https://searxng.example.com/search?format=html&q=python&page=3"


def test_build_search_url_appends_time_range(searxng_client: SearXNG):
    """Test that _build_search_url appends time_range when provided."""
    config = SearXNGSearchConfiguration(query="python", time_range=TimeRange.DAY)
    result = searxng_client._build_search_url(config)  # pylint: disable=protected-access

    assert (
        result
        == "https://searxng.example.com/search?format=html&q=python&time_range=day"
    )


def test_build_search_url_appends_results_on_new_tab_true(searxng_client: SearXNG):
    """Test that _build_search_url appends newtab=on when results_on_new_tab is True."""
    config = SearXNGSearchConfiguration(query="python", results_on_new_tab=True)
    result = searxng_client._build_search_url(config)  # pylint: disable=protected-access

    assert result == "https://searxng.example.com/search?format=html&q=python&newtab=on"


def test_build_search_url_appends_results_on_new_tab_false(searxng_client: SearXNG):
    """Test that _build_search_url appends newtab=off when results_on_new_tab is False."""
    config = SearXNGSearchConfiguration(query="python", results_on_new_tab=False)
    result = searxng_client._build_search_url(config)  # pylint: disable=protected-access

    assert (
        result == "https://searxng.example.com/search?format=html&q=python&newtab=off"
    )


def test_build_search_url_appends_image_proxy_true(searxng_client: SearXNG):
    """Test that _build_search_url appends image_proxy=on when image_proxy is True."""
    config = SearXNGSearchConfiguration(query="python", image_proxy=True)
    result = searxng_client._build_search_url(config)  # pylint: disable=protected-access

    assert (
        result
        == "https://searxng.example.com/search?format=html&q=python&image_proxy=on"
    )


def test_build_search_url_appends_image_proxy_false(searxng_client: SearXNG):
    """Test that _build_search_url appends image_proxy=off when image_proxy is False."""
    config = SearXNGSearchConfiguration(query="python", image_proxy=False)
    result = searxng_client._build_search_url(config)  # pylint: disable=protected-access

    assert (
        result
        == "https://searxng.example.com/search?format=html&q=python&image_proxy=off"
    )


def test_build_search_url_appends_autocomplete(searxng_client: SearXNG):
    """Test that _build_search_url appends autocomplete when provided."""
    config = SearXNGSearchConfiguration(
        query="python", autocomplete={Autocomplete.GOOGLE}
    )
    result = searxng_client._build_search_url(config)  # pylint: disable=protected-access

    assert (
        result
        == "https://searxng.example.com/search?format=html&q=python&autocomplete=google"
    )


def test_build_search_url_appends_safe_search(searxng_client: SearXNG):
    """Test that _build_search_url appends safe_search when provided."""
    config = SearXNGSearchConfiguration(query="python", safe_search=SafeSearch.STRICT)
    result = searxng_client._build_search_url(config)  # pylint: disable=protected-access

    assert (
        result
        == "https://searxng.example.com/search?format=html&q=python&safe_search=2"
    )


def test_build_search_url_appends_theme(searxng_client: SearXNG):
    """Test that _build_search_url appends theme when provided."""
    config = SearXNGSearchConfiguration(query="python", theme={Theme.SIMPLE})
    result = searxng_client._build_search_url(config)  # pylint: disable=protected-access

    assert (
        result == "https://searxng.example.com/search?format=html&q=python&theme=simple"
    )


def test_build_search_url_appends_enabled_plugins(searxng_client: SearXNG):
    """Test that _build_search_url appends enabled_plugins when provided."""
    config = SearXNGSearchConfiguration(
        query="python", enabled_plugins={Plugins.HASH_PLUGIN}
    )
    result = searxng_client._build_search_url(config)  # pylint: disable=protected-access

    assert (
        result
        == "https://searxng.example.com/search?format=html&q=python&enabled_plugins=Hash_plugin"
    )


def test_build_search_url_appends_disabled_plugins(searxng_client: SearXNG):
    """Test that _build_search_url appends disabled_plugins when provided."""
    config = SearXNGSearchConfiguration(
        query="python", disabled_plugins={Plugins.VIM_LIKE_HOTKEYS}
    )
    result = searxng_client._build_search_url(config)  # pylint: disable=protected-access

    assert (
        result
        == "https://searxng.example.com/search?format=html&q=python&disabled_plugins=Vim-like_hotkeys"
    )


def test_build_search_url_appends_enabled_engines(searxng_client: SearXNG):
    """Test that _build_search_url appends enabled_engines when provided."""
    config = SearXNGSearchConfiguration(query="python", enabled_engines={"bing"})
    result = searxng_client._build_search_url(config)  # pylint: disable=protected-access

    assert (
        result
        == "https://searxng.example.com/search?format=html&q=python&enabled_engines=bing"
    )


def test_build_search_url_appends_disabled_engines(searxng_client: SearXNG):
    """Test that _build_search_url appends disabled_engines when provided."""
    config = SearXNGSearchConfiguration(query="python", disabled_engines={"yahoo"})
    result = searxng_client._build_search_url(config)  # pylint: disable=protected-access

    assert (
        result
        == "https://searxng.example.com/search?format=html&q=python&disabled_engines=yahoo"
    )


def test_build_search_url_accumulates_multiple_params(searxng_client: SearXNG):
    """Test that _build_search_url correctly accumulates multiple optional parameters."""
    config = SearXNGSearchConfiguration(
        query="python",
        categories={Category.GENERAL},
        page_number=2,
        safe_search=SafeSearch.MODERATE,
    )
    result = searxng_client._build_search_url(config)  # pylint: disable=protected-access

    assert "categories=general" in result
    assert "page=2" in result
    assert "safe_search=1" in result
