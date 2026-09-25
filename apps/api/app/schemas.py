from pydantic import BaseModel, Field


class Movie(BaseModel):
    movie_id: int
    title: str


class RatingIn(BaseModel):
    user_id: int
    movie_id: int
    rating: int = Field(ge=1, le=5)


class Rating(RatingIn):
    pass


class Recommendation(BaseModel):
    movie_id: int
    title: str | None
    score: float
    rank: int


class SimilarUser(BaseModel):
    user_id: int
    similarity: float
    rank: int


class SimilarityScore(BaseModel):
    user_id: int
    other_user_id: int
    metric: str
    similarity: float
