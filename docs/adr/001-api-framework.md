# ADR-001: API framework — FastAPI

- Status: Accepted
- Date: 2026-09-25

## Context

The backend must serve recommendation reads with low latency, validate I/O, and stay maintainable for a
primarily Python team. Candidates: FastAPI, Flask, Django REST.

## Decision

Use **FastAPI** with Pydantic v2 schemas and Uvicorn.

## Consequences

- Good: free OpenAPI docs at `/docs` (needed for frontend integration in Slice 6), async support for
  concurrent reads, type-safe request/response contracts testable in CI.
- Good: the team already writes Python; no new language.
- Bad: async DB access needs discipline (use async drivers or run sync SQLAlchemy in a threadpool).
- Ugly: heavier than Flask, but the validation and docs pay for themselves at our scale.
