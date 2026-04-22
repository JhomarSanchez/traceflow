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
- Repository is still in planning/scaffolding stage; no application code has been recorded yet.
- MVP scope remains locked around an event-driven workflow execution backend in Python.
- Codex now has enough documentation to start implementation without inventing major requirements.
- Added a professional root `README.md` aligned with the documented MVP, architecture, and roadmap.

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
1. Scaffold the repository structure exactly as defined in `docs/architecture.md`.
2. Bootstrap FastAPI app, settings, logging, DB session management, Alembic, Docker, and pytest.
3. Implement Phase 1 from `docs/roadmap.md`: auth and user foundation.
4. Revisit README badges once CI, tests, and release/versioning signals actually exist.
5. Update this file after each milestone.

---

## Open Issues / Risks
- Workflow step types are intentionally minimal for MVP and may feel visually underwhelming unless the README explains the engineering value clearly.
- The event-processing flow is synchronous by design; this is correct for MVP but must not be mistaken for the final scalable architecture.
- If Codex skips the roadmap and starts from feature ideas instead of milestones, scope drift is likely.
- The current README accurately reflects a documentation-first stage; it will need another pass once runnable code, setup commands, and real verification signals exist.

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
