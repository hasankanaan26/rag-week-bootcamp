# ============================================================
# Router: /ask — Plain Q&A and Grounded Demo
# ============================================================
# Two endpoints:
#   POST /ask          -> Plain LLM answer (no context, may hallucinate)
#   POST /ask/grounded -> Manually grounded answer (hardcoded context)
#
# The grounded endpoint exists purely for teaching. It shows
# students what "grounding" means before we automate it with RAG.
#
# DEMO QUESTIONS TO TRY:
#   "How many vacation days do I get?"
#   "What is our parental leave policy?"
#   "What is the Git branching strategy at Acme Corp?"
#
# Try each question on BOTH endpoints and compare the answers.
# The plain endpoint will hallucinate. The grounded one won't.
# ============================================================

from fastapi import APIRouter
from app.models import Question, Answer
from app.llm import call_llm, get_model_name
from app.prompts.plain_answer import PLAIN_SYSTEM_PROMPT
from app.prompts.grounded_answer import GROUNDED_SYSTEM_PROMPT, DEMO_CONTEXT

router = APIRouter(prefix="/ask", tags=["Q&A"])


# Purpose:
# Answers a question using only the LLM's training data (no grounding).
# This endpoint demonstrates the hallucination problem that RAG solves.
@router.post("", response_model=Answer)
def ask_plain(request: Question):
    """
    Ask a question — answered by the LLM's general knowledge only.

    No company documents are used. The LLM may hallucinate
    facts about Acme Corp because it has no real information.
    """
    response_text = call_llm(
        user_prompt=request.question,
        system_prompt=PLAIN_SYSTEM_PROMPT,
    )

    return Answer(
        answer=response_text,
        model=get_model_name(),
        grounded=False,
    )


# Purpose:
# Answers a question using manually injected context (hardcoded company data).
# Shows students what grounding does before RAG automates it.
@router.post("/grounded", response_model=Answer)
def ask_grounded(request: Question):
    """
    Ask a question — answered using manually injected company context.

    This is NOT real RAG. The context is hardcoded in the prompt.
    Compare this answer with /ask to see the difference.
    """
    system_prompt_with_context = GROUNDED_SYSTEM_PROMPT.format(
        context=DEMO_CONTEXT
    )

    response_text = call_llm(
        user_prompt=request.question,
        system_prompt=system_prompt_with_context,
    )

    return Answer(
        answer=response_text,
        model=get_model_name(),
        grounded=True,
    )
