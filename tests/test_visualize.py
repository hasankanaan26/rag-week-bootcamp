# ============================================================
# Tests: Embedding visualization helpers
# ============================================================
# Tests dimensionality reduction logic without real embeddings.
# Logic is inlined — no external dependencies except scikit-learn.
#
#   pip install pytest scikit-learn numpy
#   pytest tests/test_visualize.py -v
# ============================================================

import numpy as np


def reduce_dimensions(embeddings, method="tsne"):
    """Inline copy of visualize.reduce_dimensions for testing."""
    matrix = np.array(embeddings)

    if method == "pca":
        from sklearn.decomposition import PCA
        reducer = PCA(n_components=2, random_state=42)
    else:
        from sklearn.manifold import TSNE
        perplexity = min(30, max(2, len(embeddings) - 1))
        reducer = TSNE(
            n_components=2,
            perplexity=perplexity,
            random_state=42,
            max_iter=500,
        )

    coords = reducer.fit_transform(matrix)
    return coords.tolist()


# --- Tests ---

def test_pca_returns_2d():
    """PCA reduces N-dimensional embeddings to 2D."""
    embeddings = np.random.rand(10, 50).tolist()
    coords = reduce_dimensions(embeddings, method="pca")
    assert len(coords) == 10
    assert all(len(c) == 2 for c in coords)


def test_tsne_returns_2d():
    """t-SNE reduces N-dimensional embeddings to 2D."""
    embeddings = np.random.rand(10, 50).tolist()
    coords = reduce_dimensions(embeddings, method="tsne")
    assert len(coords) == 10
    assert all(len(c) == 2 for c in coords)


def test_pca_preserves_count():
    """Output has the same number of points as input."""
    embeddings = np.random.rand(25, 100).tolist()
    coords = reduce_dimensions(embeddings, method="pca")
    assert len(coords) == 25


def test_small_dataset_tsne():
    """t-SNE works with small datasets (adjusts perplexity)."""
    embeddings = np.random.rand(5, 20).tolist()
    coords = reduce_dimensions(embeddings, method="tsne")
    assert len(coords) == 5
    assert all(len(c) == 2 for c in coords)
