"""Tests for HTML parser methods on the SearXNG class."""

import pytest
from bs4 import BeautifulSoup, Tag

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


def _make_article(html: str) -> Tag:
    """Parse an HTML snippet and return the first Tag element."""
    return BeautifulSoup(html, "html.parser").find(True)  # type: ignore


def _make_article_in_container(html: str) -> Tag:
    """Wrap the article in a div so child combinators (> p) work correctly."""
    soup = BeautifulSoup(f"<div>{html}</div>", "html.parser")
    return soup.find("article")  # type: ignore


# ---------------------------------------------------------------------------
# SearXNG._parse_general_or_news
# ---------------------------------------------------------------------------


def test_parse_general_or_news_returns_none_when_url_tag_missing(
    searxng_client: SearXNG,
):
    """Test that _parse_general_or_news returns None when a.url_header is absent."""
    article = _make_article(
        '<article><h3><a href="https://example.com">Title</a></h3></article>'
    )
    assert searxng_client._parse_general_or_news(article) is None  # pylint: disable=protected-access


def test_parse_general_or_news_returns_none_when_title_tag_missing(
    searxng_client: SearXNG,
):
    """Test that _parse_general_or_news returns None when h3 a is absent."""
    article = _make_article(
        '<article><a class="url_header" href="https://example.com">url</a></article>'
    )
    assert searxng_client._parse_general_or_news(article) is None  # pylint: disable=protected-access


def test_parse_general_or_news_returns_result_with_all_optional_fields(
    searxng_client: SearXNG,
):
    """Test that _parse_general_or_news returns a fully populated GeneralOrNewsResult."""
    article = _make_article("""
        <article>
            <a class="url_header" href="https://example.com/article">url</a>
            <h3><a href="https://example.com/article">My Title</a></h3>
            <p class="content">Some description</p>
            <div class="highlight">Jane Doe</div>
            <time class="published_date" datetime="2024-01-15">Jan 15, 2024</time>
        </article>
    """)
    result = searxng_client._parse_general_or_news(article)  # pylint: disable=protected-access

    assert isinstance(result, GeneralOrNewsResult)
    assert result.category == "general-or-news"
    assert result.url == "https://example.com/article"
    assert result.title == "My Title"
    assert result.description == "Some description"
    assert result.author == "Jane Doe"
    assert result.timestamp == "2024-01-15"


def test_parse_general_or_news_optional_fields_are_none_when_absent(
    searxng_client: SearXNG,
):
    """Test that description, author, and timestamp are None when their tags are absent."""
    article = _make_article("""
        <article>
            <a class="url_header" href="https://example.com/article">url</a>
            <h3><a href="https://example.com/article">My Title</a></h3>
        </article>
    """)
    result = searxng_client._parse_general_or_news(article)  # pylint: disable=protected-access

    assert isinstance(result, GeneralOrNewsResult)
    assert result.description is None
    assert result.author is None
    assert result.timestamp is None


def test_parse_general_or_news_timestamp_falls_back_to_text_when_no_datetime_attr(
    searxng_client: SearXNG,
):
    """Test that timestamp uses tag text when the datetime attribute is absent."""
    article = _make_article("""
        <article>
            <a class="url_header" href="https://example.com/article">url</a>
            <h3><a href="https://example.com/article">My Title</a></h3>
            <time class="published_date">Jan 15, 2024</time>
        </article>
    """)
    result = searxng_client._parse_general_or_news(article)  # pylint: disable=protected-access

    assert isinstance(result, GeneralOrNewsResult)
    assert result.timestamp == "Jan 15, 2024"


# ---------------------------------------------------------------------------
# SearXNG._parse_images
# ---------------------------------------------------------------------------


def test_parse_images_returns_none_when_url_tag_missing(searxng_client: SearXNG):
    """Test that _parse_images returns None when a[href] is absent."""
    article = _make_article('<article><span class="title">Title</span></article>')
    assert searxng_client._parse_images(article) is None  # pylint: disable=protected-access


