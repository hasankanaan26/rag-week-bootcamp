# Live-Coding Plan — Week 3: RAG Done Properly

A session-by-session guide for the instructor. For each session:
what to type live, what to have prebuilt, and the recommended order.

---

## Session 1 — RAG Foundations

**Time budget:** ~60 min coding, ~30 min discussion

### Prebuilt before class
- `data/knowledge/*.md` (6 Acme Corp docs)
- `.env.example`, `requirements.txt`, `Dockerfile`, `docker-compose.yml`

### Type live (in order)
1. `app/config.py` — env vars, 15 lines
2. `app/models.py` — Question + Answer, 10 lines
3. `app/llm.py` — call_llm function, 30 lines
4. `app/prompts/plain_answer.py` — system prompt, 5 lines
5. `app/routers/ask.py` — POST /ask endpoint, 15 lines
6. `app/main.py` — mount router, 10 lines
7. **DEMO:** Ask "How many vacation days?" → hallucination
8. `app/prompts/grounded_answer.py` — hardcoded context prompt
9. Add `/ask/grounded` to ask.py
10. **DEMO:** Same question → correct answer. "That's grounding."

### Key live moment
The hallucination demo. Let the class react before explaining.

---

## Session 2 — Chunking

**Time budget:** ~55 min coding, ~35 min experimentation

### Prebuilt before class
- Knowledge base docs already in `data/knowledge/`

### Type live (in order)
1. `app/rag/chunker.py` — Stage 1: naive split (no overlap)
2. **DEMO:** Show a split sentence. "See the problem?"
3. Update chunker — Stage 2: add overlap
4. `app/models.py` — add ChunkInfo, IngestResponse
5. `app/config.py` — add KNOWLEDGE_DIR and chunk settings
6. `app/routers/ingest.py` — load + chunk + return
7. Mount in `main.py`
8. **DEMO:** POST /ingest, inspect chunks
9. **EXPERIMENT:** Students try chunk_size=200, 500, 1000

### Key live moment
Building overlap in two stages. The cut-sentence demo.

---

## Session 3 — Embeddings and Vector Storage

**Time budget:** ~60 min coding, ~30 min experimentation

### Prebuilt before class
- `docker-compose.yml` with ChromaDB (if using server mode)

### Type live (in order)
1. `app/rag/embedder.py` — embed_text + embed_texts
2. **DEMO:** Show a raw embedding vector. Print first 10 values.
3. `app/rag/store.py` — add_chunks + search + count + clear
4. Update `app/routers/ingest.py` — add embed + store steps
5. Update `app/config.py` — add CHROMA_PATH and embed model
6. `app/routers/search.py` — GET /search endpoint
7. Update `app/models.py` — SearchResult, SearchResponse
8. Mount in `main.py`
9. **DEMO:** Ingest, then search "vacation days"
10. **KEY DEMO:** Search "annual leave" → same results, different words!

### Key live moment
The "annual leave" vs "vacation days" demo. Semantic search in action.

---

## Session 4 — RAG Pipeline

**Time budget:** ~55 min coding, ~35 min discussion

### Type live (in order)
1. `app/rag/retriever.py` — retrieve function (embed + search)
2. `app/prompts/rag_answer.py` — RAG system prompt with {context}
3. Show grounded_answer.py (S1) side-by-side. "Same structure!"
4. `app/routers/query.py` — build_context + POST /query
5. Update `app/models.py` — QueryRequest, QueryResponse, SourceInfo
6. Mount in `main.py`
7. **DEMO:** POST /query "How many vacation days?"
8. **COMPARE:** Same question on /ask vs /query. Pause. Let it sink in.
9. **WEAK QUERY:** "What about time off?" — discuss answer quality

### Key live moment
The /ask vs /query side-by-side comparison. This is the payoff of the
entire week so far. Let the class sit with it for a moment.

---

## Session 5 — Transparent UX

**Time budget:** ~45 min coding, ~45 min demos

### Prebuilt before class
- `app/static/query.html` (the HTML page)

