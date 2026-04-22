# AGENTS.md

## Project identity
This repository contains a Python backend MVP for **event-driven workflow execution**.
The system must:
- receive an event through an API endpoint,
- resolve the matching workflow,
- execute the workflow steps in order,
- persist execution results and step-level traces,
- expose the execution outcome through the API.

This is **not** a generic CRUD project and **not** a low-discipline tutorial app.
The goal is to showcase serious backend engineering in Python with a clean architecture, explicit business rules, and production-style project structure.

---

## Primary objective
When implementing features, prioritize the following in order:
1. correctness of business behavior,
2. architecture consistency,
3. traceability and observability,
4. security and access control,
5. testability,
6. code elegance.

Do not over-engineer beyond the MVP.
Do not add speculative features unless they are explicitly required by the docs.

---

## Required reading order before making changes
Before planning or editing code, read these files in this exact order:
1. `PROGRESS.md`
2. `docs/product_scope.md`
3. `docs/architecture.md` if present
4. `docs/domain_model.md` if present
5. `docs/api_spec.md` if present
6. `docs/engineering_rules.md` if present
7. `docs/roadmap.md` if present

If a file does not exist yet, proceed with the files that do exist.
Do not invent requirements that contradict the existing docs.

---

## Mandatory workflow for Codex
For every meaningful task, follow this sequence:
1. Read the required docs.
2. Summarize the task in 3-6 bullets internally.
3. Identify affected layers: `api`, `application`, `domain`, `infrastructure`, `tests`.
4. Make the smallest coherent implementation that satisfies the task.
5. Add or update tests.
6. Verify imports, typing, and naming consistency.
7. Update `PROGRESS.md` concisely.

If the requested change conflicts with the documented MVP scope, do not silently implement it as if it were accepted scope. Either:
- implement only the in-scope part, and clearly note the out-of-scope remainder in `PROGRESS.md`, or
- leave the code unchanged and record the scope conflict in `PROGRESS.md`.

---

## Non-negotiable engineering rules

### Architecture
- Use a **modular monolith**.
- Use **layered architecture** with clear boundaries.
- Keep responsibilities separated across:
  - `api/`
  - `application/`
  - `domain/`
  - `infrastructure/`
  - `core/`

### Strict separation rules
- Do **not** place business logic in FastAPI routers.
- Do **not** access the database directly from routers.
- Do **not** expose ORM models directly as API responses.
- Do **not** place HTTP-specific concerns inside domain logic.
- Do **not** couple use cases directly to framework details when avoidable.

### Code quality
- Prefer small, explicit functions over vague abstractions.
- Use type hints consistently.
- Use descriptive names.
- Avoid giant `utils.py` files.
- Avoid dead code, placeholder comments, and fake TODO implementations.
- Keep modules cohesive.

### SQLAlchemy and persistence
- Use SQLAlchemy 2.x style.
- Use one database session per request or per unit of work.
- Use Alembic for schema migrations.
- Use explicit foreign keys and indexes where justified.
- Use JSON/JSONB only where the domain actually needs flexible payload storage.

### API behavior
- Use `/api/v1` prefix.
- Keep request and response schemas explicit.
- Return correct HTTP status codes.
- Enforce ownership checks on protected resources.
- Add pagination to list endpoints when relevant.

### Testing
- Every meaningful feature must include tests.
- Prefer unit tests for business rules and integration tests for persistence and endpoints.
- Avoid brittle tests tied to implementation trivia.

### Logging and safety
- Use structured logs.
- Never log passwords, tokens, or secrets.
- Include execution identifiers and relevant context in logs.

---

## MVP feature boundaries

### In scope
- user registration and login,
- JWT authentication,
- workflow creation and management,
- workflow step management,
- event ingestion through API,
- workflow execution,
- execution history and detail retrieval,
- persistence and traceability,
- basic logging,
- tests.

### Out of scope for MVP
- Redis,
- Celery or background workers,
- async job queues,
- retries,
- scheduled jobs,
- external webhook signature verification,
- API keys,
- email delivery,
- PDF generation,
- metrics platforms,
- OpenTelemetry,
- multi-tenancy,
- workflow versioning,
- visual workflow builder,
- advanced CI/CD.

Do not introduce out-of-scope capabilities unless the docs are explicitly updated.

---

## Core domain expectations
The system revolves around these concepts:
- `User`
- `Workflow`
- `WorkflowStep`
- `EventRecord`
- `Execution`
- `ExecutionStep`

Minimum business expectations:
- a workflow must match an `event_type`,
- inactive workflows cannot run,
- workflows without steps cannot run,
- each received event must be recorded,
- each execution must end in `success` or `failed`,
- if one step fails, the full execution fails,
- users can only access their own workflows and executions.

---

## Preferred implementation style
When building a feature, favor this shape:
- Router receives request.
- Pydantic schema validates input.
- Use case orchestrates the operation.
- Repository interfaces mediate persistence.
- Domain rules stay explicit.
- Response schema maps output back to HTTP.

Avoid framework-first coding.
Prefer use-case-first coding.

---

## What to do when information is missing
If implementation details are not fully specified:
1. prefer the smallest decision compatible with the documented MVP,
2. keep the design easy to extend later,
3. record the decision briefly in `PROGRESS.md`.

Do not compensate for missing requirements by introducing broad speculative systems.

---

## Required `PROGRESS.md` maintenance
At the end of any substantial code change, update `PROGRESS.md`.
The update must be concise and factual.
Do not write essays.
Do not duplicate code diffs.

Always update these sections when relevant:
- `Current Status`
- `Completed`
- `Decisions Locked`
- `Next Recommended Tasks`
- `Open Issues / Risks`

If no meaningful progress was made, say so explicitly.

---

## Definition of done for any task
A task is not done unless all of these are true:
- the requested behavior is implemented,
- the implementation respects the architecture,
- tests were added or updated when applicable,
- no obvious scope creep was introduced,
- `PROGRESS.md` was updated.