def test_parse_images_returns_none_when_title_tag_missing(searxng_client: SearXNG):
    """Test that _parse_images returns None when span.title is absent."""
    article = _make_article(
        '<article><a href="https://example.com/img.jpg">link</a></article>'
    )
    assert searxng_client._parse_images(article) is None  # pylint: disable=protected-access


def test_parse_images_returns_result_with_all_optional_fields(searxng_client: SearXNG):
    """Test that _parse_images returns a fully populated ImageResult."""
    article = _make_article("""
        <article>
            <a href="https://example.com/img.jpg">link</a>
            <span class="title">A Photo</span>
            <span class="source">example.com</span>
            <span class="image_resolution">1920x1080</span>
            <img class="image_thumbnail" src="https://example.com/thumb.jpg" />
        </article>
    """)
    result = searxng_client._parse_images(article)  # pylint: disable=protected-access

    assert isinstance(result, ImageResult)
    assert result.category == "images"
    assert result.url == "https://example.com/img.jpg"
    assert result.title == "A Photo"
    assert result.description == "example.com"
    assert result.image_url == "https://example.com/img.jpg"
    assert result.thumbnail_url == "https://example.com/thumb.jpg"
    assert result.image_resolution == "1920x1080"


def test_parse_images_optional_fields_are_none_when_absent(searxng_client: SearXNG):
    """Test that description, thumbnail_url, and image_resolution are None when absent."""
    article = _make_article("""
        <article>
            <a href="https://example.com/img.jpg">link</a>
            <span class="title">A Photo</span>
        </article>
    """)
    result = searxng_client._parse_images(article)  # pylint: disable=protected-access

    assert isinstance(result, ImageResult)
    assert result.description is None
    assert result.thumbnail_url is None
    assert result.image_resolution is None


# ---------------------------------------------------------------------------
# SearXNG._parse_videos
# ---------------------------------------------------------------------------


def test_parse_videos_returns_none_when_url_tag_missing(searxng_client: SearXNG):
    """Test that _parse_videos returns None when a.url_header is absent."""
    article = _make_article_in_container(
        '<article><h3><a href="https://example.com">Title</a></h3></article>'
    )
    assert searxng_client._parse_videos(article) is None  # pylint: disable=protected-access


def test_parse_videos_returns_none_when_title_tag_missing(searxng_client: SearXNG):
    """Test that _parse_videos returns None when h3 a is absent."""
    article = _make_article_in_container(
        '<article><a class="url_header" href="https://example.com/v">url</a></article>'
    )
    assert searxng_client._parse_videos(article) is None  # pylint: disable=protected-access


def test_parse_videos_returns_result_with_all_optional_fields(searxng_client: SearXNG):
    """Test that _parse_videos returns a fully populated VideoResult."""
    article = _make_article_in_container("""
        <article>
            <a class="url_header" href="https://example.com/video">url</a>
            <h3><a href="https://example.com/video">My Video</a></h3>
            <p>intro</p>
            <p>Video description</p>
            <img class="thumbnail" src="https://example.com/thumb.jpg" />
            <span class="thumbnail_length">10:30</span>
            <div class="highlight">Channel Name</div>
        </article>
    """)
    result = searxng_client._parse_videos(article)  # pylint: disable=protected-access

    assert isinstance(result, VideoResult)
    assert result.category == "videos"
    assert result.url == "https://example.com/video"
    assert result.title == "My Video"
    assert result.description == "Video description"
    assert result.video_thumbnail_url == "https://example.com/thumb.jpg"
    assert result.video_length == "10:30"
    assert result.author == "Channel Name"


def test_parse_videos_optional_fields_are_none_when_absent(searxng_client: SearXNG):
    """Test that optional video fields are None when their tags are absent."""
    article = _make_article_in_container("""
        <article>
            <a class="url_header" href="https://example.com/video">url</a>
            <h3><a href="https://example.com/video">My Video</a></h3>
        </article>
    """)
    result = searxng_client._parse_videos(article)  # pylint: disable=protected-access

    assert isinstance(result, VideoResult)
    assert result.description is None
    assert result.video_thumbnail_url is None
    assert result.video_length is None
    assert result.author is None


