"""add salary payment description

Revision ID: 3a8d5d2f9c10
Revises: 2c9a1b44d7f0
Create Date: 2026-06-13 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "3a8d5d2f9c10"
down_revision: str | None = "2c9a1b44d7f0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("maasodeme", sa.Column("aciklama", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("maasodeme", "aciklama")
