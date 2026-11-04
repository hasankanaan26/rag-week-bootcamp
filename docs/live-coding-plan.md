# Live Coding Plan

Session-by-session guide for what to type live vs what to have pre-built.

## General Principles

- **Type the interesting parts.** Students learn by watching you think through the logic.
- **Pre-build the boring parts.** Config files, boilerplate, and format parsers add no teaching value.
- **Demo after each function.** Don't build everything, then demo. Build one thing, show it working, move on.
- **Use Swagger UI.** It's faster than writing curl commands and students can see the request/response schema.

---

## Checkpoint 1 — Foundations (~2 hours)

### Pre-built (have ready before class)
- `config.py`, `llm.py`, `models.py` — boilerplate
- `loader.py` — format parsing is tedious
- `prompts/plain_answer.py` — one-liner

### Live coding order

1. **Start from `base-app/`** — show it running (`/health` works)
2. **Build `/ask` endpoint** (~15 min)
   - Create `routers/ask.py`, write `ask_plain()`
   - Mount in `main.py`
   - Demo: ask about vacation days — observe hallucination
3. **Build grounded answer** (~15 min)
   - Create `prompts/grounded_answer.py` with hardcoded context
   - Add `ask_grounded()` to `ask.py`
   - Demo: same question, correct answer
   - Discussion: "That's grounding. RAG automates this."
4. **Build the chunker** (~20 min)
   - Create `rag/chunker.py`, write `chunk_document()`
   - Walk through: text -> chunks with overlap
   - Demo with different chunk sizes
5. **Build `/ingest`** (~15 min)
   - Wire loader + chunker into an endpoint
   - Demo: inspect the chunks
   - Discussion: chunk boundaries, overlap, strategies
6. **Show `chunk_by_sections()`** (~10 min)
   - Compare with fixed-size chunking
   - "Which chunks would you rather search against?"

### Key teaching moments
- "The LLM doesn't know anything about Acme Corp. It's making things up."
- "Grounding fixes the problem, but we had to paste the context manually."
- "Chunking lets us retrieve only the relevant parts later."

---

## Checkpoint 2 — Vector Store (~2 hours)

### Pre-built
- `embed.py`, `inspect.py` — useful but not core
- Updated `models.py` with new response types

### Live coding order

1. **Build the embedder** (~15 min)
   - Create `rag/embedder.py` with `embed_text()` and `embed_texts()`
   - Explain: "Text in, numbers out. Similar text = similar numbers."
2. **Build the store** (~20 min)
   - Create `rag/store.py` with `add_chunks()` and `search()`
   - Explain ChromaDB's upsert and query APIs
3. **Update `/ingest`** (~10 min)
   - Add embedding and storage steps
   - Demo: ingest documents, check chunk count
4. **Build `/search`** (~15 min)
   - Create `routers/search.py`
   - Demo: search "vacation days" vs "annual leave" (same results!)
   - This is the "magic moment" of the session
5. **Demo `/embed` explorer** (~10 min)
   - Show pairwise distances between synonyms and unrelated terms
   - "This is what makes semantic search possible"

### Key teaching moments
- "vacation days" and "annual leave" return the same chunks — embeddings capture meaning
- "quantum physics" returns high distances — the system knows it's irrelevant
- "The vector store is like a smart index that understands language"

---

## Checkpoint 3 — RAG Pipeline (~2 hours)

### Pre-built
- `prompts/rag_answer_minimal.py`
- Logging setup in `main.py`

### Live coding order

1. **Build the retriever** (~10 min)
   - Create `rag/retriever.py` with `retrieve()`
   - "One function that does embed + search"
2. **Build the RAG prompt** (~10 min)
   - Create `prompts/rag_answer.py`
   - Compare with `grounded_answer.py` — same structure!
   - "The only difference is WHERE the context comes from"
3. **Build `/query`** (~25 min)
   - Create `routers/query.py`
   - Write `build_context()` — show how chunks become prompt text
   - Write the main endpoint: retrieve -> build -> call LLM -> respond
   - Demo: compare `/ask` vs `/query` — hallucination vs grounded answer
4. **Build `/compare`** (~15 min)
   - Both paths in one response
   - Demo: "How many vacation days?" — RAG wins
   - Demo: "What is the capital of France?" — plain LLM wins
5. **Show the logs** (~10 min)
   - Tail the terminal while querying
   - Walk through what each log line means

### Key teaching moments
- The full RAG loop is just 5 lines: retrieve, build context, format prompt, call LLM, return
- The prompt is the control layer — try minimal vs default to see the difference
- Logs show exactly what happens inside — chunks found, distances, answer length

---

## Checkpoint 4 — Analysis (~2 hours)

### Pre-built
- `query.html` — frontend, not the focus
- `visualize.py` — explain the concept, show the output
- `routers/visualize.py` — simple endpoint wrapper

### Live coding order

1. **Build confidence scoring** (~15 min)
   - Add `score_confidence()` to `retriever.py`
   - Explain the threshold logic: high/medium/low/none
   - Discussion: "What distance counts as confident enough?"
2. **Build no-result detection** (~10 min)
   - Add `is_no_result()` to `retriever.py`
   - "A good system knows when it doesn't know"
3. **Update `/query`** (~15 min)
   - Add confidence and no-result to the endpoint
   - Demo: various queries showing different confidence levels
   - Demo: threshold overrides for live tuning
4. **Show the UI** (~10 min)
   - Open `/ui` in browser
   - Walk through confidence badges, source cards, no-result state
5. **Failure mode gallery** (~15 min)
   - Try each tricky question on `/compare`
   - Discussion: subjective, temporal, cross-domain failures
6. **Show visualization** (~15 min)
   - Visit `/visualize` — explain t-SNE projection
   - "Chunks from the same document cluster together"
   - Try PCA: `/visualize?method=pca`
   - Discuss: what makes these clusters meaningful for retrieval

### Key teaching moments
- "The system should tell users when it's not confident"
- "RAG fails on subjective, temporal, and cross-domain questions"
- "Embedding clusters show WHY semantic search works"
