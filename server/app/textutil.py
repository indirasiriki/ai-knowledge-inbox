import re


def normalize_whitespace(value) -> str:
    """Collapse messy spacing while keeping paragraph breaks."""
    text = str(value or "")
    text = text.replace("\u00a0", " ")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def clip(value, max_length: int) -> str:
    """One-line preview. Adds an ellipsis only when the text is cut."""
    flat = re.sub(r"\s+", " ", str(value or "")).strip()
    if len(flat) <= max_length:
        return flat
    if max_length <= 3:
        return flat[:max_length]
    return f"{flat[: max_length - 3].rstrip()}..."


def title_from_note(value) -> str:
    """The first non-empty line becomes the list title."""
    line = next((part.strip() for part in str(value or "").split("\n") if part.strip()), "")
    return clip(line or "Note", 80)


def limit_text(value, max_length: int) -> str:
    """Keep the front of a long page, preferring a word boundary."""
    text = str(value or "")
    if len(text) <= max_length:
        return text
    cut = text.rfind(" ", 0, max_length)
    end = cut if cut > max_length * 0.8 else max_length
    return text[:end].strip()
