# ADR-002: Datastore — Postgres (+ Redis for hot reads)

- Status: Accepted
- Date: 2026-09-25

## Context

We need to store the movie catalog, user ratings, and precomputed recommendations, and serve reads at
p95 < 200 ms (Slice 4/7). Candidates: SQLite, Postgres, fully Redis-backed.

## Decision

**Postgres** as the system of record (`users`, `movies`, `ratings`, plus `recommendations` and
`similar_users` tables written by the batch job). Add **Redis** in Slice 7 as a read-through cache for
hot recommendation endpoints only.

## Consequences

- Good: relational integrity for ratings, trivial pagination/filtering for catalog search, managed
  Postgres available on every host in ADR-005.
- Good: precomputed tables keep API reads O(1)-ish; no on-the-fly matrix math per request.
- Bad: one more service to run locally (covered by Compose in Slice 8).
- Ugly: none significant at MovieLens-100K scale.
