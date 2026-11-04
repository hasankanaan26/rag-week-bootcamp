# Instructor Notes — Checkpoint 3: RAG Pipeline

## Timing (~2 hours)

| Activity | Time | Notes |
|----------|------|-------|
| Recap Checkpoint 2 | 5 min | "We can search. Now we generate answers." |
| Build retriever | 10 min | Simple wrapper: embed + search |
| Build RAG prompt | 10 min | Compare with grounded prompt from CP1 |
| Build /query endpoint | 25 min | The full RAG loop, type live |
| Demo: /ask vs /query | 10 min | Side-by-side hallucination vs grounded |
| Build /compare | 15 min | Both paths in one call |
| Show the logs | 10 min | Tail terminal, explain each line |
| Prompt A/B test | 10 min | default vs minimal prompt |
| Lab exercise | 15 min | Students try queries, read logs |
| Wrap-up | 10 min | Preview: "What happens when RAG fails?" |

## Key Talking Points

1. **The RAG prompt is identical to the grounded prompt.** Open both files side by side. "The structure is the same. The only change is that context comes from retrieval instead of being hardcoded."

2. **The 5-step RAG loop.** Write it on the whiteboard:
   - Retrieve chunks
   - Build context string
   - Format system prompt
   - Call LLM
   - Return answer + sources

3. **Prompt engineering matters.** Show the difference between `default` and `minimal` prompt styles. "Same context, same LLM, different instructions = different answers."

4. **Logs are your debugging tool.** Show how to read request IDs, distance scores, and chunk counts in the terminal output.

## Common Questions

- "Why does /query sometimes give wrong answers?" — Retrieval quality matters. If the wrong chunks are retrieved, the answer will be wrong even with a good prompt.
- "Should I always use the strict prompt?" — For factual Q&A, yes. For creative tasks, a looser prompt may be better.
- "Why log everything?" — In production, logs are how you debug RAG failures. Start building the habit now.
