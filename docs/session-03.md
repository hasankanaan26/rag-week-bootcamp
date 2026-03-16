# Session 3 — Embeddings and Vector Storage

## Learning Goals

By the end of this session, students should be able to:

1. Explain what an embedding is and why it enables semantic search
2. Generate embeddings from text using an API
3. Store chunks with embeddings in a vector database
4. Search for relevant chunks by meaning, not keywords

## Concepts Introduced

### What Is an Embedding?

An embedding is a list of numbers (a vector) that represents the meaning of a piece of text. The key property: **texts with similar meanings produce similar vectors**.

```
"How many vacation days do I get?"  → [0.023, -0.041, 0.078, ...]
"What is the annual leave policy?"  → [0.025, -0.039, 0.081, ...]
"quantum physics homework"         → [0.512, 0.203, -0.445, ...]
```

The first two vectors are close together (similar meaning).
The third is far away (different meaning).

### How Vector Search Works

1. At ingestion time: embed each chunk → store chunk + vector in ChromaDB
2. At query time: embed the question → find chunks with the closest vectors
3. "Closest" is measured by distance — lower distance = more relevant

### What Is ChromaDB?

A vector database. It stores text alongside its vector embedding and lets you search by similarity. Think of it as "a database that understands meaning."

We use ChromaDB because it's simple: no separate server needed, clean Python API, works in-process. In production, you might use Pinecone, Weaviate, pgvector, or others — the RAG pattern stays the same.

## Files Created / Modified

| File | Change |
|------|--------|
| `app/rag/embedder.py` | **New** — embedding generation |
| `app/rag/store.py` | **New** — ChromaDB wrapper |
| `app/routers/search.py` | **New** — `/search` endpoint |
| `app/routers/embed.py` | **New** — `/embed` debug endpoint for exploring embeddings |
| `app/routers/ingest.py` | **Updated** — now embeds and stores chunks, multi-format + chunking strategies |
| `app/rag/loader.py` | **Inherited** — multi-format file loader from Session 2 |
| `app/rag/chunker.py` | **Inherited** — fixed + section-based chunking from Session 2 |
| `app/config.py` | **Updated** — embedding model, ChromaDB path, SUPPORTED_EXTENSIONS |
| `app/models.py` | **Updated** — added SearchResult, SearchResponse, EmbedRequest, EmbedResponse |
| `app/main.py` | **Updated** — mounted search, inspect, and embed routers |

## Demo Script

### 1. Ingest documents (now with embeddings)

```bash
curl -X POST http://localhost:8000/ingest
```

Notice the response now includes `chunks_stored`. The chunks are in ChromaDB.

### 2. Search for relevant chunks

```bash
curl "http://localhost:8000/search?q=How+many+vacation+days+do+I+get"
```

Look at the results: the leave policy chunks should appear with low distance scores.

### 3. Try a semantically similar query (different words, same meaning)

```bash
curl "http://localhost:8000/search?q=annual+leave+entitlement"
```

Same chunks found — even though the words are completely different! That's embeddings at work.

### 4. Try an irrelevant query

```bash
curl "http://localhost:8000/search?q=quantum+physics"
```

Results will have high distance scores. The system found "something" (it always returns top_k results) but the distances show nothing is really relevant.

### 5. Intentionally vague query

```bash
curl "http://localhost:8000/search?q=Tell+me+about+the+rules"
```

Results from multiple documents, all with mediocre distances. This shows why some queries work better than others — specificity matters.

### 6. Explore embeddings with /embed

The `/embed` endpoint lets you compare any texts in vector space:

```bash
curl -X POST http://localhost:8000/embed \
  -H "Content-Type: application/json" \
  -d '{"texts": ["vacation days", "annual leave", "Python programming"]}'
```

The response shows pairwise distances:
- "vacation days" ↔ "annual leave" → **low distance** (similar meaning)
- "vacation days" ↔ "Python programming" → **high distance** (different meaning)

Try more experiments:
```bash
# Synonyms
curl -X POST http://localhost:8000/embed \
  -H "Content-Type: application/json" \
  -d '{"texts": ["sick leave", "health absence", "medical time off"]}'

# Question vs. answer
curl -X POST http://localhost:8000/embed \
  -H "Content-Type: application/json" \
  -d '{"texts": ["How many vacation days?", "Employees receive 20 days of annual leave"]}'
```

### What's in a Vector?

Embeddings are lists of numbers — hundreds or thousands of them. Each number captures one aspect of meaning. You can't look at a single number and say "this means vacation" — the meaning emerges from the pattern of ALL numbers together.

| Embedding Model | Dimensions | Notes |
|-----------------|-----------|-------|
| text-embedding-004 (Google) | 768 | Good general-purpose model |
| gemini-embedding-001 (Google) | 768 | Newer, recommended for RAG |
| text-embedding-3-small (OpenAI) | 1536 | Good balance of quality/cost |
| text-embedding-3-large (OpenAI) | 3072 | Highest quality, most expensive |

More dimensions ≠ always better. The model's training matters more than the dimension count.

### Distance Metrics

The distance between two vectors can be measured in different ways:

| Metric | Range | What it measures |
|--------|-------|-----------------|
| L2 (Euclidean) | 0 to ∞ | Straight-line distance in vector space |
| Cosine | 0 to 2 | Angle between vectors (0 = same direction) |
| Inner Product | -∞ to ∞ | How aligned vectors are |

ChromaDB defaults to L2. For most RAG use cases, L2 and cosine give similar results.

## Lab Exercises

1. **Semantic vs keyword search:** Search for "PTO" and see if it finds the leave policy (it should — embeddings understand synonyms)
2. **Distance exploration:** Search for 5 different queries. Which ones produce low distances? Which produce high?
3. **Re-ingestion:** Hit `/ingest` twice. Does the chunk count double? (No — we use upsert)
4. **Fresh ingestion:** Hit `/ingest?fresh=true` — this clears and re-indexes

## Discussion Questions

- "We searched for 'vacation days' and found the leave policy. But we could also have searched for 'time off', 'PTO', or 'holidays'. Why does this work when keyword search wouldn't?"
- "The search always returns results, even for 'quantum physics'. How should we decide if a result is actually relevant?" (Leads into Session 6: confidence thresholds)
- "What would happen if we had 10,000 documents instead of 6? Would this still work?" (Yes — vector search scales well)
