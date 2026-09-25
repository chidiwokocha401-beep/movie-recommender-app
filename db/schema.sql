-- Postgres schema for the Movie Recommender App (Slice 2).
-- Raw MovieLens files stay in Git LFS; this schema is populated by ETL.

CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS movies (
    movie_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ratings (
    user_id INTEGER NOT NULL REFERENCES users (user_id),
    movie_id INTEGER NOT NULL REFERENCES movies (movie_id),
    rating SMALLINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    rated_at TIMESTAMPTZ,
    PRIMARY KEY (user_id, movie_id)
);
CREATE INDEX IF NOT EXISTS ratings_movie_idx ON ratings (movie_id);

-- Written by the Slice 3 batch job, read by the API.
CREATE TABLE IF NOT EXISTS recommendations (
    user_id INTEGER NOT NULL REFERENCES users (user_id),
    movie_id INTEGER NOT NULL REFERENCES movies (movie_id),
    score DOUBLE PRECISION NOT NULL,
    rank SMALLINT NOT NULL,
    computed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (user_id, rank)
);

CREATE TABLE IF NOT EXISTS similar_users (
    user_id INTEGER NOT NULL REFERENCES users (user_id),
    similar_user_id INTEGER NOT NULL REFERENCES users (user_id),
    similarity DOUBLE PRECISION NOT NULL,
    rank SMALLINT NOT NULL,
    computed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (user_id, rank),
    CHECK (user_id <> similar_user_id)
);
