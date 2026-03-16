# Instructor Notes — Session 2: Document Ingestion and Chunking

## Session Overview

- **Duration:** ~90 minutes
- **Split:** ~55% live coding, ~45% experimentation and discussion
- **Vibe:** First real RAG component. Students should leave understanding chunking intuitively and seeing how different file types get handled.

## Before Class

- [ ] Ensure Session 1 code is working (or copy from checkpoint)
- [ ] Have the `data/knowledge/` folder populated with all documents (markdown, CSV, and optionally PDF)
- [ ] Have a document open side-by-side with the terminal to show chunk boundaries visually
- [ ] Prepare to show chunking with different sizes (200, 500, 1000)
- [ ] Have `team-directory.csv` open to show what structured data looks like before/after loading

## What to Type Live vs Prebuilt

| Component | Live or Prebuilt? | Why? |
|-----------|-------------------|------|
| `rag/chunker.py` (fixed-size) | **Type live** | Core concept — must be built step by step |
| `rag/chunker.py` (sections) | **Type live** | Quick addition — shows alternative approach |
| `rag/loader.py` | **Type live** | Students need to see format dispatching |
| `routers/ingest.py` | **Type live** | Students need to see file loading logic |
| `models.py` updates | **Type live** | Small change, good reinforcement |
| `config.py` updates | **Type live** | Quick — just adding settings |
| `main.py` router mount | **Type live** | One line — shows how routers connect |
| `data/knowledge/*.md` | **Prebuilt** | Zero learning value in typing content |
| `data/knowledge/*.csv` | **Prebuilt** | Zero learning value in typing content |

## Suggested Live-Coding Order

1. **Open `leave-policy.md`** — "Here's one of our documents. How would you search this?"
2. **Discuss the problem** — "We can't paste all documents into every prompt. Why not?"
   - Token limits
   - Cost per request
   - Irrelevant noise drowning out the answer
3. **Create `rag/chunker.py`** — start with just the function signature
4. **Build the fixed-size chunking logic step by step:**
   a. First: just split by chunk_size, no overlap
   b. Demo it — show a sentence getting cut in half
   c. Add overlap — "See how the sentence is now in both chunks?"
5. **Add `chunk_by_sections()`** — "What if we split on headings instead?"
   - Show how the regex splits on `## ` headers
   - Discuss: chunks follow document structure, but sizes vary
6. **Open `team-directory.csv`** — "Not everything is markdown. How do we handle this?"
7. **Create `rag/loader.py`** — build the `load_file()` dispatcher
   - Start with `.md`/`.txt` branch (trivial)
   - Add `.csv` branch — show the "Column: Value" conversion
   - Mention `.pdf` and `.json` (students can read the code later)
8. **Update `models.py`** — add ChunkInfo and IngestResponse
9. **Update `config.py`** — add KNOWLEDGE_DIR, chunk settings, SUPPORTED_EXTENSIONS
10. **Create `routers/ingest.py`** — load files, chunk them, return results
    - Show the `chunk_strategy` query parameter
11. **Mount the router in `main.py`**
12. **Demo: POST /ingest** — show the chunks in Swagger UI
13. **Experiment: try different chunk sizes and strategies**

## Key Teaching Moments

### Building the Chunker (Steps 3-5)
Build fixed-size in two stages, then add sections:

**Stage 1 — Naive split (no overlap):**
```python
# Walk through this on the board or in comments first
# text = "ABCDEFGHIJ", chunk_size=4
# chunks: ["ABCD", "EFGH", "IJ"]
# Problem: what if "CDEF" was an important phrase? It's split across chunks.
```

**Stage 2 — Add overlap:**
```python
# text = "ABCDEFGHIJ", chunk_size=4, overlap=2
# chunks: ["ABCD", "CDEF", "EFGH", "GHIJ"]
# Now "CDEF" is a complete chunk! Overlap preserves boundary context.
```

**Stage 3 — Section-based alternative:**
```python
# "What if the document has clear sections? Let's split on headings instead."
# Pros: each chunk is a complete section, no mid-sentence cuts
# Cons: chunk sizes are unpredictable — some tiny, some huge
```

