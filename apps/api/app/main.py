import json
import os

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from recommender.service import RecommenderService
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.cache import get_cache
from app.deps import get_service
from app.observability import ObservabilityMiddleware, metrics_response
from app.schemas import (
    Movie,
    Rating,
    RatingIn,
    Recommendation,
    SimilarityScore,
    SimilarUser,
)

RECOMMENDATION_TTL_S = 300


def _rating_limit() -> str:
    return os.getenv("RATE_LIMIT_RATINGS", "30/minute")


limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Movie Recommender API")
app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    lambda request, exc: JSONResponse(
        status_code=429, content={"detail": "Rate limit exceeded, try again later."}
    ),
)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(ObservabilityMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

cache = get_cache()


def _require_user(service: RecommenderService, user_id: int) -> None:
    if user_id not in service.user_index:
        raise HTTPException(status_code=404, detail=f"Unknown user: {user_id}")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": "0.1.0"}


@app.get("/metrics")
def metrics():
    return metrics_response()


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
@limiter.limit(_rating_limit)
def create_rating(
    request: Request,
    payload: RatingIn,
    service: RecommenderService = Depends(get_service),
) -> Rating:
    _require_user(service, payload.user_id)
    if service.movie_title(payload.movie_id) is None:
        raise HTTPException(
            status_code=404, detail=f"Unknown movie: {payload.movie_id}"
        )
    service.add_rating(payload.user_id, payload.movie_id, payload.rating)
    cache.delete_pattern(f"recs:*:{payload.user_id}:*")
    return Rating(**payload.model_dump())


@app.get("/users/{user_id}/recommendations", response_model=list[Recommendation])
def get_recommendations(
    user_id: int,
    k: int = Query(default=10, ge=1, le=50),
    service: RecommenderService = Depends(get_service),
) -> list[Recommendation]:
    _require_user(service, user_id)
    cache_key = f"recs:v1:{user_id}:{k}"
    cached = cache.get(cache_key)
    if cached is not None:
        return [Recommendation(**r) for r in json.loads(cached)]
    recs = [
        Recommendation(
            movie_id=movie_id, title=service.movie_title(movie_id), score=score, rank=r
        )
        for r, (movie_id, score) in enumerate(service.recommend(user_id, k=k), start=1)
    ]
    cache.setex(
        cache_key, RECOMMENDATION_TTL_S, json.dumps([r.model_dump() for r in recs])
    )
    return recs


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
