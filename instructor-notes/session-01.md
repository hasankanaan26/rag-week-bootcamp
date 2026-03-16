# Instructor Notes — Session 1: RAG Foundations

## Session Overview

- **Duration:** ~90 minutes (adjust based on class pace)
- **Split:** ~70% live coding, ~30% discussion
- **Vibe:** This is a warm-up session. Reinforce Week 1-2 patterns while introducing the RAG motivation.

## Before Class

- [ ] Ensure `.env` is configured with a working API key
- [ ] Test that `uvicorn app.main:app --reload` starts cleanly from the base scaffold
- [ ] Have the Swagger UI open in a browser tab ready to demo
- [ ] Have the `data/knowledge/leave-policy.md` file open to show the "source of truth"

## What to Type Live vs Prebuilt

| Component | Live or Prebuilt? | Why? |
|-----------|-------------------|------|
| `main.py` | **Type live** | Review of FastAPI basics — takes 2 minutes |
| `config.py` | **Type live** | Familiar pattern from prior weeks — fast |
| `models.py` | **Type live** | Shows Pydantic usage — good reinforcement |
| `llm.py` | **Type live** | Core skill, needs to be understood deeply |
| `prompts/plain_answer.py` | **Type live** | Students should see prompt design happen |
| `prompts/grounded_answer.py` | **Type live** | THE key teaching moment of Session 1 |
| `routers/ask.py` | **Type live** | Where everything connects |
| `data/knowledge/*.md` files | **Prebuilt** | Content writing is dead time in class |
| `.env.example`, requirements | **Prebuilt** | Boring, error-prone to type |
| Dockerfile, docker-compose | **Prebuilt** | Same as prior weeks |

## Suggested Live-Coding Order

1. **Start from the base scaffold** (just `main.py` with `/health`)
2. **Add `config.py`** — "Same as Week 2, just loading our API key"
3. **Add `models.py`** — "Question in, Answer out. That's it."
4. **Add `llm.py`** — "One function. Sends a prompt, gets text back."
5. **Add `prompts/plain_answer.py`** — "Simple system prompt. Let's see what happens."
6. **Wire up `routers/ask.py`** with just the plain endpoint first
7. **Demo the plain endpoint** — ask about vacation days. Watch it hallucinate.
8. **Pause for discussion** — "Is this answer correct? How would you verify it?"
9. **Open `leave-policy.md`** — "Here's the real policy. 20 days. The LLM said [wrong number]."
10. **Add `prompts/grounded_answer.py`** — "What if we just... paste the real answer into the prompt?"
11. **Add the `/ask/grounded` endpoint** to the router
12. **Demo the grounded endpoint** — same question, correct answer now
13. **The aha moment:** "This works! But we hardcoded the context. What if we have 100 documents? We need automation. That's RAG."

## Key Talking Points

### The Hallucination Demo (Step 7)
This is the most important moment. Ask the class to predict what the LLM will say about Acme Corp's leave policy. Then show the actual answer. The gap between the LLM's answer and reality makes the case for RAG.

Good questions to use for the demo:
- "How many vacation days do I get?" (LLM will guess a number)
- "What is our parental leave policy?" (LLM will make up something generic)
- "Do I need a medical certificate for sick leave?" (LLM might say yes/no randomly)

### The Grounding Demo (Step 12)
Show the same question producing the correct answer. Then show a question outside the context ("What is the Git branching convention?") — the grounded endpoint should say it doesn't know. This is good behavior.

### Connecting to Prior Weeks
- "The `llm.py` function is the same pattern you used in Week 2"
- "The router structure is identical to what you built in Week 1"
- "The Pydantic models are the same — just different fields"

## Common Student Questions

**"Why not just fine-tune the LLM on our documents?"**
Fine-tuning is expensive, slow to update, and hard to control. RAG lets you update knowledge by changing documents, not retraining models. You can also see exactly which documents informed each answer.

**"Why not just increase the context window and paste everything?"**
Cost, latency, and noise. Even with large context windows, more irrelevant text = worse answers. Retrieval focuses the LLM on what matters.

**"Is the grounded endpoint real RAG?"**
No — it's manual RAG. Real RAG automates the retrieval step. But the grounded endpoint shows the core idea: give the LLM real context, get better answers.

## Timing Guide

| Activity | Time |
|----------|------|
| Intro and setup verification | 10 min |
| Live code: config, models, llm | 15 min |
| Live code: plain prompt + router | 15 min |
| Demo: hallucination | 10 min |
| Live code: grounded prompt + endpoint | 15 min |
| Demo: grounded vs plain comparison | 10 min |
| Discussion + Q&A | 15 min |

## If You're Running Short on Time

Skip typing `config.py` and `models.py` live — point students to the checkpoint and focus on the prompt files and the hallucination demo. The demo is more important than the boilerplate.

## If You Have Extra Time

- Let students try different questions and share what the LLM hallucinated
- Ask students to modify the `DEMO_CONTEXT` to include coding standards and test again
- Preview Session 2: "What if the system could automatically find the right context?"
