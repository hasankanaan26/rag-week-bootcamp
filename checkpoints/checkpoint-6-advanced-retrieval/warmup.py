"""
warmup.py — download the models BEFORE class, and build the child index.

    python checkpoints/checkpoint-6-advanced-retrieval/warmup.py

1. The local embedding model, all-MiniLM-L6-v2 (about 80 MB, ~/.cache/chroma)
2. The cross-encoder reranker, ms-marco-MiniLM-L-6-v2 (about 90 MB, ~/.cache/huggingface)
3. If a live index exists: the children index for parent-document retrieval

On slow Wi-Fi the downloads take minutes, so do this at home.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.rag import catalog, children, reranker  # noqa: E402
from app.rag.embedder import embed_texts, embedding_model_id  # noqa: E402

start = time.time()
print(f"1/3 Loading {embedding_model_id()} (first time: about 80 MB)...")
embed_texts(["How many vacation days do I get?"])
print(f"    ready ({time.time() - start:.1f}s)")

start = time.time()
print("2/3 Loading the cross-encoder reranker (first time: about 90 MB)...")
scores = reranker.score("team dinner limit", ["Team meals and events: up to $90 per person.", "Use the VPN."])
print(f"    ready ({time.time() - start:.1f}s): the relevant line scores {scores[0]:.1f}, the other {scores[1]:.1f}")

if catalog.active_name():
    start = time.time()
    print("3/3 Building the children index for parent-document retrieval...")
    print(f"    {children.count_children()} children ready ({time.time() - start:.1f}s)")
else:
    print("3/3 No live index yet: run sync.py --apply, then warmup.py again.")
print("You're set for class.")
