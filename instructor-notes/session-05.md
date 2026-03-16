# Instructor Notes — Session 5: Source Panel and Transparent UX

## Session Overview

- **Duration:** ~90 minutes
- **Split:** ~50% live coding, ~50% experimentation and discussion
- **Vibe:** This is where RAG becomes trustworthy. Students see honesty in action.

## Before Class

- [ ] Session 4 code working (or copy checkpoint)
- [ ] Documents ingested (`POST /ingest`)
- [ ] Have a browser ready for the /ui demo
- [ ] Prepare to show the terminal AND browser side by side

## What to Type Live vs Prebuilt

| Component | Live or Prebuilt? | Why? |
|-----------|-------------------|------|
| Config thresholds | **Type live** | Students should debate values |
| `score_confidence()` | **Type live** | Core logic, 10 lines |
| `is_no_result()` | **Type live** | Core logic, 5 lines |
| Updated `query.py` | **Type live** | Shows how confidence integrates |
| `models.py` changes | **Type live** | Small, 2 new fields |
| `routers/ui.py` | **Type live** | Very short — 10 lines |
| `static/query.html` | **Prebuilt** | HTML is not the lesson |

## Suggested Live-Coding Order

1. **Start with the question:** "What should a RAG system do when it doesn't have relevant information?"
   - Let students answer before showing code
2. **Add thresholds to `config.py`** — just 3 new lines
3. **Write `score_confidence()`** in retriever.py
   - Start simple: `if distance < 0.8: return "high"`
   - Build up the full logic step by step
4. **Write `is_no_result()`** — even simpler
5. **Update `models.py`** — add `confidence` and `no_result` to QueryResponse
6. **Update `query.py`** — add the confidence + no-result branching
7. **Demo with curl** — test high, medium, low, and none confidence
8. **Create `routers/ui.py`** — 10 lines to serve static HTML
9. **Open the prebuilt `query.html`** in browser — walk through what it shows
10. **Live demo in browser** — high confidence, vague query, out-of-domain

## Key Teaching Moments

### The Threshold Debate (Step 2)
Ask students: "What distance value should separate 'confident' from 'not confident'?"
There's no right answer. Let them pick values and see the results change. This builds intuition.

### The No-Result Demo (Step 7)
This is the most powerful moment:
- Ask "Tell me about quantum physics" via /query
- Show: `no_result: true, confidence: "none"`
- "The system said 'I don't know' instead of making something up. That's a feature, not a bug."

### The UI Walkthrough (Steps 9-10)
Open the HTML file briefly — let students see it's just fetch + innerHTML. No magic.
The point isn't the HTML. The point is:
- Green badge → trust the answer
- Yellow badge → verify the answer
- Red badge → probably wrong
- Grey box → no information

### The Vague Query Demo
"What about time off?" gives medium confidence.
"How many vacation days do I get?" gives high confidence.
Same topic, different specificity. "Your query quality determines your answer quality."

## Common Student Questions

**"Why not just use the LLM to decide if it's confident?"**
Because the LLM doesn't know what's in your knowledge base. Distance scores come from actual retrieval — they measure real similarity. The LLM can only guess.

**"Can we tune the thresholds per collection or document?"**
Yes, in production you'd likely tune per domain. For this course, global thresholds are enough to demonstrate the concept.

**"Why is the UI so basic?"**
Intentional. This is a backend course. Showing a fancy UI would distract from the RAG logic. The UI is just a window into the API responses.

**"What if the user doesn't understand 'confidence: medium'?"**
Good UX question. You'd want to phrase it in user terms: "I found some information but I'm not certain it's relevant." The badge is for developers; production UX would use natural language.

## Timing Guide

| Activity | Time |
|----------|------|
| Recap Session 4 + motivation | 10 min |
| Discussion: what should RAG do when unsure? | 10 min |
| Live code: thresholds, scoring functions | 15 min |
| Live code: update query.py with branching | 10 min |
| Demo: curl queries across confidence levels | 10 min |
| Create UI router + open prebuilt HTML | 5 min |
| Browser demo: all confidence states | 15 min |
| Student experimentation + Q&A | 15 min |

## If You Have Extra Time

- Let students modify confidence thresholds via query params and re-test queries live
- Challenge: "Use `high_threshold=0.3` — does your best query still get high confidence?"
- Challenge: "Use `no_result_threshold=0.5` — how many questions get rejected?"
- Compare prompt styles: `POST /query?prompt_style=minimal` vs default — does the minimal prompt hallucinate more in low-confidence scenarios?
- Preview Session 6: "Now that we can see confidence, how do we debug when something goes wrong?"

## Interactive Threshold Teaching Moments

The new threshold override params make this session much more interactive:

1. **Start with defaults** — show a high-confidence query
2. **Tighten `high_threshold` to 0.3** — same query now returns medium confidence
3. **Ask: "Which is right?"** — neither! The threshold defines "right"
4. **Tighten `no_result_threshold` to 0.5** — previously answerable queries now return "I don't know"
5. **Ask: "Is that better or worse?"** — depends on whether you prefer false negatives vs false positives
6. **Key takeaway:** Thresholds are a product decision, not a technical one
