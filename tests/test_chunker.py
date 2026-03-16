# ============================================================
# Tests: Chunking behavior
# ============================================================
# Zero external dependencies — logic is inlined so students
# can run these without installing anything except pytest.
#
#   pip install pytest
#   pytest tests/test_chunker.py -v
# ============================================================


def chunk_document(text, source, chunk_size=500, overlap=50):
    """
    Inline copy of the chunker for dependency-free testing.
    Must stay in sync with app/rag/chunker.py.
    """
    text = text.strip()
    if not text:
        return []

    chunks = []
    start = 0
    chunk_index = 0

    while start < len(text):
        end = start + chunk_size
        chunk_text = text[start:end].strip()

        if chunk_text:
            chunks.append({
                "text": chunk_text,
                "source": source,
                "chunk_index": chunk_index,
            })
            chunk_index += 1

        start += chunk_size - overlap

    return chunks


# --- Tests ---

def test_basic_chunking():
    """Chunking produces the expected number of chunks."""
    text = "A" * 100
    chunks = chunk_document(text, source="test.md", chunk_size=50, overlap=0)
    assert len(chunks) == 2
    assert all(c["source"] == "test.md" for c in chunks)


def test_chunk_overlap():
    """Overlapping chunks share text at boundaries."""
    text = "ABCDEFGHIJKL"  # 12 characters
    chunks = chunk_document(text, source="test.md", chunk_size=6, overlap=2)
    assert len(chunks) >= 2
    assert chunks[0]["text"][-2:] == chunks[1]["text"][:2]


def test_chunk_indexes_are_sequential():
    """Each chunk gets a sequential index starting from 0."""
    text = "Word " * 100
    chunks = chunk_document(text, source="doc.md", chunk_size=100, overlap=10)
    indexes = [c["chunk_index"] for c in chunks]
    assert indexes == list(range(len(chunks)))


def test_chunk_source_preserved():
    """Every chunk carries the source filename."""
    chunks = chunk_document("Some text here", source="policy.md", chunk_size=100, overlap=0)
    assert len(chunks) == 1
    assert chunks[0]["source"] == "policy.md"


def test_empty_text_returns_no_chunks():
    """Empty or whitespace-only text produces no chunks."""
    assert chunk_document("", source="e.md", chunk_size=100, overlap=0) == []
    assert chunk_document("   ", source="b.md", chunk_size=100, overlap=0) == []


def test_text_shorter_than_chunk_size():
    """Text shorter than chunk_size produces exactly one chunk."""
    chunks = chunk_document("Short", source="s.md", chunk_size=500, overlap=50)
    assert len(chunks) == 1
    assert chunks[0]["text"] == "Short"


def test_chunk_dict_has_required_keys():
    """Each chunk dict has text, source, and chunk_index."""
    chunks = chunk_document("Hello world", source="t.md", chunk_size=100, overlap=0)
    for chunk in chunks:
        assert "text" in chunk
        assert "source" in chunk
        assert "chunk_index" in chunk
