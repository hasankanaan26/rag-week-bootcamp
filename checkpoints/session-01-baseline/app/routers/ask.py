# ============================================================
# Router: /ask — Plain Q&A and Grounded Demo
# ============================================================
# Two endpoints:
#   POST /ask          → Plain LLM answer (no context, may hallucinate)
#   POST /ask/grounded → Manually grounded answer (hardcoded context)
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


@router.post("/grounded", response_model=Answer)
def ask_grounded(request: Question):
    """
    Ask a question — answered using manually injected company context.

    This is NOT real RAG. The context is hardcoded in the prompt.
    This endpoint exists to demonstrate what "grounding" looks like
    before we automate it with retrieval in later sessions.

    Compare this answer with the plain /ask endpoint to see
    the difference between grounded and ungrounded responses.
    """
    # Build the system prompt with hardcoded context injected
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
        grounded=True,  # Context was provided (manually)
    )
