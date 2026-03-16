# ============================================================
# Router: /ask — Plain Q&A and Grounded Demo (unchanged from Session 1)
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
    No company documents are used. The LLM may hallucinate.
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
