from fastapi import APIRouter

from app.api.v1 import courses, me, sessions, skills

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(me.router)
api_router.include_router(courses.router)
api_router.include_router(skills.router)
api_router.include_router(sessions.router)
