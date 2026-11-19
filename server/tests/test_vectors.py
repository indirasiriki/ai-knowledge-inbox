from app.services.vectors import cosine_similarity, decode_vector, encode_vector


def test_identical_vectors_score_1():
    assert abs(cosine_similarity([1, 2, 3], [1, 2, 3]) - 1) < 1e-6


def test_orthogonal_vectors_score_0():
    assert cosine_similarity([1, 0], [0, 1]) == 0


def test_opposite_vectors_score_minus_1():
    assert abs(cosine_similarity([1, 0], [-1, 0]) + 1) < 1e-6


def test_a_zero_vector_scores_0():
    assert cosine_similarity([0, 0, 0], [4, 5, 6]) == 0


def test_mismatched_lengths_score_0():
    assert cosine_similarity([1, 0], [1, 0, 0]) == 0


def test_float_vectors_round_trip_through_a_byte_buffer():
    original = [0.25, -1.5, 3, 0.125]
    assert decode_vector(encode_vector(original)) == original
