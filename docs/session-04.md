# Session 4 — RAG Pipeline Wiring

## Learning Goals

By the end of this session, students should be able to:

1. Explain the full RAG loop: Retrieve → Inject → Generate
2. Build a retriever that orchestrates embedding and search
3. Design a prompt template that injects retrieved context
4. Build an API endpoint that answers questions using RAG
5. Compare RAG answers with plain LLM answers

## Concepts Introduced

### The Full RAG Loop

```
User question: "How many vacation days do I get?"
        ↓
   RETRIEVE: embed question → search ChromaDB → get top 3 chunks
        ↓
   INJECT:   paste chunks into the prompt template
        ↓
   GENERATE: LLM reads the context and produces a grounded answer
        ↓
   Answer: "You get 20 days per year" + [source: leave-policy.md]
```

That's it. Everything in Sessions 1-3 was building toward this moment.

### Context Injection

The retrieved chunks get inserted into the system prompt between context markers. The LLM is instructed to answer ONLY from this context. This is what makes RAG answers accurate — the LLM isn't guessing, it's reading.

### Source Attribution

The response includes which chunks were used. This is transparency: the user (or developer) can verify the answer against the original documents.

## Files Created / Modified

| File | Change |
|------|--------|
| `app/rag/retriever.py` | **New** — orchestrates embed + search |
| `app/routers/query.py` | **New** — POST `/query` RAG endpoint with prompt A/B support |
| `app/routers/embed.py` | **Inherited** — `/embed` debug endpoint from Session 3 |
| `app/prompts/rag_answer.py` | **New** — strict prompt with grounding rules |
| `app/prompts/rag_answer_minimal.py` | **New** — loose prompt for A/B comparison |
| `app/rag/loader.py` | **Inherited** — multi-format loader from Session 2 |
| `app/models.py` | **Updated** — added QueryRequest, QueryResponse, SourceInfo, EmbedRequest/Response |
| `app/main.py` | **Updated** — mounted query and embed routers |

## Demo Script

### 1. Make sure documents are ingested

```bash
curl -X POST http://localhost:8000/ingest
```

### 2. Ask via RAG

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "How many vacation days do I get?"}'
```

The answer should say "20 days" and include `leave-policy.md` as a source.

### 3. Compare with the plain endpoint

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How many vacation days do I get?"}'
```

The plain LLM invents a number. The RAG endpoint gets it right.

### 4. Try a cross-document question

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the core working hours for remote employees?"}'
```

Should retrieve from `remote-work.md` and answer correctly.

### 5. Ask something NOT in the knowledge base

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the company stock price?"}'
```

The RAG system should say it doesn't have that information. (The quality of this refusal depends on the LLM — some models are better at following the "only use context" instruction.)

### 6. Try an intentionally vague query

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What about time off?"}'
```

The retriever will find leave-related chunks, but the vagueness means the answer may be broad or miss the specific intent. Good time to discuss: "How does query quality affect answer quality?"

### 7. Prompt A/B experiment

The same question with different prompts produces different answer quality:

```bash
# Default prompt (strict grounding, says "I don't know" when context is insufficient)
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "How many vacation days do I get?"}'

# Minimal prompt (loose, may mix in LLM's own knowledge)
curl -X POST "http://localhost:8000/query?prompt_style=minimal" \
  -H "Content-Type: application/json" \
  -d '{"question": "How many vacation days do I get?"}'
```

Try with an out-of-domain question:
```bash
# Default: should say "I don't have that info"
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the company stock price?"}'

# Minimal: might make up an answer!
curl -X POST "http://localhost:8000/query?prompt_style=minimal" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the company stock price?"}'
```

This shows why prompt engineering is a critical part of RAG — not just retrieval.

### Prompt A/B: What to Look For

| Behavior | Default Prompt | Minimal Prompt |
|----------|---------------|----------------|
| In-domain question | Accurate, cites sources | Usually accurate, may add extra info |
| Out-of-domain question | Says "I don't have that info" | May hallucinate an answer |
| Conflicting context | Acknowledges uncertainty | Picks one without mentioning conflict |
| Source attribution | Often mentions source files | Rarely mentions sources |

## Lab Exercises

1. **Compare all three endpoints for the same question:**
   - `/ask` (plain) — what does the LLM invent?
   - `/ask/grounded` (manual context) — correct but hardcoded
   - `/query` (RAG) — correct and automated
2. **Adjust top_k:** Try `/query?top_k=1` vs `/query?top_k=5`. Does using more chunks improve the answer?
3. **Ask a question that spans two documents:** E.g., "What do I need to set up for remote work as a new employee?" (onboarding + remote-work). How well does RAG handle it?
4. **Read the prompt:** Look at `prompts/rag_answer.py`. What happens if you remove the "only use context" instruction?

## Discussion Questions

- "The retriever always returns `top_k` chunks, even if they're irrelevant. How could we filter out bad results?" (Leads to Session 6: confidence thresholds)
- "We're putting 3 chunks into the prompt. What if a question needs information from 10 chunks? What about 100?"
- "Look at the sources in the response. How would you build a UI that lets users click through to the original document?"
- "Compare the `/query` RAG prompt with the `/ask/grounded` prompt from Session 1. What's the same? What's different? The only real change is WHERE the context comes from."
