# Engineering Rules

## Purpose

This document defines mandatory engineering rules for implementing the MVP.

These rules are not optional preferences. They are constraints intended to keep the system coherent, readable, testable, and interview-ready.

---

## Core engineering goals

The codebase must optimize for:
- clarity
- correctness
- separation of concerns
- predictable behavior
- maintainability
- interview-quality architecture

It must not optimize for maximum abstraction, novelty, or framework cleverness.

---

## Architecture rules

1. The system must be implemented as a modular monolith.
2. The codebase must be split into the following top-level layers:
   - `api`
   - `application`
   - `domain`
   - `infrastructure`
   - `core`
3. Dependencies must point inward:
   - `api` may depend on `application`
   - `application` may depend on `domain` and interfaces
   - `infrastructure` may implement interfaces used by `application`
   - `domain` must not depend on FastAPI, SQLAlchemy, or HTTP concerns
4. Do not collapse the architecture into a route-service-repository shortcut if it breaks the above layering.

---

## API rules

1. No business logic in routers.
2. Routers may do only the following:
   - receive HTTP input
   - validate/authenticate via dependencies
   - call use cases
   - map results to HTTP responses
3. All endpoints must live under `/api/v1`.
4. Every endpoint must have explicit request and response schemas.
5. Response status codes must be intentional and correct.
6. Do not return raw internal exceptions to clients.
7. Use consistent error response formatting.

---

## Application layer rules

1. Each use case must represent a meaningful business action.
2. Use case names should be explicit and action-oriented, for example:
   - `CreateWorkflow`
   - `ReceiveEvent`
   - `GetExecutionDetail`
3. Use cases must not import FastAPI objects.
4. Use cases must not know about HTTP request/response objects.
5. Use cases may depend on repository interfaces and domain services.
6. Use cases must control transactional boundaries clearly.

---

## Domain rules

1. Domain code must contain business rules and invariants.
2. Domain code must not import framework-specific modules.
3. Workflow and execution state transitions must be explicit.
4. Invalid transitions must fail loudly through controlled exceptions.
5. Enums should be used for statuses and step types.
6. Domain terminology must remain stable and aligned with documentation.

---

## Persistence rules

1. SQLAlchemy 2.x style must be used.
2. Do not build new code around legacy `Session.query()` patterns.
3. ORM models must live in `infrastructure/db/models`.
4. Repository implementations must live in `infrastructure/db/repositories`.
5. ORM models must not be used directly as HTTP response objects.
6. Every DB change must be introduced through Alembic migrations.
7. No manual schema drift is allowed.
8. Use explicit foreign keys and indexes.
9. Use JSON/JSONB fields only where justified, mainly for payloads and step config.
10. One DB session per request or unit of work. Never share a mutable session globally.

---

## Naming rules

1. File and module names must use `snake_case`.
2. Class names must use `PascalCase`.
3. Function and variable names must use `snake_case`.
4. Constants must use `UPPER_SNAKE_CASE`.
5. Avoid vague module names such as `helpers.py`, `misc.py`, `common_utils.py`, or similar dump files.
6. Names must reflect domain meaning, not implementation accident.

---

## Schema and validation rules

1. Pydantic schemas must be separated from ORM models.
2. Request schemas and response schemas must be distinct when appropriate.
3. Validation should be strict for event payload envelopes and critical fields.
4. Do not silently coerce invalid business inputs when a validation error is more appropriate.
5. Sensitive values must not be exposed in serialized output.

---

## Security rules

1. Use JWT bearer auth for protected endpoints.
2. Passwords must be hashed; never store plaintext passwords.
3. Ownership must be checked at the object level, not only at authentication level.
4. Users must never access workflows or executions they do not own.
5. Never log passwords, JWTs, or secret configuration values.
6. Security-sensitive configuration must come from environment variables.
7. Keep auth implementation simple in the MVP; do not add premature features like refresh tokens unless explicitly approved.

---

## Error handling rules

1. Use explicit domain/application exceptions for expected business failures.
2. Map known exceptions to structured HTTP errors.
3. Do not swallow exceptions silently.
4. Unexpected exceptions must be logged with context.
5. The API must return stable machine-readable error codes.
6. Execution failures must still persist final execution state when possible.

---

## Logging rules

1. Logging must be structured.
2. Include enough context to debug without exposing secrets.
3. Log at least:
   - request start/end
   - authentication failures
   - workflow creation/update
   - event received
   - execution start/end
   - execution failure
4. Include `request_id` support if practical.
5. Logging design must help trace a single event execution.

---

## Testing rules

1. Testing is mandatory from the beginning.
2. The MVP must include:
   - unit tests for domain logic and validation rules
   - integration tests for repositories and main endpoints
3. Tests must be readable and behavior-oriented.
4. Do not write superficial tests that only assert framework plumbing.
5. Prefer fixtures for reusable setup.
6. The main event-processing flow must be covered by integration tests.
7. New behavior should ship with corresponding tests unless explicitly deferred.

---

## Documentation rules

1. Documentation must stay aligned with code.
2. If implementation changes architecture, scope, domain assumptions, or endpoint behavior, the relevant `.md` files must be updated.
3. `PROGRESS.md` must be updated whenever a meaningful implementation milestone is completed.
4. Do not use documentation as decoration. It must reflect real decisions.

---

## Scope control rules

1. Do not add Redis, Celery, async workers, external email delivery, API keys, multi-tenancy, or observability platforms in the MVP unless explicitly requested.
2. Do not introduce microservices.
3. Do not introduce CQRS, event sourcing, or plugin systems.
4. Do not over-generalize the step execution engine beyond the documented MVP step types.
5. Prefer finishing the MVP cleanly over building speculative extensions.

---

## Definition of done for a feature

A feature is only done if:
1. the code works
2. the architecture rules are respected
3. validation and error behavior are handled
4. tests exist at the appropriate level
5. documentation is updated if behavior changed
6. `PROGRESS.md` is updated with a concise note

---

## Review checklist

Before considering work complete, verify:
- layering is respected
- routers are thin
- business logic sits in use cases/domain
- persistence concerns are isolated
- ownership checks exist
- statuses and transitions are explicit
- tests cover behavior
- documentation and progress notes are updated
