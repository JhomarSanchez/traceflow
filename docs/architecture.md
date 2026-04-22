# Architecture

## Purpose

This document defines the software architecture for the MVP of the event-driven workflow backend.

The architecture must optimize for:
- clarity
- maintainability
- strong separation of concerns
- testability
- backend engineering credibility
- low accidental complexity

This is **not** a microservices system.
This is a **modular monolith** with clear internal boundaries.

---

## Architectural Style

The project follows a combination of:
- **modular monolith architecture**
- **layered architecture**
- **use-case driven application design**
- **repository-based persistence abstraction**

The goal is to keep the project simple enough to finish, while structured enough to demonstrate strong engineering discipline.

---

## High-Level System View

The system receives an event, determines which workflow applies, executes the workflow steps in order, stores traceability records, and exposes the execution result through the API.

### Main runtime flow

```text
Client
  -> FastAPI router
  -> request schema validation
  -> application use case
  -> domain rules
  -> repositories / persistence
  -> execution engine
  -> execution + step records stored
  -> API response
```

### Main business flow

```text
Event received
  -> event_type validated
  -> active workflow resolved
  -> execution created with status=pending
  -> execution status changed to running
  -> workflow steps executed in order
  -> step results persisted
  -> execution finalized as success or failed
  -> result becomes queryable
```

---

## Architectural Layers

### 1. API Layer

**Responsibility:**
- expose HTTP endpoints
- validate incoming requests
- map application results into HTTP responses
- translate exceptions into proper status codes
- resolve authenticated user context

**Must not:**
- contain business logic
- access ORM models directly
- make domain decisions
- orchestrate transactions manually beyond request boundaries

Typical contents:
- routers
- API dependencies
- request/response schemas
- exception mapping

---

### 2. Application Layer

**Responsibility:**
- implement use cases
- orchestrate domain operations
- coordinate repositories
- define transactional boundaries
- shape business operations into explicit actions

This is the main orchestration layer.

Typical use cases:
- `RegisterUser`
- `LoginUser`
- `CreateWorkflow`
- `AddStepToWorkflow`
- `ReceiveEvent`
- `ProcessEvent`
- `GetExecutionDetail`
- `ListExecutions`

**Must not:**
- depend on FastAPI request objects
- depend directly on HTTP concepts
- contain raw SQL

---

### 3. Domain Layer

**Responsibility:**
- encode core business concepts
- define business rules and invariants
- express allowed state transitions
- remain independent from frameworks and transport details

Typical contents:
- entities
- enums
- value objects
- domain services
- domain exceptions

Examples of domain rules:
- inactive workflows cannot execute
- workflows cannot process events of another type
- execution must end in `success` or `failed`
- step order must be unique within a workflow

**Must not:**
- import FastAPI
- import SQLAlchemy models
- know about HTTP or JSON serialization details

---

### 4. Infrastructure Layer

**Responsibility:**
- persistence implementation
- database session management
- repository implementations
- authentication implementation details
- logging setup
- configuration loading

Typical contents:
- SQLAlchemy models
- repository implementations
- session factory
- Alembic integration
- password hashing
- JWT helpers

**May depend on:**
- SQLAlchemy
- Pydantic settings
- external libraries

---

## Dependency Direction

Dependencies must point inward.

Allowed direction:

```text
API -> Application -> Domain
API -> Application -> Infrastructure (through interfaces / wiring)
Infrastructure -> Domain
Infrastructure -> Application interfaces
```

Forbidden direction:
- Domain -> API
- Domain -> FastAPI
- Domain -> SQLAlchemy ORM models
- Application -> FastAPI request/response classes

The business core must not be framework-led.

---

## Project Structure

```text
app/
  main.py
  core/
    config.py
    security.py
    logging.py
    exceptions.py
  api/
    dependencies.py
    routers/
      auth.py
      workflows.py
      workflow_steps.py
      events.py
      executions.py
  application/
    interfaces/
      repositories/
    schemas/
    use_cases/
      auth/
      workflows/
      events/
      executions/
  domain/
    entities/
    enums/
    services/
    exceptions/
  infrastructure/
    db/
      base.py
      session.py
      models/
      repositories/
    auth/
    logging/
  tests/
    unit/
    integration/
```

### Folder intent

- `core/`: shared technical foundations
- `api/`: HTTP concerns only
- `application/`: business use-case orchestration
- `domain/`: business model and rules
- `infrastructure/`: technical implementations
- `tests/`: tests split by scope

---

## Modules in the MVP

The MVP is organized around these bounded modules:

### Auth
Responsibilities:
- register users
- authenticate users
- load current user

### Workflows
Responsibilities:
- create workflows
- update workflow metadata
- activate/deactivate workflows
- list user workflows

