from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import text

from app.deps import DbSession

router = APIRouter(tags=["health"])


class HealthOut(BaseModel):
    status: Literal["ok"]


@router.get("/api/health", response_model=HealthOut)
def health(db: DbSession) -> HealthOut:
    """Liveness check: answers only if the API can reach the database."""
    db.execute(text("SELECT 1"))
    return HealthOut(status="ok")