# ---------------------------------------------------------------------------
# SearXNG._parse_map
# ---------------------------------------------------------------------------


def test_parse_map_returns_none_when_url_tag_missing(searxng_client: SearXNG):
    """Test that _parse_map returns None when a.url_header is absent."""
    article = _make_article(
        '<article><h3><a href="https://example.com">Title</a></h3></article>'
    )
    assert searxng_client._parse_map(article) is None  # pylint: disable=protected-access


def test_parse_map_returns_none_when_title_tag_missing(searxng_client: SearXNG):
    """Test that _parse_map returns None when h3 a is absent."""
    article = _make_article(
        '<article><a class="url_header" href="https://maps.example.com">url</a></article>'
    )
    assert searxng_client._parse_map(article) is None  # pylint: disable=protected-access


def test_parse_map_returns_result_with_description(searxng_client: SearXNG):
    """Test that _parse_map returns a fully populated MapResult."""
    article = _make_article("""
        <article>
            <a class="url_header" href="https://maps.example.com/place">url</a>
            <h3><a href="https://maps.example.com/place">Central Park</a></h3>
            <table><tbody><tr><td>New York, NY</td></tr></tbody></table>
        </article>
    """)
    result = searxng_client._parse_map(article)  # pylint: disable=protected-access

    assert isinstance(result, MapResult)
    assert result.category == "map"
    assert result.url == "https://maps.example.com/place"
    assert result.title == "Central Park"
    assert result.description == "New York, NY"


def test_parse_map_description_is_none_when_absent(searxng_client: SearXNG):
    """Test that description is None when the table cell is absent."""
    article = _make_article("""
        <article>
            <a class="url_header" href="https://maps.example.com/place">url</a>
            <h3><a href="https://maps.example.com/place">Central Park</a></h3>
        </article>
    """)
    result = searxng_client._parse_map(article)  # pylint: disable=protected-access

    assert isinstance(result, MapResult)
    assert result.description is None


# ---------------------------------------------------------------------------
# SearXNG._parse_it
# ---------------------------------------------------------------------------


def test_parse_it_returns_none_when_url_tag_missing(searxng_client: SearXNG):
    """Test that _parse_it returns None when a.url_header is absent."""
    article = _make_article(
        '<article><h3><a href="https://example.com">Title</a></h3></article>'
    )
    assert searxng_client._parse_it(article) is None  # pylint: disable=protected-access


def test_parse_it_returns_none_when_title_tag_missing(searxng_client: SearXNG):
    """Test that _parse_it returns None when h3 a is absent."""
    article = _make_article(
        '<article><a class="url_header" href="https://example.com">url</a></article>'
    )
    assert searxng_client._parse_it(article) is None  # pylint: disable=protected-access


def test_parse_it_returns_result_with_all_optional_fields(searxng_client: SearXNG):
    """Test that _parse_it returns a fully populated ITResult."""
    article = _make_article("""
        <article>
            <a class="url_header" href="https://github.com/repo">url</a>
            <h3><a href="https://github.com/repo">Some Repo</a></h3>
            <p class="content">A useful library</p>
            <div class="highlight">octocat</div>
            <time datetime="2024-03-01">Mar 1, 2024</time>
        </article>
    """)
    result = searxng_client._parse_it(article)  # pylint: disable=protected-access

    assert isinstance(result, ITResult)
    assert result.category == "it"
    assert result.url == "https://github.com/repo"
    assert result.title == "Some Repo"
    assert result.description == "A useful library"
    assert result.author == "octocat"
    assert result.timestamp == "2024-03-01"


def test_parse_it_optional_fields_are_none_when_absent(searxng_client: SearXNG):
    """Test that optional IT fields are None when their tags are absent."""
    article = _make_article("""
        <article>
            <a class="url_header" href="https://github.com/repo">url</a>
            <h3><a href="https://github.com/repo">Some Repo</a></h3>
        </article>
    """)
    result = searxng_client._parse_it(article)  # pylint: disable=protected-access

    assert isinstance(result, ITResult)
    assert result.description is None
    assert result.author is None
    assert result.timestamp is None


