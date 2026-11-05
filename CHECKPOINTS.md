# Checkpoint Roadmap

## Checkpoint 1 — Foundations of RAG

**Duration:** ~2 hours

**Learning Goals:**
- Understand why plain LLMs hallucinate about private data
- See what "grounding" means (manual context injection)
- Learn how documents are split into chunks
- Compare fixed-size vs section-based chunking strategies

**Endpoints:**
- `POST /ask` — plain LLM answer (no grounding)
- `POST /ask/grounded` — manually grounded answer (hardcoded context)
- `POST /ingest` — load and chunk knowledge base documents

**Key Files:**
- `app/routers/ask.py` — hallucination demo vs grounded demo
- `app/routers/ingest.py` — document loading and chunking
- `app/rag/chunker.py` — fixed-size and section-based chunking
- `app/rag/loader.py` — multi-format file loader
- `app/prompts/grounded_answer.py` — manual grounding prompt

**Demo Flow:**
1. Ask "How many vacation days do I get?" on `/ask` — observe hallucination
2. Ask the same question on `/ask/grounded` — observe correct, grounded answer
3. Run `/ingest` — see how documents become chunks
4. Try different `chunk_size` values (200, 500, 1000) and compare

---

## Checkpoint 2 — Vector Store and Retrieval

**Duration:** ~2 hours

**Learning Goals:**
- Understand how embeddings capture semantic meaning
- Build a ChromaDB vector store
- Index chunks and retrieve them by similarity
- Explore embedding distances and metadata

**New Endpoints:**
- `POST /ingest` — now embeds chunks and stores them in ChromaDB
- `GET /search?q=...` — semantic search against stored chunks
- `POST /embed` — explore pairwise embedding distances
- `GET /store/inspect` — see what's stored in ChromaDB

**Key Files:**
- `app/rag/embedder.py` — text-to-vector embedding
- `app/rag/store.py` — ChromaDB wrapper (add, search, inspect)
- `app/routers/search.py` — retrieval without generation
- `app/routers/embed.py` — embedding exploration tool

**Demo Flow:**
1. Run `/ingest` to embed and store all documents
2. Search for "vacation days" — observe which chunks are found
3. Search for "annual leave" — same chunks, different words (semantic search!)
4. Search for "quantum physics" — high distances (irrelevant)
5. Use `/embed` to compare ["vacation days", "annual leave", "Python programming"]

---

## Checkpoint 3 — Retrieval to Generation Wiring

**Duration:** ~2 hours

**Learning Goals:**
- Wire retrieval into generation (the full RAG loop)
- See RAG vs plain LLM answers side by side
- Understand prompt engineering for RAG (strict vs minimal)
- Read structured logs to trace RAG pipeline execution

**New Endpoints:**
- `POST /query` — full RAG: retrieve, inject context, generate answer
- `POST /compare` — same question through RAG and plain LLM side-by-side

**Key Files:**
- `app/rag/retriever.py` — orchestrates embed + search
- `app/routers/query.py` — full RAG loop with logging
- `app/routers/compare.py` — RAG vs plain comparison
- `app/prompts/rag_answer.py` — strict RAG prompt
- `app/prompts/rag_answer_minimal.py` — loose prompt (for A/B testing)

**Demo Flow:**
1. Ask "How many vacation days?" on `/ask` (hallucination) and `/query` (correct)
2. Try `/compare` to see both answers side by side
3. Try `prompt_style=minimal` on `/query` — observe weaker grounding
4. Tail the terminal logs — see retrieval details for each request
5. Try "What is the capital of France?" on `/compare` — RAG struggles, plain LLM correct

---

## Checkpoint 4 — Failure Modes, Analysis, and Visualization

**Duration:** ~2 hours

**Learning Goals:**
- Handle no-result and weak-evidence cases
- Classify retrieval confidence (high/medium/low/none)
- Surface failure modes in a transparent UI
- Visualize embedding clusters with t-SNE and PCA

**New Endpoints:**
- `GET /ui` — browser-based query interface with confidence badges
- `GET /visualize?method=tsne` — 2D scatter plot of chunk embeddings

