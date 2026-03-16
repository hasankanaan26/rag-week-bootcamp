# Session Roadmap — Week 3: RAG Done Properly

## Session 1 — RAG Foundations and FastAPI Integration

**Goal:** Start where Week 2 ended. Build a plain chat endpoint, then show why it fails on company-specific questions.

**You'll build:**
- FastAPI app with `/health` and `/ask` endpoints
- Plain LLM call that answers from general knowledge
- `/ask/grounded` endpoint with manually injected company context
- Side-by-side comparison: plain vs grounded answers

**Key concept:** Grounding = giving the LLM real information to base its answer on. RAG automates this.

**Checkpoint:** `checkpoints/session-01-baseline/`

---

## Session 2 — Document Ingestion and Chunking

**Goal:** Turn company documents into small, searchable pieces.

**You'll build:**
- `rag/chunker.py` — splits documents into overlapping chunks
- `routers/ingest.py` — loads markdown files, chunks them, returns results
- Experiment with different chunk sizes and overlaps

**Key concept:** We can't paste entire documents into a prompt. Chunking lets us retrieve only the relevant parts.

**Checkpoint:** `checkpoints/session-02-chunking/`

---

## Session 3 — Embeddings and Vector Storage

**Goal:** Turn text chunks into vectors, store them, and test semantic search.

**You'll build:**
- `rag/embedder.py` — generates vector embeddings from text
- `rag/store.py` — stores and retrieves chunks from ChromaDB
- Updated `/ingest` endpoint that embeds and stores chunks
- `GET /search?q=...` endpoint for testing retrieval in isolation

**Key concept:** An embedding captures the meaning of text as a list of numbers. Similar meanings produce similar numbers — and that's how we search by meaning instead of keywords.

**Checkpoint:** `checkpoints/session-03-embeddings/`

---

## Session 4 — RAG Pipeline Wiring

**Goal:** Wire retrieval into the LLM call. The core RAG loop.

**You'll build:**
- `rag/retriever.py` — orchestrates embedding a query and searching the store
- `prompts/rag_answer.py` — prompt template with context injection
- `POST /query` — retrieve chunks, build prompt, call LLM, return answer with sources
- Side-by-side comparison: `/ask` (plain) vs `/query` (RAG)

**Key concept:** Retrieve → Inject → Generate. That's the entire RAG pattern. Everything else is refinement.

**Checkpoint:** `checkpoints/session-04-rag-pipeline/`

---

## Session 5 — Source Panel and Transparent UX

**Goal:** Make the system honest and transparent with a simple browser UI.

**You'll build:**
- Confidence scoring based on retrieval distance thresholds
- No-result handling: "I don't have that information" when nothing relevant is found
- Weak-evidence warnings for borderline queries
- A browser-based UI at `/ui` showing answers, confidence badges, sources, and distances

**Key concept:** A good RAG system knows when it doesn't know. That's more valuable than always giving an answer.

**Checkpoint:** `checkpoints/session-05-transparency/`

---

## Session 6 — RAG Failure Modes and Logging

**Goal:** Add structured logging and explore when RAG fails.

**You'll build:**
- Structured logging across the RAG pipeline
- `POST /compare` — runs the same question through plain LLM and RAG side-by-side
- Tricky queries that expose failure modes: subjective, temporal, cross-domain, near-miss
- Logs that capture query, retrieval results, confidence, and answers

**Key concept:** Logging lets you answer "why did the system give THAT answer?" Failure modes teach you what RAG can and can't do.

**Checkpoint:** `checkpoints/session-06-logging/`

---

## Session 7 — Smarter Retrieval

**Goal:** Improve retrieval quality with query rewriting and metadata filtering.

**You'll build:**
- `prompts/rewrite_query.py` — prompt that rewrites vague questions with specific terms
- `rewrite_query()` function in `retriever.py` — LLM-powered query rewriting
- Metadata filtering in `store.py` — restrict search to specific source documents
- `rewrite` and `source` query parameters on `/query`, `/compare`, and `/search`

**Key concept:** Retrieval quality determines RAG quality. Query rewriting improves *what* you search for. Metadata filtering improves *where* you search.

**Checkpoint:** `checkpoints/session-07-retrieval/`

---

## Session 8 — Evaluation & Safety

**Goal:** Build an eval pipeline and add prompt injection detection.

**You'll build:**
- `eval/test_questions.json` — 12 test cases across factual, vague, out-of-domain, and injection categories
- `eval/run_eval.py` — automated eval runner that checks source retrieval, keywords, and safety
- `POST /safety/check` — LLM-as-judge prompt injection detection
- `prompts/safety_check.py` — safety classifier prompt

**Key concept:** Evaluation tells you if your system works. Safety tells you if it can be exploited. Both are essential, not optional extras.

**Checkpoint:** `checkpoints/session-08-evaluation/`