### Workflow Steps
Responsibilities:
- add steps to workflows
- remove steps
- list steps in execution order

### Events
Responsibilities:
- receive events
- validate event payload structure at request level
- resolve workflow by `event_type`
- create event records
- trigger processing

### Executions
Responsibilities:
- create execution records
- execute workflow steps in order
- persist execution step results
- expose execution history and details

---

## Persistence Strategy

### Database
- PostgreSQL is the primary data store.
- SQLAlchemy 2.x style must be used.
- Alembic manages schema migrations.

### Repository Pattern
Repositories abstract persistence from use cases.

Expected repository interfaces:
- `UserRepository`
- `WorkflowRepository`
- `WorkflowStepRepository`
- `EventRecordRepository`
- `ExecutionRepository`
- `ExecutionStepRepository`

Repository responsibilities:
- retrieve aggregates or records
- persist changes
- encapsulate ORM queries
- keep application layer free from ORM details

### Transaction Boundaries
Each application use case must define a clear transaction boundary.

Typical pattern:
1. receive validated input
2. load required state
3. validate rules
4. perform changes
5. commit transaction
6. return response object

On failure:
- rollback transaction
- persist failure state when appropriate
- raise controlled exception

---

## Execution Engine Design

The execution engine is synchronous in the MVP.

This is intentional.

The goal is to prove domain orchestration and traceability first, without adding queue infrastructure.

### Execution lifecycle
1. create execution as `pending`
2. move execution to `running`
3. iterate steps by `step_order`
4. persist `ExecutionStep` for each step
5. mark each step `success` or `failed`
6. finalize parent execution

### Supported step types in MVP
- `persist_payload`
- `log_message`
- `mark_success`
- optional: `transform_payload`

No external email sending, PDF generation, queueing, or third-party API calls are required in v1.

---

## Error Handling Strategy

Errors must be classified.

### Categories
1. **Validation errors**
   - malformed request
   - missing required fields
   - invalid enum values

2. **Domain errors**
   - workflow inactive
   - workflow not found for event type
   - workflow has no steps
   - unauthorized access to resource

3. **Infrastructure errors**
   - database failure
   - migration mismatch
   - unexpected persistence issue

### Rules
- Domain errors must be explicit custom exceptions.
- API layer maps domain errors into HTTP responses.
- Internal errors must not leak sensitive implementation detail.
- Failures during execution must still leave traceability records when possible.

---

## Security Architecture

### Authentication
- JWT-based authentication for API access.
- Passwords stored only as hashes.
- Protected endpoints require authenticated user context.

### Authorization
Authorization is object-level, not only role-level.

Rules:
- users can only access their own workflows
- users can only access their own executions
- users can only modify workflows they own

### Sensitive Data
- never expose password hashes
- never log tokens or passwords
- event payloads may be stored, but sensitive values should be handled carefully in future versions

---

## Validation Strategy

Validation is split by concern.

### API validation
Handled through request schemas.

Covers:
- field presence
- type correctness
- basic format constraints

### Domain validation
Handled inside domain/application logic.

Covers:
- ownership rules
- workflow activation rules
- state transitions
- execution eligibility

Validation must not live only in the database.

---

## Logging Strategy

The MVP uses structured logging.

Minimum logging requirements:
- request start/end
- authenticated user id where applicable
- event receipt
- workflow resolution
- execution start/end
- execution failure with context

Logs must support debugging and demonstration value.

Do not log:
- passwords
- JWT tokens
- secret settings

---

## Testing Strategy

### Unit tests
Focus on:
- domain rules
- state transitions
- workflow execution logic
- permission logic

### Integration tests
Focus on:
- repositories
- database interaction
- API endpoints
- event processing persistence

### Priority flows to test
- register + login
- create workflow
- add ordered steps
- receive matching event
- execution success path
- execution failure path
- unauthorized resource access

---

## What This Architecture Intentionally Avoids

To keep the MVP focused, the architecture explicitly avoids:
- microservices
- distributed queues
- Redis
- Celery
- event sourcing
- CQRS
- workflow versioning
- plugin systems
- multi-tenant isolation
- external integrations as core features

These may be considered only after the MVP is complete.

---

## Definition of Done for Architecture Compliance

A feature is architecturally acceptable only if:
- router code remains thin
- business logic lives in use cases/domain services
- persistence access goes through repositories
- models are separated by purpose
- tests are added or updated
- no forbidden cross-layer dependency is introduced
- the implementation respects MVP scope

---

## Future Evolution Path

After the MVP is stable, the preferred evolution path is:
1. add Redis
2. move execution processing to Celery or equivalent worker system
3. add retry policies
4. add API keys and inbound webhook authentication
5. add metrics/observability improvements

The MVP must be designed so these can be added without rewriting the whole project.
