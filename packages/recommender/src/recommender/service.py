"""Service interface shared by the batch job (Slice 3) and the API (Slice 4)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from recommender.etl import build_matrix, load_movielens
from recommender.recommend import recommend_for_user
from recommender.similarity import (
    co_rated_counts,
    euclidean_similarity,
    pearson_similarity,
    significance_weighted,
)


class RecommenderService:
    """Precomputed similarities with per-user recommendation methods."""

    def __init__(
        self,
        ratings: pd.DataFrame,
        movies: pd.DataFrame,
        min_similarity: float = 0.0,
        min_voters: int = 10,
        gamma: float = 50.0,
    ):
        self.ratings = ratings
        self.titles = dict(zip(movies["movieID"], movies["title"]))
        self.min_similarity = min_similarity
        self.min_voters = min_voters
        self.gamma = gamma
        self.matrix, self.user_ids, self.movie_ids, self.user_index, _ = build_matrix(
            ratings
        )
        raw = pearson_similarity(self.matrix)
        self.similarities = significance_weighted(
            raw, co_rated_counts(self.matrix), gamma
        )
        self.euclidean_similarities = euclidean_similarity(self.matrix)

    @classmethod
    def from_movielens(
        cls,
        data_path: Path | str | None = None,
        item_path: Path | str | None = None,
        **kwargs,
    ) -> RecommenderService:
        ratings, movies = load_movielens(data_path, item_path)
        return cls(ratings, movies, **kwargs)

    def _row(self, user_id: int) -> int:
        try:
            return self.user_index[user_id]
        except KeyError as exc:
            raise KeyError(f"Unknown user: {user_id}") from exc

    def recommend(self, user_id: int, k: int = 10) -> list[tuple[int, float]]:
        """Top-K ``(movie_id, predicted_rating)`` for ``user_id``."""
        recs = recommend_for_user(
            self.matrix,
            self.similarities,
            self._row(user_id),
            top_k=k,
            min_similarity=self.min_similarity,
            min_voters=self.min_voters,
        )
        return [(int(self.movie_ids[i]), score) for i, score in recs]

    def similar_users(self, user_id: int, n: int = 10) -> list[tuple[int, float]]:
        """Top-N ``(user_id, similarity)`` for ``user_id``, self excluded."""
        sims = self.similarities[self._row(user_id)].copy()
        sims[self._row(user_id)] = -np.inf
        order = np.argsort(sims, kind="stable")[::-1][:n]
        return [(int(self.user_ids[i]), float(sims[i])) for i in order if sims[i] > 0]

    def similarity(self, user_a: int, user_b: int, metric: str = "pearson") -> float:
        """Pairwise similarity under ``pearson`` or ``euclidean``."""
        if metric == "euclidean":
            mat = self.euclidean_similarities
        elif metric == "pearson":
            mat = self.similarities
        else:
            raise ValueError(f"Unknown metric: {metric}")
        return float(mat[self._row(user_a), self._row(user_b)])

    def add_rating(self, user_id: int, movie_id: int, rating: int) -> None:
        """Append (or overwrite) a rating and rebuild similarities.

        Rebuilds cost ~2 s on MovieLens 100K — fine for Slice 4 scope; the
        production path (ADR-2/ADR-4) serves precomputed tables instead.
        """
        import pandas as pd

        keep = ~(
            (self.ratings["userID"] == user_id) & (self.ratings["movieID"] == movie_id)
        )
        new_row = pd.DataFrame(
            {
                "userID": [user_id],
                "movieID": [movie_id],
                "rating": [rating],
                "timestamp": [0],
            }
        )
        self.ratings = pd.concat([self.ratings[keep], new_row], ignore_index=True)
        self.matrix, _, _, self.user_index, _ = build_matrix(self.ratings)
        raw = pearson_similarity(self.matrix)
        self.similarities = significance_weighted(
            raw, co_rated_counts(self.matrix), self.gamma
        )
        self.euclidean_similarities = euclidean_similarity(self.matrix)

    def movie_title(self, movie_id: int) -> str | None:
        return self.titles.get(movie_id)
