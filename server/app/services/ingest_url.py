from app.errors import HttpError
from app.limits import MIN_PAGE_CHARS, PAGE_CHAR_LIMIT, URL_CHAR_LIMIT
from app.services.page_text import read_page
from app.services.persist_item import persist_item
from app.textutil import limit_text


async def ingest_url(db, value) -> dict:
    if not isinstance(value, str) or not value.strip():
        raise HttpError(400, "A URL is required")
    if len(value.strip()) > URL_CHAR_LIMIT:
        raise HttpError(400, "URL is too long")

    page = await read_page(value.strip())
    # Pages are often longer than a pasted note. Keep the front instead of rejecting them.
    raw_content = limit_text(page["text"], PAGE_CHAR_LIMIT)
    if len(raw_content) < MIN_PAGE_CHARS:
        raise HttpError(422, "That page did not contain enough readable text")

    return await persist_item(db, {
        "sourceType": "url",
        "title": page["title"],
        "sourceUrl": page["requestedUrl"],
        "rawContent": raw_content,
    })
