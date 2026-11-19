from app.db.chunks_repo import count_chunks, insert_chunks
from app.db.database import open_database
from app.db.items_repo import delete_item, insert_item, list_items
from app.services.retrieve import retrieve_chunks


def sample_item():
    return {
        "id": "item-1",
        "sourceType": "note",
        "title": "Colors",
        "sourceUrl": None,
        "rawContent": "red apple and blue sky",
        "createdAt": "2026-01-01T00:00:00.000Z",
    }


def test_saved_chunks_round_trip_and_the_closer_one_ranks_first():
    db = open_database(":memory:")
    item = sample_item()
    with db.transaction() as connection:
        insert_item(connection, item)
        insert_chunks(connection, [
            {"id": "c1", "itemId": item["id"], "chunkIndex": 0, "content": "red apple", "vector": [1, 0, 0]},
            {"id": "c2", "itemId": item["id"], "chunkIndex": 1, "content": "blue sky", "vector": [0, 1, 0]},
        ])

    listed = list_items(db)
    assert len(listed) == 1
    assert listed[0]["sourceType"] == "note"
    assert listed[0]["sourceUrl"] is None
    assert listed[0]["chunkCount"] == 2
    assert "red apple" in listed[0]["excerpt"]

    found = retrieve_chunks(db, [0.9, 0.1, 0], 2)
    assert found[0]["content"] == "red apple"
    assert found[0]["score"] > 0.95
    assert found[1]["content"] == "blue sky"
    assert found[0]["title"] == "Colors"
    db.close()


def test_deleting_an_item_removes_its_chunks():
    db = open_database(":memory:")
    item = sample_item()
    with db.transaction() as connection:
        insert_item(connection, item)
        insert_chunks(connection, [
            {"id": "c1", "itemId": item["id"], "chunkIndex": 0, "content": "red apple", "vector": [1, 0]},
        ])

    assert count_chunks(db) == 1
    assert delete_item(db, item["id"]) is True
    assert count_chunks(db) == 0
    assert list_items(db) == []
    assert delete_item(db, item["id"]) is False
    db.close()
