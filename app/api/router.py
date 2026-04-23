from fastapi import APIRouter

from app.api.routers.auth import router as auth_router
from app.api.routers.health import router as health_router
from app.api.routers.workflow_steps import router as workflow_steps_router
from app.api.routers.workflows import router as workflows_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(health_router, tags=["health"])
api_router.include_router(workflows_router)
api_router.include_router(workflow_steps_router)
