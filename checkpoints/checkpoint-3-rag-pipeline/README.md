# Checkpoint 3 — Retrieval to Generation Wiring

## Objective

Wire the full RAG pipeline: retrieve relevant chunks, inject them into a prompt, and generate a grounded answer.

## What's Covered

- **The RAG loop:** Retrieve -> Build context -> Generate answer
- **Retriever module:** Orchestrating embed + search in one step
- **RAG prompt engineering:** Strict vs minimal grounding prompts
- **Source attribution:** Showing which documents were used
- **RAG vs plain comparison:** Side-by-side to show value
- **Structured logging:** Tracing pipeline execution in real time

## What's New in This Checkpoint

| File | What it does |
|------|-------------|
| `app/rag/retriever.py` | `retrieve()` — embeds query and searches store |
| `app/routers/query.py` | `/query` — full RAG endpoint with logging |
| `app/routers/compare.py` | `/compare` — RAG vs plain LLM side-by-side |
| `app/prompts/rag_answer.py` | Strict RAG prompt (grounded, cite sources) |
| `app/prompts/rag_answer_minimal.py` | Loose prompt (for A/B comparison) |
| `app/main.py` | Now includes structured logging setup |

## How to Run

```bash
python run_checkpoint.py checkpoint-3-rag-pipeline
```

**Important:** Run `POST /ingest` first to populate the vector store!

## Demo Questions

Try on `/query`:
- "How many vacation days do I get?" — correct answer with sources
- "Can I expense a standing desk?" — finds expense policy
- "What are the core working hours?" — finds remote work policy

Try on `/compare`:
- "How many vacation days do I get?" — RAG correct, plain LLM invents
- "What is the capital of France?" — plain LLM correct, RAG struggles

Try prompt A/B testing:
- `POST /query?prompt_style=default` — strict grounding
- `POST /query?prompt_style=minimal` — loose, may hallucinate

## What to Type Live

Good candidates for live coding:
- `retrieve()` in `retriever.py` (simple, ties embed + search together)
- The RAG prompt in `rag_answer.py` (compare with grounded_answer.py)
- `build_context()` and the query endpoint in `query.py`
- The `/compare` endpoint in `compare.py`

Pre-built (skip live coding):
- Logging setup in `main.py`
