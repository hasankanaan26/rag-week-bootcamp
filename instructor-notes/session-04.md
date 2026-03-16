# Instructor Notes — Session 4: RAG Pipeline Wiring

## Session Overview

- **Duration:** ~90 minutes
- **Split:** ~50% live coding, ~50% demos and comparison
- **Vibe:** The "everything connects" session. Students see the full RAG loop working end-to-end. This is the climax of the week.

## Before Class

- [ ] Session 3 code is working (or copy from checkpoint)
- [ ] Documents are already ingested (`POST /ingest` — store has chunks)
- [ ] Have Swagger UI open and ready in a browser
- [ ] Prepare the comparison slide/moment: same question asked to `/ask` vs `/query`
- [ ] Have `leave-policy.md` open to verify the RAG answer is correct

## What to Type Live vs Prebuilt

| Component | Live or Prebuilt? | Why? |
|-----------|-------------------|------|
| `rag/retriever.py` | **Type live** | Short, connects embed + search — students see the orchestration |
| `prompts/rag_answer.py` | **Type live** | THE key moment — students see context injection |
| `routers/query.py` | **Type live** | Where the full loop comes together |
| `models.py` updates | **Type live** | QueryResponse shows what the API returns |
| `main.py` router mount | **Type live** | One line |

## Suggested Live-Coding Order

1. **Start with the question:** "We can retrieve relevant chunks. We can call an LLM. What's missing?"
   - Answer: "We need to put the chunks INTO the prompt."
2. **Create `rag/retriever.py`:**
   - Show it's just two lines: embed the query, search the store
   - "This orchestrates what we built in Session 3 into one function call"
3. **Create `prompts/rag_answer.py`:**
   - "Look at grounded_answer.py from Session 1. Same structure."
   - "The only difference: `{context}` will be filled with RETRIEVED chunks, not hardcoded text"
   - Walk through the prompt line by line: rules for the LLM, context markers
4. **Create `routers/query.py`:**
   - Write the `build_context()` helper first — "This formats chunks into readable text"
   - Write the endpoint step by step:
     a. Retrieve chunks
     b. Build context
     c. Format the prompt
     d. Call the LLM
     e. Build response with sources
   - "Look at the flow: five steps, each one visible, each one a single function call"
5. **Update `models.py`** — add SourceInfo, QueryRequest, QueryResponse
6. **Mount in `main.py`**
7. **The Big Demo:**

   **Step A — Ingest (if not already done):**
   ```bash
   POST /ingest
   ```

   **Step B — Ask via RAG:**
   ```bash
   POST /query  {"question": "How many vacation days do I get?"}
   ```
   → "20 days", source: leave-policy.md

   **Step C — Ask the SAME question via plain LLM:**
   ```bash
   POST /ask  {"question": "How many vacation days do I get?"}
   ```
   → Invented answer (wrong number)

   **Pause here.** Let the class absorb the difference.

   **Step D — Ask something outside the knowledge base:**
   ```bash
   POST /query  {"question": "What is the company stock price?"}
   ```
   → Should decline: "I don't have that information"

   **Step E — Intentionally vague query:**
   ```bash
   POST /query  {"question": "What about time off?"}
   ```
   → Retrieves mixed chunks, answer may be broad. Discuss why.

## Key Teaching Moments

### The Side-by-Side Comparison (Step 7, B vs C)
This is the most important demo of the entire week. Same question, drastically different answers. One is grounded in documents, one is hallucinated.

Ask the class: "Which one would you trust for your company's HR policy?"

### Connecting Back to Session 1
Open `prompts/grounded_answer.py` and `prompts/rag_answer.py` side by side. They're structurally identical. "In Session 1, we manually pasted context. Now the retriever does it automatically. That's the whole point."

### The `build_context()` Function
Walk through this carefully. Show what the context string looks like after formatting. Students should SEE the exact text that gets sent to the LLM. Transparency is a first-class concern.

### The Five-Step Flow
Draw this on a whiteboard or in comments:
```
Question → Retrieve → Build context → Call LLM → Response with sources
```
"Every RAG system follows this pattern. The details vary but the structure is always the same."

## Common Student Questions

**"What if the retriever returns irrelevant chunks?"**
Great question — this is exactly what Session 6 addresses. For now, we trust top_k. Later, we add distance thresholds to filter out poor matches.

**"Why return the sources in the response?"**
Transparency. Users should be able to verify the answer. In production, you might link to the original document.

**"Could we use more chunks for better answers?"**
Yes, but more chunks = more tokens = more cost + potential noise. 3 chunks is a good default. Experiment with `top_k` to see the tradeoff.

**"What happens if the store is empty?"**
The retriever returns an empty list, the context is empty, and the LLM should say it doesn't have information. Try it: clear the store, then query.

**"Is this the same as ChatGPT with documents?"**
Conceptually, yes! ChatGPT's "Browse" or "file upload" features use variations of this same pattern. The difference is we can see every step.

## Sample Questions by Expected Behavior

### Should work well (clear matches in knowledge base):
- "How many vacation days do I get?"
- "What is our Git branching strategy?"
- "Can I expense a monitor for my home office?"
- "What are the core working hours for remote employees?"
- "How do I get access to GitHub as a new employee?"

### Should handle gracefully (nothing relevant in knowledge base):
- "What is the company stock price?"
- "Who is the CEO?"
- "What programming language was invented in 1995?"

### Intentionally ambiguous/weak (mixed results):
- "What about time off?" — vague, matches multiple topics
- "Tell me about the rules" — too broad
- "Python" — could match tech-stack or coding-standards

## Timing Guide

| Activity | Time |
|----------|------|
| Recap Session 3 + frame the session | 5 min |
| Live code: retriever.py | 10 min |
| Live code: rag_answer.py prompt | 10 min |
| Live code: query.py router (step by step) | 20 min |
| Live code: models.py + main.py | 5 min |
| Big Demo: RAG vs plain comparison | 15 min |
| Student experimentation | 15 min |
| Discussion + Q&A | 10 min |

## If You're Running Short on Time

Skip the retriever module and put the retrieve logic directly in the query router. The retriever is a convenience, not a necessity. Prioritize the demo time — the side-by-side comparison is more valuable than clean code structure.

## If You Have Extra Time

- Let students modify the RAG prompt and see how it changes answers
- Try different `top_k` values and compare answer quality
- Ask: "What would you add to the QueryResponse to make it more useful?"
- Preview Session 5-6: "The system always returns an answer. But what about confidence? What about when it shouldn't answer at all?"