**Key Files:**
- `app/rag/retriever.py` — adds `score_confidence()` and `is_no_result()`
- `app/rag/visualize.py` — t-SNE/PCA dimensionality reduction + plotting
- `app/routers/visualize.py` — PNG image endpoint
- `app/routers/query.py` — now with confidence scoring and threshold overrides
- `app/static/query.html` — transparent UI with confidence badges

**Demo Flow:**
1. Open `/ui` in a browser
2. Ask "How many vacation days?" — high confidence, green badge
3. Ask "What about time off?" — medium confidence, yellow badge
4. Ask "Tell me about quantum physics" — no result
5. Ask "What are the rules?" — low confidence, red badge
6. Visit `/visualize` — see how chunks cluster by document
7. Visit `/visualize?method=pca` — compare with PCA projection
8. Tail logs while querying — see confidence and no-result flags

---

## Checkpoint 5 — Production Ingestion (Session 8)

**Duration:** ~2 hours

**Learning Goals:**
- Replace a one-shot `/ingest` with a sync job that keeps the index true to a changing source
- Parse the format zoo (Markdown, CSV, PDF and scans, Word, Excel, HTML, email) into sections
- Carry permissions, status, versions and effective dates from a register onto every chunk
- Filter by permission and version INSIDE the vector search; answer "as of" a past date
- Redact personal data before embedding; rebuild blue/green; measure leaks, stale chunks and ghosts

**New Endpoints:**
- `POST /sync` — dry run (plan + cost) or `?apply=true`; `?rebuild=true` for blue/green
- `GET /documents?user=` — the register next to the index
- `GET /search?user=&as_of=` and `POST /query?user=&as_of=`

**Key Files:**
- `sharepoint.py`, `sync.py`, `evaluate.py`, `search.py`, `warmup.py` — the class scripts
- `app/ingest/` — `connector.py`, `parsers.py`, `register.py`, `pii.py`, `sync.py`, `naive.py`
- `app/rag/retriever.py` — `access_filter()`; `app/rag/catalog.py` — the live-index pointer
- `app/evals/golden.json`, `judge.py` — 31 questions, quality and safety flags

**Demo Flow:**
1. `sharepoint.py reset`, `sync.py --naive` — yesterday's ingest on Friday's SharePoint
2. `sync.py` then `sync.py --apply` — the plan, its cost, the live index
3. `sharepoint.py apply all` — the weekend; `sync.py` — one action per document
4. `search.py "salary range for a senior developer" --user intern` vs `--user hr-partner`
5. `search.py "team dinner limit per person" --as-of 2023-06-01`
6. `evaluate.py` — yesterday's index vs today's on 31 questions

---

## Checkpoint 6 — Advanced Retrieval (Session 9)

**Duration:** ~2 hours

**Learning Goals:**
- Diagnose a retrieval miss by its shape before picking a fix
- Hybrid search (BM25 + dense, RRF) and cross-encoder re-ranking, with their costs
- Parent-document retrieval, HyDE, multi-query: what each fixes, what each costs
- Route list questions to a lookup: some answers are bigger than k
- Prove it: Hit@5, MRR, Recall, latency, LLM calls; regression against a baseline; an LLM judge

**New Endpoints:**
- `GET /retrieve?strategy=` — any strategy, with its trace
- `POST /query?strategy=` — default `routed`

**Key Files:**
- `app/rag/strategies.py` — nine strategies, one contract
- `app/rag/bm25.py`, `reranker.py`, `children.py`, `router.py`
- `compare.py`, `ask.py`, `judge.py` — scoreboard, traces, answer quality
- `app/evals/golden_retrieval.json` — 24 questions in six kinds, with reference answers

**Demo Flow:**
1. `compare.py --strategies dense --details` — the baseline and its misses
2. `ask.py "How many reviewers does a change to the billing code need?"` — every strategy's trace
3. `compare.py` — the scoreboard; `compare.py --llm` for HyDE and multi-query
4. `ask.py "Who works remotely?" --strategies dense,routed`
5. `judge.py --strategy dense` vs `--strategy routed` — faithful is not correct
6. `compare.py --save-baseline`, then `CANDIDATES=5 compare.py --against-baseline`
