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

    app = FastAPI(title="Duolingo Clone API", version="0.1.0", lifespan=lifespan)
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
