from fastapi import APIRouter

from app.api.v1 import courses, demo, leaderboard, me, sessions, skills

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(me.router)
api_router.include_router(courses.router)
api_router.include_router(skills.router)
api_router.include_router(sessions.router)
api_router.include_router(leaderboard.router)
api_router.include_router(demo.router)
