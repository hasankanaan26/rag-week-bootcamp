# ============================================================
# Router: /embed — Explore how embeddings work
# ============================================================
# Teaching tool for exploring embedding distances.
#
# TRY THESE EXPERIMENTS:
#   1. Synonyms: ["vacation days", "annual leave", "time off"]
#   2. Same vs different topic: ["vacation days", "annual leave", "Python programming"]
#   3. Question vs answer: ["How many vacation days?", "Employees receive 20 days of annual leave"]
# ============================================================

import math
from fastapi import APIRouter
from app.models import EmbedRequest, EmbedResponse
from app.rag.embedder import embed_texts

router = APIRouter(prefix="/embed", tags=["Embedding Explorer"])


# Purpose:
# Embeds a list of texts and computes pairwise L2 distances between them.
# Helps students build intuition about what embeddings capture.
@router.post("", response_model=EmbedResponse)
def explore_embeddings(request: EmbedRequest):
    """
    Embed a list of texts and compute pairwise distances.

    Send 2+ texts to see how similar they are in vector space.
    Low distance = similar meaning, high distance = different.
    """
    texts = request.texts
    embeddings = embed_texts(texts)
    dimensions = len(embeddings[0]) if embeddings else 0

    distances = {}
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            dist = math.sqrt(
                sum(
                    (embeddings[i][k] - embeddings[j][k]) ** 2
                    for k in range(dimensions)
                )
            )
            label = f"'{texts[i]}' <-> '{texts[j]}'"
            distances[label] = round(dist, 4)

    return EmbedResponse(distances=distances, dimensions=dimensions)
