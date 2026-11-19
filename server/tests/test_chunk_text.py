import re

from app.services.chunk_text import CHUNK_TARGET, chunk_text


def test_blank_text_produces_no_chunks():
    assert chunk_text("   \n\t  ") == []


def test_a_short_note_stays_in_one_chunk():
    note = "Standup is at 10. Bring the deployment notes."
    assert chunk_text(note) == [note]


def test_long_text_stays_within_the_target_size_and_overlaps():
    chunks = chunk_text("alpha " * 400)
    assert len(chunks) >= 3
    assert all(len(chunk) <= CHUNK_TARGET for chunk in chunks)
    tail = chunks[0][-80:].strip()
    assert tail in chunks[1]


def test_a_paragraph_boundary_near_the_end_of_the_window_is_kept_intact():
    text = f"{'A' * 800}\n\n{'B' * 800}"
    chunks = chunk_text(text)
    assert re.fullmatch(r"A+", chunks[0])
    overlapped = next(chunk for index, chunk in enumerate(chunks) if index > 0 and "B" in chunk)
    assert "A" in overlapped
