# Batch job — precomputed recommendations

- Dataset: MovieLens 100K (`u.data`), all users
- Method: Pearson + significance weighting (gamma=50), min 10 voters per prediction
- Memory: ratings matrix 943×1682 float64 (~12 MB), similarity matrix 943×943 float64 (~7 MB)

| Stage | Value |
|---|---|
| `load_and_similarity_s` | 1.78 |
| `recommend_all_s` | 51.91 |
| `store_s` | 3.77 |
| `total_s` | 55.68 |
| `users` | 943 |
| `recommendation_rows` | 18860 |
| `similar_user_rows` | 9430 |
| `db` | postgresql://user@localhost:5433/postgres |

Reproduce: `python -m recommender.batch --db data/recommender.db` (with `packages/recommender` installed). For Postgres, pass a `DATABASE_URL` to `--db` with the `postgres` extra installed.