def test_parse_it_timestamp_falls_back_to_text_when_no_datetime_attr(
    searxng_client: SearXNG,
):
    """Test that IT timestamp uses tag text when the datetime attribute is absent."""
    article = _make_article("""
        <article>
            <a class="url_header" href="https://github.com/repo">url</a>
            <h3><a href="https://github.com/repo">Some Repo</a></h3>
            <time>Mar 1, 2024</time>
        </article>
    """)
    result = searxng_client._parse_it(article)  # pylint: disable=protected-access

    assert isinstance(result, ITResult)
    assert result.timestamp == "Mar 1, 2024"


# ---------------------------------------------------------------------------
# SearXNG._parse_science
# ---------------------------------------------------------------------------


def test_parse_science_returns_none_when_url_tag_missing(searxng_client: SearXNG):
    """Test that _parse_science returns None when a is absent."""
    article = _make_article("<article><h3>Title</h3></article>")
    assert searxng_client._parse_science(article) is None  # pylint: disable=protected-access


def test_parse_science_returns_none_when_title_tag_missing(searxng_client: SearXNG):
    """Test that _parse_science returns None when both h3 and h2 are absent."""
    article = _make_article(
        '<article><a href="https://example.com/paper">link</a></article>'
    )
    assert searxng_client._parse_science(article) is None  # pylint: disable=protected-access


def test_parse_science_returns_result_with_h3_title(searxng_client: SearXNG):
    """Test that _parse_science uses h3 as the title tag."""
    article = _make_article("""
        <article>
            <a href="https://example.com/paper">link</a>
            <h3>Research Paper</h3>
            <p>Abstract text here</p>
        </article>
    """)
    result = searxng_client._parse_science(article)  # pylint: disable=protected-access

    assert isinstance(result, ScienceResult)
    assert result.category == "science"
    assert result.url == "https://example.com/paper"
    assert result.title == "Research Paper"
    assert result.description == "Abstract text here"


def test_parse_science_falls_back_to_h2_when_h3_missing(searxng_client: SearXNG):
    """Test that _parse_science falls back to h2 when h3 is absent."""
    article = _make_article("""
        <article>
            <a href="https://example.com/paper">link</a>
            <h2>Research Paper H2</h2>
        </article>
    """)
    result = searxng_client._parse_science(article)  # pylint: disable=protected-access

    assert isinstance(result, ScienceResult)
    assert result.title == "Research Paper H2"


def test_parse_science_description_is_none_when_absent(searxng_client: SearXNG):
    """Test that description is None when no p tag is present."""
    article = _make_article("""
        <article>
            <a href="https://example.com/paper">link</a>
            <h3>Research Paper</h3>
        </article>
    """)
    result = searxng_client._parse_science(article)  # pylint: disable=protected-access

    assert isinstance(result, ScienceResult)
    assert result.description is None


# ---------------------------------------------------------------------------
# SearXNG._parse_music
# ---------------------------------------------------------------------------


def test_parse_music_returns_none_when_url_tag_missing(searxng_client: SearXNG):
    """Test that _parse_music returns None when a.url_header is absent."""
    article = _make_article(
        '<article><h3><a href="https://example.com">Title</a></h3></article>'
    )
    assert searxng_client._parse_music(article) is None  # pylint: disable=protected-access


def test_parse_music_returns_none_when_title_tag_missing(searxng_client: SearXNG):
    """Test that _parse_music returns None when h3 a is absent."""
    article = _make_article(
        '<article><a class="url_header" href="https://example.com/song">url</a></article>'
    )
    assert searxng_client._parse_music(article) is None  # pylint: disable=protected-access


