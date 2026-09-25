"""Shared recommendation algorithms.

Slices 2-3: vectorized similarity metrics, top-K recommendations, MovieLens
ETL, offline evaluation, service interface, and the batch job.
"""

from recommender.batch import run
from recommender.etl import build_matrix, default_paths, load_movielens
from recommender.evaluate import evaluate, train_test_split
from recommender.recommend import recommend_for_user
from recommender.service import RecommenderService
from recommender.similarity import (
    co_rated_counts,
    euclidean_similarity,
    pearson_similarity,
    significance_weighted,
)
from recommender.store import Store

__version__ = "0.1.0"

__all__ = [
    "RecommenderService",
    "Store",
    "build_matrix",
    "co_rated_counts",
    "default_paths",
    "euclidean_similarity",
    "evaluate",
    "load_movielens",
    "pearson_similarity",
    "recommend_for_user",
    "run",
    "significance_weighted",
    "train_test_split",
]
