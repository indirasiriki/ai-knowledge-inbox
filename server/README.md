# Server

FastAPI service for the inbox. Setup, the HTTP contract, and the retrieval steps are in the root [README](../README.md).

## Run this package alone

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
copy .env.example .env
.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 3001
.venv\Scripts\python.exe -m pytest
```

From the repo root, `npm.cmd run dev:server` and `npm.cmd test` do the same thing once the virtual environment exists.

## Where to look

| File | Job |
| --- | --- |
| `app/main.py` | Open the database and expose the app |
| `app/factory.py` | Routes, the built client, status codes |
| `app/routes/items.py` | Saved notes and links |
| `app/routes/questions.py` | Questions |
| `app/services/ingest_note.py` | Validate a note |
| `app/services/ingest_url.py` | Validate a link and keep the extracted text |
| `app/services/page_text.py` | Download a page and turn HTML into text |
| `app/services/public_url.py` | Refuse private hosts, including after a redirect |
| `app/services/chunk_text.py` | Split text |
| `app/services/persist_item.py` | Embed, then write the item and chunks together |
| `app/services/retrieve.py` | Cosine rank over stored chunks |
| `app/services/answer_question.py` | Turn the top chunks into an answer and a source list |
| `app/services/language_api.py` | OpenAI embeddings and chat completions |
| `app/db/` | SQLite schema and queries |

`app/services/vectors.py` stores each embedding as a float32 blob and scores a pair with cosine similarity. There is no separate vector database. The scan is the index.

Tests use pytest and do not call OpenAI. They live in `tests/`: chunking, cosine similarity, public hosts, HTML extraction, storage with cascade delete, and HTTP status codes. `tests/test_http.py` uses an in-memory database. A note save is only attempted when `OPENAI_API_KEY` is unset, and that path must return 503 without inserting a row.

Do not import `app.main` from a test. That opens the real SQLite file. Tests set `INBOX_TESTING=1` and pass their own database into `create_app`.
