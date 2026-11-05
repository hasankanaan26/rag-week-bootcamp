# ============================================================
# Children — small chunks that point to their parent (Checkpoint 6)
# ============================================================
# Parent-document retrieval: "match small, return big".
#
#   Small chunks match a question precisely, but carry little context.
#   Big chunks carry context, but their embedding is an average of
#   everything in them, so one sentence about billing reviews is
#   drowned by four paragraphs about deployments and on-call.
#
# So we index both:
#   parents   the live index (one chunk per section, from the sync job)
#   children  each parent split into sentences, embedded on their own,
#             each remembering its parent_id
# Search the children; return their parents.
#
# The children collection is DERIVED from the live index. Its name
# includes the live collection's name, and it records which parents it
# was built from: after a sync it is rebuilt automatically. In
# production the sync job would rebuild it in the same run.
# ============================================================

import hashlib
import re

from app.config import CHILD_MAX_CHARS
from app.rag import catalog
from app.rag.embedder import embed_texts
from app.rag.store_chroma import drop_collection, get_client

SENTENCE_RE = re.compile(r"(?<=[.!?])\s+|\n+")


def split_sentences(text: str, max_chars: int) -> list[str]:
    pieces, current = [], ""
    for part in (p.strip(" -") for p in SENTENCE_RE.split(text)):
        if not part:
            continue
        if current and len(current) + 1 + len(part) > max_chars:
            pieces.append(current)
            current = part
        else:
            current = f"{current} {part}".strip()
    if current:
        pieces.append(current)
    return pieces


def _children_name(parent: str) -> str:
    return f"{parent}_children"


def _fingerprint(ids: list[str], metas: list[dict]) -> str:
    h = hashlib.sha256()
    for i, m in sorted(zip(ids, metas)):
        h.update(f"{i}|{m.get('content_hash')}|{m.get('allowed_groups')}|{m.get('status')}".encode())
    return h.hexdigest()[:16]


# Purpose:
# Make sure the children collection matches the live index; (re)build it if not.
def ensure_children() -> str:
    parent = catalog.active_name()
    if not parent:
        raise RuntimeError("No live index. Run: python sync.py --apply")
    client = get_client()
    parents = client.get_collection(parent).get(include=["documents", "metadatas"])
    fingerprint = _fingerprint(parents["ids"], parents["metadatas"])
    name = _children_name(parent)
    try:
        existing = client.get_collection(name)
        if (existing.metadata or {}).get("fingerprint") == fingerprint:
            return name
        drop_collection(name)
    except Exception:
        pass

    ids, texts, metas = [], [], []
    for pid, text, meta in zip(parents["ids"], parents["documents"], parents["metadatas"]):
        header, _, body = text.partition("\n")
        title = meta.get("title", "")
        for n, sentence in enumerate(split_sentences(body or header, CHILD_MAX_CHARS)):
            ids.append(f"{pid}#{n:02d}")
            texts.append(f"{title}: {sentence}")
            metas.append({**meta, "parent_id": pid})
    col = client.create_collection(name, metadata={"fingerprint": fingerprint, "parent": parent})
    vectors = embed_texts(texts)
    for start in range(0, len(ids), 500):
        col.add(ids=ids[start:start + 500], documents=texts[start:start + 500],
                embeddings=vectors[start:start + 500], metadatas=metas[start:start + 500])
    return name


def count_children() -> int:
    return get_client().get_collection(ensure_children()).count()
