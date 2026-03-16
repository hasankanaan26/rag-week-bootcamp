# Instructor Notes — Session 6: RAG Failure Modes and Logging

## Session Overview

- **Duration:** ~90 minutes
- **Split:** ~40% live coding, ~60% demos / discussion / experimentation
- **Vibe:** Detective work. Students learn to read the pipeline like a pro.

## Before Class

- [ ] Session 5 code working (or copy checkpoint)
- [ ] Documents ingested
- [ ] Two terminal windows ready (one for app, one for watching logs)
- [ ] Prepare the tricky questions list — don't reveal them all at once

## What to Type Live vs Prebuilt

| Component | Live or Prebuilt? | Why? |
|-----------|-------------------|------|
| Logging setup in `main.py` | **Type live** | 4 lines — connects to Week 2 tracing |
| `logger` lines in `query.py` | **Type live** | Students see what to log and where |
| `routers/compare.py` | **Type live** | Core session deliverable |
| `models.py` additions | **Type live** | Small additions — CompareResponse is interesting |
| Tricky sample questions | **Prebuilt in doc** | Read from instructor notes, show live |

## Suggested Live-Coding Order

1. **Start with the problem:** "The system gave a bad answer. How do we figure out why?"
2. **Add logging to `main.py`** — `logging.basicConfig(...)`, just 4 lines
3. **Add logger to `query.py`** — `logger = logging.getLogger("rag.query")`
4. **Add log lines step by step:**
   - Log the incoming question
   - Log retrieval results (count, distances, sources)
   - Log confidence decision
   - Log the LLM response length
5. **Demo: hit /query and read the logs** — walk through each line
6. **Write `compare.py`** — the biggest live-coding piece
   - Start with just the plain LLM call
   - Add the RAG call
   - Add the comparison note
   - Add logging
7. **Demo: hit /compare with in-domain question** — read both answers and logs
8. **Failure mode gallery** — work through tricky questions one by one

## Key Teaching Moments

### The Logging Walkthrough (Step 5)
Show a single /query request and read the log output line by line:
```
14:30:01 | rag.query | INFO | req_a3f2b1c4 | Query received | question='How many vacation days?'
14:30:01 | rag.query | INFO | req_a3f2b1c4 | Retrieved 3 chunks | best_distance=0.234 | sources=[...]
14:30:01 | rag.query | INFO | req_a3f2b1c4 | Result: OK | confidence=high
14:30:02 | rag.query | INFO | req_a3f2b1c4 | LLM responded | prompt_style=default | answer_length=95 chars
```
"From these 4 lines, you can tell: what was asked, what was found, how confident we are, and how long the answer was. The `req_a3f2b1c4` prefix ties all lines to the same request. If something goes wrong, which line tells you where?"

### The /compare Demo (Step 7)
This is the most powerful teaching moment of the week.

Ask: "How many vacation days do I get?"
- Plain LLM: "Typically companies offer 10-15 days..." (made up)
- RAG: "All full-time employees receive 20 days..." (from leave-policy.md)
- Ask the class: "Which one would you trust?"

### The Failure Mode Gallery (Step 8)
Go through these one at a time, asking students to predict what will happen BEFORE showing the result:

1. **"Is our leave policy generous?"**
   - Prediction: "The RAG should find the leave policy"
   - Reality: Retrieves facts but can't judge "generous" — students learn RAG has limits

2. **"Tell me about quantum physics"**
   - Prediction: "No result"
   - Reality: no_result=true. Show both /compare answers. Plain LLM handles this fine.
   - Teaching: "RAG isn't always better. Know when to skip it."

3. **"What changed in the latest policy update?"**
   - Prediction: varies
   - Reality: Finds policy chunks but can't answer "what changed" — no version history
   - Teaching: "RAG reflects what's in the docs. If the docs don't track changes, neither can RAG."

4. **"What's our parental leave for contractors?"**
   - Prediction: "Should find parental leave"
   - Reality: Finds employee parental leave, but the answer may be misleading for contractors
   - Teaching: "A near miss can be worse than a miss — the system is confidently answering the wrong question."

### Connecting to Week 2 Tracing
"In Week 2, you learned to add tracing to LLM calls. This is the same concept applied to a pipeline. Each log line traces one step. Notice the `req_xxxx` prefix — every log line for the same request shares this ID, so you can follow a single query through all its steps even when requests are interleaved."

## Common Student Questions

**"Should we log the full prompt?"**
For debugging, yes. For production, be careful — prompts can contain sensitive data. We log query text and answer length, not the full prompt. You could add a debug flag.

**"Why not use a logging framework like structlog?"**
Great for production. For teaching, Python's built-in logging is enough and has zero new dependencies. The concepts transfer directly.

**"How do we know if our thresholds are right?"**
You'd track no_result and low-confidence rates over time. If 50% of queries hit no_result, your knowledge base probably needs more documents. If everything is high confidence, your thresholds might be too generous.

**"Why does /compare make two LLM calls?"**
Because it runs both paths independently. In production you'd cache or only run the comparison when explicitly requested. For teaching, seeing both results is the point.

## Timing Guide

| Activity | Time |
|----------|------|
| Recap Session 5 + motivation for logging | 10 min |
| Live code: logging setup + query.py logs | 15 min |
| Demo: read logs for a /query request | 10 min |
| Live code: compare.py endpoint | 20 min |
| Demo: /compare with in-domain question | 10 min |
| Failure mode gallery (4-5 tricky questions) | 15 min |
| Student experimentation + Q&A | 10 min |

## If You Have Extra Time

- Have students write their own tricky questions and share results
- Discussion: "What would you add to the logs for a production system?"
- Challenge: "Fire two curl requests at the same time — can you match each `req_xxxx` ID to its response?"
- Try prompt A/B with logging: `POST /query?prompt_style=minimal` — see the `prompt_style=minimal` in the log output
- Preview Session 7: "Now that we can compare and debug, how do we make retrieval smarter?"
