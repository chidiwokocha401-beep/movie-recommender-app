# Implementation Plan — Movie Recommender Web App

**Goal:** turn the current Python CLI prototype (`movie-recommender-main/*.py` on MovieLens 100K)
into a deployed web app: FastAPI backend serving recommendations + React frontend with its own design system.

**Starting point (verified):** user-based collaborative filtering (Pearson/Euclidean) works but has known
defects — score accumulation overwrites instead of summing (`movie_recommender.py`), an over-strict 0.8
similarity cutoff, O(N·M) `DataFrame.loc` lookups, and fragile absolute data paths. Each slice below fixes
what it touches. Slices are ordered so every one leaves `main` in a working state.

**Conventions per slice:** goal → tasks → acceptance criteria. Sizes: S (≤1 day), M (2–4 days), L (~1 week).

---

## Slice 0 — Repository & delivery foundations (S)

- Decide layout: `apps/web` (React), `apps/api` (FastAPI), `packages/recommender` (Python core), keep
  `movie-recommender-main/` legacy code untouched until Slice 2 replaces it.
- Add `requirements.txt` / `pyproject.toml`, `package.json` workspaces, root `.gitignore`, pre-commit
  (ruff, eslint), GitHub Actions CI (lint + test on PR).
- **Accept:** `git clone` + one documented bootstrap command per app; CI green on an empty scaffold PR.

## Slice 1 — Architectural decisions (S, ADR documents in `docs/adr/`)

- ADR-1: API framework — FastAPI (async, OpenAPI gratis, typed with Pydantic).
- ADR-2: datastore — Postgres for ratings/catalog; precomputed similarity matrix in Postgres or Redis.
- ADR-3: frontend — React + TypeScript (Vite or Next.js), TanStack Query for server state.
- ADR-4: recommender execution — offline batch job precomputes top-N per user; API serves reads (<200 ms p95).
- ADR-5: hosting — Docker Compose locally; single-VM (or Render/Fly) deploy; LFS stays for raw datasets only.
- **Accept:** 5 short ADRs merged; every later slice references them instead of re-deciding.

## Slice 2 — Data layer & algorithm correctness (M)

- ETL: load `u.data`/`u.item` into Postgres (`users`, `movies`, `ratings`); resolve paths relative to repo.
- Port `pearson_score`/`euclidean_score` into `packages/recommender` vectorized (user-item matrix, NumPy).
- Fix accumulation bug (sum, don't overwrite), weighted average `Σ(r·s)/Σ(s)`, tunable cutoff/top-K.
- Add offline evaluation: train/test split, RMSE + precision@K reported in CI.
- **Accept:** `pytest` covers similarity + recommendations; evaluation numbers recorded in `docs/eval.md`.

## Slice 3 — Recommender service & batch job (M)

- Batch job: nightly (or on-demand CLI) recomputes per-user top-N recommendations + similar-users into DB tables.
- Expose a Python service interface `recommend(user_id, k)`, `similar_users(user_id, n)` used by both job and API.
- Benchmark on full MovieLens 100K; document runtime/memory.
- **Accept:** job runs end-to-end locally; API-independent timing logged; results queryable in Postgres.

## Slice 4 — Backend API (M)

- Endpoints: `GET /movies?search=`, `GET /movies/{id}`, `POST /ratings`, `GET /users/{id}/recommendations`,
  `GET /users/{id}/similar`, `GET /users/{id1}/similarity/{id2}?metric=pearson|euclidean`.
- Pydantic schemas, pagination, error format, OpenAPI docs at `/docs`, request logging + correlation IDs.
- Tests: endpoint contract tests with a seeded test DB.
- **Accept:** all endpoints exercised by tests; p95 < 200 ms on seeded data; docs render.

## Slice 5 — Design system (M)

- Tokens: color, type scale, spacing, radius (CSS variables); light/dark support.
- Components: Button, Input, MovieCard, RatingStars, ScoreBadge, EmptyState, Skeleton loaders.
- Storybook stories + visual regression baseline (Chromatic or screenshots in CI).
- Accessibility bar: keyboard-operable rating, ARIA labels, contrast AA.
- **Accept:** Storybook deploys from CI; every component has a story + a11y check passing.

## Slice 6 — Frontend app (L)

- Pages: search/browse movies, movie detail with star rating, "Recommended for you", "Similar users" panel.
- Data fetching via TanStack Query against Slice 4 API; optimistic rating updates; auth stub (single demo user
  first, real accounts only if Slice 7 demands it).
- E2E smoke (Playwright): rate a movie → recommendations refresh.
- **Accept:** demo script runs end-to-end against local Compose stack with no console errors.

## Slice 7 — Hardening (M)

- Caching headers + Redis for hot recommendation reads; rate limiting on write endpoints.
- Observability: structured logs, `/health`, basic metrics (latency, error rate).
- Load test the recommendation endpoint (k6, 100 rps target) and record results.
- **Accept:** load-test report in `docs/`; p95 holds under target; health checks wired into deploy.

## Slice 8 — Deployment (S/M)

- Dockerfiles per app + `docker-compose.yml` (web, api, postgres, redis); env-template `.env.example`.
- CI: build images, run migrations, smoke-test Compose, push to registry; CD to chosen host on `main`.
- Docs: production runbook (migrate, re-run batch job, roll back) in `docs/runbook.md`.
- **Accept:** fresh VM follows runbook to a live URL; rollback procedure tested once.

---

## Milestones

1. **M1 (Slices 0–2):** correct, tested recommender core on real data.
2. **M2 (Slices 3–4):** API serves precomputed recommendations.
3. **M3 (Slices 5–6):** usable UI on the design system.
4. **M4 (Slices 7–8):** hardened, deployed, documented.

## Risks

- Cold-start users (no ratings) → fallback to popular-movies endpoint (add in Slice 4 if time allows).
- Similarity matrix cost if dataset grows → ADR-4 batch approach already contains this; revisit past 1M ratings.
- LFS bandwidth on CI → keep raw datasets out of test fixtures; use a 1% sample in CI.
