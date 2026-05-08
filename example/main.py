"""Example usage of the SearXNG Python SDK."""

from searxng_search import SearXNG, SearXNGBaseConfiguration, SearXNGSearchConfiguration, \
    Category


async def main():
    """Run an example search query against a local SearXNG instance."""

    base_config = SearXNGBaseConfiguration(
        base_url="http://localhost:8080",
        user_agent="SearXNG Python SDK Example/0.1",
    )

    search_config = SearXNGSearchConfiguration(
        query="python=sdk",
        categories={Category.GENERAL, Category.IMAGES}
    )

    searxng = SearXNG(base_configuration=base_config)
    response = await searxng.search(search_configuration=search_config)

    print("Search URL:", response.search_url)
    print("Status Code:", response.status_code)
    print("Response Headers:", response.response_headers)
    print("Full HTML:", response.full_html[:200])
    print("Parsed Search Results:", response.search_results)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
