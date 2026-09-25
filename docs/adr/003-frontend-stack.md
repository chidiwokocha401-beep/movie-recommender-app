# ADR-003: Frontend — React + TypeScript (Vite), TanStack Query

- Status: Accepted
- Date: 2026-09-25

## Context

The UI needs search, movie detail with star ratings, and recommendation lists backed by the Slice 4 API.
Candidates: React/Vite, Next.js, Streamlit-only.

## Decision

**React 18 + TypeScript**, built with **Vite**, server state managed by **TanStack Query**.
(Choice of Vite over Next.js: no SSR requirement — content is personalized per user, so static
generation buys nothing; Vite keeps the build simple.)

## Consequences

- Good: component model maps directly onto the Slice 5 design system; TanStack Query gives caching,
  retries, and optimistic rating updates almost free.
- Good: `tsc --noEmit` in CI catches API-contract drift when OpenAPI types are generated (Slice 6).
- Bad: client-side rendering only — initial paint waits on API; acceptable for an authenticated app.
- Ugly: none; revisit if SEO/landing pages ever matter.
