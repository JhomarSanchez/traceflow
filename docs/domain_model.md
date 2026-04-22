# Domain Model

## Purpose

This document defines the core domain concepts for the MVP.

The goal is to make the model explicit so implementation decisions remain consistent across sessions and contributors.

This is the source of truth for:
- entities
- ownership rules
- state transitions
- invariants
- core relationships

---

## Domain Overview

The system is centered around **user-owned workflows** that react to incoming events.

A workflow is configured for a specific `event_type` and contains an ordered list of steps.
When an event arrives, the system resolves a matching active workflow, records the event, creates an execution, executes the steps in order, and stores the result of the execution and each step.

---

## Core Entities

## 1. User

Represents an authenticated owner of workflows and executions.

### Responsibilities
- own workflows
- trigger event submissions through authenticated API access
- view only owned resources

### Core fields
- `id`
- `email`
- `hashed_password`
- `is_active`
- `created_at`
- `updated_at`

### Invariants
- email must be unique
- password is never stored in plain text
- inactive users cannot access protected operations

---

## 2. Workflow

Represents a reusable process bound to a single event type.

### Responsibilities
- define what kind of event it handles
- hold ordered workflow steps
- expose active/inactive execution eligibility

### Core fields
- `id`
- `owner_id`
- `name`
- `description`
- `event_type`
- `is_active`
- `created_at`
- `updated_at`

### Invariants
- a workflow belongs to exactly one user
- a workflow must have a `name`
- a workflow must have an `event_type`
- a workflow can process only events matching its `event_type`
- inactive workflows cannot be executed
- a workflow without steps cannot be executed

### Ownership rule
Only the owner can view, modify, activate, deactivate, or attach steps to the workflow.

---

## 3. WorkflowStep

Represents a single ordered action inside a workflow.

### Responsibilities
- define one unit of work within a workflow
- preserve execution order
- provide step configuration for runtime execution

### Core fields
- `id`
- `workflow_id`
- `step_order`
- `step_type`
- `step_config`
- `created_at`

### Invariants
- each step belongs to exactly one workflow
- `step_order` must be unique within the workflow
- steps are executed in ascending `step_order`
- `step_type` must be one of the allowed step types

### Supported step types in MVP
- `persist_payload`
- `log_message`
- `mark_success`
- optional: `transform_payload`

### Step configuration
`step_config` stores step-specific settings.
Examples:
- `log_message`: static message template
- `transform_payload`: simple transformation instruction
- `persist_payload`: storage behavior flags if needed

---

## 4. EventRecord

Represents an incoming event received by the system.

### Responsibilities
- preserve the original event input
- link an event to the workflow it triggered
- provide traceability for later execution analysis

### Core fields
- `id`
- `workflow_id`
- `event_type`
- `payload`
- `received_at`
- `received_by_user_id`

### Invariants
- every processed event must produce an `EventRecord`
- `event_type` must be present
- `payload` must not be null
- the referenced workflow must match the event type

### Notes
`EventRecord` is stored even though the API is authenticated, because traceability is a core product requirement.

---

## 5. Execution

Represents one concrete run of a workflow triggered by an event.

### Responsibilities
- track the overall lifecycle of processing
- group the step-level execution results
- expose final success or failure status

### Core fields
- `id`
- `workflow_id`
- `event_record_id`
- `status`
- `started_at`
- `finished_at`
- `error_message`

### Allowed statuses
- `pending`
- `running`
- `success`
- `failed`

### Invariants
- every execution belongs to one workflow
- every execution belongs to one triggering event record
- execution must start as `pending`
- execution must move to `running` before step processing
- execution must end as either `success` or `failed`
- finalized executions must have `finished_at`
- failed executions may store `error_message`

### State transitions
Allowed:
- `pending -> running`
- `running -> success`
- `running -> failed`

Forbidden:
- `success -> running`
- `failed -> running`
- `pending -> success` without execution
- `pending -> failed` unless runtime setup fails after creation and policy allows marking failure directly

---

## 6. ExecutionStep

Represents the result of executing one workflow step during a specific execution.

### Responsibilities
- preserve per-step traceability
- store per-step input/output data
- record exact failure location when execution fails

### Core fields
- `id`
- `execution_id`
- `workflow_step_id`
- `status`
- `input_data`
- `output_data`
- `error_message`
- `started_at`
- `finished_at`

### Allowed statuses
- `pending`
- `running`
- `success`
- `failed`

