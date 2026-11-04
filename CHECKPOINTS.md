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
