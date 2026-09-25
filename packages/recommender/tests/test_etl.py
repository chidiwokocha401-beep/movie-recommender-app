import numpy as np

from recommender.etl import build_matrix, default_paths, load_movielens


def test_load_movielens_shapes():
    ratings, movies = load_movielens(*default_paths())
    assert list(ratings.columns) == ["userID", "movieID", "rating", "timestamp"]
    assert len(ratings) == 100000
    assert len(movies) == 1682
    title = movies.loc[movies["movieID"] == 1, "title"].iloc[0]
    assert title == "Toy Story (1995)"


def test_build_matrix_shape_and_values():
    ratings, _ = load_movielens(*default_paths())
    matrix, user_ids, movie_ids, user_index, movie_index = build_matrix(ratings)
    assert matrix.shape == (943, 1682)
    assert len(user_ids) == 943 and len(movie_ids) == 1682
    row = ratings.iloc[0]
    assert (
        matrix[user_index[row["userID"]], movie_index[row["movieID"]]] == row["rating"]
    )
    assert np.isnan(matrix).sum() > 0
