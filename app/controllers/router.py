"""API v1 router composition."""

from fastapi import APIRouter

from app.controllers import analysis, auth, health, projects, shop, tasks, users

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(shop.router, tags=["shop"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
