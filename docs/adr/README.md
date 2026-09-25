# Architecture Decision Records

Index of decisions for the Movie Recommender Web App. Newest first.

| ADR | Title | Status |
|-----|-------|--------|
| [001](001-api-framework.md) | API framework: FastAPI | Accepted |
| [002](002-datastore.md) | Datastore: Postgres (+ Redis for hot reads) | Accepted |
| [003](003-frontend-stack.md) | Frontend: React + TypeScript (Vite), TanStack Query | Accepted |
| [004](004-recommender-execution.md) | Offline batch precompute, API serves reads | Accepted |
| [005](005-hosting.md) | Docker Compose locally, single-VM deploy | Accepted |

Statuses: Proposed → Accepted → Deprecated/Superseded. Never edit a merged ADR in place;
supersede it with a new one.
