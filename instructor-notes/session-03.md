# Instructor Notes — Session 3: Embeddings and Vector Storage

## Session Overview

- **Duration:** ~90 minutes
- **Split:** ~55% live coding, ~45% demos and experimentation
- **Vibe:** The "magic" session. Students see semantic search for the first time. Expect genuine surprise when different words find the same content.

## Before Class

- [ ] Session 2 code is working (or copy from checkpoint)
- [ ] API keys are configured (Gemini or Azure — embedding model must be accessible)
- [ ] `data/knowledge/` has all documents (markdown, CSV, optionally PDF)
- [ ] `chroma_data/` directory does NOT exist (clean start for the demo)
- [ ] Have two queries ready that are semantically similar but use different words

## What to Type Live vs Prebuilt

| Component | Live or Prebuilt? | Why? |
|-----------|-------------------|------|
| `rag/embedder.py` | **Type live** | Students must see embedding is just an API call |
| `rag/store.py` | **Type live** | ChromaDB interaction must be demystified |
| `routers/search.py` | **Type live** | The payoff — students test search immediately |
| `routers/embed.py` | **Type live** | Short — builds on embedder, great exploration tool |
| `routers/ingest.py` updates | **Type live** | Shows how embed+store plugs into existing flow |
| `config.py` updates | **Type live** | Quick — just 3 new settings |
| `models.py` updates | **Type live** | Small addition |
| `main.py` router mount | **Type live** | One line |

## Suggested Live-Coding Order

1. **Recap Session 2:** "We have chunks. Now we need to make them searchable."
2. **Show a raw embedding:** Before writing code, show what an embedding looks like:
   - Open a Python REPL or notebook
   - Call the embedding API with a short sentence
   - Show the list of hundreds of numbers — "This is just what a computer thinks 'vacation days' means"
3. **Create `rag/embedder.py`:**
   - Start with `embed_text()` and `embed_texts()`
   - Show the dual-provider pattern (same as `llm.py`)
4. **Create `rag/store.py`:**
   - `get_collection()` — "ChromaDB stores data in collections, like tables"
   - `add_chunks()` — "We store text, metadata, AND the embedding vector"
   - `search()` — "Give it a vector, it finds the closest stored vectors"
   - `count()` and `clear()` — utility functions
5. **Update `routers/ingest.py`:**
   - Add `embed_texts(chunk_texts)` call
   - Add `add_chunks(all_chunks, embeddings)` call
   - Add the `fresh` parameter
   - Demo: POST /ingest — "Now chunks are embedded and stored!"
6. **Update `config.py`** and **`models.py`**
7. **Create `routers/search.py`:**
   - Embed query, search store, return results
8. **Mount in `main.py`**
9. **Demo time — the magic moment:**
   - Search: "vacation days" → finds leave policy
   - Search: "annual leave" → finds THE SAME chunks!
   - "Wait — 'vacation days' and 'annual leave' share zero words. How?"
   - Search: "quantum physics" → finds something, but high distances
   - "Distance tells us relevance. Low = good. High = irrelevant."
10. **Create `routers/embed.py`:**
    - "Let's build a tool to explore how embeddings see the world"
    - Accept a list of texts, embed them, compute pairwise distances
    - Demo: POST /embed with synonyms, then with unrelated terms
    - "This is what the search is doing under the hood"

## Key Teaching Moments

### The Synonym Demo (Step 9)
This is the most impactful moment in the entire week. Prepare two queries:
- "How many vacation days do I get?"
- "What is the annual leave entitlement?"

Both should return the same leave policy chunks. Let students absorb this before explaining — it's more powerful when they discover the implication themselves.

### The /embed Exploration Tool (Step 10)
After the search demo, the `/embed` endpoint gives students a hands-on way to understand embeddings. Suggested experiments:

- **Synonyms:** `["vacation days", "annual leave", "time off"]` → all close
- **Unrelated:** `["vacation days", "Python code", "quarterly earnings"]` → all far
- **Question↔Answer:** `["How many vacation days?", "Employees receive 20 days of annual leave"]` → close enough for RAG to work
- **Negation:** `["I love this policy", "I hate this policy"]` → surprisingly close! (embeddings often struggle with negation)

This exercise builds intuition for why some searches work better than others.

### The "Always Returns Results" Problem
Search "quantum physics". ChromaDB still returns top_k results — just with high distances. Ask: "The system always returns something. Is that good or bad?" This plants the seed for Session 6 (confidence thresholds).

### The Embedding Is Just Numbers
Show the raw output of `embed_text("hello")` — hundreds of floats. "There's nothing magical here. It's a list of numbers from a model that was trained to put similar meanings close together."

## Common Student Questions

**"How does the embedding model know that 'vacation' and 'annual leave' mean the same thing?"**
The embedding model was trained on massive amounts of text where these terms appear in similar contexts. It learned the relationships. This is a fundamental insight of modern NLP.

**"Why not just use keyword search?"**
Keyword search requires exact matches. Users might say "PTO", "time off", "holidays", "vacation" — all meaning the same thing. Embedding search handles all of these automatically.

**"How big is an embedding vector?"**
Typically 256-1536 numbers, depending on the model. `text-embedding-004` (Gemini) produces 768 dimensions. `text-embedding-3-small` (OpenAI) produces 1536.

**"Can I embed images or other media?"**
Some models support multimodal embeddings, yes. But for this course, we're focused on text.

**"Is ChromaDB production-ready?"**
For learning, absolutely. For production at scale, you'd evaluate options like Pinecone, Weaviate, pgvector, or Qdrant. The RAG code stays the same — only `store.py` changes.

## Timing Guide

| Activity | Time |
|----------|------|
| Recap Session 2 + show raw embedding | 10 min |
| Live code: embedder.py | 12 min |
| Live code: store.py | 12 min |
| Live code: update ingest.py + config | 8 min |
| Demo: /ingest with embeddings | 5 min |
| Live code: search.py router | 8 min |
| Demo: semantic search magic moment | 8 min |
| Live code: embed.py router + demo | 10 min |
| Student experimentation | 10 min |
| Discussion + Q&A | 7 min |

## If You're Running Short on Time

Skip showing a raw embedding in the REPL. Just type `embedder.py` and show the embedding vectors in the `/search` response. The semantic search demo is what matters most.

## If You Have Extra Time

- Let students search for emoji meanings: "happy", "celebration", "party" — do they find similar chunks?
- Re-ingest with a different chunk size and search again. Do the results change?
- Preview Session 4: "Now that we can retrieve relevant chunks, what if we fed them into the LLM's prompt? That's what we build next."
