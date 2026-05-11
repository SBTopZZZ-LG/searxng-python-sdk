"""SearXNG Search Module Implementation."""

from __future__ import annotations

import asyncio
import random
from enum import Enum
from typing import Union
from urllib.parse import quote

import httpx
from bs4 import BeautifulSoup
from pydantic import Field
from pydantic.dataclasses import dataclass

from ._http_url import HttpUrl as _HttpUrl
from ._logger import get_logger, log_errors

SEARXNG_FORMAT = "html"

_logger = get_logger(__name__)


class _StringEnum(str, Enum):
    """Cross-version replacement for StrEnum that preserves value stringification."""

    def __str__(self) -> str:
        return self.value


class Category(_StringEnum):
    """Enum representing search result categories in SearXNG."""

    GENERAL = "general"
    NEWS = "news"
    IMAGES = "images"
    VIDEOS = "videos"
    MAP = "map"
    IT = "it"
    SCIENCE = "science"
    MUSIC = "music"
    FILES = "files"
    SOCIAL_MEDIA = "social media"


class TimeRange(_StringEnum):
    """Enum representing time range filters for search results."""

    DAY = "day"
    MONTH = "month"
    YEAR = "year"


class Autocomplete(_StringEnum):
    """Enum representing autocomplete providers for search queries."""

    GOOGLE = "google"
    DBPEDIA = "dbpedia"
    DUCKDUCKGO = "duckduckgo"
    MWMBL = "mwmbl"
    STARTPAGE = "startpage"
    WIKIPEDIA = "wikipedia"
    SWISSCOWS = "swisscows"
    QWANT = "qwant"


class SafeSearch(_StringEnum):
    """Enum representing safe search levels for filtering search results."""

    OFF = "0"
    MODERATE = "1"
    STRICT = "2"


class Theme(_StringEnum):
    """Enum representing UI themes for the SearXNG interface."""

    SIMPLE = "simple"


class Plugins(_StringEnum):
    """Enum representing plugins that can be enabled or disabled in a SearXNG instance."""

    HASH_PLUGIN = "Hash_plugin"
    SELF_INFORMATION = "Self_Information"
    TRACKER_URL_REMOVER = "Tracker_URL_remover"
    AHMIA_BLACKLIST = "Ahmia_blacklist"
    HOSTNAMES_PLUGIN = "Hostnames_plugin"
    OPEN_ACCESS_DOI_REWRITE = "Open_Access_DOI_rewrite"
    VIM_LIKE_HOTKEYS = "Vim-like_hotkeys"
    TOR_CHECK_PLUGIN = "Tor_check_plugin"


@dataclass
class SearXNGBaseConfiguration:
    """Base configuration for a SearXNG instance.

    Attributes:
        base_url: The base URL of the SearXNG instance.
        user_agent: Optional custom User-Agent string to use for search requests.
        timeout: Optional timeout in seconds for search requests. Defaults to 30 seconds.
        handle_rate_limiting: Whether to automatically handle rate limiting by retrying
            after a delay when a 429 status code is received. Defaults to True.

    Note:
        When ``handle_rate_limiting`` is enabled, the request is automatically retried
        on HTTP 429 using fixed delays with jitter.

        Retry schedule (Fixed + Jitter strategy):

        - Attempt 1: 10s base ± 2s jitter  →  effective range: [8s, 12s]
        - Attempt 2: 15s base ± 2s jitter  →  effective range: [13s, 17s]
        - Attempt 3: 20s base ± 2s jitter  →  effective range: [18s, 22s]

        Raises after all retries are exhausted without a successful response.
    """

    base_url: _HttpUrl
    user_agent: str | None = None
    timeout: float | None = Field(
        default=30.0,
        gt=0,
        description="Timeout in seconds for search requests. Must be greater than 0.",
    )
    handle_rate_limiting: bool = Field(
        default=True,
        description="Whether to automatically handle rate limiting by retrying after a delay when a 429 status code is received.",
    )


@dataclass
class GeneralOrNewsResult:
    """Represents a general or news search result from SearXNG."""

    category: str
    title: str
    url: _HttpUrl
    description: str | None = None
    author: str | None = None
    timestamp: str | None = None


