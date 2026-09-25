"""Shared recommendation algorithms.

Populated in Slice 2: vectorized similarity metrics, top-K recommendations,
MovieLens ETL, and offline evaluation.
"""

from recommender.etl import build_matrix, load_movielens
from recommender.evaluate import evaluate, train_test_split
from recommender.recommend import recommend_for_user
from recommender.similarity import (
    co_rated_counts,
    euclidean_similarity,
    pearson_similarity,
    significance_weighted,
)

__version__ = "0.1.0"

__all__ = [
    "build_matrix",
    "co_rated_counts",
    "default_paths",
    "euclidean_similarity",
    "evaluate",
    "load_movielens",
    "pearson_similarity",
    "recommend_for_user",
    "significance_weighted",
    "train_test_split",
]
