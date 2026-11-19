from datetime import datetime, timezone
from uuid import uuid4

from app.db.chunks_repo import insert_chunks
from app.db.items_repo import insert_item, to_summary
from app.errors import HttpError
from app.services.chunk_text import chunk_text
from app.services.language_api import embed_texts


async def persist_item(db, fields: dict) -> dict:
    """Chunk, embed, and persist an item and its vector chunks in SQLite.

    Guarantees atomic persistence within a single database transaction.
    """
    # 1. Split raw text into overlapping semantic chunks
    chunks = chunk_text(fields["rawContent"])
    if not chunks:
        raise HttpError(400, "There was no usable text to save")

    # 2. Generate embedding vector for each chunk via OpenAI
    vectors = await embed_texts(chunks)
    if len(vectors) != len(chunks):
        raise HttpError(502, "Embedding count did not match the text")

    # 3. Prepare item record with UTC timestamp
    created_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    item = {
        "id": str(uuid4()),
        "sourceType": fields["sourceType"],
        "title": fields["title"],
        "sourceUrl": fields["sourceUrl"],
        "rawContent": fields["rawContent"],
        "createdAt": created_at,
    }

    # 4. Prepare chunk rows with vector embeddings
    rows = [
        {
            "id": str(uuid4()),
            "itemId": item["id"],
            "chunkIndex": index,
            "content": content,
            "vector": vectors[index],
        }
        for index, content in enumerate(chunks)
    ]

    # 5. Persist item and chunks in a single atomic database transaction
    with db.transaction() as connection:
        insert_item(connection, item)
        insert_chunks(connection, rows)

    return to_summary(item, len(rows))
