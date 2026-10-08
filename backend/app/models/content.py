from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Course(Base):
    """A language course, e.g. Spanish for English speakers. Units and lessons hang off this later."""

    __tablename__ = "courses"
    __table_args__ = (UniqueConstraint("learning_language", "from_language"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    learning_language: Mapped[str] = mapped_column(String(8))  # course code, also its flag: "es"
    from_language: Mapped[str] = mapped_column(String(8))  # language the course is taught in: "en"
    title: Mapped[str] = mapped_column(String(64))
    position: Mapped[int]  # display order in course pickers
    is_available: Mapped[bool]  # False = shown as "coming soon"
