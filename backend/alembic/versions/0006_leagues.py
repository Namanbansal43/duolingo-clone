"""Weekly leagues: leagues, league_memberships and the seeded rivals.

Revision ID: 0006
Revises: 0005
Create Date: 2026-10-09
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0006"
down_revision: str | None = "0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "leagues",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=32), nullable=False),
        sa.Column("promotion_count", sa.Integer(), nullable=False),
        sa.Column("demotion_count", sa.Integer(), nullable=False),
        sa.CheckConstraint("position >= 1", name=op.f("ck_leagues_position_positive")),
        sa.CheckConstraint(
            "promotion_count >= 0 AND demotion_count >= 0", name=op.f("ck_leagues_zones_non_negative")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_leagues")),
        sa.UniqueConstraint("name", name=op.f("uq_leagues_name")),
        sa.UniqueConstraint("position", name=op.f("uq_leagues_position")),
    )
    op.create_table(
        "rivals",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("daily_xp", sa.Integer(), nullable=False),
        sa.Column("active_days", sa.Integer(), nullable=False),
        sa.Column("simulated_until", sa.DateTime(), nullable=False),
        sa.CheckConstraint("active_days BETWEEN 1 AND 7", name=op.f("ck_rivals_active_days_in_week")),
        sa.CheckConstraint("daily_xp > 0", name=op.f("ck_rivals_daily_xp_positive")),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_rivals_user_id_users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("user_id", name=op.f("pk_rivals")),
    )
    op.create_table(
        "league_memberships",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("week_start", sa.Date(), nullable=False),
        sa.Column("league_id", sa.Integer(), nullable=False),
        sa.Column("joined_at", sa.DateTime(), nullable=False),
        sa.Column("final_rank", sa.Integer(), nullable=True),
        sa.CheckConstraint(
            "final_rank IS NULL OR final_rank >= 1", name=op.f("ck_league_memberships_final_rank_positive")
        ),
        sa.ForeignKeyConstraint(
            ["league_id"],
            ["leagues.id"],
            name=op.f("fk_league_memberships_league_id_leagues"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_league_memberships_user_id_users"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("user_id", "week_start", name=op.f("pk_league_memberships")),
    )
    with op.batch_alter_table("league_memberships", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_league_memberships_week_start_league_id"),
            ["week_start", "league_id"],
            unique=False,
        )


def downgrade() -> None:
    with op.batch_alter_table("league_memberships", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_league_memberships_week_start_league_id"))

    op.drop_table("league_memberships")
    op.drop_table("rivals")
    op.drop_table("leagues")
