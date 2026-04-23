# API Specification (MVP)

## Purpose

This document defines the HTTP API surface for the MVP of the event-driven workflow backend.

The goals of the API are:
- expose a clean, consistent REST interface
- support the MVP use cases only
- keep responses explicit and predictable
- avoid premature complexity

This is the source of truth for endpoint design in the MVP.

---

## API principles

1. All endpoints must be prefixed with `/api/v1`.
2. JSON is the default request and response format.
3. Protected endpoints require Bearer authentication.
4. Response schemas must be explicit and stable.
5. Do not return ORM models directly.
6. Use correct HTTP status codes.
7. Prefer simple, readable resource naming.
8. Pagination is required for list endpoints.

---

## Authentication model

The MVP uses JWT bearer authentication.

### Supported auth flows
- user registration
- user login
- fetch current authenticated user

### Header format
```http
Authorization: Bearer <access_token>
```

---

## Common response conventions

### Success responses
Use resource-based responses whenever possible.

Example:
```json
{
  "id": "workflow_123",
  "name": "User registration workflow",
  "event_type": "user_registered",
  "is_active": true,
  "created_at": "2026-04-22T15:00:00Z"
}
```

### List responses
All list endpoints should return paginated envelopes.

Example:
```json
{
  "items": [],
  "page": 1,
  "page_size": 20,
  "total": 0
}
```

### Error responses
All handled errors should return a consistent structure.

Example:
```json
{
  "error": {
    "code": "workflow_not_found",
    "message": "Workflow not found",
    "details": null
  }
}
```

### Standard error shape
- `code`: machine-readable error code
- `message`: human-readable summary
- `details`: optional structured context

---

## Health

### `GET /api/v1/health`

Simple health check endpoint.

#### Auth
Public

#### Response `200 OK`
```json
{
  "status": "ok"
}
```

---

## Authentication endpoints

## `POST /api/v1/auth/register`

Create a new user account.

### Auth
Public

### Request body
```json
{
  "email": "user@example.com",
  "password": "StrongPassword123!"
}
```

### Rules
- email must be unique
- password must satisfy basic validation rules

### Response `201 Created`
```json
{
  "id": "user_123",
  "email": "user@example.com",
  "is_active": true,
  "created_at": "2026-04-22T15:00:00Z"
}
```

### Errors
- `409 Conflict` if email already exists
- `422 Unprocessable Entity` if payload is invalid

---

## `POST /api/v1/auth/login`

Authenticate a user and return an access token.

### Auth
Public

### Request body
```json
{
  "email": "user@example.com",
  "password": "StrongPassword123!"
}
```

### Response `200 OK`
```json
{
  "access_token": "jwt-token",
  "token_type": "bearer"
}
```

### Errors
- `401 Unauthorized` for invalid credentials
- `422 Unprocessable Entity` for invalid payload

---

## `GET /api/v1/auth/me`

Return the current authenticated user.

### Auth
Required

### Response `200 OK`
```json
{
  "id": "user_123",
  "email": "user@example.com",
  "is_active": true,
  "created_at": "2026-04-22T15:00:00Z"
}
```

### Errors
- `401 Unauthorized`

---

## Workflow endpoints

## `POST /api/v1/workflows`

Create a workflow.

### Auth
Required

### Request body
```json
{
  "name": "User registration workflow",
  "description": "Process user_registered events",
  "event_type": "user_registered"
}
```

### Response `201 Created`
```json
{
  "id": "workflow_123",
  "name": "User registration workflow",
  "description": "Process user_registered events",
  "event_type": "user_registered",
  "is_active": true,
  "owner_id": "user_123",
  "created_at": "2026-04-22T15:00:00Z",
  "updated_at": "2026-04-22T15:00:00Z"
}
```

### Errors
- `401 Unauthorized`
- `409 Conflict` if another active workflow already exists for the same `event_type` for the authenticated user
- `422 Unprocessable Entity`

---

## `GET /api/v1/workflows`

List workflows owned by the authenticated user.

### Auth
Required

