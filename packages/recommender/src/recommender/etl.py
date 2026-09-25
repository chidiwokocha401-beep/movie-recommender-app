"""Loading MovieLens 100K files and shaping the user-item matrix."""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd


def default_paths() -> tuple[Path, Path]:
    """Locate the legacy ``u.data`` / ``u.item`` files.

    ``MOVIELENS_DATA`` / ``MOVIELENS_ITEM`` env vars override (used in Docker);
    otherwise resolved relative to the repo.
    """
    data_env, item_env = os.getenv("MOVIELENS_DATA"), os.getenv("MOVIELENS_ITEM")
    if data_env and item_env:
        return Path(data_env), Path(item_env)
    repo_root = Path(__file__).resolve().parents[4]
    legacy = repo_root / "movie-recommender-main"
    return legacy / "u.data", legacy / "u.item"


def load_movielens(
    data_path: Path | str | None = None,
    item_path: Path | str | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return ``(ratings, movies)`` DataFrames.

    ratings columns: userID, movieID, rating, timestamp.
    movies columns: movieID, title.
    """
    if data_path is None or item_path is None:
        default_data, default_item = default_paths()
        data_path = default_data if data_path is None else data_path
        item_path = default_item if item_path is None else item_path

    ratings = pd.read_csv(
        data_path,
        sep="\t",
        names=["userID", "movieID", "rating", "timestamp"],
    )
    movies = pd.read_csv(
        item_path,
        sep="|",
        encoding="latin-1",
        usecols=[0, 1],
        names=["movieID", "title"],
    )
    return ratings, movies


def build_matrix(
    ratings: pd.DataFrame,
    user_col: str = "userID",
    movie_col: str = "movieID",
    rating_col: str = "rating",
) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict, dict]:
    """Pivot ratings into a users × items matrix (NaN where unrated).

    Returns ``(matrix, user_ids, movie_ids, user_index, movie_index)``.
    """
    user_ids = np.sort(ratings[user_col].unique())
    movie_ids = np.sort(ratings[movie_col].unique())
    user_index = {u: i for i, u in enumerate(user_ids)}
    movie_index = {m: j for j, m in enumerate(movie_ids)}

    matrix = np.full((len(user_ids), len(movie_ids)), np.nan)
    rows = ratings[user_col].map(user_index).to_numpy()
    cols = ratings[movie_col].map(movie_index).to_numpy()
    matrix[rows, cols] = ratings[rating_col].to_numpy(dtype=float)
    return matrix, user_ids, movie_ids, user_index, movie_index
