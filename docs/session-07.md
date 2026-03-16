# Session 7 — Smarter Retrieval

## Learning Goals

By the end of this session, students should be able to:

1. Explain why vague queries produce poor retrieval results
2. Use query rewriting to improve retrieval quality
3. Apply metadata filtering to restrict search to specific documents
4. Compare retrieval results with and without query rewriting

## Concepts Introduced

### Query Rewriting

When a user asks "What about time off?", the embedding model doesn't have much to work with. The query is vague and lacks specific terms that appear in the documents.

**Query rewriting** sends the user's question to the LLM first, asking it to rephrase it with specific terms, synonyms, and formal language. For example:

| Original Query | Rewritten Query |
|---------------|----------------|
| "What about time off?" | "employee vacation leave PTO time off policy" |
| "rules for spending money" | "expense reimbursement policy spending limits" |
| "how do we write code?" | "coding standards guidelines practices programming" |

The rewritten query embeds better and retrieves more relevant chunks.

### Metadata Filtering

Every chunk stored in ChromaDB carries metadata — at minimum, the `source` filename. Metadata filtering lets you restrict search to a specific document:

```bash
# Only search within leave-policy.md
curl -X POST "http://localhost:8000/query?source=leave-policy.md"
```

This is useful when:
- A user asks about a specific policy
- You want to avoid cross-document noise
- You're debugging retrieval for a particular file

### How They Work Together

Query rewriting improves *what* you search for.
Metadata filtering improves *where* you search.

Used together, you get precise retrieval: the right terms matched against the right documents.

## Files Created / Modified

| File | Change |
|------|--------|
| `app/prompts/rewrite_query.py` | **New** — prompt template for query rewriting |
| `app/rag/retriever.py` | Added `rewrite_query()` function, `retrieve()` now accepts `rewrite` and `where` params |
| `app/rag/store.py` | `search()` accepts optional `where` metadata filter |
| `app/routers/query.py` | Added `rewrite` and `source` query parameters |
| `app/routers/compare.py` | Added `rewrite` query parameter |
| `app/routers/search.py` | Added `source` query parameter |
| `app/models.py` | Added `rewritten_query` field to `QueryResponse` |
| `app/main.py` | Updated title/version for Session 7 |

## Demo Script

### 1. Start the app and ingest

```bash
uvicorn app.main:app --reload
curl -X POST http://localhost:8000/ingest
```

### 2. Vague query WITHOUT rewriting

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What about time off?"}'
```

Look at the confidence score and distances. Likely low confidence.

### 3. Same query WITH rewriting

```bash
curl -X POST "http://localhost:8000/query?rewrite=true" \
  -H "Content-Type: application/json" \
  -d '{"question": "What about time off?"}'
```

Check the `rewritten_query` field in the response. Notice the distances are lower (better) and confidence is higher.

### 4. Metadata filtering

```bash
curl -X POST "http://localhost:8000/query?source=leave-policy.md" \
  -H "Content-Type: application/json" \
  -d '{"question": "How many vacation days?"}'
```

Only chunks from `leave-policy.md` are retrievied.

### 5. Combined: rewrite + filter

```bash
curl -X POST "http://localhost:8000/query?rewrite=true&source=expense-policy.md" \
  -H "Content-Type: application/json" \
  -d '{"question": "rules for spending money"}'
```

### 6. Compare mode with rewrite

```bash
curl -X POST "http://localhost:8000/compare?rewrite=true" \
  -H "Content-Type: application/json" \
  -d '{"question": "What about time off?"}'
```

Watch the logs to see the original and rewritten queries.

## Experiment Guide

### Experiment 1: Vague vs Specific

Try these pairs and compare distances:

| Vague | Expected Rewrite Effect |
|-------|------------------------|
| "stuff about money" | → expense/reimbursement terms |
| "tech things" | → technology stack, programming, tools |
| "time off rules" | → leave, vacation, PTO policy |

### Experiment 2: Source Filtering

Try the same question with different source filters:
- `source=leave-policy.md` vs `source=expense-policy.md`
- Notice how filtering changes which chunks appear

### Experiment 3: When Rewriting Hurts

Try a very specific, well-formed query with rewrite=true:
- "What is the maximum meal reimbursement amount?"
- The rewritten version may add unnecessary terms
- This shows rewriting isn't always better

## Discussion Questions

- "When does query rewriting help most? When could it hurt?"
- "What other metadata could we filter on besides source filename?"
- "How would you decide whether to enable rewriting by default?"