@dataclass
class ImageResult:
    """Represents an image search result from SearXNG."""

    category: str
    title: str
    url: _HttpUrl
    description: str | None = None
    image_url: str | None = None
    thumbnail_url: str | None = None
    image_resolution: str | None = None


@dataclass
class VideoResult:
    """Represents a video search result from SearXNG."""

    category: str
    title: str
    url: _HttpUrl
    description: str | None = None
    video_thumbnail_url: str | None = None
    video_length: str | None = None
    author: str | None = None


@dataclass
class MapResult:
    """Represents a map search result from SearXNG."""

    category: str
    title: str
    url: _HttpUrl
    description: str | None = None


@dataclass
class ITResult:
    """Represents an IT-related search result from SearXNG."""

    category: str
    title: str
    url: _HttpUrl
    description: str | None = None
    author: str | None = None
    timestamp: str | None = None


@dataclass
class ScienceResult:
    """Represents a science-related search result from SearXNG."""

    category: str
    title: str
    url: _HttpUrl
    description: str | None = None


@dataclass
class MusicResult:
    """Represents a music-related search result from SearXNG."""

    category: str
    title: str
    url: _HttpUrl
    description: str | None = None
    artist: str | None = None
    timestamp: str | None = None
    music_video_thumbnail_url: str | None = None


@dataclass
class FileResult:
    """Represents a file search result from SearXNG."""

    category: str
    title: str
    url: _HttpUrl
    description: str | None = None
    file_url: str | None = None
    file_thumbnail_url: str | None = None
    timestamp: str | None = None


@dataclass
class SocialMediaResult:
    """Represents a social media search result from SearXNG."""

    category: str
    title: str
    url: _HttpUrl
    description: str | None = None
    thumbnail_url: str | None = None
    timestamp: str | None = None


_SearxngSearchResult = Union[
    GeneralOrNewsResult,
    ImageResult,
    VideoResult,
    MapResult,
    ITResult,
    ScienceResult,
    MusicResult,
    FileResult,
    SocialMediaResult,
]


@dataclass
class SearXNGResponse:
    """
    Represents the response from a SearXNG search request,
    including metadata and parsed search results.
    """

    search_url: _HttpUrl
    status_code: int
    response_headers: dict[str, str]
    full_html: str
    search_results: list[_SearxngSearchResult]


@dataclass
class SearXNGSearchConfiguration:
    """Configuration for a SearXNG search request.

    Attributes:
        query: The search query string.
        custom_params: Optional dictionary of custom query parameters to include in the search URL.
        custom_headers: Optional dictionary of custom HTTP headers to include in the search request.
        categories: Optional set of categories to search within. (Check :class:`Category` enum)
        engines: Optional set of search engines to use.
        page_number: Optional page number for paginated results.
        time_range: Optional time range filter for results. (Check :class:`TimeRange` enum)
        results_on_new_tab: Optional flag to open results in a new tab.
        image_proxy: Optional flag to enable image proxying.
        autocomplete: Optional set of autocomplete providers. (Check :class:`Autocomplete` enum)
        safe_search: Optional safe search level (0=off, 1=moderate, 2=strict). \
            (Check :class:`SafeSearch` enum)
        theme: Optional set of UI themes. (Check :class:`Theme` enum)
        enabled_plugins: Optional set of plugins to enable. (Check :class:`Plugins` enum)
        disabled_plugins: Optional set of plugins to disable. (Check :class:`Plugins` enum)
        enabled_engines: Optional set of search engines to enable.
        disabled_engines: Optional set of search engines to disable.
    """

    query: str = Field(min_length=1, description="The search query string.")
    custom_params: dict[str, str] | None = None
    custom_headers: dict[str, str] | None = None
    categories: set[Category | str] | None = None
    engines: set[str] | None = None
    page_number: int | None = None
    time_range: TimeRange | str | None = None
    results_on_new_tab: bool | None = None
    image_proxy: bool | None = None
    autocomplete: set[Autocomplete | str] | None = None
    safe_search: SafeSearch | int | None = None
    theme: set[Theme | str] | None = None
    enabled_plugins: set[Plugins | str] | None = None
    disabled_plugins: set[Plugins | str] | None = None
    enabled_engines: set[str] | None = None
    disabled_engines: set[str] | None = None


