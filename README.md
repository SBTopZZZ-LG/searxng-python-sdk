# searxng-python-sdk

[![CI](https://github.com/SBTopZZZ-LG/searxng-python-sdk/actions/workflows/ci.yml/badge.svg)](https://github.com/SBTopZZZ-LG/searxng-python-sdk/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/SBTopZZZ-LG/searxng-python-sdk/graph/badge.svg?token=K5EmyPXCmA)](https://codecov.io/gh/SBTopZZZ-LG/searxng-python-sdk)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-%3E%3D3.11-blue)](https://www.python.org/)
[![Latest Release](https://img.shields.io/github/v/tag/SBTopZZZ-LG/searxng-python-sdk?label=release)](https://github.com/SBTopZZZ-LG/searxng-python-sdk/tags)

An unofficial Python SDK for interacting with [SearXNG](https://github.com/searxng/searxng) instances. Provides a simple async interface for querying any self-hosted SearXNG instance and receiving structured, typed search results.

---

## Installation

**Latest version**

```bash
pip install git+https://github.com/SBTopZZZ-LG/searxng-python-sdk.git@latest
```

**Pinned to a specific version**

```bash
pip install git+https://github.com/SBTopZZZ-LG/searxng-python-sdk.git@v1.0.0
```

---

## Usage

```python
import asyncio
from searxng_search import SearXNG, SearXNGBaseConfiguration, SearXNGSearchConfiguration, Category

async def main():
    client = SearXNG(
        base_configuration=SearXNGBaseConfiguration(
            base_url="http://localhost:8080",  # replace with your SearXNG instance URL
        )
    )

    response = await client.search(
        SearXNGSearchConfiguration(
            query="python",
            categories={Category.GENERAL},
        )
    )
    print(response.search_results)

asyncio.run(main())
```

---

## Reference

### `SearXNGBaseConfiguration`

| Property | Type | Default | Description |
|---|---|---|---|
| `base_url` | `str` | — | Base URL of the SearXNG instance |
| `user_agent` | `str \| None` | `None` | Custom `User-Agent` header |
| `timeout` | `float \| None` | `30.0` | Request timeout in seconds |
| `handle_rate_limiting` | `bool` | `True` | Auto-retry on HTTP 429 with backoff (3 attempts: 10 s, 15 s, 20 s ± 2 s jitter) |

### `SearXNGSearchConfiguration`

| Property | Type | Description |
|---|---|---|
| `query` | `str` | Search query (required, min length 1) |
| `categories` | `set[Category \| str] \| None` | Categories to search within |
| `engines` | `set[str] \| None` | Engines to use |
| `page_number` | `int \| None` | Page number for pagination |
| `time_range` | `TimeRange \| str \| None` | Filter by time (`day`, `month`, `year`) |
| `safe_search` | `SafeSearch \| int \| None` | Safe search level (`0` off, `1` moderate, `2` strict) |
| `autocomplete` | `set[Autocomplete \| str] \| None` | Autocomplete providers |
| `image_proxy` | `bool \| None` | Enable image proxying |
| `results_on_new_tab` | `bool \| None` | Open results in a new tab |
| `theme` | `set[Theme \| str] \| None` | UI theme to use (`simple`, `oscar`, `auto`) |
| `enabled_plugins` / `disabled_plugins` | `set[Plugins \| str] \| None` | Plugins to enable/disable |
| `enabled_engines` / `disabled_engines` | `set[str] \| None` | Engines to enable/disable |
| `custom_params` | `dict[str, str] \| None` | Extra query parameters appended to the URL |
| `custom_headers` | `dict[str, str] \| None` | Extra HTTP headers sent with the request |

> **`engines` vs `enabled_engines`/`disabled_engines`**: `engines` selects which engines are active for a specific query. `enabled_engines`/`disabled_engines` toggle engines on or off relative to the instance's default configuration.

### `SearXNGResponse`

| Property | Type | Description |
|---|---|---|
| `search_url` | `str` | Final URL used for the request |
| `status_code` | `int` | HTTP status code |
| `response_headers` | `dict[str, str]` | Response headers |
| `full_html` | `str` | Raw HTML of the response page |
| `search_results` | `list[...]` | Parsed, typed search results |

### Errors

`search()` raises the following exceptions:

| Exception | When |
|---|---|
| `httpx.HTTPStatusError` | Non-2xx HTTP response (includes exhausted rate-limit retries when `handle_rate_limiting=True`) |
| `httpx.RequestError` | Network or connection failure |

---

## Result types

`search_results` is a list that may contain any mix of the following types. Use `isinstance` to distinguish them.

| Type | Extra properties |
|---|---|
| `GeneralOrNewsResult` | `author`, `timestamp` |
| `ImageResult` | `image_url`, `thumbnail_url`, `image_resolution` |
| `VideoResult` | `video_thumbnail_url`, `video_length`, `author` |
| `MapResult` | — |
| `ITResult` | `author`, `timestamp` |
| `ScienceResult` | — |
| `MusicResult` | `artist`, `timestamp`, `music_video_thumbnail_url` |
| `FileResult` | `file_url`, `file_thumbnail_url`, `timestamp` |
| `SocialMediaResult` | `thumbnail_url`, `timestamp` |

All types share a common base of `category`, `title`, `url`, and `description`.

### Example: handling mixed result types

```python
from searxng_search import (
    GeneralOrNewsResult,
    ImageResult,
    VideoResult,
    MapResult,
    ITResult,
    ScienceResult,
    MusicResult,
    FileResult,
    SocialMediaResult,
)

for result in response.search_results:
    if isinstance(result, GeneralOrNewsResult):
        print(f"[General/News] {result.title} — {result.url}")
        if result.author:
            print(f"  Author: {result.author}")
    elif isinstance(result, ImageResult):
        print(f"[Image] {result.title} ({result.image_resolution})")
        print(f"  Thumbnail: {result.thumbnail_url}")
    elif isinstance(result, VideoResult):
        print(f"[Video] {result.title} [{result.video_length}]")
    elif isinstance(result, MapResult):
        print(f"[Map] {result.title} — {result.url}")
    elif isinstance(result, ITResult):
        print(f"[IT] {result.title}")
    elif isinstance(result, ScienceResult):
        print(f"[Science] {result.title}")
    elif isinstance(result, MusicResult):
        print(f"[Music] {result.title} by {result.artist}")
    elif isinstance(result, FileResult):
        print(f"[File] {result.title} — {result.file_url}")
    elif isinstance(result, SocialMediaResult):
        print(f"[Social] {result.title} — {result.thumbnail_url}")
```

---

## Contributing

### Prerequisites

- Python 3.11+
- [Docker](https://docs.docker.com/get-docker/) (for running a local SearXNG instance)

### Local setup

```bash
git clone https://github.com/SBTopZZZ-LG/searxng-python-sdk.git
cd searxng-python-sdk
make setup
```

This creates a `.venv` virtual environment, installs all dependencies (including dev dependencies), and sets up [pre-commit](https://pre-commit.com/) hooks. The hooks run automatically on each `git commit` to enforce linting and formatting before code reaches CI.

### Starting a local SearXNG instance

Integration tests require a running SearXNG instance. Start one with Docker:

```bash
docker compose up -d
```

This spins up SearXNG on `http://localhost:8080`. Shut it down when done:

```bash
docker compose down
```

### Running tests

| Command | What it runs |
|---|---|
| `make test` | All tests (unit + integration) |
| `make test-unit` | Unit tests only (`tests/searxng_search/`) |
| `make test-integration` | Integration tests only (`tests/integration/`) — requires a running SearXNG instance |

> Integration tests default to `http://localhost:8080`. Override with the `SEARXNG_BASE_URL` environment variable:
>
> ```bash
> SEARXNG_BASE_URL=http://my-instance:8080 make test-integration
> ```

### Linting & formatting

```bash
make lint      # ruff check
make format    # ruff format
```

### Running the example

```bash
make example
```

This runs [example/main.py](example/main.py) against the local SearXNG instance.
