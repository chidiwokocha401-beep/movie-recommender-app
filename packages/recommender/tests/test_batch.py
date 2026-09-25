import sqlite3

import pandas as pd

from recommender.batch import run
from recommender.service import RecommenderService


def _service() -> RecommenderService:
    ratings = pd.DataFrame(
        {
            "userID": [1, 1, 2, 2, 2, 3, 3, 3],
            "movieID": [10, 20, 10, 20, 30, 10, 20, 30],
            "rating": [5, 4, 5, 4, 5, 1, 2, 1],
            "timestamp": [0] * 8,
        }
    )
    movies = pd.DataFrame({"movieID": [10, 20, 30], "title": ["A", "B", "C"]})
    return RecommenderService(ratings, movies, min_voters=1)


def test_batch_writes_queryable_tables(tmp_path):
    target = str(tmp_path / "test.db")
    timings = run(_service(), target, top_n=5, similar_n=2)
    assert timings["users"] == 3
    assert timings["recommendation_rows"] > 0

    conn = sqlite3.connect(target)
    try:
        rec_rows = conn.execute(
            "SELECT user_id, movie_id, score, rank FROM recommendations"
            " ORDER BY user_id, rank"
        ).fetchall()
        sim_rows = conn.execute(
            "SELECT user_id, similar_user_id, similarity, rank FROM similar_users"
            " ORDER BY user_id, rank"
        ).fetchall()
        titles = conn.execute("SELECT COUNT(*) FROM movies").fetchone()[0]
    finally:
        conn.close()

    assert titles == 3
    # ranks are dense per user and scores descend
    for user_id in (1, 2, 3):
        user_rows = [r for r in rec_rows if r[0] == user_id]
        assert [r[3] for r in user_rows] == list(range(1, len(user_rows) + 1))
        assert [r[2] for r in user_rows] == sorted(
            [r[2] for r in user_rows], reverse=True
        )
    assert rec_rows, "expected recommendation rows"
    assert sim_rows, "expected similar-user rows"
    assert all(u != v for u, v, _, _ in sim_rows)
