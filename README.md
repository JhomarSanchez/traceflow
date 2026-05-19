# traceflow

[![Scope](https://img.shields.io/badge/scope-MVP-blue)](./docs/product_scope.md)
[![Architecture](https://img.shields.io/badge/architecture-modular%20monolith-1f6feb)](./docs/architecture.md)
[![API](https://img.shields.io/badge/api-FastAPI-009688?logo=fastapi&logoColor=white)](./docs/api_spec.md)
[![Python](https://img.shields.io/badge/python-3.12-3776AB?logo=python&logoColor=white)](#stack)
[![Database](https://img.shields.io/badge/database-PostgreSQL-4169E1?logo=postgresql&logoColor=white)](./docs/product_scope.md)
[![ORM](https://img.shields.io/badge/orm-SQLAlchemy-D71F00?logo=sqlalchemy&logoColor=white)](./docs/engineering_rules.md)
[![Migrations](https://img.shields.io/badge/migrations-Alembic-222222)](./docs/engineering_rules.md)
[![Auth](https://img.shields.io/badge/auth-JWT-black)](./docs/api_spec.md)
[![Container](https://img.shields.io/badge/dev%20env-Docker-2496ED?logo=docker&logoColor=white)](./docs/roadmap.md)

`traceflow` is a Python backend MVP for event-driven workflow execution with persisted traceability.

It is designed as a backend engineering portfolio project: an authenticated API receives an event, resolves the matching workflow, executes ordered steps, persists execution and step-level traces, and exposes the result for later inspection.

## What this project demonstrates

- FastAPI application structure beyond a single-file CRUD demo.
- Modular-monolith architecture with explicit layered boundaries.
- JWT-protected ownership and access-control flows.
- PostgreSQL persistence through SQLAlchemy 2.x and Alembic migrations.
- Event ingestion, workflow resolution, ordered step execution, and persisted traces.
- Docker-based local environment and pytest-based test coverage.

## Core flow

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

## Quickstart

Run the local stack:

```bash
docker compose up --build
```

The API will be available at:

```text
http://localhost:8000/api/v1
```

Apply migrations manually when not using the Docker command:

```bash
python -m alembic upgrade head
```

Run tests:

```bash
pytest
```

## MVP capabilities

- User registration, login, and current-user retrieval with JWT authentication.
- Workflow creation, listing, detail retrieval, update, activation, and deactivation.
- Workflow step management with ordered execution.
- Event ingestion through API.
- Synchronous workflow execution for matching active workflows.
- Execution history and execution-detail retrieval with step-level traces.
- PostgreSQL persistence, Alembic migrations, Docker-based local environment, and tests.

## Domain model

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

## Stack

- Python 3.12
- FastAPI
- PostgreSQL
- SQLAlchemy 2.x
- Alembic
- JWT authentication
- Docker
- pytest

## API snapshot

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

## Example event

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
- `transform_payload` optional

## Evaluation path

For a hands-on walkthrough, see:

- [API walkthrough](./docs/api_walkthrough.md)

That document demonstrates the intended evaluation flow: register, log in, create a workflow, add ordered steps, send an event, and inspect execution traces.

## Documentation

- [Progress tracker](./PROGRESS.md)
- [Product scope](./docs/product_scope.md)
- [Architecture](./docs/architecture.md)
- [Domain model](./docs/domain_model.md)
- [API specification](./docs/api_spec.md)
- [API walkthrough](./docs/api_walkthrough.md)
- [Engineering rules](./docs/engineering_rules.md)
- [Roadmap](./docs/roadmap.md)
- [Repository metadata recommendations](./docs/repository-metadata.md)

## Recommended GitHub metadata

Use this repository description:

```text
Event-driven workflow backend with execution tracing, JWT auth, PostgreSQL persistence and modular architecture.
```

Recommended topics:

```text
python, fastapi, postgresql, sqlalchemy, alembic, docker, jwt, backend, workflow-engine, traceability, audit-log, modular-monolith, pytest
```

## Badge policy

This README uses badges selectively.

Included:

- stack and architecture badges that reflect real, documented decisions.

Intentionally excluded for now:

- CI badges,
- coverage badges,
- release/version badges,
- security compliance badges such as OpenSSF.

Those should only be added once the underlying automation, release process, or certification actually exists.