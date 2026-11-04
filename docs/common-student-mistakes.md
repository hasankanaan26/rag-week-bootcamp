# Common Student Mistakes

Issues that come up regularly during the sessions. Keep this open for quick reference.

## Setup Issues

**"ModuleNotFoundError: No module named 'app'"**
- Make sure you're running from the correct directory
- For checkpoints: use `python run_checkpoint.py checkpoint-N-name` from the repo root
- For base-app: `cd base-app` first, then `uvicorn app.main:app --reload`

**"GEMINI_API_KEY is empty"**
- Copy `.env.example` to `.env` and add your API key
- Make sure `.env` is in the repo root (not inside a checkpoint folder)

**"chromadb not found" or import errors**
- Run `pip install -r requirements.txt`
- Make sure you're using the virtual environment: `source .venv/bin/activate`

**Port 8000 already in use**
- Another checkpoint or server is still running
- Kill it with Ctrl+C in the other terminal, or use a different port: `--port 8001`

## Checkpoint 1 Issues

**"Why does /ask/grounded not know about coding standards?"**
- The grounded endpoint uses hardcoded leave policy context only
- That's the limitation we're showing — RAG automates this for all documents

**Chunks look weird or cut mid-sentence**
- Expected! Fixed-size chunking doesn't respect sentence boundaries
- Try `chunk_strategy=sections` to split on headings instead
- Discuss: this is the tradeoff between fixed-size and structural chunking

## Checkpoint 2 Issues

**"/search returns empty results"**
- Run `POST /ingest` first to populate the vector store
- Check `/store/inspect` to verify chunks are stored

**"All distances look the same"**
- The embedding model may not differentiate well for very short texts
- Try longer, more specific queries

**ChromaDB permission errors on Windows**
- Make sure `chroma_data/` is writable
- Try deleting `chroma_data/` and re-ingesting

## Checkpoint 3 Issues

**"The RAG answer ignores some chunks"**
- The LLM processes all retrieved chunks but may focus on the most relevant
- Try `top_k=1` to see how a single chunk affects the answer
- This is expected — more chunks give more context but also more noise

**"/compare takes a long time"**
- It makes two LLM calls (plain + RAG) — expected to be ~2x slower
- The logs show each step's timing

## Checkpoint 4 Issues

**"All queries return high confidence"**
- The default thresholds may be too generous for your embedding model
- Try adjusting: `high_threshold=0.5` and `low_threshold=1.0`
- Or set stricter values in `.env`

**"/visualize returns an error"**
- Make sure scikit-learn and matplotlib are installed
- Run `POST /ingest` first — need at least 2 chunks to visualize
- On some systems, matplotlib needs a display backend: the code uses "Agg" (non-interactive), so this should work headless

**"The t-SNE plot looks different each time"**
- t-SNE is stochastic by default, but we set `random_state=42` for reproducibility
- If you see different results, you may have different data in the store
