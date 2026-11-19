import math
import struct


def encode_vector(values) -> bytes:
    """Little-endian float32, the same layout a browser would store."""
    return struct.pack(f"<{len(values)}f", *[float(value) for value in values])


def decode_vector(stored: bytes) -> list[float]:
    count = len(stored) // 4
    return list(struct.unpack(f"<{count}f", stored[: count * 4]))


def cosine_similarity(left, right) -> float:
    """1 means the same direction. 0 means unrelated. Mismatched lengths score 0."""
    if not left or len(left) != len(right):
        return 0.0

    dot = 0.0
    left_norm = 0.0
    right_norm = 0.0
    for left_value, right_value in zip(left, right):
        dot += left_value * right_value
        left_norm += left_value * left_value
        right_norm += right_value * right_value

    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / math.sqrt(left_norm * right_norm)
