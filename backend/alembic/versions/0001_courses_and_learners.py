"""Courses and learners.

Revision ID: 0001
Revises:
Create Date: 2026-10-08
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "courses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("learning_language", sa.String(length=8), nullable=False),
        sa.Column("from_language", sa.String(length=8), nullable=False),
        sa.Column("title", sa.String(length=64), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("is_available", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_courses")),
        sa.UniqueConstraint(
            "learning_language", "from_language", name=op.f("uq_courses_learning_language_from_language")
        ),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=32), nullable=False),
        sa.Column("display_name", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("timezone", sa.String(length=64), nullable=False),
        sa.Column("active_course_id", sa.Integer(), nullable=True),
        sa.Column("daily_goal_xp", sa.Integer(), nullable=False),
        sa.Column("total_xp", sa.Integer(), nullable=False),
        sa.Column("gems", sa.Integer(), nullable=False),
        sa.Column("hearts", sa.Integer(), nullable=False),
        sa.Column("max_hearts", sa.Integer(), nullable=False),
        sa.Column("hearts_updated_at", sa.DateTime(), nullable=False),
        sa.Column("current_streak", sa.Integer(), nullable=False),
        sa.Column("longest_streak", sa.Integer(), nullable=False),
        sa.Column("last_streak_date", sa.Date(), nullable=True),
        sa.CheckConstraint("daily_goal_xp IN (10, 20, 30, 50)", name=op.f("ck_users_daily_goal_option")),
        sa.CheckConstraint("total_xp >= 0", name=op.f("ck_users_total_xp_non_negative")),
        sa.CheckConstraint("gems >= 0", name=op.f("ck_users_gems_non_negative")),
        sa.CheckConstraint(
            "max_hearts > 0 AND hearts BETWEEN 0 AND max_hearts", name=op.f("ck_users_hearts_in_range")
        ),
        sa.CheckConstraint(
            "current_streak >= 0 AND longest_streak >= current_streak", name=op.f("ck_users_streak_valid")
        ),
        sa.ForeignKeyConstraint(
            ["active_course_id"],
            ["courses.id"],
            name=op.f("fk_users_active_course_id_courses"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("username", name=op.f("uq_users_username")),
    )


def downgrade() -> None:
    op.drop_table("users")
    op.drop_table("courses")
