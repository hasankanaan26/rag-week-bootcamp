# ============================================================
# Chunker — splits a document into overlapping text chunks
# ============================================================
# This is the first piece of RAG infrastructure students build.
#
# WHY CHUNKING?
#   - LLMs have token limits — we can't paste entire documents.
#   - Even if we could, most of the document is irrelevant to
#     any single question. Passing everything wastes tokens and
#     adds noise that confuses the LLM.
#   - Chunks let us retrieve ONLY the relevant pieces later.
#
# WHY OVERLAP?
#   - A sentence might be split across two chunks.
#   - Overlap ensures important context at chunk boundaries
#     isn't lost. Try overlap=0 and overlap=50 to see the
#     difference in where sentences get cut.
#
# TRADEOFFS:
#   - Small chunks (200 chars): precise retrieval, but may
#     lose context. A single chunk might not have enough info.
#   - Large chunks (1000+ chars): more context per chunk, but
#     retrieval is less precise and uses more tokens.
#   - 400-600 chars is a reasonable starting point.
#
# TODO (Lab exercise): Try different chunk_size values (200,
# 500, 1000) on the same document and compare the chunks.
# Which size gives the most useful chunks for Q&A?
# ============================================================


# Purpose:
# Splits text into smaller chunks so retrieval works on meaningful units
# instead of whole documents. Uses a fixed character window with overlap.
def chunk_document(
    text: str,
    source: str,
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[dict]:
    """
    Split a document into overlapping text chunks.

    Args:
        text: The full document text to split.
        source: Filename or identifier for this document.
        chunk_size: Maximum number of characters per chunk.
        overlap: Number of characters to overlap between chunks.

    Returns:
        A list of dicts, each with: text, source, chunk_index.
    """
    text = text.strip()

    if len(text) <= chunk_size:
        return [{"text": text, "source": source, "chunk_index": 0}]

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


# ============================================================
# Section-based chunker — splits on paragraph or heading breaks
# ============================================================
# ALTERNATIVE STRATEGY:
#   Instead of splitting every N characters, split on document
#   structure: blank lines (paragraphs) or markdown headings.
#
# WHEN TO USE THIS:
#   - Documents have clear sections (e.g., policy docs with headers)
#   - You want each chunk to be a "complete thought"
#
# TRADEOFFS vs fixed-size:
#   - Pros: Chunks follow natural document structure, no mid-sentence cuts
#   - Cons: Chunk sizes are unpredictable — some sections are tiny,
#     others are huge. No overlap between sections.
#
# TODO (Lab exercise): Run both strategies on the same document.
# Compare chunk counts and read a few chunks — which ones
# would you rather search against?
# ============================================================

import re


# Purpose:
# Splits text on markdown headings or blank lines, keeping each section
# as a self-contained chunk. Preserves document structure.
def chunk_by_sections(text: str, source: str) -> list[dict]:
    """
    Split a document into chunks based on markdown headings or
    blank-line-separated paragraphs.

    Args:
        text: The full document text.
        source: Filename or identifier for this document.

    Returns:
        A list of dicts, each with: text, source, chunk_index.
    """
    text = text.strip()

    # Try splitting on markdown headings first (## or #)
    sections = re.split(r"\n(?=#{1,3}\s)", text)

    # If no headings found, fall back to splitting on double newlines
    if len(sections) <= 1:
        sections = re.split(r"\n\n+", text)

    chunks = []
    for i, section in enumerate(sections):
        section = section.strip()
        if section:
            chunks.append({
                "text": section,
                "source": source,
                "chunk_index": i,
            })

    return chunks
