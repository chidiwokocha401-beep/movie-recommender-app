# ADR-004: Recommender execution — offline batch precompute, API serves reads

- Status: Accepted
- Date: 2026-09-25

## Context

The prototype scores every user pair on demand with O(N·M) DataFrame lookups — far too slow per request.
Options: (a) compute on demand with optimized in-memory matrices, (b) precompute offline and serve reads.

## Decision

**(b) Offline batch job** (Slice 3) recomputes per-user top-N recommendations and similar-users on a
schedule (and on demand via CLI), writing results to Postgres tables per ADR-002. The API only reads.

## Consequences

- Good: API latency becomes a DB lookup — the <200 ms p95 budget is easily met; batch cost is isolated
  and schedulable.
- Good: recommendations are deterministic snapshots — debuggable and evaluable (Slice 2 metrics).
- Bad: freshness lag — a new rating isn't reflected until the next run; acceptable for movies, mitigated
  by on-demand reruns for active users if ever needed.
- Ugly: batch runtime must be watched as data grows; revisit past ~1M ratings.
