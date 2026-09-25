import numpy as np

from recommender.recommend import recommend_for_user


def test_scores_accumulate_over_all_voters():
    # Target user 0 rated item 0 only; users 1 and 2 both rated item 1.
    matrix = np.array(
        [
            [5.0, np.nan],
            [4.0, 5.0],
            [2.0, 3.0],
        ]
    )
    sim = np.array(
        [
            [1.0, 0.9, 0.8],
            [0.9, 1.0, 0.0],
            [0.8, 0.0, 1.0],
        ]
    )
    recs = recommend_for_user(
        matrix, sim, 0, top_k=10, min_similarity=0.0, min_voters=2
    )
    assert [i for i, _ in recs] == [1]
    expected = (5.0 * 0.9 + 3.0 * 0.8) / (0.9 + 0.8)
    assert recs[0][1] == expected


def test_single_voter_filtered_by_default():
    matrix = np.array([[5.0, np.nan], [5.0, 5.0]])
    sim = np.array([[1.0, 0.9], [0.9, 1.0]])
    assert recommend_for_user(matrix, sim, 0) == []
    recs = recommend_for_user(matrix, sim, 0, min_voters=1)
    assert [i for i, _ in recs] == [1]


def test_rated_items_never_recommended():
    matrix = np.array([[5.0, np.nan], [5.0, 4.0]])
    sim = np.array([[1.0, 0.9], [0.9, 1.0]])
    recs = recommend_for_user(matrix, sim, 0, min_voters=1)
    assert [i for i, _ in recs] == [1]


def test_no_voters_returns_empty():
    matrix = np.array([[5.0, np.nan], [5.0, 4.0]])
    sim = np.array([[1.0, 0.2], [0.2, 1.0]])
    assert recommend_for_user(matrix, sim, 0, min_similarity=0.99) == []


def test_ranking_best_first():
    matrix = np.array(
        [
            [5.0, np.nan, np.nan],
            [5.0, 1.0, 5.0],
        ]
    )
    sim = np.array([[1.0, 0.9], [0.9, 1.0]])
    recs = recommend_for_user(matrix, sim, 0, top_k=2, min_voters=1)
    assert [i for i, _ in recs] == [2, 1]
