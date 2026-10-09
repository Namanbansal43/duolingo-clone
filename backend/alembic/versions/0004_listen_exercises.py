"""Allow "listen" exercises ("Tap what you hear").

Revision ID: 0004
Revises: 0003
Create Date: 2026-10-09
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

OLD_TYPES = "'multiple_choice', 'word_bank', 'match_pairs', 'fill_blank', 'type_answer'"


def upgrade() -> None:
    # SQLite can't alter a CHECK in place, so batch mode rebuilds the exercises table around it.
    with op.batch_alter_table("exercises", schema=None) as batch_op:
        batch_op.drop_constraint(op.f("ck_exercises_type_known"), type_="check")
        batch_op.create_check_constraint(op.f("ck_exercises_type_known"), f"type IN ({OLD_TYPES}, 'listen')")


def downgrade() -> None:
    # A listen exercise is a word bank whose prompt is heard instead of read; keep it, and its answers, as one.
    op.execute("UPDATE exercises SET type = 'word_bank' WHERE type = 'listen'")
    with op.batch_alter_table("exercises", schema=None) as batch_op:
        batch_op.drop_constraint(op.f("ck_exercises_type_known"), type_="check")
        batch_op.create_check_constraint(op.f("ck_exercises_type_known"), f"type IN ({OLD_TYPES})")
