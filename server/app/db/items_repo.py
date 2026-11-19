from app.textutil import clip


def to_summary(item: dict, chunk_count: int) -> dict:
    """Shape returned by both the list and the create response."""
    return {
        "id": item["id"],
        "sourceType": item["sourceType"],
        "title": item["title"],
        "sourceUrl": item["sourceUrl"],
        "excerpt": clip(item["rawContent"], 160),
        "chunkCount": chunk_count,
        "createdAt": item["createdAt"],
    }


def insert_item(connection, item: dict) -> None:
    connection.execute(
        """
        INSERT INTO items (id, source_type, title, source_url, raw_content, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            item["id"],
            item["sourceType"],
            item["title"],
            item["sourceUrl"],
            item["rawContent"],
            item["createdAt"],
        ),
    )


def list_items(db) -> list[dict]:
    rows = db.read(
        """
        SELECT
          i.id,
          i.source_type,
          i.title,
          i.source_url,
          i.raw_content,
          i.created_at,
          (SELECT COUNT(*) FROM chunks c WHERE c.item_id = i.id) AS chunk_count
        FROM items i
        ORDER BY i.created_at DESC
        """
    )
    return [
        to_summary(
            {
                "id": row["id"],
                "sourceType": row["source_type"],
                "title": row["title"],
                "sourceUrl": row["source_url"],
                "rawContent": row["raw_content"],
                "createdAt": row["created_at"],
            },
            int(row["chunk_count"]),
        )
        for row in rows
    ]


def delete_item(db, item_id: str) -> bool:
    """Deleting the item also deletes its chunks because of ON DELETE CASCADE."""
    cursor = db.write("DELETE FROM items WHERE id = ?", (item_id,))
    return cursor.rowcount > 0
