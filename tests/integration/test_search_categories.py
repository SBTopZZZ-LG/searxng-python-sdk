"""Integration tests: verify the parser correctly identifies result types per category."""

import os

import httpx
import pytest

from searxng_search.searxng_search import (
    Category,
    FileResult,
    GeneralOrNewsResult,
    ImageResult,
    ITResult,
    MapResult,
    MusicResult,
    ScienceResult,
    SearXNG,
    SearXNGBaseConfiguration,
    SearXNGSearchConfiguration,
    SocialMediaResult,
    VideoResult,
)


@pytest.mark.integration
async def test_general_results_parsed_correctly(searxng_client: SearXNG):
    """General category results are parsed as GeneralOrNewsResult."""
    response = await searxng_client.search(
        SearXNGSearchConfiguration(
            query="python",
            categories={Category.GENERAL},
        )
    )

    assert len(response.search_results) > 0
    assert all(isinstance(r, GeneralOrNewsResult) for r in response.search_results)


@pytest.mark.integration
async def test_news_results_parsed_correctly(searxng_client: SearXNG):
    """News category results are parsed as GeneralOrNewsResult."""
    response = await searxng_client.search(
        SearXNGSearchConfiguration(
            query="python",
            categories={Category.NEWS},
        )
    )

    assert len(response.search_results) > 0
    assert all(isinstance(r, GeneralOrNewsResult) for r in response.search_results)


@pytest.mark.integration
async def test_image_results_parsed_correctly(searxng_client: SearXNG):
    """Images category results are parsed as ImageResult."""
    response = await searxng_client.search(
        SearXNGSearchConfiguration(
            query="python",
            categories={Category.IMAGES},
        )
    )

    assert len(response.search_results) > 0
    assert all(isinstance(r, ImageResult) for r in response.search_results)


@pytest.mark.integration
async def test_video_results_parsed_correctly(searxng_client: SearXNG):
    """Videos category results are parsed as VideoResult."""
    response = await searxng_client.search(
        SearXNGSearchConfiguration(
            query="python tutorial",
            categories={Category.VIDEOS},
        )
    )

    assert len(response.search_results) > 0
    assert all(isinstance(r, VideoResult) for r in response.search_results)


@pytest.mark.integration
async def test_map_results_parsed_correctly(searxng_client: SearXNG):
    """Map category results are parsed as MapResult."""
    response = await searxng_client.search(
        SearXNGSearchConfiguration(
            query="New York",
            categories={Category.MAP},
        )
    )

    assert len(response.search_results) > 0
    assert all(isinstance(r, MapResult) for r in response.search_results)


@pytest.mark.integration
async def test_it_results_parsed_correctly(searxng_client: SearXNG):
    """IT category results are parsed as ITResult."""
    response = await searxng_client.search(
        SearXNGSearchConfiguration(
            query="python programming",
            categories={Category.IT},
        )
    )

    assert len(response.search_results) > 0
    assert all(isinstance(r, ITResult) for r in response.search_results)


@pytest.mark.integration
async def test_science_results_parsed_correctly(searxng_client: SearXNG):
    """Science category results are parsed as ScienceResult."""
    response = await searxng_client.search(
        SearXNGSearchConfiguration(
            query="quantum physics",
            categories={Category.SCIENCE},
        )
    )

    assert len(response.search_results) > 0
    assert all(isinstance(r, ScienceResult) for r in response.search_results)


@pytest.mark.integration
async def test_music_results_parsed_correctly(searxng_client: SearXNG):
    """Music category results are parsed as MusicResult."""
    response = await searxng_client.search(
        SearXNGSearchConfiguration(
            query="jazz",
            categories={Category.MUSIC},
        )
    )

    assert len(response.search_results) > 0
    # Music category may include video results (e.g. YouTube) alongside MusicResult
    assert any(isinstance(r, MusicResult) for r in response.search_results)
    assert all(
        isinstance(r, MusicResult | VideoResult) for r in response.search_results
    )


@pytest.mark.integration
async def test_file_results_parsed_correctly(searxng_client: SearXNG):
    """Files category results are parsed as FileResult."""
    response = await searxng_client.search(
        SearXNGSearchConfiguration(
            query="python pdf",
            categories={Category.FILES},
        )
    )

    assert len(response.search_results) > 0
    assert all(isinstance(r, FileResult) for r in response.search_results)


@pytest.mark.integration
async def test_social_media_results_parsed_correctly(searxng_client: SearXNG):
    """Social media category results are parsed as SocialMediaResult."""
    response = await searxng_client.search(
        SearXNGSearchConfiguration(
            query="python",
            categories={Category.SOCIAL_MEDIA},
        )
    )

    assert len(response.search_results) > 0
    assert all(isinstance(r, SocialMediaResult) for r in response.search_results)


@pytest.mark.integration
async def test_search_raises_on_timeout():
    """A near-zero timeout causes search() to raise httpx.RequestError."""
    base_url = os.environ.get("SEARXNG_BASE_URL", "http://localhost:8080")
    tiny_timeout_client = SearXNG(
        base_configuration=SearXNGBaseConfiguration(base_url=base_url, timeout=0.001)
    )

    with pytest.raises(httpx.RequestError):
        await tiny_timeout_client.search(SearXNGSearchConfiguration(query="python"))