### Invariants
- every execution step belongs to one execution
- every execution step references one workflow step definition
- every executed workflow step must produce one execution step record
- failed execution steps may store `error_message`
- finalized step records must have `finished_at`

### State transitions
Allowed:
- `pending -> running`
- `running -> success`
- `running -> failed`

---

## Entity Relationships

```text
User 1 --- * Workflow
User 1 --- * EventRecord
Workflow 1 --- * WorkflowStep
Workflow 1 --- * EventRecord
Workflow 1 --- * Execution
EventRecord 1 --- 1 Execution
Execution 1 --- * ExecutionStep
WorkflowStep 1 --- * ExecutionStep
```

### Relationship notes
- a workflow has many step definitions
- an event record references the workflow chosen for that event
- an execution is the runtime instance of a workflow for a given event
- execution steps are runtime snapshots of workflow step definitions

---

## Domain Enums

## Workflow step type

```text
persist_payload
log_message
mark_success
transform_payload   (optional in MVP)
```

## Execution status

```text
pending
running
success
failed
```

## Execution step status

```text
pending
running
success
failed
```

---

## Business Rules

## User rules
1. A user email must be unique.
2. Only authenticated active users may access protected features.
3. A user may only access owned workflows and executions.

## Workflow rules
4. A workflow must have a non-empty name.
5. A workflow must have exactly one event type.
6. A workflow can only be executed if it is active.
7. A workflow can only be executed if it has at least one step.
8. Step order must be unique within a workflow.

## Event rules
9. Incoming events must contain `event_type`.
10. Incoming events must contain non-null `payload`.
11. The system must reject events that do not match an active workflow.
12. Every accepted event must create an `EventRecord`.

## Execution rules
13. Every accepted event must create an `Execution`.
14. Every execution must persist traceability even on failure.
15. A failure in one step fails the entire execution.
16. Execution steps must follow workflow step order.
17. The final execution state must always be explicit.
18. Execution details must remain queryable after completion.

---

## Aggregate Thinking

For implementation purposes, the most important aggregate roots are:

### Workflow aggregate
Includes:
- `Workflow`
- `WorkflowStep`

Why:
- step order and step composition are governed by the workflow
- ownership and activation rules apply at workflow level

### Execution aggregate
Includes:
- `Execution`
- `ExecutionStep`

Why:
- execution state is derived from ordered step execution
- step failures affect execution outcome

`EventRecord` is strongly associated with execution creation, but it can remain its own persisted record referenced by `Execution`.

---

## Runtime Behavior Model

### Event processing scenario

1. Authenticated user submits an event.
2. System validates event request structure.
3. System resolves active workflow by `event_type`.
4. System creates `EventRecord`.
5. System creates `Execution` in `pending`.
6. System marks execution `running`.
7. System loads workflow steps ordered by `step_order`.
8. System executes each step and stores `ExecutionStep` records.
9. If all steps succeed, execution becomes `success`.
10. If any step fails, execution becomes `failed` and stores error context.

---

## Ownership and Access Model

Ownership is user-based in the MVP.

### Ownership rules
- workflow ownership is determined by `Workflow.owner_id`
- event submissions are attributed through `EventRecord.received_by_user_id`
- executions are visible only through ownership of the underlying workflow

There is no multi-tenant organization model in v1.

---

## Domain Constraints to Preserve in Code

These constraints must be enforced in application/domain logic, not only assumed:

- cannot process event for inactive workflow
- cannot process event for workflow with no steps
- cannot modify a workflow owned by another user
- cannot list executions of another user's workflow
- cannot create duplicate step order in the same workflow
- cannot finalize an execution without setting a final state
- cannot expose sensitive user data in responses

---

## Persistence Notes

These are implementation-aligned but domain-relevant:

- `payload`, `step_config`, `input_data`, and `output_data` should use JSON-compatible structures
- timestamps must be timezone-aware where possible
- indexes should exist for `Workflow.owner_id`, `Workflow.event_type`, `Execution.workflow_id`, `Execution.status`, and `EventRecord.received_by_user_id`

---

## MVP Boundaries of the Domain

The domain does **not** include the following in v1:
- async job queues
- retries
- external email delivery
- third-party integrations
- webhook signatures
- versioned workflows
- workflow branching/conditions
- scheduled triggers
- organizations/teams

These are possible future extensions, but they are not part of the current model.

---

## Future-Friendly Extension Points

The current domain model should make these future additions possible without a rewrite:
- execution retries
- workflow versioning
- richer step types
- async processing workers
- API key-based event ingestion
- external integration steps

No current code should assume these exist now.
