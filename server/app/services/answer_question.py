from app.config import config
from app.db.chunks_repo import count_chunks
from app.services.language_api import complete_chat, embed_texts, is_live_openai
from app.services.retrieve import retrieve_chunks
from app.textutil import clip

# System prompt enforcing grounded answers and source citations
SYSTEM_PROMPT = " ".join([
    "Answer the question using only the numbered notes in the user message.",
    "If the notes do not contain the answer, say so in one or two sentences.",
    "Write plain sentences.",
    "When a note supports a sentence, cite it as [1] or [2].",
    "Do not add facts that are not in the notes.",
])


async def answer_question(db, question: str) -> dict:
    """Run RAG pipeline: embed query, retrieve matching chunks, generate LLM response with citations."""
    # Fast path: if inbox has no saved content, return immediately without calling OpenAI
    if count_chunks(db) == 0:
        return {
            "answer": "Nothing is saved yet. Add a note or a link first.",
            "sources": [],
        }

    # Step 1: Embed the user's question
    vectors = await embed_texts([question])

    # Step 2: Retrieve top matching chunks meeting minimum similarity threshold
    min_threshold = 0.08 if not is_live_openai() else config.min_score
    matches = [
        match for match in retrieve_chunks(db, vectors[0], config.top_k)
        if match["score"] >= min_threshold
    ]
    if not matches:
        return {
            "answer": "None of the saved notes look related to that question.",
            "sources": [],
        }

    # Step 3: Send question + retrieved context chunks to LLM
    answer = await complete_chat(SYSTEM_PROMPT, _user_message(question, matches))

    # Step 4: Return answer and formatted source cards with relevance match scores
    return {
        "answer": answer,
        "sources": [
            {
                "label": index + 1,
                "itemId": match["itemId"],
                "title": match["title"],
                "sourceType": match["sourceType"],
                "sourceUrl": match["sourceUrl"],
                "snippet": clip(match["content"], 320),
                "score": round(match["score"], 4),
            }
            for index, match in enumerate(matches)
        ],
    }


def _user_message(question: str, matches: list[dict]) -> str:
    """Format user prompt containing the question and numbered context chunks for citation."""
    notes = []
    for index, match in enumerate(matches):
        origin = f"{match['title']} ({match['sourceUrl']})" if match["sourceUrl"] else match["title"]
        notes.append(f"[{index + 1}] {origin}\n{match['content']}")
    return f"Question: {question}\n\nNotes:\n" + "\n\n".join(notes)
