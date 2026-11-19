import hashlib
import math
import re
import httpx

from app.config import config
from app.errors import HttpError

EMBED_BATCH = 64
VECTOR_DIM = 1536

# Common English stop words and conversational query filler filtered during local token extraction
_STOP_WORDS = {
    "is", "the", "a", "an", "and", "or", "in", "on", "at", "to", "for", "of",
    "with", "by", "from", "when", "what", "where", "who", "which", "how",
    "why", "do", "does", "did", "we", "i", "you", "it", "they", "this", "that",
    "about", "save", "saved", "saving", "tell", "show", "know", "can", "could",
    "would", "should", "find", "get", "give", "notes", "note", "item", "items",
    "me", "my", "have", "had", "has", "there", "any", "anything", "mention", "mentioned"
}


def is_live_openai() -> bool:
    """Check if a live OpenAI secret key (starting with sk-) is configured."""
    key = (config.openai_key or "").strip()
    return key.startswith("sk-")


async def embed_texts(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for text chunks.

    Uses OpenAI text-embedding-3-small when a key is present, or falls back to
    deterministic local vector hashing when running offline without a key.
    """
    if not is_live_openai():
        return [_local_embed(text) for text in texts]

    vectors = []
    for index in range(0, len(texts), EMBED_BATCH):
        batch = texts[index:index + EMBED_BATCH]
        payload = await _post_openai("/v1/embeddings", {
            "model": config.embedding_model,
            "input": batch,
        }, 30.0)
        rows = list(payload.get("data") or [])
        rows.sort(key=lambda row: row.get("index", 0))
        if len(rows) != len(batch):
            raise HttpError(502, "Embedding count did not match the text")
        vectors.extend(row["embedding"] for row in rows)
    return vectors


async def complete_chat(system: str, user: str) -> str:
    """Generate an answer grounded in the retrieved chunks.

    Uses OpenAI gpt-4o-mini when a key is present, or local extractive
    grounded synthesis when running offline without a key.
    """
    if not is_live_openai():
        return _local_chat(system, user)

    payload = await _post_openai("/v1/chat/completions", {
        "model": config.answer_model,
        "temperature": 0.2,
        "max_tokens": 700,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }, 45.0)
    text = (((payload.get("choices") or [{}])[0].get("message") or {}).get("content"))
    if not isinstance(text, str) or not text.strip():
        raise HttpError(502, "No answer text came back")
    return text.strip()


def _local_embed(text: str) -> list[float]:
    """Generate a deterministic 1536-dimensional normalized vector for offline RAG."""
    vector = [0.0] * VECTOR_DIM
    clean_words = [w for w in re.findall(r"\b\w+\b", text.lower()) if w not in _STOP_WORDS]
    if not clean_words:
        clean_words = re.findall(r"\b\w+\b", text.lower())
    if not clean_words:
        return vector

    # Build unigrams and bigrams
    tokens = list(clean_words)
    for i in range(len(clean_words) - 1):
        tokens.append(f"{clean_words[i]}_{clean_words[i+1]}")

    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        idx = int.from_bytes(digest[:4], "little") % VECTOR_DIM
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        weight = 2.0 if "_" in token else 1.0
        vector[idx] += sign * weight

    # L2 normalize
    norm = math.sqrt(sum(v * v for v in vector))
    if norm > 0:
        vector = [v / norm for v in vector]
    return vector


def _local_chat(system: str, user_prompt: str) -> str:
    """Offline answer synthesis: extract best matching sentences from cited chunks."""
    lines = user_prompt.strip().split("\n")
    question = ""
    notes = []
    current_note = None

    for line in lines:
        if line.startswith("Question:"):
            question = line[len("Question:"):].strip()
        elif re.match(r"^\[\d+\]", line):
            m = re.match(r"^\[(\d+)\]\s*(.*)", line)
            current_note = {"num": m.group(1), "header": m.group(2), "lines": []}
            notes.append(current_note)
        elif current_note is not None:
            current_note["lines"].append(line)

    q_words = set(w for w in re.findall(r"\b\w+\b", question.lower()) if w not in _STOP_WORDS)
    matches = []

    for note in notes:
        text = " ".join(note["lines"])
        sentences = re.split(r"(?<=[.!?])\s+", text)
        for s in sentences:
            s_clean = s.strip()
            if not s_clean:
                continue
            s_words = set(re.findall(r"\b\w+\b", s_clean.lower()))
            overlap = len(q_words & s_words)
            if overlap > 0:
                matches.append((overlap, note["num"], s_clean))

    if not matches:
        return "The saved notes do not contain sufficient information to answer this question."

    matches.sort(key=lambda x: x[0], reverse=True)
    answers = []
    seen = set()
    for score, num, sent in matches[:3]:
        if sent not in seen:
            seen.add(sent)
            answers.append(f"[{num}] {sent}")

    return " ".join(answers)


async def _post_openai(path: str, body: dict, timeout_seconds: float) -> dict:
    """Execute authenticated HTTP POST request to OpenAI API."""
    if not config.openai_key:
        raise HttpError(503, "Set OPENAI_API_KEY in server/.env and restart the server.")

    try:
        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            response = await client.post(
                f"https://api.openai.com{path}",
                headers={
                    "authorization": f"Bearer {config.openai_key}",
                    "content-type": "application/json",
                },
                json=body,
            )
    except httpx.TimeoutException as error:
        raise HttpError(502, "OpenAI request timed out.") from error
    except httpx.HTTPError as error:
        raise HttpError(502, "OpenAI is unreachable.") from error

    if response.status_code in (401, 403):
        raise HttpError(503, "OpenAI rejected the API key.")
    if response.status_code == 429:
        raise HttpError(429, "OpenAI rate limit reached. Wait a moment and try again.")
    if response.status_code >= 400:
        print(f"OpenAI {path} failed with HTTP {response.status_code}")
        raise HttpError(502, "OpenAI request failed.")

    try:
        return response.json()
    except ValueError as error:
        raise HttpError(502, "OpenAI returned a response that was not JSON.") from error
