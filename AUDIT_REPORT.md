# Noble Prism MVP Audit Report

Date: 2026-07-05

## Architecture Snapshot

- Frontend: React 19, TypeScript, Vite, Tailwind CSS, TanStack Router, TanStack Query.
- Primary backend: FastAPI in `backend/app`, with SQLAlchemy models, Pydantic schemas, route modules, service modules, Alembic migrations, and integration tests.
- Secondary backend: `noble_prism_backend_v2`, a smaller FastAPI app. It appears older and is not the backend wired to the main frontend package.
- Database: SQLAlchemy supports SQLite locally and PostgreSQL through `DATABASE_URL`; deployment should use Supabase PostgreSQL.
- API integration: frontend calls are centralized in `src/lib/api.ts`; React Query hooks live in `src/hooks/useApi.ts`.

## Findings

1. The product brief names Spring Boot, but the codebase is FastAPI. Rewriting the backend framework would be high-risk and unnecessary for MVP readiness.
2. Production secrets are mostly environment-driven, but there is no committed `.env.example` for the primary app.
3. The primary backend has route/service/model separation and integration tests, but the generic exception response can leak exception type names.
4. CORS is environment-configurable in the primary backend, but docker-compose includes hardcoded local database credentials and should not be treated as production secret storage.
5. OpenRouter is requested in the brief, but there is no isolated AI provider service in the primary backend yet.
6. API responses are frontend-compatible raw payloads. Introducing a universal success wrapper now would break the frontend unless performed as a versioned API change.
7. The frontend still imports mock data for fallback displays. This is useful for resilience but should be gradually replaced with explicit loading/error states where business accuracy matters.
8. Generated/cache artifacts exist in the tree (`__pycache__`, SQLite WAL/SHM files). They should be ignored or cleaned in source control, not used as production artifacts.
9. There are integration tests for core scenarios, agents, policies, ledger, insights, kill switch, and commerce workflows.
10. Render deployment files are absent from the primary app root.

## Safe Remediation Scope For This Pass

- Preserve FastAPI architecture and existing frontend API contracts.
- Add production environment documentation without committing secrets.
- Add Render deployment configuration using environment variables.
- Add an isolated OpenRouter client service with timeout, safe logging, retry, and in-memory prompt-result caching.
- Harden global exception output to avoid leaking exception class names.
- Add request IDs to API responses and logs for operations support.
- Run backend tests and frontend build to verify the MVP still works.

## Deferred Work

- JWT authentication and refresh flow across frontend/backend.
- Versioned API response envelope for all success responses.
- Removing mock fallbacks page by page after live endpoint parity is confirmed.
- Full Supabase schema normalization beyond the current SQLAlchemy/Alembic model set.
- Persistent distributed rate limiting for AI calls and public API endpoints.
