import json

from fastapi import Request

from app.errors import HttpError
from app.limits import BODY_BYTE_LIMIT


async def read_json(request: Request) -> dict:
    """Parse a JSON object and keep the error shape the client already expects."""
    raw = await request.body()
    if len(raw) > BODY_BYTE_LIMIT:
        raise HttpError(413, "Request body is too large")
    if not raw:
        raise HttpError(400, "Request body is required")
    try:
        body = json.loads(raw)
    except json.JSONDecodeError as error:
        raise HttpError(400, "Request body must be JSON") from error
    if not isinstance(body, dict):
        raise HttpError(400, "Request body is required")
    return body
