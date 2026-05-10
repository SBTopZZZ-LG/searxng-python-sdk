"""Shared fixtures for integration tests."""

import asyncio
import os

import pytest

from searxng_search.searxng_search import SearXNG, SearXNGBaseConfiguration

_DEFAULT_BASE_URL = "http://localhost:8080"


@pytest.fixture(scope="session")
def searxng_client() -> SearXNG:
    """Return a SearXNG client pointed at the live instance.

    Override the base URL by setting the SEARXNG_BASE_URL environment variable.
    """
    base_url = os.environ.get("SEARXNG_BASE_URL", _DEFAULT_BASE_URL)
    return SearXNG(base_configuration=SearXNGBaseConfiguration(base_url=base_url))


@pytest.fixture(autouse=True)
async def rate_limit_delay():
    """Pause for one second after each integration test to avoid tripping rate limits."""
    yield
    await asyncio.sleep(1)
