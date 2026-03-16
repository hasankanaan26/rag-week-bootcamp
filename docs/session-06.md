# Session 6 — RAG Failure Modes and Logging

## Learning Goals

By the end of this session, students should be able to:

1. Add structured logging to a RAG pipeline
2. Explain common RAG failure modes with examples
3. Compare RAG vs plain LLM answers side-by-side
4. Read logs to diagnose why a RAG answer was wrong or weak

## Concepts Introduced

### Structured Logging

Every RAG request creates a chain of operations. Logging each step lets you answer: "Why did the system give THAT answer?"

What we log at each stage:
- **Query received:** the raw question text
- **Retrieval:** number of chunks, distances, source files
- **Confidence:** high/medium/low/none and why
- **LLM call:** answer length
- **Compare:** both paths logged side-by-side

### RAG Failure Modes

RAG systems fail in predictable ways. Knowing these helps you build better systems.

| Failure Mode | Example Question | What Happens |
|-------------|-----------------|--------------|
| **Out of domain** | "Tell me about quantum physics" | No relevant chunks found → no_result |
| **Vague query** | "What about time off?" | Poor retrieval → mixed context → weak answer |
| **Subjective question** | "Is our leave policy generous?" | Retrieves facts but can't judge → unsatisfying answer |
| **Temporal question** | "What changed in the latest update?" | Docs don't track versions → can't answer |
| **Cross-domain** | "Compare our benefits to Google's" | Only knows Acme Corp → partial answer |
| **Too broad** | "What are the rules?" | Retrieves everything, nothing specific |
| **Near miss** | "What's our parental leave... for contractors?" | Retrieves parental leave but for employees |

### RAG vs Plain LLM Comparison

The `/compare` endpoint is a teaching tool. It shows:

1. The plain LLM answer (often confidently wrong for domain-specific questions)
2. The RAG answer (grounded in documents, with sources)
3. A note explaining the difference

This comparison is the clearest way to demonstrate the value of RAG.

## Files Created / Modified

| File | Change |
|------|--------|
| `app/main.py` | Added logging config, mounted compare + embed routers |
| `app/models.py` | Added CompareRequest, CompareResponse, PlainResult, RAGResult, `request_id` field, EmbedRequest/EmbedResponse |
| `app/routers/query.py` | Structured logging with `req_xxxx` IDs, `prompt_style`, threshold overrides |
| `app/routers/compare.py` | **New** — side-by-side comparison with `req_xxxx` tracing |
| `app/routers/embed.py` | Embedding exploration endpoint (from Session 3) |
| `app/routers/ingest.py` | Multi-format loading + `chunk_strategy` param |
| `app/rag/loader.py` | Multi-format file loader (from Session 2) |
| `app/rag/chunker.py` | Added `chunk_by_sections()` |
| `app/rag/retriever.py` | Optional threshold overrides (from Session 5) |
| `app/config.py` | Added `SUPPORTED_EXTENSIONS` |
| `app/prompts/rag_answer_minimal.py` | Minimal prompt for A/B testing |

## Demo Script

### 1. Start the app and tail logs

```bash
# Terminal 1: Start the app
uvicorn app.main:app --reload

# Terminal 2: Watch the logs (they appear in terminal 1)
```

### 2. Compare: in-domain question

```bash
curl -X POST http://localhost:8000/compare \
  -H "Content-Type: application/json" \
  -d '{"question": "How many vacation days do I get?"}'
```

Watch the logs — you'll see retrieval, confidence scoring, both LLM calls.
The RAG answer cites 20 days from leave-policy.md. The plain answer invents a number.

### 3. Compare: out-of-domain question

```bash
curl -X POST http://localhost:8000/compare \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the capital of France?"}'
```

The RAG path returns no_result. The plain LLM answers correctly. RAG isn't always better — it depends on the question.

### 4. Tricky failure mode questions

Try each of these and discuss the results:

```bash
# Subjective — RAG has facts but can't judge
curl -X POST http://localhost:8000/compare \
  -H "Content-Type: application/json" \
  -d '{"question": "Is our leave policy generous?"}'

# Cross-domain — RAG only knows Acme Corp
curl -X POST http://localhost:8000/compare \
  -H "Content-Type: application/json" \
  -d '{"question": "How does our leave compare to industry standard?"}'

# Temporal — docs don't track history
curl -X POST http://localhost:8000/compare \
  -H "Content-Type: application/json" \
  -d '{"question": "What changed in the latest policy update?"}'
```

### 5. Read the logs

Point out the log pattern for each request:
```
14:30:01 | rag.compare        | INFO  | req_a3f2b1c4 | Compare request | question='How many vacation days do I get?'
14:30:01 | rag.compare        | INFO  | req_a3f2b1c4 | Running plain LLM (no retrieval)
14:30:02 | rag.compare        | INFO  | req_a3f2b1c4 | Plain LLM responded | answer_length=89 chars
14:30:02 | rag.compare        | INFO  | req_a3f2b1c4 | Running RAG pipeline
14:30:02 | rag.compare        | INFO  | req_a3f2b1c4 | RAG retrieved 3 chunks | best_distance=0.234 | sources=['leave-policy.md', ...]
14:30:03 | rag.compare        | INFO  | req_a3f2b1c4 | RAG LLM responded | confidence=high | answer_length=112 chars
14:30:03 | rag.compare        | INFO  | req_a3f2b1c4 | Compare complete | confidence=high | no_result=False
```

Notice the `req_a3f2b1c4` prefix — every log line from the same request shares this ID.
When multiple requests arrive concurrently, the `req_xxxx` IDs let you trace each request's
journey through the pipeline. The `request_id` also appears in the JSON response.

## Tricky Sample Questions

Use these to demonstrate failure modes live:

| Question | Failure Mode | Discussion Point |
|----------|-------------|-----------------|
| "Is our leave policy generous?" | Subjective | RAG retrieves facts but can't make value judgments |
| "What changed recently?" | Temporal | Documents are static — no version tracking |
| "Compare us to Google" | Cross-domain | RAG only has Acme Corp data |
| "What does John in engineering think?" | Personal opinion | Not in any document |
| "Tell me everything" | Too broad | Retrieves random chunks, useless context |
| "What's our parental leave for contractors?" | Near miss | Finds parental leave for employees |

## Discussion Questions

- "When should you use RAG vs just the plain LLM?"
- "What does the log output tell you about why an answer was wrong?"
- "If you saw confidence=low in production logs, what would you do?"
- "How does the request_id help when debugging concurrent requests?"
