from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_current_user, get_user_repository
from app.api.schemas.auth import (
    LoginUserRequest,
    RegisterUserRequest,
    TokenResponse,
    UserResponse,
)
from app.application.use_cases.auth import LoginUser, RegisterUser
from app.domain.entities import User
from app.infrastructure.db.repositories import SqlAlchemyUserRepository

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    payload: RegisterUserRequest,
    user_repository: Annotated[SqlAlchemyUserRepository, Depends(get_user_repository)],
) -> UserResponse:
    use_case = RegisterUser(user_repository)
    user = use_case(email=payload.email, password=payload.password)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse)
def login_user(
    payload: LoginUserRequest,
    user_repository: Annotated[SqlAlchemyUserRepository, Depends(get_user_repository)],
) -> TokenResponse:
    use_case = LoginUser(user_repository)
    access_token = use_case(email=payload.email, password=payload.password)
    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=UserResponse)
def get_authenticated_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    return UserResponse.model_validate(current_user)
