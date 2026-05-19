# TraceFlow API walkthrough

This walkthrough shows the intended demo path for evaluating TraceFlow as a backend portfolio project.

## Prerequisites

Run the local stack:

```bash
docker compose up --build
```

The API will be available at:

```text
http://localhost:8000/api/v1
```

## 1. Register a user

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@example.com",
    "password": "StrongPassword123!",
    "full_name": "Demo User"
  }'
```

## 2. Log in

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@example.com",
    "password": "StrongPassword123!"
  }'
```

Save the returned access token:

```bash
export TRACEFLOW_TOKEN="paste-token-here"
```

## 3. Create a workflow

```bash
curl -X POST http://localhost:8000/api/v1/workflows \
  -H "Authorization: Bearer $TRACEFLOW_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "User onboarding workflow",
    "event_type": "user_registered",
    "is_active": true
  }'
```

Save the returned workflow ID:

```bash
export WORKFLOW_ID="paste-workflow-id-here"
```

## 4. Add ordered workflow steps

```bash
curl -X POST http://localhost:8000/api/v1/workflows/$WORKFLOW_ID/steps \
  -H "Authorization: Bearer $TRACEFLOW_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Log registration event",
    "step_type": "log_message",
    "position": 1,
    "config": {
      "message": "A user registration event was received."
    }
  }'
```

```bash
curl -X POST http://localhost:8000/api/v1/workflows/$WORKFLOW_ID/steps \
  -H "Authorization: Bearer $TRACEFLOW_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Persist payload snapshot",
    "step_type": "persist_payload",
    "position": 2,
    "config": {}
  }'
```

## 5. Send an event

```bash
curl -X POST http://localhost:8000/api/v1/events \
  -H "Authorization: Bearer $TRACEFLOW_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "user_registered",
    "payload": {
      "email": "new.user@example.com",
      "full_name": "New User"
    }
  }'
```

Expected result:

- the event is stored,
- the matching active workflow is resolved,
- an execution is created,
- steps run in order,
- step-level traces are persisted,
- the final execution summary is returned.

## 6. Inspect execution history

```bash
curl http://localhost:8000/api/v1/executions \
  -H "Authorization: Bearer $TRACEFLOW_TOKEN"
```

Then fetch a specific execution:

```bash
curl http://localhost:8000/api/v1/executions/$EXECUTION_ID \
  -H "Authorization: Bearer $TRACEFLOW_TOKEN"
```

## What this walkthrough demonstrates

- JWT-protected API flows.
- User-owned workflows and executions.
- Event-driven workflow resolution.
- Ordered step execution.
- Persisted event, execution, and step-level traces.
- Failure boundaries for invalid or incomplete workflows.