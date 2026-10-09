from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import sessionmaker

from app.api import health
from app.api.v1 import api_router
from app.core.clock import Clock, SystemClock
from app.core.config import Settings
from app.core.db import create_db_engine, run_migrations
from app.core.errors import register_error_handlers
from app.seed import seed_database

API_DESCRIPTION = """
There is no login: the brief assumes a logged-in user, so every request acts as the built-in learner.

Every error response has the shape `{"error": {"code", "message", "details"?}}`.
Times are ISO 8601 in UTC, for example `2026-10-08T12:25:00Z`.
A Markdown version of this reference is in `docs/API.md`.
"""


def create_app(settings: Settings | None = None, clock: Clock | None = None) -> FastAPI:
    """Build the API. Run with: uvicorn app.main:create_app --factory --reload"""
    settings = settings or Settings()
    clock = clock or SystemClock()
    engine = create_db_engine(settings.database_url)
    session_factory = sessionmaker(engine)

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        if settings.auto_migrate:
            run_migrations(engine)
        if settings.seed_on_startup:
            with session_factory() as db:
                seed_database(db, default_username=settings.default_username, now=clock.now())
        yield
        engine.dispose()

    app = FastAPI(
        title="Duolingo Clone API",
        version="0.1.0",
        description=API_DESCRIPTION,
        openapi_tags=[
            {"name": "me", "description": "The logged-in learner: profile, live stats and preferences."},
            {"name": "courses", "description": "The course catalogue and each course's learning path."},
            {"name": "path", "description": "Actions on path nodes."},
            {
                "name": "sessions",
                "description": "Playing a lesson: start it, answer each exercise, finish or quit.",
            },
            {
                "name": "leaderboard",
                "description": "Weekly leagues: this week's standings, and moving up or down a league.",
            },
            {"name": "health", "description": "Liveness check."},
        ],
        lifespan=lifespan,
    )
    app.state.settings = settings
    app.state.clock = clock
    app.state.session_factory = session_factory

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_error_handlers(app)
    app.include_router(health.router)
    app.include_router(api_router)
    return app
