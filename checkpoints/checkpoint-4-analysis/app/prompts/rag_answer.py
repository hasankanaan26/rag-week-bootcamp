# ============================================================
# Prompt: RAG answer — grounded in retrieved context
# ============================================================
# This is the core RAG prompt. It tells the LLM:
#   1. Here is some context from our documents
#   2. Answer the question based ONLY on that context
#   3. If the context doesn't help, say so
#
# TEACHING POINT:
#   Compare this with grounded_answer.py from Checkpoint 1.
#   The structure is identical! The only difference is WHERE
#   the context comes from:
#     Checkpoint 1: hardcoded by the developer
#     Checkpoint 3: retrieved automatically from the vector store
#
#   That's the entire point of RAG — automating the grounding.
#
# The {context} placeholder gets filled with retrieved chunks.
# ============================================================

RAG_SYSTEM_PROMPT = """You are a helpful assistant for Acme Corp employees.
Answer the user's question using the context provided below.

Rules:
- Base your answer on the provided context.
- If the context contains relevant information, use it to answer even if it doesn't cover every detail.
- Only say "I don't have information about that in the knowledge base" if the context is completely unrelated to the question.
- Be concise and direct.
- When possible, mention which document the information comes from.

--- CONTEXT START ---
{context}
--- CONTEXT END ---"""
