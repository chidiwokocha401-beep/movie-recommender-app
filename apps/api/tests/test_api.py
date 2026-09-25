import pandas as pd
import pytest
from fastapi.testclient import TestClient
from recommender.service import RecommenderService

from app.deps import get_service
from app.main import app


@pytest.fixture
def client():
    ratings = pd.DataFrame(
        {
            "userID": [1, 1, 1, 2, 2, 2, 3, 3, 3],
            "movieID": [10, 20, 30, 10, 20, 30, 10, 20, 40],
            "rating": [5, 4, 3, 5, 4, 2, 4, 3, 5],
            "timestamp": [0] * 9,
        }
    )
    movies = pd.DataFrame({"movieID": [10, 20, 30, 40], "title": ["A", "B", "C", "D"]})
    service = RecommenderService(ratings, movies, min_voters=1)
    app.dependency_overrides[get_service] = lambda: service
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_health_no_service_needed():
    app.dependency_overrides.clear()
    with TestClient(app) as test_client:
        assert test_client.get("/health").json() == {"status": "ok"}


def test_list_movies_and_search(client):
    assert [m["movie_id"] for m in client.get("/movies").json()] == [10, 20, 30, 40]
    assert client.get("/movies", params={"search": "b"}).json()[0]["title"] == "B"
    assert (
        client.get("/movies", params={"limit": 1, "offset": 1}).json()[0]["movie_id"]
        == 20
    )


def test_cors_allows_web_dev_origin(client):
    response = client.get("/movies", headers={"Origin": "http://127.0.0.1:5173"})
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:5173"


def test_get_movie_and_404(client):
    assert client.get("/movies/10").json() == {"movie_id": 10, "title": "A"}
    assert client.get("/movies/999").status_code == 404


def test_create_rating_and_validation(client):
    created = client.post("/ratings", json={"user_id": 1, "movie_id": 40, "rating": 4})
    assert created.status_code == 201
    assert created.json()["rating"] == 4
    assert (
        client.post(
            "/ratings", json={"user_id": 1, "movie_id": 40, "rating": 6}
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/ratings", json={"user_id": 999, "movie_id": 40, "rating": 4}
        ).status_code
        == 404
    )
    assert (
        client.post(
            "/ratings", json={"user_id": 1, "movie_id": 999, "rating": 4}
        ).status_code
        == 404
    )


def test_recommendations_shape_and_unknown_user(client):
    recs = client.get("/users/1/recommendations", params={"k": 5}).json()
    assert recs and all({"movie_id", "title", "score", "rank"} <= set(r) for r in recs)
    assert [r["rank"] for r in recs] == list(range(1, len(recs) + 1))
    assert client.get("/users/999/recommendations").status_code == 404


def test_similar_users_shape(client):
    similar = client.get("/users/1/similar", params={"n": 2}).json()
    assert similar and all(u["user_id"] != 1 for u in similar)
    assert [u["rank"] for u in similar] == list(range(1, len(similar) + 1))


def test_similarity_metrics(client):
    pearson = client.get("/users/1/similarity/2").json()
    assert pearson["metric"] == "pearson"
    euclidean = client.get(
        "/users/1/similarity/2", params={"metric": "euclidean"}
    ).json()
    assert euclidean["metric"] == "euclidean"
    assert pearson["similarity"] != euclidean["similarity"]
    assert (
        client.get("/users/1/similarity/2", params={"metric": "cosine"}).status_code
        == 422
    )
    assert client.get("/users/1/similarity/999").status_code == 404
