# Evaluation — recommender core

- Date: 2026-09-25
- Dataset: MovieLens 100K (`u.data`), 20% per-user holdout, seed 42
- Method: Pearson user similarity on train matrix, similarity-weighted average predictions

| Metric | Value |
|---|---|
| `users_evaluated` | 943 |
| `test_ratings` | 20000 |
| `precision@10` | 0.07158006362672323 |
| `rmse` | 0.7200471629356691 |
| `coverage` | 0.03375 |
| `top_k` | 10 |
| `min_similarity` | 0.0 |
| `min_voters` | 10 |
| `gamma` | 50.0 |
| `seed` | 42 |

## Tuning explored (same protocol, seed 42)

Single-vote predictions (obscure movies rated 5/5 once) dominated the
ranking until a minimum-voter guard was added. Significance weighting
(gamma) discounts ±1 correlations from 2-movie overlaps.

| min_voters | min_similarity | gamma | precision@10 | rmse | coverage |
|---|---|---|---|---|---|
| 2 | 0.0 | 50 | 0.0070 | 1.0015 | 0.0033 |
| 5 | 0.0 | 50 | 0.0567 | 0.7305 | 0.0268 |
| 10 | 0.0 | 50 | 0.0716 | 0.7200 | 0.0338 |
| 5 | 0.2 | 50 | 0.0667 | 0.7743 | 0.0315 |
| 10 | 0.2 | 50 | 0.0834 | 0.7295 | 0.0393 |
| 2 | 0.0 | 25 | 0.0097 | 0.8855 | 0.0046 |
| 2 | 0.0 | 100 | 0.0091 | 0.9880 | 0.0043 |

Reproduce: `python -m recommender.evaluate` (with `packages/recommender` installed).
