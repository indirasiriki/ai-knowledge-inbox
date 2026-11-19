from fastapi import APIRouter, Request

from app.errors import HttpError
from app.limits import QUESTION_CHAR_LIMIT
from app.routes.json_body import read_json
from app.services.answer_question import answer_question

router = APIRouter()


@router.post("")
async def ask(request: Request):
    """Answer a user question based on retrieved knowledge snippets.

    Accepts JSON body with either 'question' or 'query' field.
    """
    body = await read_json(request)
    # Support both 'question' and 'query' field names
    raw_value = body.get("question") if "question" in body else body.get("query")
    question = _read_question(raw_value)
    return await answer_question(request.app.state.db, question)


def _read_question(value) -> str:
    """Validate question input string and enforce length bounds."""
    if not isinstance(value, str) or not value.strip():
        raise HttpError(400, "Question is required")
    question = value.strip()
    if len(question) > QUESTION_CHAR_LIMIT:
        raise HttpError(400, "Question is too long")
    return question
