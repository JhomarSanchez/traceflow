# PROGRESS.md

## Purpose
This file is the working memory snapshot for coding agents and future sessions.
It exists to reduce unnecessary repository re-reading and to preserve momentum across separate Codex chats.

Use this file as a concise operational summary, not as a long narrative.

---

## Update rules for Codex
When making meaningful progress, update this file immediately before ending the task.

Rules:
- Keep entries concise and factual.
- Prefer bullets over paragraphs.
- Record decisions, not raw thought process.
- Do not paste large code snippets.
- Do not duplicate commit-style diffs.
- If a task was partially completed, say exactly what is done and what remains.
- If a requested feature was rejected as out of scope, record it under `Open Issues / Risks`.

---

## Current Status
- Documentation baseline completed and reviewed for internal consistency.
- Repository now has Phase 0 foundation plus Phase 1 auth fully implemented and verified locally and through Docker Compose.
- MVP scope remains locked around an event-driven workflow execution backend in Python.
- Codex now has enough documentation to start implementation without inventing major requirements.
- Root documentation now reflects a runnable codebase with auth endpoints, not just scaffolding.

---

## Completed
- Defined product direction: event-driven workflow backend MVP.
- Defined architecture direction: modular monolith with layered boundaries.
- Defined domain model, API surface, engineering rules, and roadmap.
- Added `AGENTS.md`.
- Added `PROGRESS.md`.
- Added `docs/product_scope.md`.
- Added `docs/architecture.md`.
- Added `docs/domain_model.md`.
- Added `docs/api_spec.md`.
- Added `docs/engineering_rules.md`.
- Added `docs/roadmap.md`.
- Performed a quick cross-document consistency review.
- Added `README.md` with project positioning, architecture summary, API snapshot, linked documentation, and truthful static badges.
- Added `pyproject.toml` with Phase 0 runtime and dev dependencies.
- Added the initial `app/` scaffold aligned with documented layers.
- Added `FastAPI` bootstrap and `GET /api/v1/health`.
- Added base settings, logging configuration, SQLAlchemy base/session setup, and Alembic scaffold.
- Added `Dockerfile`, `docker-compose.yml`, and `.env.example` for local development baseline.
- Added an initial integration test for the health endpoint.
- Removed the mandatory `.env` dependency from `docker-compose.yml` by inlining safe local defaults for container startup.
- Added model autodiscovery in `app.infrastructure.db.models` so Alembic autogenerate will pick up ORM modules once they are introduced.
- Added `User` domain entity, auth use cases, repository interface, SQLAlchemy user model, and SQLAlchemy repository implementation.
- Added JWT token creation/validation, password hashing, current-user dependency, and structured API error handling for auth flows.
- Added `POST /api/v1/auth/register`, `POST /api/v1/auth/login`, and `GET /api/v1/auth/me`.
- Added the first Alembic migration for the `users` table.
- Added unit and integration tests for registration, login, duplicate email handling, and protected current-user retrieval.
- Verified auth test suite passes and confirmed the initial migration applies successfully against a temporary SQLite database.
- Updated `README.md` so repository status matches the implemented milestones.
- Updated Docker API startup so Alembic migrations run before `uvicorn`, fixing the missing `users` table when booting the local stack through Docker Compose.
- Verified Docker Compose end-to-end for Phase 1: stack boots, health responds, user registration works, login returns JWT, and `/api/v1/auth/me` succeeds with Bearer auth.

---

## Decisions Locked
- The project is an **MVP**, not a full platform.
- Main goal: look credible and serious as a Python backend portfolio project.
- Initial stack: FastAPI, PostgreSQL, SQLAlchemy, Alembic, JWT, Docker.
- Out of MVP: Redis, Celery, retries, scheduling, external integrations, advanced observability.
- Primary demo flow: `user_registered` event -> workflow resolution -> ordered step execution -> persisted execution trace.
- Only one active workflow per user per `event_type` should exist in the MVP.
- Codex must update this file after meaningful progress.
- README badge policy: use only truthful, low-maintenance badges; do not add CI, coverage, release, or certification badges before those signals exist.
- Phase 0 foundation uses a minimal runnable skeleton first, without introducing premature domain or auth code.
- `docker-compose.yml` must remain self-contained enough to boot the local stack even before a developer creates a custom `.env`.
- Alembic environment must explicitly import ORM model modules before relying on `Base.metadata` for autogeneration.
- Password hashing uses `pbkdf2_sha256` through `passlib` to avoid the Windows `bcrypt` backend compatibility issue encountered in this environment.
- The Docker API container is responsible for applying pending Alembic migrations on startup in the local MVP environment.

---

## Planned Core Entities
- `User`
- `Workflow`
- `WorkflowStep`
- `EventRecord`
- `Execution`
- `ExecutionStep`

---

## Planned Core Use Cases
- `RegisterUser`
- `LoginUser`
- `GetCurrentUser`
- `CreateWorkflow`
- `ListWorkflows`
- `GetWorkflowDetail`
- `UpdateWorkflow`
- `ActivateWorkflow`
- `DeactivateWorkflow`
- `AddStepToWorkflow`
- `ListWorkflowSteps`
- `RemoveStepFromWorkflow`
- `ReceiveEvent`
- `ProcessEvent`
- `GetExecutionDetail`
- `ListExecutions`

---

## Next Recommended Tasks
1. Implement Phase 2 from `docs/roadmap.md`: workflow management.
2. Reuse the existing auth dependency to protect workflow endpoints and enforce owner scoping from the first workflow slice.
3. Verify Docker startup locally once Docker is installed on the machine.
4. Revisit README badges once CI, tests, and release/versioning signals actually exist.
5. Update this file after each milestone.

---

## Open Issues / Risks
- Workflow step types are intentionally minimal for MVP and may feel visually underwhelming unless the README explains the engineering value clearly.
- The event-processing flow is synchronous by design; this is correct for MVP but must not be mistaken for the final scalable architecture.
- If Codex skips the roadmap and starts from feature ideas instead of milestones, scope drift is likely.
- A leftover Windows permission warning still appears in `git status` for a stray `pytest-cache-files-*` directory outside the tracked source tree, but it did not affect test execution.

---

## Session Handoff Notes
When starting in a new Codex session:
1. Read this file first.
2. Read `AGENTS.md`.
3. Read `docs/product_scope.md`.
4. Read `docs/architecture.md`.
5. Read `docs/domain_model.md`.
6. Read `docs/api_spec.md`.
7. Read `docs/engineering_rules.md`.
8. Read `docs/roadmap.md`.
9. Continue from `Next Recommended Tasks` unless the human gives a more specific task.
