"""Tests for _get_search_results_from_html on the SearXNG class."""

import pytest

from searxng_search.searxng_search import (
    FileResult,
    GeneralOrNewsResult,
    ImageResult,
    ITResult,
    MapResult,
    MusicResult,
    ScienceResult,
    SearXNG,
    SearXNGBaseConfiguration,
    SocialMediaResult,
    VideoResult,
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
# SearXNG._get_search_results_from_html
# ---------------------------------------------------------------------------


def test_dispatcher_returns_empty_list_for_empty_html(searxng_client: SearXNG):
    """Test that an HTML page with no article.result elements returns []."""
    result = searxng_client._get_search_results_from_html("<html><body></body></html>")  # pylint: disable=protected-access

    assert result == []


def test_dispatcher_skips_articles_without_result_class(searxng_client: SearXNG):
    """Test that articles missing the 'result' class are ignored."""
    html = """
        <html><body>
            <article class="other">
                <a class="url_header" href="https://example.com">url</a>
                <h3><a href="https://example.com">Title</a></h3>
            </article>
        </body></html>
    """
    result = searxng_client._get_search_results_from_html(html)  # pylint: disable=protected-access

    assert result == []


def test_dispatcher_filters_out_none_results(searxng_client: SearXNG):
    """Test that articles that fail to parse (return None) are excluded from results."""
    html = """
        <html><body>
            <article class="result">
            </article>
        </body></html>
    """
    result = searxng_client._get_search_results_from_html(html)  # pylint: disable=protected-access

    assert result == []


def test_dispatcher_routes_result_images_to_parse_images(searxng_client: SearXNG):
    """Test that article.result.result-images dispatches to _parse_images."""
    html = """
        <html><body>
            <article class="result result-images">
                <a href="https://example.com/img.jpg">link</a>
                <span class="title">A Photo</span>
            </article>
        </body></html>
    """
    results = searxng_client._get_search_results_from_html(html)  # pylint: disable=protected-access

    assert len(results) == 1
    assert isinstance(results[0], ImageResult)


def test_dispatcher_routes_result_videos_to_parse_videos(searxng_client: SearXNG):
    """Test that article.result.result-videos dispatches to _parse_videos."""
    html = """
        <html><body>
            <article class="result result-videos">
                <a class="url_header" href="https://example.com/video">url</a>
                <h3><a href="https://example.com/video">My Video</a></h3>
            </article>
        </body></html>
    """
    results = searxng_client._get_search_results_from_html(html)  # pylint: disable=protected-access

    assert len(results) == 1
    assert isinstance(results[0], VideoResult)


def test_dispatcher_routes_result_map_to_parse_map(searxng_client: SearXNG):
    """Test that article.result.result-map dispatches to _parse_map."""
    html = """
        <html><body>
            <article class="result result-map">
                <a class="url_header" href="https://maps.example.com/place">url</a>
                <h3><a href="https://maps.example.com/place">Central Park</a></h3>
            </article>
        </body></html>
    """
    results = searxng_client._get_search_results_from_html(html)  # pylint: disable=protected-access

    assert len(results) == 1
    assert isinstance(results[0], MapResult)


def test_dispatcher_routes_result_it_to_parse_it(searxng_client: SearXNG):
    """Test that article.category-it dispatches to _parse_it."""
    html = """
        <html><body>
            <article class="result result-default category-it">
                <a class="url_header" href="https://github.com/repo">url</a>
                <h3><a href="https://github.com/repo">Some Repo</a></h3>
            </article>
        </body></html>
    """
    results = searxng_client._get_search_results_from_html(html)  # pylint: disable=protected-access

    assert len(results) == 1
    assert isinstance(results[0], ITResult)


def test_dispatcher_routes_result_science_to_parse_science(searxng_client: SearXNG):
    """Test that article.category-science dispatches to _parse_science."""
    html = """
        <html><body>
            <article class="result result-default category-science">
                <a href="https://example.com/paper">link</a>
                <h3>Research Paper</h3>
            </article>
        </body></html>
    """
    results = searxng_client._get_search_results_from_html(html)  # pylint: disable=protected-access

    assert len(results) == 1
    assert isinstance(results[0], ScienceResult)


def test_dispatcher_routes_result_music_to_parse_music(searxng_client: SearXNG):
    """Test that article.category-music dispatches to _parse_music."""
    html = """
        <html><body>
            <article class="result result-default category-music">
                <a class="url_header" href="https://example.com/song">url</a>
                <h3><a href="https://example.com/song">Great Song</a></h3>
            </article>
        </body></html>
    """
    results = searxng_client._get_search_results_from_html(html)  # pylint: disable=protected-access

    assert len(results) == 1
    assert isinstance(results[0], MusicResult)


def test_dispatcher_routes_result_files_to_parse_files(searxng_client: SearXNG):
    """Test that article.category-files dispatches to _parse_files."""
    html = """
        <html><body>
            <article class="result result-torrent category-files">
                <a class="url_header" href="https://example.com/file.pdf">url</a>
                <h3><a href="https://example.com/file.pdf">My Document</a></h3>
            </article>
        </body></html>
    """
    results = searxng_client._get_search_results_from_html(html)  # pylint: disable=protected-access

    assert len(results) == 1
    assert isinstance(results[0], FileResult)


def test_dispatcher_routes_category_social_media_to_parse_social_media(
    searxng_client: SearXNG,
):
    """Test that article.result.category-social.media dispatches to _parse_social_media."""
    html = """
        <html><body>
            <article class="result category-social media">
                <a class="url_header" href="https://example.com/post">url</a>
                <h3>Post Title</h3>
            </article>
        </body></html>
    """
    results = searxng_client._get_search_results_from_html(html)  # pylint: disable=protected-access

    assert len(results) == 1
    assert isinstance(results[0], SocialMediaResult)


def test_dispatcher_routes_unrecognised_class_to_parse_general_or_news(
    searxng_client: SearXNG,
):
    """Test that an article.result with no special class dispatches to _parse_general_or_news."""
    html = """
        <html><body>
            <article class="result">
                <a class="url_header" href="https://example.com/article">url</a>
                <h3><a href="https://example.com/article">My Title</a></h3>
            </article>
        </body></html>
    """
    results = searxng_client._get_search_results_from_html(html)  # pylint: disable=protected-access

    assert len(results) == 1
    assert isinstance(results[0], GeneralOrNewsResult)


def test_dispatcher_returns_multiple_results_in_order(searxng_client: SearXNG):
    """Test that multiple article elements are all parsed and returned in document order."""
    html = """
        <html><body>
            <article class="result">
                <a class="url_header" href="https://example.com/one">url</a>
                <h3><a href="https://example.com/one">First</a></h3>
            </article>
            <article class="result result-images">
                <a href="https://example.com/img.jpg">link</a>
                <span class="title">A Photo</span>
            </article>
            <article class="result result-default category-it">
                <a class="url_header" href="https://github.com/repo">url</a>
                <h3><a href="https://github.com/repo">Some Repo</a></h3>
            </article>
        </body></html>
    """
    results = searxng_client._get_search_results_from_html(html)  # pylint: disable=protected-access

    assert len(results) == 3
    assert isinstance(results[0], GeneralOrNewsResult)
    assert isinstance(results[1], ImageResult)
    assert isinstance(results[2], ITResult)


def test_dispatcher_mixed_valid_and_invalid_articles(searxng_client: SearXNG):
    """Test that unparseable articles are dropped while valid ones are kept."""
    html = """
        <html><body>
            <article class="result">
                <a class="url_header" href="https://example.com/article">url</a>
                <h3><a href="https://example.com/article">My Title</a></h3>
            </article>
            <article class="result result-images">
            </article>
            <article class="result result-default category-it">
                <a class="url_header" href="https://github.com/repo">url</a>
                <h3><a href="https://github.com/repo">Some Repo</a></h3>
            </article>
        </body></html>
    """
    results = searxng_client._get_search_results_from_html(html)  # pylint: disable=protected-access

    assert len(results) == 2
    assert isinstance(results[0], GeneralOrNewsResult)
    assert isinstance(results[1], ITResult)
