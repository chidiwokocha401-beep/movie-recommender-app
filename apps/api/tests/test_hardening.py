import os

import pandas as pd
import pytest
from fastapi.testclient import TestClient
from recommender.service import RecommenderService

from app.deps import get_service
from app.main import app


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_RATINGS", "2/minute")
    ratings = pd.DataFrame(
        {
            "userID": [1, 1, 2, 2],
            "movieID": [10, 20, 10, 20],
            "rating": [5, 4, 5, 3],
            "timestamp": [0] * 4,
        }
    )
    movies = pd.DataFrame({"movieID": [10, 20], "title": ["A", "B"]})
    service = RecommenderService(ratings, movies, min_voters=1)
    app.dependency_overrides[get_service] = lambda: service
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_rate_limit_returns_429(client):
    payload = {"user_id": 1, "movie_id": 10, "rating": 5}
    assert client.post("/ratings", json=payload).status_code == 201
    assert client.post("/ratings", json=payload).status_code == 201
    response = client.post("/ratings", json=payload)
    assert response.status_code == 429
    assert "Rate limit" in response.json()["detail"]
    assert os.getenv("RATE_LIMIT_RATINGS") == "2/minute"


def test_metrics_endpoint_reports_requests(client):
    client.get("/movies")
    client.get("/movies/999")
    metrics = client.get("/metrics").text
    assert "http_request_duration_seconds" in metrics
    assert 'route="/movies"' in metrics
