# Checkpoint 4 — Failure Modes, Analysis, and Visualization

## Objective

Handle RAG failures gracefully, add transparency, and visualize how embeddings work.

## What's Covered

- **Confidence scoring:** Classifying retrieval quality (high/medium/low/none)
- **No-result handling:** Detecting when nothing relevant was found
- **Weak-evidence warnings:** Alerting users when results may be unreliable
- **Failure mode gallery:** Subjective, temporal, and cross-domain questions
- **Browser UI:** Transparent interface with confidence badges
- **Embedding visualization:** t-SNE and PCA scatter plots

## What's New in This Checkpoint

| File | What it does |
|------|-------------|
| `app/rag/retriever.py` | Adds `score_confidence()` and `is_no_result()` |
| `app/rag/visualize.py` | t-SNE/PCA dimensionality reduction + plotting |
| `app/routers/query.py` | Now with confidence scoring and threshold overrides |
| `app/routers/compare.py` | Now with confidence in RAG results |
| `app/routers/visualize.py` | `GET /visualize` — returns PNG scatter plot |
| `app/routers/ui.py` | `GET /ui` — browser workbench covering every endpoint |
| `app/static/query.html` | Workbench page: Ask, Compare, LLM only, Search, Embeddings, Ingest, Store, Visualize |
| `app/static/ui.js`, `ui.css` | Workbench logic (vanilla JS) and styles |
| `app/rag/store_chroma.py`, `store_postgres.py` | Interchangeable vector stores, chosen by `VECTOR_STORE` |
| `app/config.py` | Adds confidence thresholds, `VECTOR_STORE` and `DATABASE_URL` |

## How to Run

```bash
python run_checkpoint.py checkpoint-4-analysis
```

**Important:** Run `POST /ingest` first, then try the endpoints below.

## Demo Questions

Open http://localhost:8000/ui for the browser interface.

| Question | Expected Behavior |
|----------|------------------|
| "How many vacation days do I get?" | High confidence, green badge |
| "What is our Git branching strategy?" | High confidence |
| "What about time off?" | Medium confidence (vague query) |
| "Tell me about quantum physics" | No result (out of domain) |
| "What are the rules?" | Low confidence (too broad) |

**Failure mode questions** (try on `/compare`):
- "Is the leave policy generous?" — subjective, RAG retrieves facts but can't judge
- "What changed in the latest policy update?" — temporal, docs don't track versions
- "Compare our benefits to Google's" — cross-domain, RAG only knows Acme Corp

## Visualization

After ingesting documents:
- `GET /visualize` — t-SNE scatter plot (default)
- `GET /visualize?method=pca` — PCA scatter plot

Each dot is a chunk. Color = source document. Nearby dots = similar meaning.

## What to Type Live

Good candidates for live coding:
- `score_confidence()` and `is_no_result()` in `retriever.py`
- The no-result handling logic in `query.py`
- Discussion of threshold values and their effects
- Walk through `visualize.py` (explain, don't necessarily type)

Pre-built (skip live coding):
- `query.html` (frontend, not the focus)
- `visualize.py` plotting code (explain the concept, show the output)
