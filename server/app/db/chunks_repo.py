from app.services.vectors import decode_vector, encode_vector


def insert_chunks(connection, chunks: list[dict]) -> None:
    for chunk in chunks:
        connection.execute(
            """
            INSERT INTO chunks (id, item_id, chunk_index, content, embedding)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                chunk["id"],
                chunk["itemId"],
                chunk["chunkIndex"],
                chunk["content"],
                encode_vector(chunk["vector"]),
            ),
        )


def count_chunks(db) -> int:
    row = db.read_one("SELECT COUNT(*) AS total FROM chunks")
    return int(row["total"])


def list_chunks_for_search(db) -> list[dict]:
    """Every stored chunk, with its parent title, ready to score in process."""
    rows = db.read(
        """
        SELECT
          c.id,
          c.item_id,
          c.content,
          c.embedding,
          i.title,
          i.source_type,
          i.source_url
        FROM chunks c
        JOIN items i ON i.id = c.item_id
        """
    )
    return [
        {
            "id": row["id"],
            "itemId": row["item_id"],
            "content": row["content"],
            "title": row["title"],
            "sourceType": row["source_type"],
            "sourceUrl": row["source_url"],
            "vector": decode_vector(row["embedding"]),
        }
        for row in rows
    ]
