# ============================================================
# BM25 — keyword search, by hand (Checkpoint 6)
# ============================================================
# Embeddings match MEANING. They are weak at EXACT tokens: a ticket
# number (IT-4112), an incident id (INC-2024-017), a library name
# (Zustand). To an embedding model "IT-4112" and "IT-4120" look
# almost the same. To a keyword index they are different words.
#
# BM25 is the classic keyword score (Elasticsearch and OpenSearch use
# it by default). For each query word that appears in a chunk:
#
#   idf(word)   rare words count more        log(1 + (N - n + 0.5) / (n + 0.5))
#   tf(word)    more occurrences count more, but with diminishing returns (k1)
#   length      long chunks are penalised a little (b)
#
# In production the keyword index lives in a search engine (or a
# Postgres tsvector column) next to the vectors, filtered the same
# way. Here it is 40 lines over the chunks this user may read.
# ============================================================

import math
import re
from collections import Counter

# Keeps identifiers whole: "inc-2024-017", "it-4112", "4.2", "ext.4357" -> parts
TOKEN_RE = re.compile(r"[a-z0-9]+(?:[-.][a-z0-9]+)*")
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "can", "do", "does", "for", "from", "has", "have",
    "how", "i", "if", "in", "is", "it", "its", "my", "of", "on", "or", "our", "should", "so", "that",
    "the", "their", "there", "this", "to", "was", "we", "what", "when", "where", "which", "who", "why",
    "will", "with", "you", "your", "me", "am", "any", "about", "into", "per",
}


def tokenize(text: str) -> list[str]:
    tokens = []
    for token in TOKEN_RE.findall(text.lower()):
        if token in STOPWORDS:
            continue
        tokens.append(token)
        if "-" in token or "." in token:  # also index the parts: "it-4112" -> "it", "4112"
            tokens.extend(p for p in re.split(r"[-.]", token) if p and p not in STOPWORDS)
    return tokens


class BM25:
    """Okapi BM25 over a fixed list of texts."""

    def __init__(self, texts: list[str], k1: float = 1.5, b: float = 0.75):
        self.k1, self.b = k1, b
        self.docs = [Counter(tokenize(t)) for t in texts]
        self.lengths = [sum(d.values()) for d in self.docs]
        self.avg_length = (sum(self.lengths) / len(self.lengths)) if self.lengths else 0.0
        df = Counter()
        for d in self.docs:
            df.update(d.keys())
        n = len(self.docs)
        self.idf = {w: math.log(1 + (n - c + 0.5) / (c + 0.5)) for w, c in df.items()}

    def scores(self, query: str) -> list[float]:
        words = tokenize(query)
        out = []
        for doc, length in zip(self.docs, self.lengths):
            score = 0.0
            for w in words:
                tf = doc.get(w, 0)
                if not tf:
                    continue
                norm = tf * (self.k1 + 1) / (tf + self.k1 * (1 - self.b + self.b * length / (self.avg_length or 1)))
                score += self.idf.get(w, 0.0) * norm
            out.append(score)
        return out


# Purpose:
# Reciprocal Rank Fusion: merge several rankings without comparing their
# scores (a cosine distance and a BM25 score are not on the same scale).
# Each list votes 1 / (k + rank) for each item; k=60 is the usual constant.
def rrf(rankings: list[list[str]], k: int = 60) -> list[tuple[str, float]]:
    scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, item in enumerate(ranking, 1):
            scores[item] = scores.get(item, 0.0) + 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
