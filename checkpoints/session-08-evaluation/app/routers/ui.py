# ============================================================
# Router: /ui — Transparent RAG interface (Session 5)
# ============================================================
# Serves a simple HTML page where students can:
#   - Type a question and see the RAG answer
#   - See retrieved sources with snippet previews
#   - See confidence level and distance scores
#   - See clear no-result and weak-evidence states
#
# TEACHING POINT:
#   This is NOT a frontend course. The HTML is deliberately
#   minimal — vanilla JS, inline CSS, no frameworks.
#   The point is to show transparent UX, not build a UI.
#
#   Students should focus on what information is displayed,
#   not how it looks.
# ============================================================

from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["UI"])


@router.get("/ui", response_class=HTMLResponse)
def show_query_ui():
    """
    Serve the transparent RAG query interface.

    Open http://localhost:8000/ui in your browser.
    """
    html_path = Path(__file__).parent.parent / "static" / "query.html"
    html_content = html_path.read_text(encoding="utf-8")
    return HTMLResponse(content=html_content)
