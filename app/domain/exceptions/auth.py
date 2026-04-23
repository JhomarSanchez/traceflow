from __future__ import annotations

from app.core.exceptions import TraceflowError


class EmailAlreadyExistsError(TraceflowError):
    code = "email_already_exists"
    message = "Email already exists"


class InvalidCredentialsError(TraceflowError):
    code = "invalid_credentials"
    message = "Invalid credentials"


class AuthenticationRequiredError(TraceflowError):
    code = "authentication_required"
    message = "Authentication required"


class InactiveUserError(TraceflowError):
    code = "inactive_user"
    message = "Inactive user cannot access protected operations"