class SearXNG:
    """Main class for interacting with a SearXNG instance."""

    def __init__(self, base_configuration: SearXNGBaseConfiguration) -> None:
        self.base_configuration = base_configuration

    def _urlencode_set(self, items: set) -> str:
        if items is None or len(items) == 0:
            return ""
        return ",".join(quote(str(item), safe="") for item in items)

    def _urlencode_custom_params(self, custom_params: dict[str, str]) -> str:
        if custom_params is None or len(custom_params) == 0:
            return ""
        return "&".join(
            f"{quote(param_name, safe='')}={quote(param_value, safe='')}"
            for param_name, param_value in custom_params.items()
        )

    def _urlencode_boolean(
        self,
        is_true: bool,
        mapping_for_true: str,
        mapping_for_false: str,
    ) -> str:
        if is_true:
            return mapping_for_true
        return mapping_for_false

    def _build_search_url(
        self, search_configuration: SearXNGSearchConfiguration
    ) -> str:
        base_url = self.base_configuration.base_url.rstrip("/")
        search_url = f"{base_url}/search?format={SEARXNG_FORMAT}&q={quote(search_configuration.query, safe='')}"

        if search_configuration.custom_params is not None:
            search_url += (
                f"&{self._urlencode_custom_params(search_configuration.custom_params)}"
            )
        if search_configuration.categories is not None:
            search_url += (
                f"&categories={self._urlencode_set(search_configuration.categories)}"
            )
        if search_configuration.engines is not None:
            search_url += (
                f"&engines={self._urlencode_set(search_configuration.engines)}"
            )
        if search_configuration.page_number is not None:
            search_url += f"&page={search_configuration.page_number}"
        if search_configuration.time_range is not None:
            search_url += (
                f"&time_range={quote(search_configuration.time_range, safe='')}"
            )
        if search_configuration.results_on_new_tab is not None:
            search_url += f"&newtab={self._urlencode_boolean(search_configuration.results_on_new_tab, 'on', 'off')}"
        if search_configuration.image_proxy is not None:
            search_url += f"&image_proxy={self._urlencode_boolean(search_configuration.image_proxy, 'on', 'off')}"
        if search_configuration.autocomplete is not None:
            search_url += f"&autocomplete={self._urlencode_set(search_configuration.autocomplete)}"
        if search_configuration.safe_search is not None:
            search_url += f"&safe_search={search_configuration.safe_search}"
        if search_configuration.theme:
            search_url += f"&theme={self._urlencode_set(search_configuration.theme)}"
        if search_configuration.enabled_plugins is not None:
            search_url += f"&enabled_plugins={self._urlencode_set(search_configuration.enabled_plugins)}"
        if search_configuration.disabled_plugins is not None:
            search_url += f"&disabled_plugins={self._urlencode_set(search_configuration.disabled_plugins)}"
        if search_configuration.enabled_engines is not None:
            search_url += f"&enabled_engines={self._urlencode_set(search_configuration.enabled_engines)}"
        if search_configuration.disabled_engines is not None:
            search_url += f"&disabled_engines={self._urlencode_set(search_configuration.disabled_engines)}"

        return search_url

    def _parse_general_or_news(self, article) -> GeneralOrNewsResult | None:
        url_tag = article.select_one("a.url_header")
        title_tag = article.select_one("h3 a")
        if not url_tag or not title_tag:
            return None

        description_tag = article.select_one("p.content")
        author_tag = article.select_one("div.highlight")
        time_tag = article.select_one("time.published_date")

        return GeneralOrNewsResult(
            category="general-or-news",
            url=url_tag["href"],
            title=title_tag.get_text(strip=True),
            description=description_tag.get_text(strip=True)
            if description_tag
            else None,
            author=author_tag.get_text(strip=True) if author_tag else None,
            timestamp=time_tag.get("datetime") or time_tag.get_text(strip=True)
            if time_tag
            else None,
        )

    def _parse_images(self, article) -> ImageResult | None:
        url_tag = article.select_one("a[href]")
        title_tag = article.select_one("span.title")
        if not url_tag or not title_tag:
            return None

        description_tag = article.select_one("span.source")
        resolution_tag = article.select_one("span.image_resolution")
        thumbnail_tag = article.select_one("img.image_thumbnail")

        return ImageResult(
            category="images",
            url=url_tag["href"],
            title=title_tag.get_text(strip=True),
            description=description_tag.get_text(strip=True)
            if description_tag
            else None,
            image_url=url_tag["href"],
            thumbnail_url=thumbnail_tag["src"] if thumbnail_tag else None,
            image_resolution=resolution_tag.get_text(strip=True)
            if resolution_tag
            else None,
        )

    def _parse_videos(self, article) -> VideoResult | None:
        url_tag = article.select_one("a.url_header")
        title_tag = article.select_one("h3 a")
        if not url_tag or not title_tag:
            return None

        thumbnail_tag = article.select_one("img.thumbnail")
        length_tag = article.select_one("span.thumbnail_length")
        author_tag = article.select_one("div.highlight")
        child_p_tags = [
            tag for tag in article.children if getattr(tag, "name", None) == "p"
        ]
        description = (
            child_p_tags[1].get_text(strip=True) if len(child_p_tags) > 1 else None
        )

        return VideoResult(
            category="videos",
            url=url_tag["href"],
            title=title_tag.get_text(strip=True),
            description=description,
            video_thumbnail_url=thumbnail_tag["src"] if thumbnail_tag else None,
            video_length=length_tag.get_text(strip=True) if length_tag else None,
            author=author_tag.get_text(strip=True) if author_tag else None,
        )

    def _parse_map(self, article) -> MapResult | None:
        url_tag = article.select_one("a.url_header")
        title_tag = article.select_one("h3 a")
        if not url_tag or not title_tag:
            return None

        description_tag = article.select_one("table tbody tr:first-child td")

        return MapResult(
            category="map",
            url=url_tag["href"],
            title=title_tag.get_text(strip=True),
            description=description_tag.get_text(strip=True)
            if description_tag
            else None,
        )

    def _parse_it(self, article) -> ITResult | None:
        url_tag = article.select_one("a.url_header")
        title_tag = article.select_one("h3 a")
        if not url_tag or not title_tag:
            return None

        description_tag = article.select_one("p.content")
        author_tag = article.select_one("div.highlight")
        time_tag = article.select_one("time")

        return ITResult(
            category="it",
            url=url_tag["href"],
            title=title_tag.get_text(strip=True),
            description=description_tag.get_text(strip=True)
            if description_tag
            else None,
            author=author_tag.get_text(strip=True) if author_tag else None,
            timestamp=time_tag.get("datetime") or time_tag.get_text(strip=True)
            if time_tag
            else None,
        )

    def _parse_science(self, article) -> ScienceResult | None:
        url_tag = article.select_one("a")
        title_tag = article.select_one("h3") or article.select_one("h2")
        if not url_tag or not title_tag:
            return None

        description_tag = article.select_one("p:first-of-type")

        return ScienceResult(
            category="science",
            url=url_tag["href"],
            title=title_tag.get_text(strip=True),
            description=description_tag.get_text(strip=True)
            if description_tag
            else None,
        )

    def _parse_music(self, article) -> MusicResult | None:
        url_tag = article.select_one("a.url_header")
        title_tag = article.select_one("h3 a")
        if not url_tag or not title_tag:
            return None

        description_tag = article.select_one("p.content")
        artist_tag = article.select_one("div.highlight")
        time_tag = article.select_one("time")
        thumbnail_tag = article.select_one("img.thumbnail")

        return MusicResult(
            category="music",
            url=url_tag["href"],
            title=title_tag.get_text(strip=True),
            description=description_tag.get_text(strip=True)
            if description_tag
            else None,
            artist=artist_tag.get_text(strip=True) if artist_tag else None,
            timestamp=time_tag.get("datetime") or time_tag.get_text(strip=True)
            if time_tag
            else None,
            music_video_thumbnail_url=thumbnail_tag["src"] if thumbnail_tag else None,
        )

    def _parse_files(self, article) -> FileResult | None:
        url_tag = article.select_one("a.url_header")
        title_tag = article.select_one("h3 a")
        if not url_tag or not title_tag:
            return None

        description_tag = article.select_one("p.content")
        time_tag = article.select_one("time")
        thumbnail_tag = article.select_one("img")

        return FileResult(
            category="files",
            url=url_tag["href"],
            title=title_tag.get_text(strip=True),
            description=description_tag.get_text(strip=True)
            if description_tag
            else None,
            file_url=url_tag["href"],
            file_thumbnail_url=thumbnail_tag["src"] if thumbnail_tag else None,
            timestamp=time_tag.get("datetime") or time_tag.get_text(strip=True)
            if time_tag
            else None,
        )

    def _parse_social_media(self, article) -> SocialMediaResult | None:
        url_tag = article.select_one("a.url_header")
        title_tag = article.select_one("h3 a") or article.select_one("h3")
        if not url_tag or not title_tag:
            return None

        description_tag = article.select_one("p.content")
        time_tag = article.select_one("time")
        thumbnail_tag = article.select_one("img.image_thumbnail")

        return SocialMediaResult(
            category="social-media",
            url=url_tag["href"],
            title=title_tag.get_text(strip=True),
            description=description_tag.get_text(strip=True)
            if description_tag
            else None,
            thumbnail_url=thumbnail_tag["src"] if thumbnail_tag else None,
            timestamp=time_tag.get("datetime") or time_tag.get_text(strip=True)
            if time_tag
            else None,
        )

    def _get_search_results_from_html(self, html: str) -> list:
        soup = BeautifulSoup(html, "html.parser")
        results = []

        for article in soup.select("article.result"):
            classes = article.get("class") or []

            if "result-images" in classes:
                result = self._parse_images(article)
            elif "result-videos" in classes:
                result = self._parse_videos(article)
            elif "result-map" in classes:
                result = self._parse_map(article)
            elif "category-it" in classes:
                result = self._parse_it(article)
            elif "category-science" in classes:
                result = self._parse_science(article)
            elif "category-music" in classes:
                result = self._parse_music(article)
            elif "category-files" in classes:
                result = self._parse_files(article)
            elif "category-social" in classes and "media" in classes:
                result = self._parse_social_media(article)
            else:
                result = self._parse_general_or_news(article)

            if result is not None:
                results.append(result)

        return results

    @log_errors(_logger)
    async def search(
        self, search_configuration: SearXNGSearchConfiguration
    ) -> SearXNGResponse:
        """
        Performs a search on the SearXNG instance using the provided
        configuration and returns a structured response.
        """

        search_url = self._build_search_url(search_configuration)
        _logger.debug("Search URL: %s", search_url)

        headers: dict[str, str] | None = None
        if self.base_configuration.user_agent:
            headers = {"User-Agent": self.base_configuration.user_agent}
            if search_configuration.custom_headers:
                headers.update(search_configuration.custom_headers)
        elif search_configuration.custom_headers is not None:
            headers = search_configuration.custom_headers

        _retry_schedule = [(10, 2), (15, 2), (20, 2)]  # (base_seconds, jitter_seconds)
        _max_attempts = len(_retry_schedule) + 1  # initial + 3 retries

        response: httpx.Response | None = None

        async with httpx.AsyncClient(timeout=self.base_configuration.timeout) as client:
            for attempt in range(_max_attempts):
                try:
                    response = await client.get(
                        search_url,
                        headers=headers,
                    )
                    response.raise_for_status()
                    break
                except httpx.HTTPStatusError as e:
                    if (
                        e.response.status_code == 429
                        and self.base_configuration.handle_rate_limiting
                        and attempt < len(_retry_schedule)
                    ):
                        base, jitter = _retry_schedule[attempt]
                        delay = base + random.uniform(-jitter, jitter)
                        _logger.warning(
                            "Rate limited (429). Retrying in %.1fs (attempt %d/%d).",
                            delay,
                            attempt + 1,
                            len(_retry_schedule),
                        )
                        await asyncio.sleep(delay)
                    else:
                        raise httpx.HTTPStatusError(
                            f"Search request failed with status {e.response.status_code}: {e.response.text}",
                            request=e.request,
                            response=e.response,
                        ) from e
                except httpx.RequestError as e:
                    raise httpx.RequestError(
                        f"Search request failed: {e}",
                        request=e.request,
                    ) from e

        assert response is not None
        response_html = response.text
        search_results = self._get_search_results_from_html(response_html)

        return SearXNGResponse(
            search_url=search_url,
            status_code=response.status_code,
            response_headers=dict(response.headers),
            full_html=response_html,
            search_results=search_results,
        )
