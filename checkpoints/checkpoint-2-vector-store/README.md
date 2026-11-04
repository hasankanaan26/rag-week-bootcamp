# Checkpoint 2 — Vector Store and Retrieval

## Objective

Build a vector store with ChromaDB and understand semantic search.

## What's Covered

- **Embeddings:** How text becomes a vector that captures meaning
- **ChromaDB:** Storing chunks with their embedding vectors
- **Semantic search:** Finding relevant chunks by meaning, not keywords
- **Metadata:** Tracking source files and chunk indexes for traceability
- **Embedding exploration:** Measuring distance between concepts

## What's New in This Checkpoint

| File | What it does |
|------|-------------|
| `app/rag/embedder.py` | Converts text to embedding vectors (Gemini or Azure) |
| `app/rag/store.py` | ChromaDB wrapper — add, search, inspect, clear |
| `app/routers/search.py` | `/search` — semantic search without LLM |
| `app/routers/embed.py` | `/embed` — explore pairwise embedding distances |
| `app/routers/inspect.py` | `/store/inspect` — see what's stored in ChromaDB |
| `app/routers/ingest.py` | Updated — now embeds and stores chunks |

## How to Run

```bash
python run_checkpoint.py checkpoint-2-vector-store
```

**Important:** Run `POST /ingest` first to populate the vector store!

## Demo Questions

Try these on `/search`:

| Query | Expected Result |
|-------|----------------|
| "How many vacation days do I get?" | leave-policy.md (low distance) |
| "What is our Git branching strategy?" | coding-standards.md |
| "Can I work from home?" | remote-work.md |
| "annual leave" | Same chunks as "vacation days" (semantic match!) |
| "quantum physics" | High distances (nothing relevant) |

Try these on `/embed`:
```json
{"texts": ["vacation days", "annual leave", "time off"]}
```
All three should have low distances (similar meaning).

```json
{"texts": ["vacation days", "Python programming"]}
```
High distance (different topics).

## What to Type Live

Good candidates for live coding:
- `embed_text()` and `embed_texts()` in `embedder.py`
- `add_chunks()` and `search()` in `store.py`
- The `/search` endpoint in `search.py`

Pre-built (skip live coding):
- `inspect.py` (useful but not core)
- `embed.py` (exploration tool, can demo but no need to type)
