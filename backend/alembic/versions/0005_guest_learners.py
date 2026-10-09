"""Mark learners who started over through "Get started" as guests until they create a profile.

Revision ID: 0005
Revises: 0004
Create Date: 2026-10-09
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(sa.Column("is_guest", sa.Boolean(), server_default=sa.text("0"), nullable=False))


def downgrade() -> None:
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("is_guest")
