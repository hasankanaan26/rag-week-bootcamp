# ============================================================
# Prompt: Plain answer — no context, just the LLM's own knowledge
# ============================================================
# This is the "before" prompt. The LLM answers from its training data.
# When students ask about Acme Corp, this prompt will produce
# hallucinated answers — which is exactly the point.
# ============================================================

PLAIN_SYSTEM_PROMPT = """You are a helpful assistant for Acme Corp employees.
Answer the user's question clearly and concisely.
If you don't know the answer, say so honestly."""