def test_parse_music_returns_result_with_all_optional_fields(searxng_client: SearXNG):
    """Test that _parse_music returns a fully populated MusicResult."""
    article = _make_article("""
        <article>
            <a class="url_header" href="https://example.com/song">url</a>
            <h3><a href="https://example.com/song">Great Song</a></h3>
            <p class="content">Album: Greatest Hits</p>
            <div class="highlight">The Artist</div>
            <time datetime="2023-06-01">Jun 1, 2023</time>
            <img class="thumbnail" src="https://example.com/cover.jpg" />
        </article>
    """)
    result = searxng_client._parse_music(article)  # pylint: disable=protected-access

    assert isinstance(result, MusicResult)
    assert result.category == "music"
    assert result.url == "https://example.com/song"
    assert result.title == "Great Song"
    assert result.description == "Album: Greatest Hits"
    assert result.artist == "The Artist"
    assert result.timestamp == "2023-06-01"
    assert result.music_video_thumbnail_url == "https://example.com/cover.jpg"


def test_parse_music_optional_fields_are_none_when_absent(searxng_client: SearXNG):
    """Test that optional music fields are None when their tags are absent."""
    article = _make_article("""
        <article>
            <a class="url_header" href="https://example.com/song">url</a>
            <h3><a href="https://example.com/song">Great Song</a></h3>
        </article>
    """)
    result = searxng_client._parse_music(article)  # pylint: disable=protected-access

    assert isinstance(result, MusicResult)
    assert result.description is None
    assert result.artist is None
    assert result.timestamp is None
    assert result.music_video_thumbnail_url is None


def test_parse_music_timestamp_falls_back_to_text_when_no_datetime_attr(
    searxng_client: SearXNG,
):
    """Test that music timestamp uses tag text when the datetime attribute is absent."""
    article = _make_article("""
        <article>
            <a class="url_header" href="https://example.com/song">url</a>
            <h3><a href="https://example.com/song">Great Song</a></h3>
            <time>Jun 1, 2023</time>
        </article>
    """)
    result = searxng_client._parse_music(article)  # pylint: disable=protected-access

    assert isinstance(result, MusicResult)
    assert result.timestamp == "Jun 1, 2023"


# ---------------------------------------------------------------------------
# SearXNG._parse_files
# ---------------------------------------------------------------------------


def test_parse_files_returns_none_when_url_tag_missing(searxng_client: SearXNG):
    """Test that _parse_files returns None when a.url_header is absent."""
    article = _make_article(
        '<article><h3><a href="https://example.com">Title</a></h3></article>'
    )
    assert searxng_client._parse_files(article) is None  # pylint: disable=protected-access


def test_parse_files_returns_none_when_title_tag_missing(searxng_client: SearXNG):
    """Test that _parse_files returns None when h3 a is absent."""
    article = _make_article(
        '<article><a class="url_header" href="https://example.com/file.pdf">url</a></article>'
    )
    assert searxng_client._parse_files(article) is None  # pylint: disable=protected-access


def test_parse_files_returns_result_with_all_optional_fields(searxng_client: SearXNG):
    """Test that _parse_files returns a fully populated FileResult."""
    article = _make_article("""
        <article>
            <a class="url_header" href="https://example.com/file.pdf">url</a>
            <h3><a href="https://example.com/file.pdf">My Document</a></h3>
            <p class="content">A PDF document</p>
            <time datetime="2024-02-10">Feb 10, 2024</time>
            <img src="https://example.com/preview.jpg" />
        </article>
    """)
    result = searxng_client._parse_files(article)  # pylint: disable=protected-access

    assert isinstance(result, FileResult)
    assert result.category == "files"
    assert result.url == "https://example.com/file.pdf"
    assert result.title == "My Document"
    assert result.description == "A PDF document"
    assert result.file_url == "https://example.com/file.pdf"
    assert result.file_thumbnail_url == "https://example.com/preview.jpg"
    assert result.timestamp == "2024-02-10"


def test_parse_files_optional_fields_are_none_when_absent(searxng_client: SearXNG):
    """Test that optional file fields are None when their tags are absent."""
    article = _make_article("""
        <article>
            <a class="url_header" href="https://example.com/file.pdf">url</a>
            <h3><a href="https://example.com/file.pdf">My Document</a></h3>
        </article>
    """)
    result = searxng_client._parse_files(article)  # pylint: disable=protected-access

    assert isinstance(result, FileResult)
    assert result.description is None
    assert result.file_thumbnail_url is None
    assert result.timestamp is None


