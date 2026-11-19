from app.errors import HttpError
from app.limits import NOTE_CHAR_LIMIT
from app.services.persist_item import persist_item
from app.textutil import normalize_whitespace, title_from_note


async def ingest_note(db, text) -> dict:
    if not isinstance(text, str) or not text.strip():
        raise HttpError(400, "Note text is required")

    trimmed = text.strip()
    if len(trimmed) > NOTE_CHAR_LIMIT:
        raise HttpError(400, "Note is too long (50,000 characters max)")

    raw_content = normalize_whitespace(trimmed)
    if not raw_content:
        raise HttpError(400, "Note text is required")

    return await persist_item(db, {
        "sourceType": "note",
        "title": title_from_note(raw_content),
        "sourceUrl": None,
        "rawContent": raw_content,
    })
