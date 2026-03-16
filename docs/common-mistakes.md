# Common Student Mistakes — Week 3: RAG Done Properly

A reference for instructors. When a student hits one of these, you can
point them here or address it live.

---

## Session 1-2: Foundations

### Forgetting to create `.env`
**Symptom:** App starts but LLM calls fail with empty API key errors.
**Fix:** `cp .env.example .env` and fill in keys.

### Importing from the wrong `config.py`
**Symptom:** Module not found errors for config values.
**Fix:** Imports should always be `from app.config import ...`.
Checkpoints have their own config.py — if running a checkpoint,
run from the checkpoint's directory.

### Editing the wrong file
**Symptom:** Changes don't appear in the running app.
**Fix:** Make sure you're editing the `app/` folder that uvicorn
is actually loading, not a checkpoint folder.

### Not restarting uvicorn after adding a new router
**Symptom:** New endpoint returns 404.
**Fix:** `--reload` should catch it, but sometimes you need to
restart manually. Also check that `main.py` mounts the new router.

---

## Session 2: Chunking

### Overlap larger than chunk size
**Symptom:** Infinite loop or duplicate chunks.
**Fix:** overlap must be < chunk_size. Add a check or mention it
to the class before the experiment phase.

### Empty chunks from trailing whitespace
**Symptom:** chunks with blank or near-blank text.
**Fix:** The chunker strips whitespace, but students modifying
the logic may forget this step.

---

## Session 3: Embeddings

### Not ingesting before searching
**Symptom:** `/search` returns empty results.
**Fix:** `POST /ingest` first. The vector store starts empty.

### Wrong embedding model name
**Symptom:** 404 or model-not-found errors from the embedding API.
**Fix:** Check `.env` — the embedding model name must match what
the provider actually offers (e.g., `text-embedding-004` for Gemini).

### Mixing up LLM and embedding API keys
**Symptom:** Auth errors on embedding calls that worked for chat.
**Fix:** Some providers use the same key for both; others don't.
Check the provider's docs.

---

## Session 4: RAG Pipeline

### Forgetting to ingest after restarting (if using ephemeral store)
**Symptom:** `/query` returns empty or irrelevant answers.
**Fix:** Re-run `POST /ingest`. With PersistentClient this
shouldn't happen, but if students switch to ephemeral mode, it will.

### Context block too large for the model's context window
**Symptom:** API error about token limit exceeded.
**Fix:** Reduce top_k or chunk_size. For most teaching scenarios
with 6 small documents, this won't happen, but mention it.

### Prompt injection in user questions
**Symptom:** The LLM ignores the grounding context.
**Fix:** Not addressed in this course, but mention it as a
production concern. "Ignore all previous instructions" in a query
field is a real attack vector.

---

## Session 5: Transparency

### Thresholds too tight — everything is "no result"
**Symptom:** Every query returns no_result=true.
**Fix:** Loosen the NO_RESULT_DISTANCE threshold. The right value
depends on the embedding model. Start generous, tighten.

### Thresholds too loose — everything is "high confidence"
**Symptom:** Even bad queries show high confidence.
**Fix:** Tighten CONFIDENCE_HIGH_THRESHOLD. Have students
check actual distance values via `/search` first.

### HTML page not loading
**Symptom:** 404 on `/ui` or blank page.
**Fix:** Check that `static/query.html` exists relative to the
routers directory, and that `ui.py` router is mounted in `main.py`.

---

## Session 6: Logging and Comparison

### Logs not appearing
**Symptom:** No log output in terminal.
**Fix:** Check that `logging.basicConfig()` is called in `main.py`
BEFORE the app starts, and that level is `INFO` not `WARNING`.

### /compare is slow
**Symptom:** Each request takes 5-10 seconds.
**Fix:** It makes TWO LLM calls (plain + RAG). This is expected.
Mention that production systems would cache or parallelize.

### Students confused by LLM non-determinism
**Symptom:** Same question gives different comparison results.
**Fix:** LLMs are non-deterministic even at low temperature.
The point isn't exact answers — it's the structural difference
between grounded and ungrounded responses.

---

## General Mistakes

### Running `pip install` in the wrong environment
**Symptom:** ImportError for packages that should be installed.
**Fix:** Activate the virtual environment first. Check with
`which python` or `pip list`.

### Port 8000 already in use
**Symptom:** uvicorn fails to start.
**Fix:** Kill the previous instance or use a different port:
`uvicorn app.main:app --reload --port 8001`

### Students ahead of the class
**Tip:** Give them a TODO exercise from the instructor notes.
Each session has lab ideas for students who finish early.
