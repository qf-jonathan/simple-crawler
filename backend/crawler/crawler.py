import httpx
from bs4 import BeautifulSoup
from storage.models import CrawletUrl
from urllib.parse import urlparse
from collections import deque


def link_normalizer(base_url: str, url: str) -> str:
    if url.startswith("http"):
        return url

    parsed_url = urlparse(base_url)
    if url.startswith("/"):
        return f"{parsed_url.scheme}://{parsed_url.netloc}{url}"

    if parsed_url.path:
        return f"{parsed_url.scheme}://{parsed_url.netloc}/{parsed_url.path}/{url}"

    return f"{parsed_url.scheme}://{parsed_url.netloc}/{url}"


def get_url_instance_from_response(response: httpx.Response) -> CrawletUrl:
    url_instance = CrawletUrl(url=str(response.url), status_code=response.status_code)

    if url_instance.status_code != 200:
        return url_instance

    content_type = response.headers.get("Content-Type", "unknown")
    if content_type.startswith("text/html"):
        soup = BeautifulSoup(response.text, "html.parser")
        url_instance.content_title = soup.title.text if soup.title else ""
        url_instance.content_size = len(response.text)

        for link in soup.find_all("a"):
            if link.get("href"):
                normalized_link = link_normalizer(url_instance.url, link.get("href"))
                url_instance.links.append(normalized_link)

    return url_instance


async def get_page_content(url: str) -> tuple[int, str, str]:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            return get_url_instance_from_response(response)
        except httpx.HTTPError:
            return CrawletUrl(url=url, status_code=404)


async def crawl_url(root_url: str, max_depth: int) -> list[CrawletUrl]:
    queue = deque([(root_url, 0)])
    visited_urls = {}

    while queue:
        url, depth = queue.popleft()
        if url in visited_urls or depth >= max_depth:
            continue
        page_content = await get_page_content(url)
        visited_urls[url] = page_content

        for link in page_content.links:
            queue.append((link, depth + 1))

    return visited_urls.values()