### Query params
- `page` (default: 1)
- `page_size` (default: 20, max: 100)
- `is_active` (optional)
- `event_type` (optional)

### Response `200 OK`
```json
{
  "items": [
    {
      "id": "workflow_123",
      "name": "User registration workflow",
      "description": "Process user_registered events",
      "event_type": "user_registered",
      "is_active": true,
      "owner_id": "user_123",
      "created_at": "2026-04-22T15:00:00Z",
      "updated_at": "2026-04-22T15:00:00Z"
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 1
}
```

---

## `GET /api/v1/workflows/{workflow_id}`

Return workflow detail.

### Auth
Required

### Response `200 OK`
```json
{
  "id": "workflow_123",
  "name": "User registration workflow",
  "description": "Process user_registered events",
  "event_type": "user_registered",
  "is_active": true,
  "owner_id": "user_123",
  "created_at": "2026-04-22T15:00:00Z",
  "updated_at": "2026-04-22T15:00:00Z"
}
```

### Errors
- `401 Unauthorized`
- `403 Forbidden`
- `404 Not Found`

---

## `PATCH /api/v1/workflows/{workflow_id}`

Update editable workflow fields.

### Auth
Required

### Editable fields
- `name`
- `description`
- `event_type`

### Request body
```json
{
  "name": "Updated workflow name",
  "description": "Updated description"
}
```

### Response `200 OK`
```json
{
  "id": "workflow_123",
  "name": "Updated workflow name",
  "description": "Updated description",
  "event_type": "user_registered",
  "is_active": true,
  "owner_id": "user_123",
  "created_at": "2026-04-22T15:00:00Z",
  "updated_at": "2026-04-22T15:15:00Z"
}
```

### Errors
- `401 Unauthorized`
- `403 Forbidden`
- `404 Not Found`
- `409 Conflict` if the update would create a second active workflow for the same `event_type`
- `422 Unprocessable Entity`

---

## `POST /api/v1/workflows/{workflow_id}/activate`

Activate a workflow.

### Auth
Required

### Response `200 OK`
```json
{
  "id": "workflow_123",
  "is_active": true
}
```

### Errors
- `401 Unauthorized`
- `403 Forbidden`
- `404 Not Found`
- `409 Conflict` if another active workflow already exists for the same `event_type`

---

## `POST /api/v1/workflows/{workflow_id}/deactivate`

Deactivate a workflow.

### Auth
Required

### Response `200 OK`
```json
{
  "id": "workflow_123",
  "is_active": false
}
```

---

## Workflow step endpoints

## `POST /api/v1/workflows/{workflow_id}/steps`

Add a step to a workflow.

### Auth
Required

### Allowed step types in MVP
- `log_message`
- `persist_payload`
- `mark_success`
- `transform_payload` (optional but supported by domain design)

### Request body
```json
{
  "step_order": 1,
  "step_type": "log_message",
  "step_config": {
    "message": "User registration event received"
  }
}
```

### Response `201 Created`
```json
{
  "id": "step_123",
  "workflow_id": "workflow_123",
  "step_order": 1,
  "step_type": "log_message",
  "step_config": {
    "message": "User registration event received"
  },
  "created_at": "2026-04-22T15:20:00Z"
}
```

### Errors
- `401 Unauthorized`
- `403 Forbidden`
- `404 Not Found`
- `409 Conflict` if step order already exists
- `422 Unprocessable Entity`

---

## `GET /api/v1/workflows/{workflow_id}/steps`

List steps for a workflow, ordered by `step_order` ascending.

### Auth
Required

### Response `200 OK`
```json
{
  "items": [
    {
      "id": "step_123",
      "workflow_id": "workflow_123",
      "step_order": 1,
      "step_type": "log_message",
      "step_config": {
        "message": "User registration event received"
      },
      "created_at": "2026-04-22T15:20:00Z"
    }
  ]
}
```

### Errors
- `401 Unauthorized`
- `403 Forbidden`
- `404 Not Found`

---

## `DELETE /api/v1/workflows/{workflow_id}/steps/{step_id}`

Remove a step from a workflow.

### Auth
Required

