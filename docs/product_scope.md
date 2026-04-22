# Product Scope

## Product summary
This project is a Python backend MVP for **event-driven workflow execution**.

The system receives an event through an API, determines which workflow should handle that event, executes the workflow steps in order, records the full execution trail, and exposes the result for later inspection.

This is intended to be a **serious backend portfolio project**, not a feature-heavy product.

---

## Primary goal
Demonstrate that the author can design and build a backend system that shows:
- clear API design,
- sound data modeling,
- layered architecture,
- explicit business rules,
- authentication and access control,
- execution traceability,
- disciplined scope control,
- professional project structure.

---

## Product statement
In one sentence:

> A backend that receives events, resolves the matching workflow, executes ordered steps, records everything that happened, and makes the final execution outcome queryable.

---

## Target outcome for reviewers
A recruiter, interviewer, or technical reviewer should conclude that this project demonstrates:
- backend maturity beyond CRUD-only apps,
- understanding of API architecture,
- understanding of persistence and execution state,
- understanding of ownership and security boundaries,
- ability to design maintainable software.

---

## MVP scope

### Included in MVP
The MVP must include the following capabilities:

#### Authentication
- user registration,
- user login,
- current-user retrieval,
- JWT-based authentication.

#### Workflow management
- create workflow,
- list workflows,
- retrieve workflow detail,
- update workflow,
- activate workflow,
- deactivate workflow.

#### Workflow step management
- add workflow step,
- list workflow steps,
- remove workflow step.

#### Event ingestion and execution
- receive event through API,
- resolve the workflow by `event_type`,
- persist the received event,
- create an execution record,
- execute workflow steps in order,
- record each step outcome,
- finalize execution as `success` or `failed`.

#### Execution visibility
- retrieve execution detail,
- list executions for the authenticated owner,
- inspect step-level outcomes.

#### Engineering baseline
- PostgreSQL persistence,
- SQLAlchemy ORM,
- Alembic migrations,
- Dockerized local environment,
- basic structured logging,
- tests for important behavior.

---

## Explicit non-goals for MVP
These items are intentionally excluded from the MVP:
- Redis,
- Celery,
- asynchronous background workers,
- automatic retries,
- scheduled jobs / cron execution,
- external webhook signature verification,
- API key auth,
- external email sending,
- PDF generation,
- advanced metrics tooling,
- OpenTelemetry,
- multi-tenant organizations,
- workflow versioning,
- visual workflow editor,
- complex notification systems,
- advanced CI/CD pipelines.

These may be future enhancements, but they are not required to make the project credible.

---

## Example MVP scenario
The canonical demo workflow for the MVP is:

### Event type
`user_registered`

### Example event payload
```json
{
  "event_type": "user_registered",
  "payload": {
    "email": "user@example.com",
    "full_name": "Jane Doe"
  }
}
```

### Example workflow behavior
A matching workflow may execute these step types:
1. `persist_payload`
2. `log_message`
3. `mark_success`

This scenario is intentionally small but sufficient to prove the architecture and execution engine.

---

## Step types for MVP
Keep step types intentionally narrow.
The allowed initial step types are:
- `log_message`
- `persist_payload`
- `mark_success`
- optional: `transform_payload`

Do not expand step types aggressively unless the documentation is updated.

---

## Core domain objects
The MVP is built around these core entities:
- `User`
- `Workflow`
- `WorkflowStep`
- `EventRecord`
- `Execution`
- `ExecutionStep`

---

## Core business rules
The MVP must enforce these minimum business rules:

### User and ownership rules
- email must be unique,
- only authenticated users can create and manage workflows,
- users can only access their own workflows,
- users can only access their own executions.

### Workflow rules
- a workflow must have a `name` and an `event_type`,
- a workflow only handles events that match its `event_type`,
- inactive workflows cannot execute,
- workflows with zero steps cannot execute,
- workflow step order must be unique within a workflow.

### Event rules
- every received event must be persisted,
- every event must include `event_type`,
- event payload must not be null,
- if no active workflow matches the event type, execution must be rejected.

### Execution rules
- an execution record must exist before step execution begins,
- execution status must transition to a terminal state,
- terminal states are `success` and `failed`,
- if one step fails, the whole execution fails,
- each executed step must leave its own trace record,
- started and finished timestamps must be recorded.

---

## Quality expectations
This project must feel deliberate and disciplined.
That means:
- good naming,
- strong separation of concerns,
- no giant mixed-purpose files,
- explicit schemas,
- explicit status handling,
- meaningful tests,
- documentation aligned with implementation.

---

## What success looks like
The MVP is successful when a reviewer can:
1. inspect the codebase and understand the architecture quickly,
2. see a complete event-to-execution flow,
3. verify that workflow execution state is persisted and queryable,
4. see that the system is secure enough for a portfolio-level backend,
5. conclude that the author understands backend engineering beyond basic CRUD.

---

## Out-of-scope warning for coding agents
Do not add infrastructure or product features just because they are common in “real-world systems”.
This project is intentionally constrained.
The correct implementation is the smallest coherent system that proves the architecture and business flow.

