# Instructor Notes — Checkpoint 1: Foundations

## Timing (~2 hours)

| Activity | Time | Notes |
|----------|------|-------|
| Setup + base-app demo | 10 min | Make sure everyone has the app running |
| Build /ask endpoint | 15 min | Type live, demo hallucination |
| Build grounded prompt | 15 min | Type live, demo correct answer |
| Discussion: grounding | 10 min | "RAG automates this" |
| Build chunker | 20 min | Type live, explain overlap |
| Build /ingest endpoint | 15 min | Wire it together, demo chunks |
| Chunking comparison | 10 min | Fixed vs sections |
| Lab exercise | 15 min | Students try different chunk sizes |
| Wrap-up | 10 min | Preview: "Next we make the search automatic" |

## Key Talking Points

1. **Start with the problem.** Ask students: "What happens if I ask the LLM about Acme Corp's leave policy?" Let them guess, then show the hallucination.

2. **The grounded answer is the "aha" moment.** Same question, correct answer. "All we did was paste real information into the prompt."

3. **RAG = automating grounding.** "Instead of us pasting context into the prompt, we'll build a system that finds the right context automatically."

4. **Chunking tradeoffs matter.** Small chunks = precise but may miss context. Large chunks = more context but more noise. There's no perfect size.

## Common Questions

- "Why not paste the whole document?" — Token limits, cost, noise.
- "How do we know what chunk size to use?" — It depends on your data. 400-600 chars is a good starting point.
- "Does overlap help?" — Yes, it prevents information from being split across chunk boundaries. Try overlap=0 to see the problem.

## Things That Can Go Wrong

- `.env` not configured — students get API key errors
- Wrong working directory — module not found errors
- Port already in use — someone left a previous server running
