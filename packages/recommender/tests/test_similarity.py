import importlib.util
from pathlib import Path

import numpy as np
import pytest

from recommender.etl import build_matrix, default_paths, load_movielens
from recommender.similarity import (
    euclidean_similarity,
    pearson_similarity,
    significance_weighted,
)

LEGACY_DIR = Path(__file__).resolve().parents[3] / "movie-recommender-main"


def _legacy_module():
    path = LEGACY_DIR / "similarity_scores.py"
    spec = importlib.util.spec_from_file_location("legacy_similarity", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_identical_users_pearson_one():
    matrix = np.array([[5.0, 3.0, 4.0], [5.0, 3.0, 4.0], [1.0, 2.0, 5.0]])
    sim = pearson_similarity(matrix)
    assert sim[0, 1] == pytest.approx(1.0)
    assert sim[0, 0] == pytest.approx(1.0)


def test_no_overlap_scores_zero():
    matrix = np.array([[5.0, np.nan], [np.nan, 4.0]])
    assert pearson_similarity(matrix)[0, 1] == 0.0
    assert euclidean_similarity(matrix)[0, 1] == 0.0


def test_zero_variance_pearson_zero():
    matrix = np.array([[3.0, 3.0, 3.0], [1.0, 5.0, 2.0]])
    assert pearson_similarity(matrix)[0, 1] == 0.0


def test_euclidean_known_value():
    matrix = np.array([[5.0, 3.0], [4.0, 2.0]])
    expected = 1.0 / (1.0 + np.sqrt(2.0))
    assert euclidean_similarity(matrix)[0, 1] == pytest.approx(expected)


def test_significance_weighting_discounts_thin_overlap():
    sim = np.array([[1.0, 0.9], [0.9, 1.0]])
    counts = np.array([[100.0, 2.0], [2.0, 100.0]])
    weighted = significance_weighted(sim, counts, gamma=50.0)
    assert weighted[0, 1] == pytest.approx(0.9 * 2.0 / 50.0)
    assert weighted[0, 0] == pytest.approx(1.0)
    assert significance_weighted(sim, np.zeros((2, 2)))[0, 1] == 0.0


def test_matches_legacy_pearson_on_real_data():
    ratings, movies = load_movielens(*default_paths())
    dataset = ratings.merge(movies, on="movieID")
    matrix, _user_ids, _, user_index, _ = build_matrix(ratings)
    sim = pearson_similarity(matrix)
    legacy = _legacy_module()
    for user1, user2 in [(1, 2), (1, 10), (5, 100)]:
        expected = legacy.pearson_score(dataset, user1, user2)
        assert sim[user_index[user1], user_index[user2]] == pytest.approx(expected)
