from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, Response

from app.db.items_repo import delete_item, list_items
from app.errors import HttpError
from app.routes.json_body import read_json
from app.services.ingest_item import ingest_item

router = APIRouter()


@router.get("")
def get_items(request: Request):
    """List all saved items.

    Returns lightweight item summaries (id, title, excerpt, chunkCount, etc.).
    Full text remains in the database for RAG search.
    """
    return {"items": list_items(request.app.state.db)}


@router.post("", status_code=201)
async def create_item(request: Request):
    """Ingest a new note or URL.

    Fetches URL content (if url), cleans text, chunks, embeds, and saves to SQLite.
    """
    body = await read_json(request)
    item = await ingest_item(request.app.state.db, body)
    return JSONResponse(item, status_code=201)


@router.delete("/{item_id}", status_code=204)
def remove_item(item_id: str, request: Request):
    """Delete a saved item by its ID.

    Cascades in SQLite to also delete all corresponding vector chunks.
    """
    if not delete_item(request.app.state.db, item_id):
        raise HttpError(404, "Saved item not found")
    return Response(status_code=204)
