# Session 1 — RAG Foundations and FastAPI Integration

## Learning Goals

By the end of this session, students should be able to:

1. Explain what RAG is and why it's needed
2. Build a FastAPI endpoint that calls an LLM
3. Demonstrate the difference between a plain LLM answer and a grounded one
4. Explain what "grounding" means in the context of LLM applications

## Concepts Introduced

### What is RAG?

Retrieval-Augmented Generation (RAG) is a pattern where you:
1. **Retrieve** relevant information from a knowledge base
2. **Augment** the LLM's prompt with that information
3. **Generate** an answer that's grounded in real data

The LLM doesn't memorize your company's documents. You have to give it the relevant pieces at query time.

### Why not just use the LLM's training data?

- The LLM was trained on public internet data, not your company's internal docs
- Even if it was, training data has a cutoff date — policies change
- The LLM can't distinguish between real company facts and plausible-sounding fiction
- When an LLM makes something up that sounds right, that's called **hallucination**

### What is "grounding"?

Grounding means providing factual context so the LLM bases its answer on real information instead of guessing. In Session 1, we ground manually (hardcoded context). In later sessions, we automate grounding with retrieval.

## Files Created

| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI app with health check |
| `app/config.py` | LLM settings from environment |
| `app/models.py` | Question and Answer Pydantic models |
| `app/llm.py` | LLM caller function |
| `app/routers/ask.py` | `/ask` (plain) and `/ask/grounded` endpoints |
| `app/prompts/plain_answer.py` | System prompt for plain answers |
| `app/prompts/grounded_answer.py` | System prompt with hardcoded context |

## Demo Script

### 1. Start the app

```bash
uvicorn app.main:app --reload
```

### 2. Ask a plain question (will hallucinate)

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How many vacation days do I get at Acme Corp?"}'
```

Notice: The LLM invents an answer. It might say 15 days, 10 days, or "it depends on your role." None of this is real.

### 3. Ask the same question with grounding

```bash
curl -X POST http://localhost:8000/ask/grounded \
  -H "Content-Type: application/json" \
  -d '{"question": "How many vacation days do I get at Acme Corp?"}'
```

Notice: The answer now correctly says 20 days, because the real leave policy was injected into the prompt.

### 4. Ask something outside the grounded context

```bash
curl -X POST http://localhost:8000/ask/grounded \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the Git branching convention?"}'
```

Notice: The grounded endpoint correctly says it doesn't have that information, because the coding standards weren't included in the hardcoded context. This is honest behavior — and exactly what we want.

## Discussion Questions

- "Why did the plain endpoint make up an answer instead of saying it didn't know?"
- "What's the problem with hardcoding context into the prompt? What if we have 100 documents?"
- "How would you automate the process of finding the right context for each question?"

That last question leads directly into Session 2.
