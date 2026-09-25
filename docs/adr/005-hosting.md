# ADR-005: Hosting — Docker Compose locally, single-VM deploy

- Status: Accepted
- Date: 2026-09-25

## Context

The team needs one local setup and one simple production target. Candidates: single VM (Render/Fly),
Kubernetes, serverless.

## Decision

**Docker Compose** (`web`, `api`, `postgres`, `redis`) as the local and CI contract; deploy containers to
a **single VM host** (Render/Fly or plain VM) with CI-built images. Raw datasets stay in **Git LFS**;
only small fixtures ship in test images.

## Consequences

- Good: dev/prod parity via the same Compose file; no cluster to operate.
- Good: rollback = previous image tag (documented in the Slice 8 runbook).
- Bad: single VM is a scaling ceiling — fine for launch, revisit with load-test data from Slice 7.
- Ugly: LFS bandwidth on CI — mitigated by keeping raw data out of test fixtures (1% sample).
