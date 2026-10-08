from fastapi import APIRouter

from app.api.v1 import courses, me

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(me.router)
api_router.include_router(courses.router)
