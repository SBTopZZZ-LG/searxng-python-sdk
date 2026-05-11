"""Tests for the search() method on the SearXNG class."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from searxng_search.searxng_search import (
    GeneralOrNewsResult,
    SearXNG,
    SearXNGBaseConfiguration,
    SearXNGResponse,
    SearXNGSearchConfiguration,
)

_MINIMAL_HTML = "<html><body></body></html>"

_ARTICLE_HTML = """
    <html><body>
        <article class="result">
            <a class="url_header" href="https://example.com/article">url</a>
            <h3><a href="https://example.com/article">My Title</a></h3>
        </article>
    </body></html>
"""


def _make_mock_response(
    status_code: int = 200,
    text: str = _MINIMAL_HTML,
    headers: dict | None = None,
) -> MagicMock:
    """Return a mock httpx.Response."""
    mock = MagicMock(spec=httpx.Response)
    mock.status_code = status_code
    mock.text = text
    mock.headers = httpx.Headers(headers or {"content-type": "text/html"})
    mock.raise_for_status = MagicMock()
    return mock


@pytest.fixture
def searxng_client() -> SearXNG:
    """Return a SearXNG client with a default base configuration."""
    return SearXNG(
        base_configuration=SearXNGBaseConfiguration(
            base_url="https://searxng.example.com"
        )
    )


@pytest.fixture
def searxng_client_with_user_agent() -> SearXNG:
    """Return a SearXNG client with a user agent configured."""
    return SearXNG(
        base_configuration=SearXNGBaseConfiguration(
            base_url="https://searxng.example.com",
            user_agent="TestBot/1.0",
        )
    )


# ---------------------------------------------------------------------------
# SearXNG.search
# ---------------------------------------------------------------------------


async def test_search_returns_searxng_response(searxng_client: SearXNG):
    """Test that search() returns a SearXNGResponse on a successful request."""
    mock_response = _make_mock_response()
    with patch("httpx.AsyncClient.get", new=AsyncMock(return_value=mock_response)):
        result = await searxng_client.search(SearXNGSearchConfiguration(query="python"))

    assert isinstance(result, SearXNGResponse)


async def test_search_response_contains_correct_fields(searxng_client: SearXNG):
    """Test that the returned SearXNGResponse has the correct status code, html, and url."""
    mock_response = _make_mock_response(
        status_code=200,
        text=_MINIMAL_HTML,
        headers={"content-type": "text/html; charset=utf-8"},
    )
    with patch("httpx.AsyncClient.get", new=AsyncMock(return_value=mock_response)):
        result = await searxng_client.search(SearXNGSearchConfiguration(query="python"))

    assert result.status_code == 200
    assert result.full_html == _MINIMAL_HTML
    assert "searxng.example.com" in result.search_url
    assert result.response_headers["content-type"] == "text/html; charset=utf-8"


async def test_search_parses_results_from_html(searxng_client: SearXNG):
    """Test that search() populates search_results by parsing the response HTML."""
    mock_response = _make_mock_response(text=_ARTICLE_HTML)
    with patch("httpx.AsyncClient.get", new=AsyncMock(return_value=mock_response)):
        result = await searxng_client.search(SearXNGSearchConfiguration(query="python"))

    assert len(result.search_results) == 1
    assert isinstance(result.search_results[0], GeneralOrNewsResult)


async def test_search_sends_no_headers_by_default(searxng_client: SearXNG):
    """Test that when no user_agent or custom_headers are set, headers=None is passed."""
    mock_get = AsyncMock(return_value=_make_mock_response())
    with patch("httpx.AsyncClient.get", new=mock_get):
        await searxng_client.search(SearXNGSearchConfiguration(query="python"))

    _, call_kwargs = mock_get.call_args
    assert call_kwargs.get("headers") is None


async def test_search_sends_user_agent_header(searxng_client_with_user_agent: SearXNG):
    """Test that user_agent from base_configuration is sent as User-Agent header."""
    mock_get = AsyncMock(return_value=_make_mock_response())
    with patch("httpx.AsyncClient.get", new=mock_get):
        await searxng_client_with_user_agent.search(
            SearXNGSearchConfiguration(query="python")
        )

    _, call_kwargs = mock_get.call_args
    assert call_kwargs["headers"]["User-Agent"] == "TestBot/1.0"


async def test_search_merges_user_agent_and_custom_headers(
    searxng_client_with_user_agent: SearXNG,
):
    """Test that custom_headers are merged on top of the User-Agent header."""
    mock_get = AsyncMock(return_value=_make_mock_response())
    with patch("httpx.AsyncClient.get", new=mock_get):
        await searxng_client_with_user_agent.search(
            SearXNGSearchConfiguration(
                query="python",
                custom_headers={"X-Custom": "value"},
            )
        )

    _, call_kwargs = mock_get.call_args
    assert call_kwargs["headers"]["User-Agent"] == "TestBot/1.0"
    assert call_kwargs["headers"]["X-Custom"] == "value"


async def test_search_sends_only_custom_headers_when_no_user_agent(
    searxng_client: SearXNG,
):
    """Test that custom_headers are passed directly when no user_agent is set."""
    mock_get = AsyncMock(return_value=_make_mock_response())
    with patch("httpx.AsyncClient.get", new=mock_get):
        await searxng_client.search(
            SearXNGSearchConfiguration(
                query="python",
                custom_headers={"X-Custom": "value"},
            )
        )

    _, call_kwargs = mock_get.call_args
    assert call_kwargs["headers"] == {"X-Custom": "value"}


async def test_search_raises_http_status_error_on_4xx(searxng_client: SearXNG):
    """Test that a 4xx response raises httpx.HTTPStatusError."""
    error_response = MagicMock(spec=httpx.Response)
    error_response.status_code = 404
    error_response.text = "Not Found"
    http_error = httpx.HTTPStatusError(
        "404", request=MagicMock(), response=error_response
    )
    mock_response = _make_mock_response()
    mock_response.raise_for_status.side_effect = http_error

    with patch("httpx.AsyncClient.get", new=AsyncMock(return_value=mock_response)):
        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            await searxng_client.search(SearXNGSearchConfiguration(query="python"))

    assert "404" in str(exc_info.value)


async def test_search_raises_request_error_on_network_failure(searxng_client: SearXNG):
    """Test that a network-level failure raises httpx.RequestError."""
    network_error = httpx.RequestError("Connection refused", request=MagicMock())
    with patch("httpx.AsyncClient.get", new=AsyncMock(side_effect=network_error)):
        with pytest.raises(httpx.RequestError) as exc_info:
            await searxng_client.search(SearXNGSearchConfiguration(query="python"))

    assert "Connection refused" in str(exc_info.value)


async def test_search_log_errors_decorator_logs_on_exception(searxng_client: SearXNG):
    """Test that the @log_errors decorator logs an error before re-raising."""
    network_error = httpx.RequestError("boom", request=MagicMock())
    with patch("httpx.AsyncClient.get", new=AsyncMock(side_effect=network_error)):
        with patch("searxng_search.searxng_search._logger.error") as mock_log_error:
            with pytest.raises(httpx.RequestError):
                await searxng_client.search(SearXNGSearchConfiguration(query="python"))

    mock_log_error.assert_called_once()


def _patch_async_client(mock_get: AsyncMock):
    """Patch httpx.AsyncClient so the constructor is inspectable and get() returns mock_get."""
    mock_instance = MagicMock()
    mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
    mock_instance.__aexit__ = AsyncMock(return_value=False)
    mock_instance.get = mock_get
    return patch(
        "searxng_search.searxng_search.httpx.AsyncClient", return_value=mock_instance
    )


async def test_search_passes_default_timeout_to_async_client(searxng_client: SearXNG):
    """Test that search() creates AsyncClient with the default 30.0s timeout."""
    mock_get = AsyncMock(return_value=_make_mock_response())
    with _patch_async_client(mock_get) as mock_client:
        await searxng_client.search(SearXNGSearchConfiguration(query="python"))

    mock_client.assert_called_once_with(timeout=30.0)


async def test_search_passes_custom_timeout_to_async_client():
    """Test that search() creates AsyncClient with a custom timeout from base config."""
    client = SearXNG(
        base_configuration=SearXNGBaseConfiguration(
            base_url="https://searxng.example.com",
            timeout=5.0,
        )
    )
    mock_get = AsyncMock(return_value=_make_mock_response())
    with _patch_async_client(mock_get) as mock_client:
        await client.search(SearXNGSearchConfiguration(query="python"))

    mock_client.assert_called_once_with(timeout=5.0)


async def test_search_passes_none_timeout_to_async_client():
    """Test that search() creates AsyncClient with timeout=None when configured."""
    client = SearXNG(
        base_configuration=SearXNGBaseConfiguration(
            base_url="https://searxng.example.com",
            timeout=None,
        )
    )
    mock_get = AsyncMock(return_value=_make_mock_response())
    with _patch_async_client(mock_get) as mock_client:
        await client.search(SearXNGSearchConfiguration(query="python"))

    mock_client.assert_called_once_with(timeout=None)


# ---------------------------------------------------------------------------
# Rate limiting (HTTP 429)
# ---------------------------------------------------------------------------


def _make_429_response() -> MagicMock:
    """Return a mock httpx.Response with status 429 that raises HTTPStatusError."""
    request_mock = MagicMock()
    mock = MagicMock(spec=httpx.Response)
    mock.status_code = 429
    mock.text = "Too Many Requests"
    mock.headers = httpx.Headers({"content-type": "text/html"})
    mock.raise_for_status.side_effect = httpx.HTTPStatusError(
        "429", request=request_mock, response=mock
    )
    return mock


async def test_search_raises_immediately_on_429_when_handle_rate_limiting_disabled():
    """Test that a 429 raises immediately without retrying when handle_rate_limiting=False."""
    client = SearXNG(
        base_configuration=SearXNGBaseConfiguration(
            base_url="https://searxng.example.com",
            handle_rate_limiting=False,
        )
    )
    mock_get = AsyncMock(return_value=_make_429_response())
    with _patch_async_client(mock_get):
        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            await client.search(SearXNGSearchConfiguration(query="python"))

    assert "429" in str(exc_info.value)
    assert mock_get.call_count == 1


async def test_search_retries_on_429_and_raises_after_all_retries_exhausted(
    searxng_client: SearXNG,
):
    """Test that search() performs 3 retries on 429 then raises HTTPStatusError."""
    mock_get = AsyncMock(return_value=_make_429_response())
    mock_sleep = AsyncMock()
    with _patch_async_client(mock_get):
        with patch("searxng_search.searxng_search.asyncio.sleep", new=mock_sleep):
            with pytest.raises(httpx.HTTPStatusError) as exc_info:
                await searxng_client.search(SearXNGSearchConfiguration(query="python"))

    assert "429" in str(exc_info.value)
    assert mock_get.call_count == 4  # 1 initial + 3 retries
    assert mock_sleep.call_count == 3  # slept before each retry


async def test_search_retries_on_429_and_succeeds_on_later_attempt(
    searxng_client: SearXNG,
):
    """Test that search() retries on 429 and returns a result on a subsequent success."""
    mock_get = AsyncMock(side_effect=[_make_429_response(), _make_mock_response()])
    with _patch_async_client(mock_get):
        with patch("searxng_search.searxng_search.asyncio.sleep", new=AsyncMock()):
            result = await searxng_client.search(
                SearXNGSearchConfiguration(query="python")
            )

    assert isinstance(result, SearXNGResponse)
    assert mock_get.call_count == 2


async def test_search_uses_correct_base_delays_on_429_retries(
    searxng_client: SearXNG,
):
    """Test that retry delays use base values of 10s, 15s, 20s (jitter zeroed out)."""
    mock_get = AsyncMock(return_value=_make_429_response())
    mock_sleep = AsyncMock()
    with _patch_async_client(mock_get):
        with patch("searxng_search.searxng_search.asyncio.sleep", new=mock_sleep):
            with patch(
                "searxng_search.searxng_search.random.uniform", return_value=0.0
            ):
                with pytest.raises(httpx.HTTPStatusError):
                    await searxng_client.search(
                        SearXNGSearchConfiguration(query="python")
                    )

    sleep_delays = [call.args[0] for call in mock_sleep.call_args_list]
    assert sleep_delays == [10.0, 15.0, 20.0]
