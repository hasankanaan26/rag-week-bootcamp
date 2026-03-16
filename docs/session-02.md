# Session 2 — Document Ingestion and Chunking

## Learning Goals

By the end of this session, students should be able to:

1. Explain why documents need to be chunked for RAG
2. Implement a character-based chunking function with overlap
3. Describe the tradeoffs of different chunk sizes
4. Build an ingestion endpoint that loads and chunks files
5. Load multiple file formats (Markdown, CSV, PDF, JSON) into a RAG pipeline
6. Compare fixed-size vs section-based chunking strategies

## Concepts Introduced

### Why Chunk Documents?

Three reasons you can't just paste entire documents into the prompt:

1. **Token limits** — LLMs have a maximum context window. A 50-page document won't fit.
2. **Cost** — More tokens in the prompt = more money per API call.
3. **Noise** — If you paste an entire document, most of it is irrelevant to the question. The LLM has to find the needle in the haystack, and sometimes it picks the wrong needle.

Chunking solves all three: break the document into small pieces, and later retrieve only the relevant ones.

### What Makes a Good Chunk?

- **Self-contained**: A chunk should make sense on its own, without needing the rest of the document.
- **Right-sized**: Big enough to contain useful information, small enough to be precise.
- **Overlapping**: Consecutive chunks should overlap slightly, so sentences at boundaries don't get cut in half.

### Chunk Size Tradeoffs

| Chunk Size | Pros | Cons |
|------------|------|------|
| Small (200 chars) | Precise retrieval, less noise | May lack context, fragments sentences |
| Medium (500 chars) | Good balance of precision and context | May include some irrelevant info |
| Large (1000+ chars) | Rich context per chunk | Less precise retrieval, uses more tokens |

### Multi-Format File Loading

Real knowledge bases aren't all markdown. Our loader supports:

| Format | Extension | How It's Converted |
|--------|-----------|-------------------|
| Markdown / Text | `.md`, `.txt` | Read as-is |
| CSV | `.csv` | Each row → "Column: Value" lines |
| PDF | `.pdf` | Text extracted from all pages via pypdf |
| JSON | `.json` | Key-value pairs flattened to readable text |

The key insight: **convert everything to plain text first, then chunk it**. This keeps the chunker simple — it only deals with text strings.

### Chunking Strategies

| Strategy | How It Works | Best For |
|----------|-------------|----------|
| **Fixed-size** | Split every N characters with overlap | Uniform chunks, predictable sizes |
| **Section-based** | Split on headings (`##`) or paragraph breaks | Structured documents with clear sections |

Neither strategy is universally better. Fixed-size is predictable but may cut mid-sentence. Section-based respects document structure but produces chunks of wildly different sizes.

## Files Created / Modified

| File | Change |
|------|--------|
| `app/rag/chunker.py` | **New** — `chunk_document()` + `chunk_by_sections()` |
| `app/rag/loader.py` | **New** — multi-format file loader |
| `app/routers/ingest.py` | **New** — `/ingest` endpoint with format + strategy support |
| `app/models.py` | **Updated** — added ChunkInfo and IngestResponse |
| `app/config.py` | **Updated** — added KNOWLEDGE_DIR, chunk settings, SUPPORTED_EXTENSIONS |
| `app/main.py` | **Updated** — mounted ingest router |

## Demo Script

### 1. Ingest with default settings

```bash
curl -X POST http://localhost:8000/ingest
```

Look at the response: how many files were processed? How many total chunks? Notice that CSV and PDF files are included now — not just markdown.

### 2. Try different chunk sizes

```bash
# Small chunks
curl -X POST "http://localhost:8000/ingest?chunk_size=200&overlap=20"

# Large chunks
curl -X POST "http://localhost:8000/ingest?chunk_size=1000&overlap=100"
```

Compare: How does the number of chunks change? Read a few chunks — which size produces the most useful pieces?

### 3. Compare chunking strategies

```bash
# Fixed-size (default)
curl -X POST "http://localhost:8000/ingest?chunk_strategy=fixed"

# Section-based
curl -X POST "http://localhost:8000/ingest?chunk_strategy=sections"
```

Compare the chunks: section-based chunks follow heading boundaries. Fixed-size chunks are all roughly the same length.

### 4. Inspect chunk boundaries

Look at consecutive chunks from the same file. Can you see where they overlap? Find a sentence that appears in two consecutive chunks — that's the overlap at work.

### 5. Look at CSV chunks

Find the chunks from `team-directory.csv`. Each employee record becomes "Name: ..., Role: ..., Department: ..." text. How does this look compared to the markdown chunks?

## Lab Exercise

**TODO markers in the code:** Students can try:

1. Modify `chunk_size` and `overlap` parameters and observe the results
2. Count how many chunks each document produces at different sizes
3. Find a chunk that would be a good answer to "How many vacation days do I get?"
4. Find a chunk that got cut awkwardly — how would you fix it?
5. Compare fixed vs section-based chunking on `leave-policy.md` — which produces better chunks?
6. Look at the CSV chunks — would you chunk a CSV differently than a markdown file?

## Discussion Questions

- "What chunk size would you choose for short FAQ-style documents vs long policy documents?"
- "What happens if overlap is zero? When might that be okay?"
- "Fixed-size chunking splits on character count. Section-based splits on headings. Can you think of other strategies?" (Hint: by sentence, by token count, recursive)
- "The CSV loader turns rows into 'Column: Value' text. Is there a better way to represent tabular data for RAG?"
- "If two documents contain conflicting information (e.g., old vs new expense limits), how should the RAG system handle that?"
- "Right now, chunks are just printed. Where should we store them so we can search them later?"

That last question leads into Session 3: Embeddings and Vector Storage.
