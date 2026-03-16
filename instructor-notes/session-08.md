# Instructor Notes — Session 8: Evaluation & Safety

## Session Overview

- **Duration:** ~90 minutes
- **Split:** ~40% live coding, ~30% demos, ~30% exercises and discussion
- **Vibe:** Capstone. Students build guardrails and learn to test their system.

## Before Class

- [ ] Session 7 checkpoint working (or copy session-08-evaluation checkpoint)
- [ ] Documents ingested
- [ ] Two terminal windows ready (one for server, one for running eval)
- [ ] `eval/test_questions.json` and `eval/run_eval.py` ready

## What to Type Live vs Prebuilt

| Component | Live or Prebuilt? | Why? |
|-----------|-------------------|------|
| `safety_check.py` prompt | **Type live** | Students see safety prompt design |
| `safety.py` router | **Type live** | Simple endpoint — shows the pattern |
| `test_questions.json` | **Prebuilt** | Show structure, don't type JSON live |
| `run_eval.py` | **Prebuilt** | Complex script — walk through it |
| Model additions | **Prebuilt** | Just wiring |

## Suggested Flow

1. **Motivate the problem** (10 min)
   - "Your RAG system works. But how do you KNOW it works?"
   - "What if someone tries to trick it?"
   - Show a prompt injection attack on the current system (no safety check)

2. **Build the safety classifier** (15 min)
   - Create `app/prompts/safety_check.py` — design the prompt together
   - Create `app/routers/safety.py` — simple POST endpoint
   - Demo: try safe and unsafe questions
   - "This is the LLM-as-judge pattern"

3. **Try to break it** (10 min)
   - Students brainstorm injection attacks
   - Test each one through `/safety/check`
   - Keep a scoreboard: how many get through?
   - "No safety system is perfect — it's about layers"

4. **Walk through the eval pipeline** (10 min)
   - Show `test_questions.json` — explain the 4 categories
   - Walk through `run_eval.py` — what it checks and how
   - "This is the simplest useful eval. Production uses RAGAS, DeepEval, etc."

5. **Run the eval** (10 min)
   - `python eval/run_eval.py`
   - Watch the results together
   - Discuss: why did certain tests fail?
   - "A failing test isn't bad — it tells you where to improve"

6. **Student exercise: Expand the eval** (20 min)
   - Each student adds 3 test cases to test_questions.json:
     - 1 factual question about a document they've read
     - 1 creative injection attempt
     - 1 edge case (very short query, all caps, emoji, etc.)
   - Re-run eval with expanded test set
   - Share findings

7. **Wrap-up and full recap** (15 min)
   - Recap the 8-session arc:
     - Session 1: Plain LLM chat
     - Session 2: Document loading and chunking
     - Session 3: Embeddings and vector search
     - Session 4: RAG pipeline with prompts
     - Session 5: Confidence scoring and transparency
     - Session 6: Logging and failure modes
     - Session 7: Query rewriting and metadata filtering
     - Session 8: Evaluation and safety
   - "You built a working, tested, defended RAG system from scratch"
   - Final questions

## Timing Guide

| Activity | Time |
|----------|------|
| Motivate the problem | 10 min |
| Build safety classifier | 15 min |
| Try to break it | 10 min |
| Walk through eval pipeline | 10 min |
| Run the eval | 10 min |
| Student exercise | 20 min |
| Wrap-up and recap | 15 min |

## Teaching Moments

### "LLM-as-Judge Is Circular"
Students will notice: "We're using an LLM to protect against LLM attacks?" Yes! And that's intentional:
- It's a simple, effective first layer
- It can be fooled — that's why we need multiple layers
- In production you'd add regex, content classifiers, rate limiting

### "Eval Is Not Testing"
- Testing checks specific code paths (unit tests)
- Eval checks the whole system's behavior end-to-end
- Both matter — eval catches issues testing misses (and vice versa)

### "100% Pass Rate Is Suspicious"
If all tests pass, your tests might be too easy. Good test suites include cases that are hard to get right. A few failures tell you where to focus improvement.

## If You Have Extra Time

- Challenge: "Add a pre-check that runs /safety/check before /query automatically"
- Challenge: "Write a test case that the safety classifier consistently gets wrong"
- Discussion: "What would you measure in a production RAG dashboard?"
- Advanced: "Design a multi-layer safety pipeline with regex + LLM + output filtering"

All great ideas. Acknowledge them and note that Week 3 gave them the foundation to implement any of these.

## Timing Guide

| Activity | Time |
|----------|------|
| Live-code: chunker tests | 15 min |
| Live-code: confidence tests | 10 min |
| Show full test suite | 5 min |
| System walkthrough (whiteboard) | 20 min |
| Production readiness discussion | 15 min |
| Code review exercise | 15 min |
| Wrap-up + final questions | 10 min |

## If You Have Extra Time

- Let students write their own test case and contribute it to the test suite
- Discuss: "If you had to explain RAG to a non-technical manager in 2 sentences, what would you say?"
- Challenge: "Add a test that verifies the chunker handles Unicode text correctly"