def test_parse_files_timestamp_falls_back_to_text_when_no_datetime_attr(
    searxng_client: SearXNG,
):
    """Test that file timestamp uses tag text when the datetime attribute is absent."""
    article = _make_article("""
        <article>
            <a class="url_header" href="https://example.com/file.pdf">url</a>
            <h3><a href="https://example.com/file.pdf">My Document</a></h3>
            <time>Feb 10, 2024</time>
        </article>
    """)
    result = searxng_client._parse_files(article)  # pylint: disable=protected-access

    assert isinstance(result, FileResult)
    assert result.timestamp == "Feb 10, 2024"


# ---------------------------------------------------------------------------
# SearXNG._parse_social_media
# ---------------------------------------------------------------------------


def test_parse_social_media_returns_none_when_url_tag_missing(searxng_client: SearXNG):
    """Test that _parse_social_media returns None when a.url_header is absent."""
    article = _make_article("<article><h3>Title</h3></article>")
    assert searxng_client._parse_social_media(article) is None  # pylint: disable=protected-access


def test_parse_social_media_returns_none_when_title_tag_missing(
    searxng_client: SearXNG,
):
    """Test that _parse_social_media returns None when both h3 variants are absent."""
    article = _make_article(
        '<article><a class="url_header" href="https://example.com/post">url</a></article>'
    )
    assert searxng_client._parse_social_media(article) is None  # pylint: disable=protected-access


def test_parse_social_media_returns_result_with_all_optional_fields(
    searxng_client: SearXNG,
):
    """Test that _parse_social_media returns a fully populated SocialMediaResult."""
    article = _make_article("""
        <article>
            <a class="url_header" href="https://example.com/post">url</a>
            <h3>Post Title</h3>
            <p class="content">Post content here</p>
            <time datetime="2024-04-20">Apr 20, 2024</time>
            <img class="image_thumbnail" src="https://example.com/thumb.jpg" />
        </article>
    """)
    result = searxng_client._parse_social_media(article)  # pylint: disable=protected-access

    assert isinstance(result, SocialMediaResult)
    assert result.category == "social-media"
    assert result.url == "https://example.com/post"
    assert result.title == "Post Title"
    assert result.description == "Post content here"
    assert result.thumbnail_url == "https://example.com/thumb.jpg"
    assert result.timestamp == "2024-04-20"


def test_parse_social_media_optional_fields_are_none_when_absent(
    searxng_client: SearXNG,
):
    """Test that optional social media fields are None when their tags are absent."""
    article = _make_article("""
        <article>
            <a class="url_header" href="https://example.com/post">url</a>
            <h3>Post Title</h3>
        </article>
    """)
    result = searxng_client._parse_social_media(article)  # pylint: disable=protected-access

    assert isinstance(result, SocialMediaResult)
    assert result.description is None
    assert result.thumbnail_url is None
    assert result.timestamp is None


def test_parse_social_media_timestamp_falls_back_to_text_when_no_datetime_attr(
    searxng_client: SearXNG,
):
    """Test that social media timestamp uses tag text when the datetime attribute is absent."""
    article = _make_article("""
        <article>
            <a class="url_header" href="https://example.com/post">url</a>
            <h3>Post Title</h3>
            <time>Apr 20, 2024</time>
        </article>
    """)
    result = searxng_client._parse_social_media(article)  # pylint: disable=protected-access

    assert isinstance(result, SocialMediaResult)
    assert result.timestamp == "Apr 20, 2024"


def test_parse_social_media_title_from_h3_anchor_when_present(
    searxng_client: SearXNG,
):
    """Test that _parse_social_media uses the h3 a text when an anchor is present inside h3."""
    article = _make_article("""
        <article>
            <a class="url_header" href="https://example.com/post">url</a>
            <h3><a href="https://example.com/post">Linked Title</a></h3>
        </article>
    """)
    result = searxng_client._parse_social_media(article)  # pylint: disable=protected-access

    assert isinstance(result, SocialMediaResult)
    assert result.title == "Linked Title"
