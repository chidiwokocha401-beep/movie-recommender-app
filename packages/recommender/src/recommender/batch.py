"""Offline batch job: precompute top-N recommendations and similar users.

Run: ``python -m recommender.batch --db data/recommender.db`` (SQLite), or pass a
Postgres ``DATABASE_URL`` with ``--db``. Writes ``docs/batch.md`` with timings.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from recommender.service import RecommenderService
from recommender.store import Store

REPO_ROOT = Path(__file__).resolve().parents[4]


def run(
    service: RecommenderService,
    target: str,
    top_n: int = 20,
    similar_n: int = 10,
) -> dict:
    """Compute outputs for every user and store them. Returns stage timings."""
    timings: dict[str, float] = {}
    started = time.perf_counter()

    recommendations: list[tuple[int, int, float, int]] = []
    similar: list[tuple[int, int, float, int]] = []
    mark = time.perf_counter()
    for user_id in service.user_ids:
        for rank, (movie_id, score) in enumerate(
            service.recommend(int(user_id), k=top_n), start=1
        ):
            recommendations.append((int(user_id), movie_id, score, rank))
        for rank, (other_id, sim) in enumerate(
            service.similar_users(int(user_id), n=similar_n), start=1
        ):
            similar.append((int(user_id), other_id, sim, rank))
    timings["recommend_all_s"] = round(time.perf_counter() - mark, 2)

    mark = time.perf_counter()
    store = Store.open(target)
    try:
        store.save_catalog(
            [int(u) for u in service.user_ids],
            [(int(m), service.titles[m]) for m in service.titles],
        )
        store.replace_outputs(recommendations, similar)
    finally:
        store.close()
    timings["store_s"] = round(time.perf_counter() - mark, 2)

    timings["total_s"] = round(time.perf_counter() - started, 2)
    timings["users"] = len(service.user_ids)
    timings["recommendation_rows"] = len(recommendations)
    timings["similar_user_rows"] = len(similar)
    return timings


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Precompute recommendations")
    parser.add_argument("--db", default="data/recommender.db")
    parser.add_argument("--top-n", type=int, default=20)
    parser.add_argument("--similar-n", type=int, default=10)
    args = parser.parse_args(argv)

    mark = time.perf_counter()
    service = RecommenderService.from_movielens()
    timings = {"load_and_similarity_s": round(time.perf_counter() - mark, 2)}

    target = args.db
    if not target.startswith("postgres"):
        target = str(REPO_ROOT / target)
        Path(target).parent.mkdir(parents=True, exist_ok=True)
    timings.update(run(service, target, args.top_n, args.similar_n))
    timings["db"] = args.db

    doc = REPO_ROOT / "docs" / "batch.md"
    lines = [
        "# Batch job — precomputed recommendations",
        "",
        "- Dataset: MovieLens 100K (`u.data`), all users",
        (
            "- Method: Pearson + significance weighting (gamma=50), "
            "min 10 voters per prediction"
        ),
        (
            "- Memory: ratings matrix 943×1682 float64 (~12 MB), "
            "similarity matrix 943×943 float64 (~7 MB)"
        ),
        "",
        "| Stage | Value |",
        "|---|---|",
    ]
    for key, value in timings.items():
        lines.append(f"| `{key}` | {value} |")
    lines += [
        "",
        (
            "Reproduce: `python -m recommender.batch --db data/recommender.db` "
            "(with `packages/recommender` installed). For Postgres, pass a "
            "`DATABASE_URL` to `--db` with the `postgres` extra installed."
        ),
        "",
    ]
    doc.write_text("\n".join(lines))
    print(json.dumps(timings, indent=2))


if __name__ == "__main__":
    main()