### Response `204 No Content`
No response body.

### Errors
- `401 Unauthorized`
- `403 Forbidden`
- `404 Not Found`

---

## Event and execution endpoints

## `POST /api/v1/events`

Receive an event and synchronously process the matching workflow.

### Auth
Required

### Behavior
1. validate event payload
2. find active workflow owned by authenticated user for `event_type`
3. create an event record
4. create an execution with status `pending`, then move it to `running`
5. execute workflow steps in order
6. persist execution result and step-level traces
7. return execution summary

### Request body
```json
{
  "event_type": "user_registered",
  "payload": {
    "email": "user@example.com",
    "full_name": "Jane Doe"
  }
}
```

### Response `201 Created`
```json
{
  "execution_id": "execution_123",
  "workflow_id": "workflow_123",
  "event_record_id": "event_123",
  "status": "success",
  "started_at": "2026-04-22T15:30:00Z",
  "finished_at": "2026-04-22T15:30:01Z",
  "error_message": null
}
```

### Errors
- `401 Unauthorized`
- `404 Not Found` if no active workflow exists for the event type
- `409 Conflict` if workflow has no steps
- `422 Unprocessable Entity`
- `500 Internal Server Error` for unexpected failures

### Notes
- If the workflow exists but has no steps, the accepted event still leaves a persisted failed execution trace before returning `409`.
- If a runtime step failure occurs, the accepted event still leaves persisted failed execution and execution-step records before returning `500`.

---

## `GET /api/v1/executions`

List executions for workflows owned by the authenticated user.

### Auth
Required

### Query params
- `page` (default: 1)
- `page_size` (default: 20, max: 100)
- `status` (optional)
- `workflow_id` (optional)
- `event_type` (optional)

### Response `200 OK`
```json
{
  "items": [
    {
      "id": "execution_123",
      "workflow_id": "workflow_123",
      "event_record_id": "event_123",
      "status": "success",
      "started_at": "2026-04-22T15:30:00Z",
      "finished_at": "2026-04-22T15:30:01Z",
      "error_message": null
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 1
}
```

---

## `GET /api/v1/executions/{execution_id}`

Return execution detail including step-level results.

### Auth
Required

### Response `200 OK`
```json
{
  "id": "execution_123",
  "workflow_id": "workflow_123",
  "event_record_id": "event_123",
  "status": "success",
  "started_at": "2026-04-22T15:30:00Z",
  "finished_at": "2026-04-22T15:30:01Z",
  "error_message": null,
  "steps": [
    {
      "id": "execution_step_1",
      "workflow_step_id": "step_123",
      "status": "success",
      "input_data": {
        "email": "user@example.com",
        "full_name": "Jane Doe"
      },
      "output_data": {
        "message": "logged"
      },
      "error_message": null,
      "started_at": "2026-04-22T15:30:00Z",
      "finished_at": "2026-04-22T15:30:00Z"
    }
  ]
}
```

### Errors
- `401 Unauthorized`
- `403 Forbidden`
- `404 Not Found`

---

## Error catalog

The following handled error codes should exist in the MVP:

- `invalid_credentials`
- `email_already_exists`
- `active_workflow_conflict`
- `workflow_not_found`
- `workflow_inactive`
- `workflow_has_no_steps`
- `invalid_workflow_data`
- `step_order_conflict`
- `workflow_step_not_found`
- `event_type_not_supported`
- `execution_not_found`
- `forbidden_resource_access`
- `invalid_event_payload`
- `unexpected_execution_error`

---

## Ownership and authorization rules

1. Users may only access their own workflows.
2. Users may only access executions linked to their own workflows.
3. Workflow step endpoints must verify ownership through the parent workflow.
4. Event execution must only target workflows owned by the authenticated user.

---

## Notes for implementation

- The MVP processes events synchronously.
- Only one active workflow per user per `event_type` should be allowed in the MVP.
- `POST /events` is the main demonstration endpoint and must be implemented carefully.
- Prefer stable enums for execution and step statuses.
- Use explicit Pydantic request and response schemas for every endpoint.
