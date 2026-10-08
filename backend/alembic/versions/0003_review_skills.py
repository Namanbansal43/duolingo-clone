"""Allow "review" path nodes (the trophy that ends each unit).

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-09
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # SQLite can't alter a CHECK in place, so batch mode rebuilds the skills table around it.
    with op.batch_alter_table("skills", schema=None) as batch_op:
        batch_op.drop_constraint(op.f("ck_skills_kind_known"), type_="check")
        batch_op.create_check_constraint(
            op.f("ck_skills_kind_known"), "kind IN ('lesson', 'chest', 'review')"
        )


def downgrade() -> None:
    # Review nodes become plain lesson nodes rather than being deleted with their history.
    op.execute("UPDATE skills SET kind = 'lesson' WHERE kind = 'review'")
    with op.batch_alter_table("skills", schema=None) as batch_op:
        batch_op.drop_constraint(op.f("ck_skills_kind_known"), type_="check")
        batch_op.create_check_constraint(op.f("ck_skills_kind_known"), "kind IN ('lesson', 'chest')")
