# ============================================================
# Router: /embed — Explore how embeddings work
# ============================================================
import math
from fastapi import APIRouter
from app.models import EmbedRequest, EmbedResponse
from app.rag.embedder import embed_texts

router = APIRouter(prefix="/embed", tags=["Embedding Explorer"])


@router.post("", response_model=EmbedResponse)
def explore_embeddings(request: EmbedRequest):
    """Embed a list of texts and compute pairwise distances."""
    texts = request.texts
    embeddings = embed_texts(texts)
    dimensions = len(embeddings[0]) if embeddings else 0
    distances = {}
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            dist = math.sqrt(
                sum((embeddings[i][k] - embeddings[j][k]) ** 2 for k in range(dimensions))
            )
            label = f"'{texts[i]}' ↔ '{texts[j]}'"
            distances[label] = round(dist, 4)
    return EmbedResponse(distances=distances, dimensions=dimensions)
