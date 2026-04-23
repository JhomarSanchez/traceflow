# traceflow

[![Status](https://img.shields.io/badge/status-phase%201%20auth%20foundation-brightgreen)](./PROGRESS.md)
[![Scope](https://img.shields.io/badge/scope-MVP-blue)](./docs/product_scope.md)
[![Architecture](https://img.shields.io/badge/architecture-modular%20monolith-1f6feb)](./docs/architecture.md)
[![API](https://img.shields.io/badge/api-FastAPI-009688?logo=fastapi&logoColor=white)](./docs/api_spec.md)
[![Python](https://img.shields.io/badge/python-3.x-3776AB?logo=python&logoColor=white)](#planned-stack)
[![Database](https://img.shields.io/badge/database-PostgreSQL-4169E1?logo=postgresql&logoColor=white)](./docs/product_scope.md)
[![ORM](https://img.shields.io/badge/orm-SQLAlchemy-D71F00?logo=sqlalchemy&logoColor=white)](./docs/engineering_rules.md)
[![Migrations](https://img.shields.io/badge/migrations-Alembic-222222)](./docs/engineering_rules.md)
[![Auth](https://img.shields.io/badge/auth-JWT-black)](./docs/api_spec.md)
[![Container](https://img.shields.io/badge/dev%20env-Docker-2496ED?logo=docker&logoColor=white)](./docs/roadmap.md)

`traceflow` is a Python backend MVP for event-driven workflow execution.

It is designed as a serious backend engineering portfolio project: an authenticated API receives an event, resolves the matching workflow, executes its steps in order, persists execution and step-level traces, and exposes the result for later inspection.

## Why This Project

This repository is intentionally focused on demonstrating backend engineering maturity beyond CRUD:

- clear API design,
- layered modular-monolith architecture,
- explicit domain rules,
- ownership and access control,
- synchronous workflow execution with persisted traceability,
- disciplined MVP scope.

## Core Flow

```text
Client
  -> POST /api/v1/events
  -> event validated
  -> active workflow resolved by event_type
  -> EventRecord persisted
  -> Execution created and moved through its lifecycle
  -> Workflow steps executed in order
  -> ExecutionStep traces persisted
  -> final result returned and remains queryable
```

## MVP Capabilities

- User registration, login, and current-user retrieval with JWT authentication.
- Workflow creation, listing, detail retrieval, update, activation, and deactivation.
- Workflow step management with ordered execution.
- Event ingestion through API.
- Synchronous workflow execution for matching active workflows.
- Execution history and execution-detail retrieval with step-level traces.
- PostgreSQL persistence, Alembic migrations, Docker-based local environment, and tests.

## Domain Model

The MVP revolves around these core entities:

- `User`
- `Workflow`
- `WorkflowStep`
- `EventRecord`
- `Execution`
- `ExecutionStep`

Minimum business guarantees include:

- inactive workflows cannot run,
- workflows without steps cannot run,
- every received event must be recorded,
- every execution must end in `success` or `failed`,
- a step failure fails the whole execution,
- users can access only their own workflows and executions.

## Architecture

`traceflow` follows a modular monolith with layered boundaries:

- `api/` for HTTP transport, request validation, and response mapping.
- `application/` for use-case orchestration.
- `domain/` for business concepts, rules, and state transitions.
- `infrastructure/` for persistence, authentication internals, logging, and configuration.
- `core/` for shared technical foundations.

The main design principle is simple: routers stay thin, business behavior lives in use cases and domain logic, and persistence details stay behind repository boundaries.

## Planned Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy 2.x
- Alembic
- JWT authentication
- Docker
- pytest

## API Snapshot

Base path:

```text
/api/v1
```

Key endpoints:

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `POST /api/v1/workflows`
- `GET /api/v1/workflows`
- `POST /api/v1/workflows/{workflow_id}/steps`
- `POST /api/v1/events`
- `GET /api/v1/executions`
- `GET /api/v1/executions/{execution_id}`

The main demonstration endpoint is `POST /api/v1/events`, which processes an event synchronously and returns the execution summary.

## Example Event

```json
{
  "event_type": "user_registered",
  "payload": {
    "email": "user@example.com",
    "full_name": "Jane Doe"
  }
}
```

Example MVP step types:

- `log_message`
- `persist_payload`
- `mark_success`
- `transform_payload` (optional)

## Project Status

The repository now includes:

- Phase 0 foundation: project scaffold, FastAPI bootstrap, settings, logging, Alembic baseline, Docker files, and test setup.
- Phase 1 auth foundation: user model, registration, login, current-user retrieval, JWT handling, password hashing, and auth tests.
- Phase 2 workflow management: workflow creation, listing, detail retrieval, update, activation/deactivation, owner scoping, and workflow tests.
- Docker API startup applies Alembic migrations before launching the app so the local stack is usable without a separate manual migration step.

The next implementation milestone is workflow step management.

## Documentation

- [Progress tracker](./PROGRESS.md)
- [Product scope](./docs/product_scope.md)
- [Architecture](./docs/architecture.md)
- [Domain model](./docs/domain_model.md)
- [API specification](./docs/api_spec.md)
- [Engineering rules](./docs/engineering_rules.md)
- [Roadmap](./docs/roadmap.md)

## Badge Policy

This README uses badges selectively.

Included:

- stack and architecture badges that reflect real, documented decisions,
- a status badge that matches the current stage of the repository.

Intentionally excluded for now:

- CI badges,
- coverage badges,
- release/version badges,
- security compliance badges such as OpenSSF.

Those should only be added once the underlying automation, release process, or certification actually exists.
