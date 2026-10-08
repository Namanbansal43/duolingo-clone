from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Runtime configuration, read from environment variables or backend/.env."""

    model_config = SettingsConfigDict(env_file=BACKEND_DIR / ".env", extra="ignore")

    database_url: str = f"sqlite:///{(BACKEND_DIR / 'data' / 'app.db').as_posix()}"
    cors_origins: list[str] = ["http://localhost:3000"]

    # The brief assumes one logged-in learner; every request acts as this seeded user.
    default_username: str = "alex"

    # Real Duolingo refills a heart every few hours; a short interval keeps the demo testable.
    heart_regen_minutes: int = 30

    # Bring the schema up to date and insert missing seed data when the app starts.
    auto_migrate: bool = True
    seed_on_startup: bool = True
