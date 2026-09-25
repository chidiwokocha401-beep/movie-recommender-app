from fastapi import Depends, FastAPI, HTTPException, Query
from recommender.service import RecommenderService

from app.deps import get_service
from app.schemas import (
    Movie,
    Rating,
    RatingIn,
    Recommendation,
    SimilarityScore,
    SimilarUser,
)

app = FastAPI(title="Movie Recommender API")


def _require_user(service: RecommenderService, user_id: int) -> None:
    if user_id not in service.user_index:
        raise HTTPException(status_code=404, detail=f"Unknown user: {user_id}")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/movies", response_model=list[Movie])
def list_movies(
    search: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    service: RecommenderService = Depends(get_service),
) -> list[Movie]:
    items = [Movie(movie_id=int(m), title=service.titles[m]) for m in service.movie_ids]
    if search:
        needle = search.casefold()
        items = [m for m in items if needle in m.title.casefold()]
    return items[offset : offset + limit]


@app.get("/movies/{movie_id}", response_model=Movie)
def get_movie(
    movie_id: int, service: RecommenderService = Depends(get_service)
) -> Movie:
    title = service.movie_title(movie_id)
    if title is None:
        raise HTTPException(status_code=404, detail=f"Unknown movie: {movie_id}")
    return Movie(movie_id=movie_id, title=title)


@app.post("/ratings", response_model=Rating, status_code=201)
def create_rating(
    payload: RatingIn, service: RecommenderService = Depends(get_service)
) -> Rating:
    _require_user(service, payload.user_id)
    if service.movie_title(payload.movie_id) is None:
        raise HTTPException(
            status_code=404, detail=f"Unknown movie: {payload.movie_id}"
        )
    service.add_rating(payload.user_id, payload.movie_id, payload.rating)
    return Rating(**payload.model_dump())


@app.get("/users/{user_id}/recommendations", response_model=list[Recommendation])
def get_recommendations(
    user_id: int,
    k: int = Query(default=10, ge=1, le=50),
    service: RecommenderService = Depends(get_service),
) -> list[Recommendation]:
    _require_user(service, user_id)
    return [
        Recommendation(
            movie_id=movie_id, title=service.movie_title(movie_id), score=score, rank=r
        )
        for r, (movie_id, score) in enumerate(service.recommend(user_id, k=k), start=1)
    ]


@app.get("/users/{user_id}/similar", response_model=list[SimilarUser])
def get_similar_users(
    user_id: int,
    n: int = Query(default=10, ge=1, le=50),
    service: RecommenderService = Depends(get_service),
) -> list[SimilarUser]:
    _require_user(service, user_id)
    return [
        SimilarUser(user_id=other_id, similarity=sim, rank=r)
        for r, (other_id, sim) in enumerate(
            service.similar_users(user_id, n=n), start=1
        )
    ]


@app.get("/users/{user_id}/similarity/{other_id}", response_model=SimilarityScore)
def get_similarity(
    user_id: int,
    other_id: int,
    metric: str = Query(default="pearson", pattern="^(pearson|euclidean)$"),
    service: RecommenderService = Depends(get_service),
) -> SimilarityScore:
    _require_user(service, user_id)
    _require_user(service, other_id)
    return SimilarityScore(
        user_id=user_id,
        other_user_id=other_id,
        metric=metric,
        similarity=service.similarity(user_id, other_id, metric=metric),
    )
