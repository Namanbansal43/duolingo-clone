"""Dark mode becomes a three-way choice (system, on, off), and the demo clock for "Advance a day".

Revision ID: 0007
Revises: 0006
Create Date: 2026-10-09
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0007"
down_revision: str | None = "0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("user_settings", schema=None) as batch_op:
        batch_op.alter_column("dark_mode", existing_type=sa.Boolean(), type_=sa.String(length=8))
    # Dark mode could not be changed before the settings page existed: a stored "off" was only the
    # default, so it becomes "system", the new default. "On" stays on.
    op.execute(
        "UPDATE user_settings SET dark_mode = CASE WHEN dark_mode IN ('1', 1) THEN 'on' ELSE 'system' END"
    )
    with op.batch_alter_table("user_settings", schema=None) as batch_op:
        batch_op.create_check_constraint(
            op.f("ck_user_settings_dark_mode_known"), "dark_mode IN ('system', 'on', 'off')"
        )

    op.create_table(
        "demo_clock",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("days_ahead", sa.Integer(), nullable=False),
        sa.CheckConstraint("days_ahead >= 0", name=op.f("ck_demo_clock_days_ahead_non_negative")),
        sa.CheckConstraint("id = 1", name=op.f("ck_demo_clock_single_row")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_demo_clock")),
    )


def downgrade() -> None:
    op.drop_table("demo_clock")
    with op.batch_alter_table("user_settings", schema=None) as batch_op:
        batch_op.drop_constraint(op.f("ck_user_settings_dark_mode_known"), type_="check")
    op.execute("UPDATE user_settings SET dark_mode = CASE WHEN dark_mode = 'on' THEN 1 ELSE 0 END")
    with op.batch_alter_table("user_settings", schema=None) as batch_op:
        batch_op.alter_column("dark_mode", existing_type=sa.String(length=8), type_=sa.Boolean())