### Type live (in order)
1. Discuss: "What should a RAG system do when it doesn't know?"
2. Add thresholds to `config.py` — 4 new lines
3. Write `score_confidence()` in retriever.py — build incrementally
4. Write `is_no_result()` — very short
5. Update `models.py` — add confidence + no_result fields
6. Update `query.py` — add branching logic
7. **DEMO with curl:** High, medium, low, none confidence
8. Write `routers/ui.py` — 10 lines to serve HTML
9. **BROWSER DEMO:** Open /ui, try all confidence levels
10. **KEY DEMO:** "Tell me about quantum physics" → no_result=true

### Key live moment
The no-result demo in the browser UI. Grey box, honest answer, no
hallucination. "A good system knows when it doesn't know."

---

## Session 6 — Failure Modes and Logging

**Time budget:** ~35 min coding, ~55 min demos and discussion

### Prebuilt before class
- Tricky questions list (in instructor notes)

### Type live (in order)
1. Add `logging.basicConfig(...)` to `main.py` — 4 lines
2. Add `logger` to `query.py` — add log lines step by step
3. **DEMO:** Hit /query, read the log output line by line
4. Write `models.py` additions — CompareRequest/Response
5. Write `routers/compare.py` — type it step by step with logging
6. Mount in `main.py`
7. **DEMO:** /compare with "How many vacation days?"
8. **FAILURE MODE GALLERY:** Go through tricky questions one by one

### Key live moment
The failure mode gallery. Ask students to PREDICT the result before
showing it. The subjective question ("Is our policy generous?") and
the near-miss ("parental leave for contractors?") generate great discussion.

---

## Session 7 — Comparison Polish

**Time budget:** ~40 min coding, ~50 min exploration and discussion

### Prebuilt before class
- Session 6 checkpoint (all endpoints working, logging in place)

### Type live (in order)
1. Open `compare.py` — review it. "This duplicates build_context. Let's fix that."
2. Refactor `compare.py` — import `build_context` and `NO_RESULT_ANSWER` from `query.py`
3. **DEMO:** POST /compare, verify it still works after refactoring
4. Open `static/query.html` — add RAG/Plain/Compare radio toggle
5. Update `submitQuery()` — route to different endpoints based on mode
6. Add `renderCompareResult()` — side-by-side grid layout
7. **BROWSER DEMO:** Open /ui, switch between RAG, Plain, and Compare modes
8. Add sample questions section to the UI with categorized examples
9. **STUDENT EXERCISE:** Give students the tricky questions list. Have them
   predict the outcome before clicking. Discuss the surprises.

### Key live moment
The mode toggle in the browser. Students can now see RAG vs plain answers
with one click. This makes the value of RAG viscerally obvious.

---

## Session 8 — Production Polish

**Time budget:** ~30 min coding, ~60 min walkthrough and review

### Prebuilt before class
- `tests/` directory with test files (run through them, don't type them)
- Session 7 checkpoint as starting point

### Type live (in order)
1. Walk through the full codebase: main.py → config.py → routers → rag/
2. Update `main.py` header — add comprehensive endpoint documentation
3. Update version to `1.0.0`
4. **RUN TESTS:** `pytest tests/ -v` — show all 20 passing
5. Walk through one test file to explain the self-contained test strategy
6. **FULL DEMO:** Ingest → Search → Query → Compare, all in the browser UI
7. **DISCUSSION:** What would you change for production?
   - Authentication, rate limiting, caching
   - Persistent vs ephemeral store tradeoffs
   - Monitoring, eval metrics, prompt versioning
8. **WRAPUP:** Review the journey from Session 1 hallucination to Session 8

### Key live moment
The full system walkthrough. Students see how every piece connects.
The test run gives confidence that everything works. The production
discussion plants seeds for real-world application.

---

## General Tips

- **Type at explanation speed, not coding speed.** Every line is a teaching moment.
- **Leave intentional pauses.** After a demo, wait 5 seconds. Let the result register.
- **Use Swagger UI** (`/docs`) for all API demos. Students can follow along.
- **Keep terminal visible** for log output in Sessions 6+.
- **Every session should end with** "next session we'll..." to maintain the narrative arc.
