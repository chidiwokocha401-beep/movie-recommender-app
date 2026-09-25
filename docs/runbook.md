# Production runbook

## First deploy (fresh VM with Docker + Compose plugin)

```bash
git clone <repo-url> && cd movie-recommender-main
cp .env.example .env   # set a real POSTGRES_PASSWORD
docker compose build
docker compose up -d postgres redis
docker compose run --rm api python -m recommender.batch \
  --db "$DATABASE_URL"
docker compose up -d
curl -sf http://localhost:8000/health
curl -sf http://localhost/api/users/1/recommendations?k=3
```

The batch step writes `recommendations` / `similar_users` tables to Postgres
(schema in `db/schema.sql`). Re-run it after data changes or deploys.

## Verify

- API docs: `http://<host>:8000/docs`
- App: `http://<host>/`, search → rate → recommendations refresh (Slice 6 E2E)
- Metrics: `http://<host>:8000/metrics`

## Roll back

Images are built locally, so roll back with git + rebuild:

```bash
git log --oneline -5            # pick the last good commit
git checkout <good-commit>
docker compose up -d --build
```

Data survives in the `pgdata` volume. To roll data back too, restore the
volume from your host backup before `up`.

## Notes

- The API serves recommendations from its in-memory service with a Redis
  cache (`REDIS_URL`); Postgres holds the batch tables for analytics and the
  future DB-read path (ADR-2/ADR-4).
- Never commit `.env`. Rotate `POSTGRES_PASSWORD` by updating `.env` and
  recreating the `postgres` service.
