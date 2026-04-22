# Roadmap

## Purpose

This roadmap defines the recommended implementation order for the MVP.

Its purpose is not product planning theater. It exists to keep implementation sequence disciplined, reduce unnecessary token usage, and prevent Codex from starting in the wrong place.

This document is the execution path for the MVP.

---

## Roadmap principles

1. Build foundations before features.
2. Prefer vertical slices that end in working behavior.
3. Avoid speculative infrastructure.
4. Keep the main demo flow working as early as possible.
5. Update `PROGRESS.md` after each completed milestone.

---

## Phase 0 - Repository and project foundation

### Goal
Create a stable foundation for the codebase.

### Deliverables
- project scaffold based on documented architecture
- dependency management configured
- FastAPI application bootstrapped
- environment-based settings
- database connection setup
- Alembic initialized
- Docker and docker-compose for local development
- base logging setup
- health endpoint
- pytest setup

### Definition of done
- app boots locally
- DB connectivity works
- migrations can run
- `/api/v1/health` returns success
- tests can execute
- progress updated

---

## Phase 1 - Authentication and user foundation

### Goal
Implement the minimum user/auth layer required for protected workflows.

### Deliverables
- `User` entity and ORM model
- user repository
- password hashing
- register endpoint
- login endpoint
- current-user endpoint
- auth dependencies for protected routes
- tests for auth flows

### Definition of done
- user can register
- user can log in
- protected endpoint access works with JWT
- duplicate email is handled correctly
- progress updated

---

## Phase 2 - Workflow management

### Goal
Allow authenticated users to create and manage workflows.

### Deliverables
- `Workflow` entity and ORM model
- workflow repository
- create workflow use case and endpoint
- list workflow use case and endpoint
- workflow detail endpoint
- workflow update endpoint
- activate/deactivate endpoints
- ownership checks
- tests for workflow CRUD behavior in MVP scope

### Definition of done
- authenticated user can manage own workflows
- user cannot access another user's workflows
- workflow activation state is persisted correctly
- progress updated

---

## Phase 3 - Workflow steps

### Goal
Add step definition support to workflows.

### Deliverables
- `WorkflowStep` entity and ORM model
- step repository or workflow-owned step access pattern
- add step endpoint
- list steps endpoint
- remove step endpoint
- allowed step type validation
- unique step order enforcement
- tests for step ordering and ownership

### Definition of done
- steps can be added and listed in correct order
- duplicate step order is rejected
- only owner can manage steps
- progress updated

---

## Phase 4 - Event ingestion and execution engine

### Goal
Implement the main MVP value: receive an event and process a workflow.

### Deliverables
- `EventRecord`, `Execution`, and `ExecutionStep` models
- repositories for event and execution persistence
- `ReceiveEvent` / `ProcessEvent` use case
- synchronous step execution engine
- execution status lifecycle
- step result persistence
- handled failure behavior
- `POST /api/v1/events`
- integration tests for the main event-processing flow

### Definition of done
- event can be submitted
- matching workflow is resolved
- execution is created and completed
- step-level results are stored
- failure path produces `failed` execution state
- progress updated

---

## Phase 5 - Execution querying and demo readiness

### Goal
Expose execution history clearly enough for portfolio/demo use.

### Deliverables
- list executions endpoint
- execution detail endpoint with step results
- filtering by workflow/status/event type where defined in spec
- improved structured logs around event processing
- final polish on API responses
- final integration test pass

### Definition of done
- execution history is queryable
- detailed execution output is useful in demo
- logs help trace the main flow
- progress updated

---

## Recommended implementation order inside each phase

Within each phase, work in this order:
1. domain definitions
2. application interfaces/use cases
3. infrastructure models/repositories
4. API schemas and routers
5. tests
6. documentation/progress update

This order is mandatory unless there is a strong reason to deviate.

---

## Demo milestone

The MVP is considered demo-ready when the following end-to-end story works:

1. register a user
2. log in
3. create a workflow for `user_registered`
4. add steps to the workflow
5. submit an event to `/api/v1/events`
6. receive execution result
7. inspect execution details and step history

If this story works cleanly, the MVP is portfolio-usable.

---

## Explicit non-goals for this roadmap

Do not start these during the MVP roadmap:
- Redis
- Celery
- async workers
- external email providers
- PDF generation
- API key auth
- multi-tenant design
- metrics platforms
- OpenTelemetry
- CI/CD pipelines beyond basic local readiness

These are future extensions, not MVP responsibilities.

---

## After MVP

Only after the MVP is complete and stable may future work be considered, such as:
- background processing with Redis + Celery
- retry policies
- richer step types
- API keys
- better observability
- workflow versioning

These are not part of the current implementation mandate.
