"""Path content, learner progress, activity history and achievements.

Adds the 14 remaining tables of the schema (see DATABASE.md) and users.streak_freezes.

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-09
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # users first: adding a CHECK makes SQLite rebuild the table, best done before anything references it.
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("streak_freezes", sa.Integer(), server_default=sa.text("0"), nullable=False)
        )
        batch_op.create_check_constraint(
            op.f("ck_users_streak_freezes_in_range"), "streak_freezes BETWEEN 0 AND 2"
        )

    op.create_table(
        "achievements",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("key", sa.String(length=32), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=64), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("metric", sa.String(length=32), nullable=False),
        sa.CheckConstraint(
            "metric IN ('streak', 'total_xp', 'lessons_completed', 'perfect_lessons')",
            name=op.f("ck_achievements_metric_known"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_achievements")),
        sa.UniqueConstraint("key", name=op.f("uq_achievements_key")),
    )
    op.create_table(
        "achievement_tiers",
        sa.Column("achievement_id", sa.Integer(), nullable=False),
        sa.Column("tier", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("threshold", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "tier >= 1 AND threshold > 0", name=op.f("ck_achievement_tiers_tier_and_threshold_positive")
        ),
        sa.ForeignKeyConstraint(
            ["achievement_id"],
            ["achievements.id"],
            name=op.f("fk_achievement_tiers_achievement_id_achievements"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("achievement_id", "tier", name=op.f("pk_achievement_tiers")),
    )
    op.create_table(
        "units",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=128), nullable=False),
        sa.ForeignKeyConstraint(
            ["course_id"], ["courses.id"], name=op.f("fk_units_course_id_courses"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_units")),
        sa.UniqueConstraint("course_id", "position", name=op.f("uq_units_course_id_position")),
    )
    op.create_table(
        "skills",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("unit_id", sa.Integer(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=128), nullable=False),
        sa.Column("kind", sa.String(length=16), nullable=False),
        sa.CheckConstraint("kind IN ('lesson', 'chest')", name=op.f("ck_skills_kind_known")),
        sa.ForeignKeyConstraint(
            ["unit_id"], ["units.id"], name=op.f("fk_skills_unit_id_units"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_skills")),
        sa.UniqueConstraint("unit_id", "position", name=op.f("uq_skills_unit_id_position")),
    )
    op.create_table(
        "user_achievements",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("achievement_id", sa.Integer(), nullable=False),
        sa.Column("tier", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("unlocked_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["achievement_id", "tier"],
            ["achievement_tiers.achievement_id", "achievement_tiers.tier"],
            name=op.f("fk_user_achievements_achievement_id_achievement_tiers"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_user_achievements_user_id_users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("user_id", "achievement_id", "tier", name=op.f("pk_user_achievements")),
    )
    op.create_table(
        "user_settings",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("sound_effects", sa.Boolean(), nullable=False),
        sa.Column("animations", sa.Boolean(), nullable=False),
        sa.Column("motivational_messages", sa.Boolean(), nullable=False),
        sa.Column("listening_exercises", sa.Boolean(), nullable=False),
        sa.Column("dark_mode", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_user_settings_user_id_users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("user_id", name=op.f("pk_user_settings")),
    )
    op.create_table(
        "lessons",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("skill_id", sa.Integer(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["skill_id"], ["skills.id"], name=op.f("fk_lessons_skill_id_skills"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_lessons")),
        sa.UniqueConstraint("skill_id", "position", name=op.f("uq_lessons_skill_id_position")),
    )
    op.create_table(
        "user_skill_progress",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("skill_id", sa.Integer(), nullable=False),
        sa.Column("lessons_completed", sa.Integer(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.CheckConstraint(
            "lessons_completed >= 0", name=op.f("ck_user_skill_progress_lessons_completed_non_negative")
        ),
        sa.ForeignKeyConstraint(
            ["skill_id"],
            ["skills.id"],
            name=op.f("fk_user_skill_progress_skill_id_skills"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_user_skill_progress_user_id_users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("user_id", "skill_id", name=op.f("pk_user_skill_progress")),
    )
    op.create_table(
        "exercises",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("lesson_id", sa.Integer(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(length=16), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=True),
        sa.Column("prompt_language", sa.String(length=8), nullable=True),
        sa.CheckConstraint(
            "type = 'match_pairs' OR prompt IS NOT NULL", name=op.f("ck_exercises_prompt_required")
        ),
        sa.CheckConstraint(
            "type IN ('multiple_choice', 'word_bank', 'match_pairs', 'fill_blank', 'type_answer')",
            name=op.f("ck_exercises_type_known"),
        ),
        sa.ForeignKeyConstraint(
            ["lesson_id"], ["lessons.id"], name=op.f("fk_exercises_lesson_id_lessons"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_exercises")),
        sa.UniqueConstraint("lesson_id", "position", name=op.f("uq_exercises_lesson_id_position")),
    )
    op.create_table(
        "lesson_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("lesson_id", sa.Integer(), nullable=False),
        sa.Column("mode", sa.String(length=16), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("mistakes", sa.Integer(), nullable=False),
        sa.Column("xp_earned", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "(status = 'in_progress') = (finished_at IS NULL)",
            name=op.f("ck_lesson_sessions_finished_matches_status"),
        ),
        sa.CheckConstraint("mode IN ('lesson', 'practice')", name=op.f("ck_lesson_sessions_mode_known")),
        sa.CheckConstraint(
            "status IN ('in_progress', 'completed', 'failed', 'abandoned')",
            name=op.f("ck_lesson_sessions_status_known"),
        ),
        sa.CheckConstraint(
            "mistakes >= 0 AND xp_earned >= 0", name=op.f("ck_lesson_sessions_counts_non_negative")
        ),
        sa.ForeignKeyConstraint(
            ["lesson_id"],
            ["lessons.id"],
            name=op.f("fk_lesson_sessions_lesson_id_lessons"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_lesson_sessions_user_id_users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_lesson_sessions")),
    )
    with op.batch_alter_table("lesson_sessions", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_lesson_sessions_user_id_started_at"), ["user_id", "started_at"], unique=False
        )

    op.create_table(
        "accepted_answers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("exercise_id", sa.Integer(), nullable=False),
        sa.Column("text", sa.String(length=255), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["exercise_id"],
            ["exercises.id"],
            name=op.f("fk_accepted_answers_exercise_id_exercises"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_accepted_answers")),
        sa.UniqueConstraint("exercise_id", "text", name=op.f("uq_accepted_answers_exercise_id_text")),
    )
    with op.batch_alter_table("accepted_answers", schema=None) as batch_op:
        batch_op.create_index(
            "ix_accepted_answers_one_primary",
            ["exercise_id"],
            unique=True,
            sqlite_where=sa.text("is_primary"),
        )

    op.create_table(
        "exercise_options",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("exercise_id", sa.Integer(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("text", sa.String(length=255), nullable=False),
        sa.Column("match_text", sa.String(length=255), nullable=True),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["exercise_id"],
            ["exercises.id"],
            name=op.f("fk_exercise_options_exercise_id_exercises"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_exercise_options")),
        sa.UniqueConstraint("exercise_id", "position", name=op.f("uq_exercise_options_exercise_id_position")),
    )
    with op.batch_alter_table("exercise_options", schema=None) as batch_op:
        batch_op.create_index(
            "ix_exercise_options_one_correct",
            ["exercise_id"],
            unique=True,
            sqlite_where=sa.text("is_correct"),
        )

    op.create_table(
        "session_answers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("exercise_id", sa.Integer(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("answered_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["exercise_id"],
            ["exercises.id"],
            name=op.f("fk_session_answers_exercise_id_exercises"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["lesson_sessions.id"],
            name=op.f("fk_session_answers_session_id_lesson_sessions"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_session_answers")),
    )
    with op.batch_alter_table("session_answers", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_session_answers_session_id"), ["session_id"], unique=False)

    op.create_table(
        "xp_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=True),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("source", sa.String(length=16), nullable=False),
        sa.Column("earned_at", sa.DateTime(), nullable=False),
        sa.Column("local_date", sa.Date(), nullable=False),
        sa.CheckConstraint(
            "source IN ('lesson', 'practice', 'chest', 'achievement')", name=op.f("ck_xp_events_source_known")
        ),
        sa.CheckConstraint("amount > 0", name=op.f("ck_xp_events_amount_positive")),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["lesson_sessions.id"],
            name=op.f("fk_xp_events_session_id_lesson_sessions"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_xp_events_user_id_users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_xp_events")),
    )
    with op.batch_alter_table("xp_events", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_xp_events_local_date"), ["local_date"], unique=False)
        batch_op.create_index(
            batch_op.f("ix_xp_events_user_id_local_date"), ["user_id", "local_date"], unique=False
        )


def downgrade() -> None:
    with op.batch_alter_table("xp_events", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_xp_events_user_id_local_date"))
        batch_op.drop_index(batch_op.f("ix_xp_events_local_date"))

    op.drop_table("xp_events")
    with op.batch_alter_table("session_answers", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_session_answers_session_id"))

    op.drop_table("session_answers")
    with op.batch_alter_table("exercise_options", schema=None) as batch_op:
        batch_op.drop_index("ix_exercise_options_one_correct", sqlite_where=sa.text("is_correct"))

    op.drop_table("exercise_options")
    with op.batch_alter_table("accepted_answers", schema=None) as batch_op:
        batch_op.drop_index("ix_accepted_answers_one_primary", sqlite_where=sa.text("is_primary"))

    op.drop_table("accepted_answers")
    with op.batch_alter_table("lesson_sessions", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_lesson_sessions_user_id_started_at"))

    op.drop_table("lesson_sessions")
    op.drop_table("exercises")
    op.drop_table("user_skill_progress")
    op.drop_table("lessons")
    op.drop_table("user_settings")
    op.drop_table("user_achievements")
    op.drop_table("skills")
    op.drop_table("units")
    op.drop_table("achievement_tiers")
    op.drop_table("achievements")

    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_constraint(op.f("ck_users_streak_freezes_in_range"), type_="check")
        batch_op.drop_column("streak_freezes")
