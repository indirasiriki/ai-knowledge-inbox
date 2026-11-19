from app.db.chunks_repo import list_chunks_for_search
from app.services.vectors import cosine_similarity


def retrieve_chunks(db, query_vector, limit: int) -> list[dict]:
    """Score every stored chunk against query_vector and return top matches.

    Performs an in-memory scan computing cosine similarity for each chunk.
    Fast and lightweight for personal inbox scale (thousands of chunks).
    """
    scored = []
    for chunk in list_chunks_for_search(db):
        vector = chunk.pop("vector")
        chunk["score"] = cosine_similarity(query_vector, vector)
        scored.append(chunk)
    scored.sort(key=lambda chunk: chunk["score"], reverse=True)
    return scored[:limit]
