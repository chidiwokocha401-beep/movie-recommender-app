"""Persistence for batch outputs: SQLite locally, Postgres in production.

The canonical DDL lives in ``db/schema.sql`` (Postgres). SQLite accepts the
same DDL except for the ``now()`` default, so this module carries a small
SQLite variant. Inserts always pass explicit timestamps and ``?``/``%s``
placeholders per dialect.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

SQLITE_SCHEMA = """
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
CREATE TABLE IF NOT EXISTS recommendations (
    user_id INTEGER NOT NULL REFERENCES users (user_id),
    movie_id INTEGER NOT NULL REFERENCES movies (movie_id),
    score DOUBLE PRECISION NOT NULL,
    rank SMALLINT NOT NULL,
    computed_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (user_id, rank)
);
CREATE TABLE IF NOT EXISTS similar_users (
    user_id INTEGER NOT NULL REFERENCES users (user_id),
    similar_user_id INTEGER NOT NULL REFERENCES users (user_id),
    similarity DOUBLE PRECISION NOT NULL,
    rank SMALLINT NOT NULL,
    computed_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (user_id, rank),
    CHECK (user_id <> similar_user_id)
);
"""


class Store:
    """Thin wrapper over a SQLite or Postgres connection."""

    def __init__(self, conn, dialect: str):
        self.conn = conn
        self.dialect = dialect
        self.ph = "?" if dialect == "sqlite" else "%s"

    @classmethod
    def open(cls, target: str) -> Store:
        """Open ``target``: a ``.db`` file path (SQLite) or a ``DATABASE_URL``."""
        if target.startswith("postgres"):
            try:
                import psycopg
            except ImportError as exc:
                raise RuntimeError(
                    "Postgres output needs the extra: pip install recommender[postgres]"
                ) from exc
            try:
                from psycopg.sql import SQL
            except ImportError as exc:  # pragma: no cover
                raise RuntimeError("psycopg installation is broken") from exc
            conn = psycopg.connect(target)
            schema = (
                Path(__file__).resolve().parents[4] / "db" / "schema.sql"
            ).read_text()
            with conn.cursor() as cur:
                cur.execute(SQL(schema))
            conn.commit()
            return cls(conn, "postgres")
        conn = sqlite3.connect(target)
        conn.executescript(SQLITE_SCHEMA)
        return cls(conn, "sqlite")

    def close(self) -> None:
        self.conn.close()

    def save_catalog(self, users: list[int], movies: list[tuple[int, str]]) -> None:
        cur = self.conn.cursor() if self.dialect == "postgres" else self.conn
        cur.executemany(
            f"INSERT INTO users (user_id) VALUES ({self.ph}) ON CONFLICT DO NOTHING"
            if self.dialect == "postgres"
            else f"INSERT OR IGNORE INTO users (user_id) VALUES ({self.ph})",
            [(u,) for u in users],
        )
        cur.executemany(
            f"INSERT INTO movies (movie_id, title) VALUES ({self.ph}, {self.ph}) "
            "ON CONFLICT DO NOTHING"
            if self.dialect == "postgres"
            else f"INSERT OR IGNORE INTO movies (movie_id, title) VALUES ({self.ph}, {self.ph})",
            movies,
        )
        self.conn.commit()

    def replace_outputs(
        self,
        recommendations: list[tuple[int, int, float, int]],
        similar: list[tuple[int, int, float, int]],
    ) -> None:
        """Replace batch tables. Rows: ``(user_id, movie_id, score, rank)`` and
        ``(user_id, similar_user_id, similarity, rank)``."""
        now = datetime.now(timezone.utc).isoformat()
        cur = self.conn.cursor() if self.dialect == "postgres" else self.conn
        cur.execute("DELETE FROM recommendations")
        cur.execute("DELETE FROM similar_users")
        cur.executemany(
            f"INSERT INTO recommendations (user_id, movie_id, score, rank, computed_at)"
            f" VALUES ({self.ph}, {self.ph}, {self.ph}, {self.ph}, {self.ph})",
            [(u, m, s, r, now) for u, m, s, r in recommendations],
        )
        cur.executemany(
            f"INSERT INTO similar_users (user_id, similar_user_id, similarity, rank,"
            f" computed_at) VALUES ({self.ph}, {self.ph}, {self.ph}, {self.ph},"
            f" {self.ph})",
            [(u, v, s, r, now) for u, v, s, r in similar],
        )
        self.conn.commit()
