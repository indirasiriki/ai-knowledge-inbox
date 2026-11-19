from app.textutil import normalize_whitespace

# Aim for this many characters, then step back to a natural break.
CHUNK_TARGET = 900
# Repeat this many characters so a sentence on the boundary stays searchable.
CHUNK_OVERLAP = 150
LOOKBACK = 280


def chunk_text(raw) -> list[str]:
    """Split saved text into overlapping windows.

    A short note stays one chunk. Longer text breaks near the end of each
    window on a paragraph, then a sentence, then a word.
    """
    text = normalize_whitespace(raw)
    if not text:
        return []
    if len(text) <= CHUNK_TARGET:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        hard_end = min(start + CHUNK_TARGET, len(text))
        end = hard_end if hard_end == len(text) else _choose_break(text, start, hard_end)
        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= len(text):
            break

        # Start the next window inside this one so the shared tail is searchable twice.
        overlapped = max(end - CHUNK_OVERLAP, start + 1)
        candidate = _snap_to_word(text, overlapped)
        start = candidate if start < candidate < len(text) else end

    return chunks


def _choose_break(text: str, start: int, hard_end: int) -> int:
    """Pick a break in the last part of the window so chunks stay near the target size."""
    lookback = min(LOOKBACK, (hard_end - start) // 2)
    floor = hard_end - lookback
    window = text[floor:hard_end]

    paragraph_at = window.rfind("\n\n")
    if paragraph_at != -1:
        return floor + paragraph_at

    sentence_at = max(window.rfind(". "), window.rfind("? "), window.rfind("! "))
    if sentence_at != -1:
        return floor + sentence_at + 1

    line_at = window.rfind("\n")
    if line_at != -1:
        return floor + line_at

    space_at = window.rfind(" ")
    if space_at != -1:
        return floor + space_at

    return hard_end


def _snap_to_word(text: str, index: int) -> int:
    """If the overlap starts mid-word, move forward to the next space."""
    cursor = index
    at_word = (
        cursor > 0
        and cursor < len(text)
        and not text[cursor].isspace()
        and not text[cursor - 1].isspace()
    )
    if at_word:
        space = text.find(" ", cursor)
        if space != -1 and space - cursor <= 40:
            cursor = space + 1

    while cursor < len(text) and text[cursor].isspace():
        cursor += 1
    return cursor
