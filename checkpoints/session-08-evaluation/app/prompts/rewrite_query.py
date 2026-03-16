# ============================================================
# Prompt: Query Rewriting for better retrieval
# ============================================================
# Vague or colloquial questions often fail at retrieval because
# the embedding of "time off" is far from "annual leave" in
# some models, or the user question is too short.
#
# Query rewriting asks the LLM to rephrase the question with
# more specific terms, synonyms, and formal language that
# better matches what's in the knowledge base.
#
# WHEN TO USE:
#   - Short, vague queries: "time off" → adds "vacation", "leave"
#   - Colloquial language: "Can I WFH?" → "remote work policy"
#   - Questions with pronouns: "How do I do it?" → needs context
#
# WHEN IT HURTS:
#   - Already specific queries: rewriting adds noise
#   - Factual lookups: "What is the meal expense limit?" is fine
#
# TEACHING POINT:
#   Toggle rewrite=true vs false on the same query and compare
#   the retrieval distances. Rewriting often lowers the distance
#   (better match) for vague queries.
# ============================================================

REWRITE_PROMPT = """You are a search query optimizer for a company knowledge base.

The knowledge base contains documents about:
- Leave and vacation policies
- Expense policies and limits
- Coding standards and tech stack
- Remote work guidelines
- Onboarding procedures
- Team directory and FAQ

Given the user's question, rewrite it as a more specific search query that will
match relevant documents. Add synonyms and formal terms. Keep it as a single
question — do not add explanations.

User question: {question}

Rewritten search query:"""
