# ============================================================
# Prompts: an LLM as a judge of answers (Checkpoint 6)
# ============================================================
# Retrieval metrics need no LLM: did the right document come back?
# Answer quality does. Two questions, two prompts:
#
#   faithfulness   Is every claim in the answer supported by the
#                  retrieved context? (catches hallucination)
#   correctness    Does the answer agree with the hand-written
#                  reference answer? (catches wrong-but-grounded,
#                  e.g. a correct quote of a superseded policy)
#
# Eyes open: the judge is an LLM too. Same model judging its own
# answers inflates scores; scores vary between runs; it costs a call
# per question per metric. Spot-check 10 verdicts by hand before you
# trust any number it produces.
# ============================================================

FAITHFULNESS_PROMPT = """You check whether an answer is supported by a context.

Context:
{context}

Answer:
{answer}

Split the answer into its factual claims (ignore phrases like "according to the policy").
For each claim, decide if the context states it or directly implies it.
Reply with JSON only: {{"claims": [{{"claim": "...", "supported": true}}]}}"""

CORRECTNESS_PROMPT = """You compare an answer with a reference answer written by a person.

Question: {question}
Reference answer: {reference}
Answer to grade: {answer}

Does the answer state the same facts as the reference (numbers, names, conditions)?
Extra correct detail is fine. A missing key fact or a contradiction is not.
Reply with JSON only: {{"correct": true, "reason": "one short sentence"}}"""