### The Multi-Format Loader (Steps 6-7)
This is a great "aha" moment. Open the CSV in the terminal, then show what it looks like after `load_file()` converts it:

```
Before: "Alice Chen,Engineering Lead,Engineering,NYC,alice.chen@acmecorp.com"
After:  "Name: Alice Chen\nRole: Engineering Lead\nDepartment: Engineering..."
```

Ask: "Which version would an LLM understand better?"

### The Chunking Strategy Comparison (Step 13)
Run both strategies on the same document and compare:

```bash
# Fixed-size on leave-policy.md
curl -X POST "http://localhost:8000/ingest?chunk_strategy=fixed"
# Count chunks, read a few

# Section-based on leave-policy.md
curl -X POST "http://localhost:8000/ingest?chunk_strategy=sections"
# Count chunks, compare boundaries
```

Ask: "Which chunks would be more useful for answering 'How many vacation days do I get?'"

### The Conflicting Documents Setup
Point out that `expense-policy.md` says the meal limit is $50, but `expense-policy-2024-update.md` says $75. Ask: "What will happen when we search for 'meal expense limit' later?" This sets up a recurring theme throughout the bootcamp.

### Connecting to Session 1
"In Session 1, we manually pasted leave policy text into the prompt. Now we've automated the first step: loading and chunking documents — regardless of their format. Next session, we'll make these chunks searchable."

## Common Student Questions

**"Why character-based chunking? Why not by paragraph or sentence?"**
That's exactly why we have two strategies! Character-based is the simplest to implement and understand. Section-based is a step toward structure-aware chunking. In production, you might use sentence-based, recursive, or even semantic chunking.

**"What's the right chunk size?"**
There's no universal answer. It depends on the documents and the questions. 400-600 characters is a reasonable default. The experiment in this session helps build intuition.

**"Why isn't chunking at word boundaries?"**
Good observation! Our simple chunker might cut mid-word. In production, you'd split on word or sentence boundaries. But for teaching, character-based chunking makes the overlap math obvious. Mention this as a TODO exercise.

**"Where do the chunks go after /ingest returns?"**
Nowhere yet! They're just returned in the response so we can inspect them. Session 3 will add embedding and storage.

**"Why convert CSV to text instead of keeping it structured?"**
Embeddings work on text — they don't understand CSV structure. By converting to "Column: Value" format, we make the data searchable in the same way as our markdown documents. More advanced approaches might preserve table structure differently.

## Lab Exercise Ideas

1. **Chunk size comparison:** Each student picks a different chunk_size, shares their results
2. **Strategy comparison:** All students run both `fixed` and `sections` on the same document, compare chunk counts and quality
3. **Find the best chunk:** Given the question "How do I request leave?", which strategy + chunk_size produces a chunk that best answers it?
4. **Boundary analysis:** Find a chunk that cuts a sentence awkwardly. What overlap value fixes it?
5. **CSV inspection:** Look at the chunks from `team-directory.csv`. Does the "Column: Value" format make sense? Would you do it differently?
6. **TODO in code:** Students can try adding a `min_chunk_size` parameter that drops chunks below a threshold

## Timing Guide

| Activity | Time |
|----------|------|
| Recap Session 1 + setup | 10 min |
| Discussion: why chunking? | 10 min |
| Live code: chunker.py (step by step) | 20 min |
| Live code: models + config updates | 5 min |
| Live code: ingest router | 15 min |
| Demo: /ingest with different sizes | 10 min |
| Student experimentation | 10 min |
| Discussion + Q&A | 10 min |

## If You're Running Short on Time

Skip building the chunker in two stages (naive then overlap). Just build the final version and explain the overlap concept verbally. The ingest endpoint demo is more important.

## If You Have Extra Time

- Challenge: "Can you modify the chunker to split on paragraph boundaries (double newlines) instead of character count?"
- Preview Session 3: "Now that we have chunks, how do we search them? Not by keywords — by meaning. That's what embeddings do."
- Discuss: "What metadata should we store with each chunk?" (source, position, section heading, etc.)
