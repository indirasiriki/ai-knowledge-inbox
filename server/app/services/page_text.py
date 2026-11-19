from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from app.errors import HttpError
from app.limits import PAGE_BYTE_LIMIT
from app.services.public_url import assert_public_url
from app.textutil import clip, normalize_whitespace

MAX_HOPS = 5
PAGE_HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,text/plain;q=0.9,*/*;q=0.8",
    "accept-language": "en",
}
_DROP_TAGS = ["script", "style", "noscript", "svg", "iframe", "canvas", "form", "nav", "footer"]
_BLOCK_TAGS = ["p", "div", "li", "h1", "h2", "h3", "h4", "h5", "tr", "section", "article", "blockquote"]


def html_to_text(html: str, page_url: str) -> dict:
    """Keep the article text. Drop scripts, menus, and footers before chunking."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all(_DROP_TAGS):
        tag.decompose()
    for tag in soup.find_all("br"):
        tag.replace_with("\n")
    # Newlines stop block elements from gluing the next sentence onto the previous one.
    for tag in soup.find_all(_BLOCK_TAGS):
        tag.insert_before("\n")
        tag.append("\n")

    title = _og_title(soup) or _plain(soup.title) or _plain(soup.find("h1"))
    body = soup.body.get_text() if soup.body else ""
    host = urlparse(page_url).hostname or ""
    return {
        "title": clip(normalize_whitespace(title) or host or "Saved page", 120),
        "text": normalize_whitespace(body),
    }


async def read_page(value: str) -> dict:
    """Download a page without following a redirect until that hop is checked."""
    current = assert_public_url(value).geturl()
    requested_url = current
    timeout = httpx.Timeout(12.0)

    async with httpx.AsyncClient(timeout=timeout, follow_redirects=False, headers=PAGE_HEADERS) as client:
        for _hop in range(MAX_HOPS):
            try:
                response = await client.send(client.build_request("GET", current), stream=True)
            except httpx.TimeoutException as error:
                raise HttpError(502, "The page took too long to respond") from error
            except httpx.HTTPError as error:
                raise HttpError(502, "The page could not be reached") from error

            try:
                if response.status_code in (301, 302, 303, 307, 308):
                    location = response.headers.get("location")
                    if not location:
                        raise HttpError(502, "The page redirect was missing a location")
                    # A public page can forward to a private address. Check every hop.
                    current = assert_public_url(urljoin(current, location)).geturl()
                    continue

                if response.status_code >= 400:
                    raise HttpError(502, f"The page returned HTTP {response.status_code}")

                body = await _read_limited(response)
                content_type = response.headers.get("content-type") or ""
                _assert_readable(content_type)
                if _is_plain_text(content_type):
                    return {
                        "requestedUrl": requested_url,
                        "title": urlparse(current).hostname or "Saved page",
                        "text": normalize_whitespace(body),
                    }

                extracted = html_to_text(body, current)
                return {
                    "requestedUrl": requested_url,
                    "title": extracted["title"],
                    "text": extracted["text"],
                }
            finally:
                await response.aclose()

    raise HttpError(502, "That page redirected too many times")


def _og_title(soup: BeautifulSoup) -> str:
    tag = soup.find("meta", attrs={"property": "og:title"})
    if tag is None:
        return ""
    return tag.get("content") or ""


def _plain(tag) -> str:
    if tag is None:
        return ""
    return tag.get_text() or ""


def _is_plain_text(content_type: str) -> bool:
    lowered = content_type.lower()
    return "text/plain" in lowered and "html" not in lowered


def _assert_readable(content_type: str) -> None:
    lowered = content_type.lower()
    if not lowered or "html" in lowered or "text/plain" in lowered or lowered.startswith("text/"):
        return
    raise HttpError(415, "Only HTML and plain text pages can be saved")


async def _read_limited(response: httpx.Response) -> str:
    """Stop once the page exceeds the cap, instead of buffering an unbounded download."""
    declared = response.headers.get("content-length")
    if declared and declared.isdigit() and int(declared) > PAGE_BYTE_LIMIT:
        await response.aclose()
        raise HttpError(413, "That page is too large to save")

    parts = []
    received = 0
    async for chunk in response.aiter_bytes():
        received += len(chunk)
        if received > PAGE_BYTE_LIMIT:
            await response.aclose()
            raise HttpError(413, "That page is too large to save")
        parts.append(chunk)
    return b"".join(parts).decode("utf-8", errors="replace")
