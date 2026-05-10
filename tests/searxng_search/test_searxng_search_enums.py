"""Tests for enums and the SEARXNG_FORMAT constant in the searxng_search module."""

import pytest

from searxng_search.searxng_search import (
    SEARXNG_FORMAT,
    Autocomplete,
    Category,
    Plugins,
    SafeSearch,
    Theme,
    TimeRange,
)


def test_searxng_response_format_is_html():
    """Test that SEARXNG_FORMAT is set to 'html'."""
    assert SEARXNG_FORMAT == "html"


# ---------------------------------------------------------------------------
# Enum string values
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "member,expected",
    [
        (Category.GENERAL, "general"),
        (Category.NEWS, "news"),
        (Category.IMAGES, "images"),
        (Category.VIDEOS, "videos"),
        (Category.MAP, "map"),
        (Category.IT, "it"),
        (Category.SCIENCE, "science"),
        (Category.MUSIC, "music"),
        (Category.FILES, "files"),
        (Category.SOCIAL_MEDIA, "social-media"),
    ],
)
def test_category_string_values(member: Category, expected: str):
    """Test that Category enum members produce the correct URL parameter strings."""
    assert member == expected


@pytest.mark.parametrize(
    "member,expected",
    [
        (TimeRange.DAY, "day"),
        (TimeRange.MONTH, "month"),
        (TimeRange.YEAR, "year"),
    ],
)
def test_time_range_string_values(member: TimeRange, expected: str):
    """Test that TimeRange enum members produce the correct URL parameter strings."""
    assert member == expected


@pytest.mark.parametrize(
    "member,expected",
    [
        (SafeSearch.OFF, "0"),
        (SafeSearch.MODERATE, "1"),
        (SafeSearch.STRICT, "2"),
    ],
)
def test_safe_search_string_values(member: SafeSearch, expected: str):
    """Test that SafeSearch enum members produce the correct URL parameter strings."""
    assert member == expected


@pytest.mark.parametrize(
    "member,expected",
    [
        (Autocomplete.GOOGLE, "google"),
        (Autocomplete.DBPEDIA, "dbpedia"),
        (Autocomplete.DUCKDUCKGO, "duckduckgo"),
        (Autocomplete.MWMBL, "mwmbl"),
        (Autocomplete.STARTPAGE, "startpage"),
        (Autocomplete.WIKIPEDIA, "wikipedia"),
        (Autocomplete.SWISSCOWS, "swisscows"),
        (Autocomplete.QWANT, "qwant"),
    ],
)
def test_autocomplete_string_values(member: Autocomplete, expected: str):
    """Test that Autocomplete enum members produce the correct URL parameter strings."""
    assert member == expected


def test_theme_simple_string_value():
    """Test that Theme.SIMPLE produces the correct URL parameter string."""
    assert Theme.SIMPLE == "simple"


@pytest.mark.parametrize(
    "member,expected",
    [
        (Plugins.HASH_PLUGIN, "Hash_plugin"),
        (Plugins.SELF_INFORMATION, "Self_Information"),
        (Plugins.TRACKER_URL_REMOVER, "Tracker_URL_remover"),
        (Plugins.AHMIA_BLACKLIST, "Ahmia_blacklist"),
        (Plugins.HOSTNAMES_PLUGIN, "Hostnames_plugin"),
        (Plugins.OPEN_ACCESS_DOI_REWRITE, "Open_Access_DOI_rewrite"),
        (Plugins.VIM_LIKE_HOTKEYS, "Vim-like_hotkeys"),
        (Plugins.TOR_CHECK_PLUGIN, "Tor_check_plugin"),
    ],
)
def test_plugins_string_values(member: Plugins, expected: str):
    """Test that Plugins enum members produce the correct URL parameter strings."""
    assert member == expected
