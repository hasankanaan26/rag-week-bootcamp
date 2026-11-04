# Checkpoint 1 — Foundations of RAG

## Objective

Understand why RAG is needed and how documents are prepared for retrieval.

## What's Covered

- **The hallucination problem:** Plain LLMs make up facts about your private data
- **Grounding:** Injecting real context into the prompt fixes accuracy
- **Document loading:** Reading different file formats into plain text
- **Chunking:** Splitting documents into retrievable units
- **Chunking strategies:** Fixed-size with overlap vs section-based splitting

## What's New in This Checkpoint

| File | What it does |
|------|-------------|
| `app/routers/ask.py` | `/ask` (plain LLM) and `/ask/grounded` (hardcoded context) |
| `app/routers/ingest.py` | `/ingest` — loads and chunks documents |
| `app/rag/loader.py` | Reads .md, .txt, .csv, .pdf, .json into plain text |
| `app/rag/chunker.py` | Fixed-size chunking with overlap + section-based chunking |
| `app/prompts/grounded_answer.py` | Grounding prompt with hardcoded leave policy |

## How to Run

```bash
# From the repo root:
python run_checkpoint.py checkpoint-1-foundations

# Or directly:
cd checkpoints/checkpoint-1-foundations
uvicorn app.main:app --reload
```

Open http://localhost:8000/docs for the Swagger UI.

## Demo Questions

Try these on **both** `/ask` and `/ask/grounded`:

| Question | `/ask` (plain) | `/ask/grounded` |
|----------|---------------|----------------|
| "How many vacation days do I get?" | Invents a number | 20 days (correct) |
| "What is our parental leave policy?" | Generic answer | 16 weeks primary, 4 weeks secondary |
| "What is the Git branching strategy?" | Makes something up | Not in hardcoded context |

Then try `/ingest` with different parameters:
- `POST /ingest` — default (500 char chunks, 50 overlap)
- `POST /ingest?chunk_size=200` — smaller chunks
- `POST /ingest?chunk_size=1000` — larger chunks
- `POST /ingest?chunk_strategy=sections` — section-based splitting

## What to Type Live

Good candidates for live coding during this session:
- The `/ask` endpoint in `ask.py` (simple, shows the hallucination problem)
- The `chunk_document()` function in `chunker.py` (core algorithm, easy to explain)
- The grounded prompt in `grounded_answer.py` (shows the grounding idea)

Pre-built (skip live coding):
- `loader.py` (format parsing is tedious to type)
- `config.py`, `llm.py` (boilerplate)
