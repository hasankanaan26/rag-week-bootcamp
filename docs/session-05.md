# Session 5 — Source Panel and Transparent UX

## Learning Goals

By the end of this session, students should be able to:

1. Explain why transparent UX matters for RAG systems
2. Implement confidence scoring based on retrieval distances
3. Handle no-result and weak-evidence states gracefully
4. Build a simple browser interface that shows the full RAG pipeline output

## Concepts Introduced

### Why Transparency?

A RAG system that always gives an answer — even when it has no relevant information — is dangerous. Users trust it, act on it, and only discover the hallucination when damage is done.

A transparent RAG system shows:
- **What it found** — the actual source chunks it used
- **How confident it is** — based on how well the query matched
- **When it doesn't know** — a clear "no result" instead of a made-up answer

### Confidence Scoring

We classify retrieval confidence using the distance between query and chunk embeddings:

| Distance Range | Confidence | What It Means |
|---------------|------------|---------------|
| ≤ 0.8 | High | Strong match — answer is well-supported |
| ≤ 1.4 | Medium | Reasonable match — answer is likely correct |
| > 1.4 | Low | Weak evidence — answer may be unreliable |
| > 1.6 or empty | None | No relevant documents found |

These thresholds are configurable. In real applications, you'd tune them based on your embedding model and document domain.

### No-Result vs Weak-Evidence

- **No result:** The system found nothing relevant at all. The best action is to say "I don't have that information."
- **Weak evidence:** The system found something, but the match is poor. The answer might work, but the user should know it's uncertain.

Both are better than hallucinating.

## Files Created / Modified

| File | Change |
|------|--------|
| `app/config.py` | Added confidence thresholds + `SUPPORTED_EXTENSIONS` |
| `app/models.py` | Added `confidence`, `no_result`, `distance` fields + `EmbedRequest`/`EmbedResponse` |
| `app/rag/retriever.py` | Added `score_confidence()`, `is_no_result()` with optional threshold overrides |
| `app/rag/loader.py` | Multi-format file loader (from Session 2) |
| `app/rag/chunker.py` | Added `chunk_by_sections()` (from Session 2) |
| `app/routers/query.py` | Confidence + no-result logic, `prompt_style` param, interactive threshold overrides |
| `app/routers/ingest.py` | Multi-format loading + `chunk_strategy` param |
| `app/routers/embed.py` | Embedding exploration endpoint (from Session 3) |
| `app/routers/ui.py` | **New** — serves the HTML interface |
| `app/prompts/rag_answer_minimal.py` | Minimal prompt for A/B testing (from Session 4) |
| `app/static/query.html` | **New** — transparent RAG browser UI |
| `app/main.py` | Mounted UI and embed routers |

## Demo Script

### 1. Ingest documents (if not already done)

```bash
curl -X POST http://localhost:8000/ingest
```

### 2. Open the UI

Navigate to http://localhost:8000/ui in your browser.

### 3. High confidence query

Type: **"How many vacation days do I get?"**
- Confidence badge: green "HIGH"
- Sources show leave-policy.md with low distance scores

### 4. Vague query (medium confidence)

Type: **"What about time off?"**
- Confidence badge: yellow "MEDIUM"
- Sources may be less targeted — the query is vague

### 5. Out-of-domain query (no result)

Type: **"Tell me about quantum physics"**
- No-result state: grey box with "No relevant documents found"
- No hallucination — the system honestly says it doesn't know

### 6. Broad query (weak evidence)

Type: **"What are the rules?"**
- Confidence badge: red "LOW" with warning bar
- The system found something, but the match quality is poor

## Discussion Questions

- "When should a system say 'I don't know' vs give its best guess?"
- "How would you choose the right distance thresholds for your domain?"
- "What information should every RAG answer show to the user?"
- "Is it better to show nothing or show a low-confidence answer?"

## Interactive Threshold Tuning

Session 5 adds query-time threshold overrides. You can change confidence
boundaries without restarting the server:

```bash
# Default thresholds (from config / .env)
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "How many vacation days?"}'

# Override: make high-confidence harder to achieve
curl -X POST "http://localhost:8000/query?high_threshold=0.3" \
  -H "Content-Type: application/json" \
  -d '{"question": "How many vacation days?"}'

# Override: set a very strict no-result cutoff
curl -X POST "http://localhost:8000/query?no_result_threshold=0.5" \
  -H "Content-Type: application/json" \
  -d '{"question": "What about time off?"}'
```

### Threshold Parameters

| Parameter | Default | What It Controls |
|-----------|---------|-----------------|
| `high_threshold` | 0.8 | Max distance for "high" confidence |
| `low_threshold` | 1.4 | Max distance for "medium" confidence |
| `no_result_threshold` | 1.6 | Max distance before "no result" |

### Experiment: Finding Your Thresholds

1. Ingest documents: `POST /ingest`
2. Send a known good question with `top_k=5`
3. Note the distances in the response
4. Try `high_threshold=<your_best_distance>` — does confidence change?
5. Try `no_result_threshold=0.5` — does a good question now return "no result"?
6. Discuss: what happens when thresholds are too strict? Too lenient?

## Sample Questions

| Question | Expected Confidence | Why |
|----------|-------------------|-----|
| "How many vacation days do I get?" | High | Exact match in leave-policy.md |
| "What is our Git branching strategy?" | High | Covered in coding-standards.md |
| "Can I expense a standing desk?" | High | Covered in expense-policy.md |
| "What about time off?" | Medium | Vague, matches leave policy loosely |
| "What are the rules?" | Low | Too broad, matches everything poorly |
| "Tell me about quantum physics" | None | Not in any document |
| "How do I request parental leave?" | High | Specific, in leave-policy.md |
