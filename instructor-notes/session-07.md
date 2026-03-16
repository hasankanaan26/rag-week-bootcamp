# Instructor Notes — Session 7: Smarter Retrieval

## Session Overview

- **Duration:** ~90 minutes
- **Split:** ~50% live coding, ~30% demos, ~20% exercises and discussion
- **Vibe:** Students see how retrieval quality makes or breaks RAG.

## Before Class

- [ ] Session 6 checkpoint working (or copy session-07-retrieval checkpoint)
- [ ] Documents ingested
- [ ] Two terminal windows ready (one for server, one for curl)

## What to Type Live vs Prebuilt

| Component | Live or Prebuilt? | Why? |
|-----------|-------------------|------|
| `rewrite_query.py` prompt | **Type live** | Students see prompt engineering in action |
| `retriever.py` changes | **Type live** | Core concept — rewrite then retrieve |
| `store.py` where filter | **Type live** | Simple change, shows metadata power |
| `query.py` new params | **Prebuilt** | Wiring — not the lesson |
| `compare.py` rewrite param | **Prebuilt** | Just plumbing |

## Suggested Flow

1. **Motivate the problem** (10 min)
   - Ask "What about time off?" with current system (no rewrite)
   - Show the distances are high and confidence is low
   - "The question is fine for a human but terrible for embedding search"

2. **Build the rewrite prompt** (10 min)
   - Create `app/prompts/rewrite_query.py`
   - Walk through the prompt: what it asks the LLM to do
   - Discuss: "Why one line? Why synonyms?"

3. **Add rewriting to retriever** (15 min)
   - Add `rewrite_query()` function — calls LLM with the prompt
   - Update `retrieve()` to accept `rewrite=True`
   - If rewrite, rewrite first, then embed and search
   - Return the rewritten query alongside results

4. **Demo the improvement** (10 min)
   - Same question: "What about time off?"
   - Without rewrite: low confidence, weak chunks
   - With rewrite: better distances, higher confidence
   - Show `rewritten_query` in the response
   - "Look at the logs — you can see the original and rewritten queries"

5. **Add metadata filtering** (10 min)
   - Update `store.py` search to accept `where` dict
   - Update search.py and query.py to pass `source` param
   - Demo: same question filtered to leave-policy.md vs unfiltered

6. **Student exercises** (20 min)
   - Each student tries 5 vague queries with and without rewriting
   - Each student tries 3 queries with different source filters
   - Document which queries improve most from rewriting
   - Find one query where rewriting makes things worse

7. **Class discussion** (15 min)
   - Share findings: "When did rewriting help? When did it hurt?"
   - "What other retrieval improvements could we make?"
   - "How would you decide whether to enable rewriting by default?"

## Timing Guide

| Activity | Time |
|----------|------|
| Motivate the problem | 10 min |
| Build rewrite prompt | 10 min |
| Add rewriting to retriever | 15 min |
| Demo improvement | 10 min |
| Add metadata filtering | 10 min |
| Student exercises | 20 min |
| Class discussion + wrap-up | 15 min |

## Teaching Moments

### "Why Not Always Rewrite?"

Rewriting adds an extra LLM call per query. For specific, well-formed queries it can actually add noise. Show the example:
- Original: "What is the maximum meal reimbursement amount?"
- Rewritten: "meal reimbursement maximum amount expense policy dining food"
- The rewrite adds terms that might pull in irrelevant chunks

### "Metadata Filtering Is Under-Appreciated"

Most RAG tutorials skip metadata filtering. But in production, it's extremely useful:
- User selects a document → filter to that source
- Chat mode → filter to recent documents
- Access control → filter to documents the user has access to

### "Query Rewriting Is a Form of Prompt Engineering"

The rewrite prompt IS the strategy. Different prompts produce different results:
- "Add synonyms" → broader retrieval
- "Use formal terms" → matches policy language
- "Translate to keywords" → very different from natural language

## If You Have Extra Time

- Challenge: "Write a rewrite prompt that translates questions to keyword-only format"
- Challenge: "Add a `category` metadata field during ingestion and filter by category"
- Discussion: "How would you build a hybrid system that rewrites only when confidence is low?"
- Advanced: "Try chaining two rewrites — does double-rewriting help or hurt?"
