import os

from fastapi.testclient import TestClient

from app.db.database import open_database
from app.factory import create_app

# Quiet request logs and the missing-key startup line while the suite runs.
os.environ["INBOX_TESTING"] = "1"


def test_health_validation_empty_questions_and_missing_rows():
    database = open_database(":memory:")
    client = TestClient(create_app(database))

    health_response = client.get("/api/health")
    assert health_response.status_code == 200
    health = health_response.json()
    assert health["ok"] is True
    assert isinstance(health["ready"], bool)

    assert client.get("/api/does-not-exist").status_code == 404

    bad_json = client.post("/api/items", content=b"{", headers={"content-type": "application/json"})
    assert bad_json.status_code == 400

    bad_type = client.post("/api/items", json={"sourceType": "file"})
    assert bad_type.status_code == 400

    empty_note = client.post("/api/items", json={"sourceType": "note", "text": "   "})
    assert empty_note.status_code == 400

    items_response = client.get("/api/items")
    assert items_response.status_code == 200
    assert items_response.json() == {"items": []}

    # Test GET /items endpoint alias
    assert client.get("/items").status_code == 200
    assert client.get("/items").json() == {"items": []}

    assert client.delete("/api/items/missing-id").status_code == 404

    empty_question = client.post("/api/questions", json={"question": "  "})
    assert empty_question.status_code == 400

    unanswered = client.post("/api/questions", json={"question": "When is the deploy window?"})
    assert unanswered.status_code == 200
    body = unanswered.json()
    assert "Nothing is saved yet" in body["answer"]
    assert body["sources"] == []

    # Test POST /query alias with {"query": ...}
    query_alias = client.post("/query", json={"query": "When is the deploy window?"})
    assert query_alias.status_code == 200
    assert "Nothing is saved yet" in query_alias.json()["answer"]

    if not health["ready"]:
        denied = client.post("/api/items", json={"sourceType": "note", "text": "Standup is at 10."})
        assert denied.status_code == 503
        assert client.get("/api/items").json()["items"] == []

        # Test POST /ingest alias when key is missing
        denied_ingest = client.post("/ingest", json={"source_type": "note", "text": "Standup is at 10."})
        assert denied_ingest.status_code == 503

    database.close()
