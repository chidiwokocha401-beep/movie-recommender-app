"""Service singleton. Lazily built on first request so tests can override
it with a small synthetic service via ``app.dependency_overrides``."""

from recommender.service import RecommenderService

_service: RecommenderService | None = None


def get_service() -> RecommenderService:
    global _service
    if _service is None:
        _service = RecommenderService.from_movielens()
    return _service
