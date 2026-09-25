# Load test — recommendations endpoint

- Date: 2026-09-25
- Tool: k6 (`load/k6/recommendations.js`), 100 rps constant arrival, 2 min, ≤50 VUs
- Target: local uvicorn, warmed service (MovieLens 100K in memory)
- Scenario: `GET /users/{1-50}/recommendations?k=10` (random user per iteration)

| Metric | Result | Budget |
|---|---|---|
| `http_req_failed` | 0.00% (0/11,863) | < 1% ✓ |
| `http_req_duration p95` | 27.5 ms | < 200 ms ✓ |
| `http_req_duration avg` | 18.5 ms | — |
| sustained rate | 98.9 rps | 100 rps ✓ |

Notes:

- A first attempt failed 100% with connection-refused: the k6 run started
  against a stale server process. Reran with a fresh server + warmup call;
  above are the clean numbers.
- Reads are served from the in-memory service with a 5-min cache layer;
  p95 budget holds with wide margin on laptop hardware.

Reproduce: start the API (`uvicorn app.main:app --app-dir apps/api`),
warm one request, then `k6 run load/k6/recommendations.js`.
