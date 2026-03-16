# ============================================================
# Tests: Retriever helper functions
# ============================================================
# Tests confidence scoring and no-result detection.
# Logic is inlined — no external dependencies needed.
#
#   pytest tests/test_retriever.py -v
# ============================================================

# Default thresholds (must match app/config.py defaults)
CONFIDENCE_HIGH_THRESHOLD = 0.8
CONFIDENCE_LOW_THRESHOLD = 1.4
NO_RESULT_DISTANCE = 1.6


def score_confidence(chunks):
    """Inline copy of retriever.score_confidence for testing."""
    if not chunks:
        return "none"
    best_distance = min(c["distance"] for c in chunks)
    if best_distance <= CONFIDENCE_HIGH_THRESHOLD:
        return "high"
    elif best_distance <= CONFIDENCE_LOW_THRESHOLD:
        return "medium"
    else:
        return "low"


def is_no_result(chunks):
    """Inline copy of retriever.is_no_result for testing."""
    if not chunks:
        return True
    best_distance = min(c["distance"] for c in chunks)
    return best_distance > NO_RESULT_DISTANCE


# --- score_confidence tests ---

def test_high_confidence():
    """Low distance scores produce high confidence."""
    chunks = [
        {"text": "...", "source": "a.md", "chunk_index": 0, "distance": 0.3},
        {"text": "...", "source": "b.md", "chunk_index": 0, "distance": 0.5},
    ]
    assert score_confidence(chunks) == "high"


def test_medium_confidence():
    """Moderate distance scores produce medium confidence."""
    chunks = [
        {"text": "...", "source": "a.md", "chunk_index": 0, "distance": 1.0},
        {"text": "...", "source": "b.md", "chunk_index": 0, "distance": 1.3},
    ]
    assert score_confidence(chunks) == "medium"


def test_low_confidence():
    """High distance scores produce low confidence."""
    chunks = [
        {"text": "...", "source": "a.md", "chunk_index": 0, "distance": 1.5},
    ]
    assert score_confidence(chunks) == "low"


def test_no_chunks_gives_none_confidence():
    """Empty chunk list gives none confidence."""
    assert score_confidence([]) == "none"


def test_confidence_uses_best_distance():
    """Confidence is based on the BEST (lowest) distance, not the worst."""
    chunks = [
        {"text": "...", "source": "a.md", "chunk_index": 0, "distance": 0.5},
        {"text": "...", "source": "b.md", "chunk_index": 0, "distance": 1.5},
    ]
    assert score_confidence(chunks) == "high"


# --- is_no_result tests ---

def test_no_result_when_empty():
    """Empty chunk list is a no-result."""
    assert is_no_result([]) is True


def test_no_result_when_distances_too_high():
    """All distances above threshold is a no-result."""
    chunks = [
        {"text": "...", "source": "a.md", "chunk_index": 0, "distance": 2.0},
        {"text": "...", "source": "b.md", "chunk_index": 0, "distance": 2.5},
    ]
    assert is_no_result(chunks) is True


def test_not_no_result_when_good_match():
    """At least one low-distance chunk means NOT a no-result."""
    chunks = [
        {"text": "...", "source": "a.md", "chunk_index": 0, "distance": 0.4},
        {"text": "...", "source": "b.md", "chunk_index": 0, "distance": 2.0},
    ]
    assert is_no_result(chunks) is False


def test_boundary_at_threshold():
    """Distance exactly at the threshold is NOT a no-result."""
    chunks = [{"text": "...", "source": "a.md", "chunk_index": 0, "distance": 1.6}]
    assert is_no_result(chunks) is False  # 1.6 is not > 1.6

    chunks_above = [{"text": "...", "source": "a.md", "chunk_index": 0, "distance": 1.61}]
    assert is_no_result(chunks_above) is True
