"""Course content: courses > units > skills (path nodes) > lessons > exercises.

Seeded once and read-only at runtime. Deleting a row deletes everything beneath it, unless a
learner has already answered one of its exercises (see app.models.activity).
"""

from enum import StrEnum

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy import text as sql_text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, one_of


class SkillKind(StrEnum):
    LESSON = "lesson"  # a node with lessons to play
    CHEST = "chest"  # a treasure chest that pays out gems
    REVIEW = "review"  # the trophy that ends a unit: lessons mixing everything in it


class ExerciseType(StrEnum):
    MULTIPLE_CHOICE = "multiple_choice"
    WORD_BANK = "word_bank"
    MATCH_PAIRS = "match_pairs"
    FILL_BLANK = "fill_blank"
    TYPE_ANSWER = "type_answer"
    LISTEN = "listen"  # "Tap what you hear": the prompt is read aloud, the learner rebuilds it from tiles


class Course(Base):
    """A language course, e.g. Spanish for English speakers."""

    __tablename__ = "courses"
    __table_args__ = (UniqueConstraint("learning_language", "from_language"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    learning_language: Mapped[str] = mapped_column(String(8))  # course code, also its flag: "es"
    from_language: Mapped[str] = mapped_column(String(8))  # language the course is taught in: "en"
    title: Mapped[str] = mapped_column(String(64))
    position: Mapped[int]  # display order in course pickers
    is_available: Mapped[bool]  # False = shown as "coming soon"

    units: Mapped[list["Unit"]] = relationship(
        back_populates="course", order_by="Unit.position", cascade="all, delete-orphan", passive_deletes=True
    )


class Unit(Base):
    """A themed block of the path, shown with a coloured header: "Unit 1 · Order food and drink"."""

    __tablename__ = "units"
    __table_args__ = (UniqueConstraint("course_id", "position"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"))
    position: Mapped[int]
    title: Mapped[str] = mapped_column(String(128))

    course: Mapped[Course] = relationship(back_populates="units")
    skills: Mapped[list["Skill"]] = relationship(
        back_populates="unit", order_by="Skill.position", cascade="all, delete-orphan", passive_deletes=True
    )


class Skill(Base):
    """One node on the learning path. Lesson nodes are played lesson by lesson; chests are opened once."""

    __tablename__ = "skills"
    __table_args__ = (
        UniqueConstraint("unit_id", "position"),
        CheckConstraint(one_of("kind", SkillKind), name="kind_known"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    unit_id: Mapped[int] = mapped_column(ForeignKey("units.id", ondelete="CASCADE"))
    position: Mapped[int]
    title: Mapped[str] = mapped_column(String(128))
    kind: Mapped[str] = mapped_column(String(16), default=SkillKind.LESSON)

    unit: Mapped[Unit] = relationship(back_populates="skills")
    lessons: Mapped[list["Lesson"]] = relationship(
        back_populates="skill", order_by="Lesson.position", cascade="all, delete-orphan", passive_deletes=True
    )


class Lesson(Base):
    """One playable lesson of a skill ("Lesson 2 of 4")."""

    __tablename__ = "lessons"
    __table_args__ = (UniqueConstraint("skill_id", "position"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"))
    position: Mapped[int]

    skill: Mapped[Skill] = relationship(back_populates="lessons")
    exercises: Mapped[list["Exercise"]] = relationship(
        back_populates="lesson",
        order_by="Exercise.position",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Exercise(Base):
    """One challenge in a lesson. How each type uses options and accepted answers:

    multiple_choice, fill_blank  options are the choices, exactly one is_correct
    word_bank, listen            options are the tiles (distractors included); accepted_answers grade it
    type_answer                  accepted_answers only
    match_pairs                  each option is one pair: text <-> match_text; no prompt
    """

    __tablename__ = "exercises"
    __table_args__ = (
        UniqueConstraint("lesson_id", "position"),
        CheckConstraint(one_of("type", ExerciseType), name="type_known"),
        CheckConstraint(f"type = '{ExerciseType.MATCH_PAIRS}' OR prompt IS NOT NULL", name="prompt_required"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"))
    position: Mapped[int]
    type: Mapped[str] = mapped_column(String(16))
    prompt: Mapped[str | None] = mapped_column(Text)  # "Hola, soy Ana." or "Yo ___ agua."
    prompt_language: Mapped[str | None] = mapped_column(String(8))  # picks the instruction and the TTS voice

    lesson: Mapped[Lesson] = relationship(back_populates="exercises")
    options: Mapped[list["ExerciseOption"]] = relationship(
        back_populates="exercise",
        order_by="ExerciseOption.position",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    accepted_answers: Mapped[list["AcceptedAnswer"]] = relationship(
        back_populates="exercise", cascade="all, delete-orphan", passive_deletes=True
    )


class ExerciseOption(Base):
    """A choice, a word tile, or a matching pair, depending on the exercise type."""

    __tablename__ = "exercise_options"
    __table_args__ = (
        UniqueConstraint("exercise_id", "position"),
        # At most one correct choice per exercise (a partial unique index: only is_correct rows count).
        Index(
            "ix_exercise_options_one_correct", "exercise_id", unique=True, sqlite_where=sql_text("is_correct")
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id", ondelete="CASCADE"))
    position: Mapped[int]
    text: Mapped[str] = mapped_column(String(255))
    match_text: Mapped[str | None] = mapped_column(String(255))  # match_pairs only: the other half
    is_correct: Mapped[bool] = mapped_column(default=False)

    exercise: Mapped[Exercise] = relationship(back_populates="options")


class AcceptedAnswer(Base):
    """A correct answer for word_bank, listen and type_answer. Grading normalises case, punctuation and
    spacing; the primary answer is the one shown as "Correct solution"."""

    __tablename__ = "accepted_answers"
    __table_args__ = (
        UniqueConstraint("exercise_id", "text"),
        Index(
            "ix_accepted_answers_one_primary", "exercise_id", unique=True, sqlite_where=sql_text("is_primary")
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id", ondelete="CASCADE"))
    text: Mapped[str] = mapped_column(String(255))
    is_primary: Mapped[bool] = mapped_column(default=False)

    exercise: Mapped[Exercise] = relationship(back_populates="accepted_answers")
