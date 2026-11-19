import os
from pathlib import Path

from dotenv import load_dotenv

# server/app/config.py -> server/
SERVER_ROOT = Path(__file__).resolve().parents[1]
# The React build lives next to the server package.
CLIENT_DIST = SERVER_ROOT.parent / "client" / "dist"

# Always read server/.env, even when uvicorn is started from the repo root.
load_dotenv(SERVER_ROOT / ".env")


def _number(value, fallback: float) -> float:
    if value is None or value == "":
        return fallback
    try:
        return float(value)
    except ValueError:
        return fallback


def _database_path() -> Path:
    configured = os.environ.get("DATABASE_PATH")
    if not configured:
        return SERVER_ROOT / "data" / "inbox.sqlite"
    path = Path(configured)
    if path.is_absolute():
        return path
    return (SERVER_ROOT / path).resolve()


_top_k = round(_number(os.environ.get("TOP_K"), 5))
_min_score = _number(os.environ.get("MIN_SCORE"), 0.22)


class Config:
    """Settings loaded once at import. Restart the process after editing .env."""

    port = round(_number(os.environ.get("PORT"), 3001))
    client_origin = os.environ.get("CLIENT_ORIGIN") or "http://localhost:5173"
    database_path = _database_path()
    openai_key = os.environ.get("OPENAI_API_KEY") or ""
    embedding_model = os.environ.get("EMBEDDING_MODEL") or "text-embedding-3-small"
    answer_model = os.environ.get("ANSWER_MODEL") or "gpt-4o-mini"
    top_k = min(10, max(1, _top_k))
    min_score = min(1.0, max(0.0, _min_score))


config = Config()
