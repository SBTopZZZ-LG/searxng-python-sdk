"""Integration tests: rate limiting retry logic using a controlled mock HTTP server.

Each test spins up a real TCP server in a background thread. The server returns 429
for the first ``fail_count`` requests, then returns a minimal valid 200 response.
``asyncio.sleep`` is patched to a no-op so the tests stay fast.
"""

import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from searxng_search.searxng_search import (
    SearXNG,
    SearXNGBaseConfiguration,
    SearXNGSearchConfiguration,
)

_MINIMAL_HTML = b"<html><body></body></html>"


class _RateLimitHandler(BaseHTTPRequestHandler):
    """Serves 429 for the first ``server._fail_count`` requests, then 200."""

    def log_message(self, format, *args):  # pylint: disable=arguments-differ,redefined-builtin
        pass  # silence request logs in test output

    def do_GET(self):  # pylint: disable=invalid-name
        """Handle GET requests with rate limiting logic based on server state."""

        with self.server._lock:  # type: ignore # pylint: disable=protected-access
            count = self.server._request_count  # type: ignore # pylint: disable=protected-access
            self.server._request_count += 1  # type: ignore

        if count < self.server._fail_count:  # type: ignore # pylint: disable=protected-access
            self.send_response(429)
            self.end_headers()
            self.wfile.write(b"Too Many Requests")
        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(_MINIMAL_HTML)))
            self.end_headers()
            self.wfile.write(_MINIMAL_HTML)


def _start_server(fail_count: int) -> HTTPServer:
    """Bind an HTTPServer to a free port and serve in a daemon thread."""
    server = HTTPServer(("127.0.0.1", 0), _RateLimitHandler)
    server._lock = threading.Lock()  # type: ignore # pylint: disable=protected-access
    server._request_count = 0  # type: ignore # pylint: disable=protected-access
    server._fail_count = fail_count  # type: ignore # pylint: disable=protected-access
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


@pytest.fixture
def make_client_and_server():
    """
    Factory fixture that creates a mock server + SearXNG client pair.

    Usage::

        client, server = make_client_and_server(fail_count=2)
        client, server = make_client_and_server(
            fail_count=999, handle_rate_limiting=False
        )

    All servers are shut down automatically after the test.
    """
    servers: list[HTTPServer] = []

    def _factory(
        fail_count: int,
        handle_rate_limiting: bool = True,
    ) -> tuple[SearXNG, HTTPServer]:
        server = _start_server(fail_count)
        servers.append(server)
        port = server.server_address[1]
        client = SearXNG(
            base_configuration=SearXNGBaseConfiguration(
                base_url=f"http://127.0.0.1:{port}",
                handle_rate_limiting=handle_rate_limiting,
            )
        )
        return client, server

    yield _factory

    for s in servers:
        s.shutdown()


async def test_rate_limiting_retries_and_succeeds(make_client_and_server):
    """search() retries on 429 and returns a result when the server eventually responds 200."""
    client, server = make_client_and_server(fail_count=2)

    with patch("searxng_search.searxng_search.asyncio.sleep", new=AsyncMock()):
        result = await client.search(SearXNGSearchConfiguration(query="python"))

    assert result.status_code == 200
    assert (
        server._request_count == 3  # pylint: disable=protected-access
    )  # 2 × 429 then 1 × 200


async def test_rate_limiting_raises_after_all_retries_exhausted(make_client_and_server):
    """search() raises HTTPStatusError with a 429 response after exhausting all 3 retries."""
    client, server = make_client_and_server(fail_count=999)  # always 429

    with patch("searxng_search.searxng_search.asyncio.sleep", new=AsyncMock()):
        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            await client.search(SearXNGSearchConfiguration(query="python"))

    assert exc_info.value.response.status_code == 429
    assert (
        server._request_count == 4  # pylint: disable=protected-access
    )  # 1 initial + 3 retries


async def test_rate_limiting_disabled_raises_immediately_on_429(make_client_and_server):
    """search() raises immediately on the first 429 when handle_rate_limiting=False."""
    client, server = make_client_and_server(fail_count=999, handle_rate_limiting=False)

    with pytest.raises(httpx.HTTPStatusError) as exc_info:
        await client.search(SearXNGSearchConfiguration(query="python"))

    assert exc_info.value.response.status_code == 429
    assert server._request_count == 1  # no retries # pylint: disable=protected-access
