import pandas as pd
import pytest

from recommender.service import RecommenderService


def _service() -> RecommenderService:
    ratings = pd.DataFrame(
        {
            "userID": [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4],
            "movieID": [10, 20, 30, 10, 20, 30, 10, 20, 40, 10, 20, 40],
            "rating": [5, 4, 3, 5, 4, 2, 4, 3, 5, 1, 1, 4],
            "timestamp": [0] * 12,
        }
    )
    movies = pd.DataFrame({"movieID": [10, 20, 30, 40], "title": ["A", "B", "C", "D"]})
    return RecommenderService(ratings, movies, min_voters=1)


def test_recommend_returns_ids_and_excludes_rated():
    service = _service()
    recs = service.recommend(1, k=10)
    assert recs, "expected recommendations"
    rated = {10, 20, 30}
    assert not (rated & {m for m, _ in recs})
    assert [s for _, s in recs] == sorted([s for _, s in recs], reverse=True)


def test_recommend_unknown_user_raises():
    with pytest.raises(KeyError):
        _service().recommend(999)


def test_similar_users_sorted_and_excludes_self():
    service = _service()
    similar = service.similar_users(1, n=3)
    assert all(u != 1 for u, _ in similar)
    assert [s for _, s in similar] == sorted([s for _, s in similar], reverse=True)
    assert all(s > 0 for _, s in similar)


def test_movie_title_lookup():
    service = _service()
    assert service.movie_title(10) == "A"
    assert service.movie_title(999) is None
