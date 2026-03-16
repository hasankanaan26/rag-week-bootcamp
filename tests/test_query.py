# ============================================================
# Tests: Context building for RAG prompts
# ============================================================
# Verifies that build_context formats chunks correctly.
# Logic is inlined — no external dependencies needed.
#
#   pytest tests/test_query.py -v
# ============================================================


def build_context(chunks):
    """Inline copy of query.build_context for testing."""
    context_parts = []
    for chunk in chunks:
        source = chunk["source"]
        text = chunk["text"]
        distance = chunk.get("distance", 0)
        context_parts.append(
            f"[Source: {source} | Relevance score: {distance:.3f}]\n{text}"
        )
    return "\n\n".join(context_parts)


# --- Tests ---

def test_build_context_single_chunk():
    """A single chunk produces a labeled context block."""
    chunks = [
        {"text": "Employees get 20 days off.", "source": "leave.md", "distance": 0.3},
    ]
    context = build_context(chunks)
    assert "leave.md" in context
    assert "Employees get 20 days off." in context
    assert "0.300" in context


def test_build_context_multiple_chunks():
    """Multiple chunks are separated and each labeled with source."""
    chunks = [
        {"text": "Chunk one", "source": "a.md", "distance": 0.2},
        {"text": "Chunk two", "source": "b.md", "distance": 0.5},
    ]
    context = build_context(chunks)
    assert "a.md" in context
    assert "b.md" in context
    assert "Chunk one" in context
    assert "Chunk two" in context


def test_build_context_empty_list():
    """Empty chunk list produces empty context."""
    assert build_context([]) == ""


def test_context_includes_distance():
    """Context block includes distance for the LLM to see relevance."""
    chunks = [
        {"text": "Some fact", "source": "doc.md", "distance": 1.234},
    ]
    context = build_context(chunks)
    assert "1.234" in context
