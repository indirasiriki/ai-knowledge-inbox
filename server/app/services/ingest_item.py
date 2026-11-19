from app.errors import HttpError
from app.services.ingest_note import ingest_note
from app.services.ingest_url import ingest_url


async def ingest_item(db, body) -> dict:
    """Validate and route an ingest request to either note or URL ingestion.

    Supports both camelCase ('sourceType') and snake_case ('source_type'),
    or automatically infers the source type if 'url' or 'text'/'content' is provided.
    """
    if not isinstance(body, dict):
        raise HttpError(400, "Request body is required")

    # Check explicit source type (supports sourceType, source_type, or type)
    source_type = (
        body.get("sourceType")
        or body.get("source_type")
        or body.get("type")
    )

    # Infer source type if not explicitly passed
    if not source_type:
        if body.get("url"):
            source_type = "url"
        elif body.get("text") or body.get("content"):
            source_type = "note"

    if source_type == "note":
        text_content = body.get("text") if body.get("text") is not None else body.get("content")
        return await ingest_note(db, text_content)

    if source_type == "url":
        return await ingest_url(db, body.get("url"))

    raise HttpError(400, "sourceType must be note or url")
