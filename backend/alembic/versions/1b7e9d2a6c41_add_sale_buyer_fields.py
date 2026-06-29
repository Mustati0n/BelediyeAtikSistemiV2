"""add sale buyer fields

Revision ID: 1b7e9d2a6c41
Revises: 00f31c245a1a
Create Date: 2026-06-13 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "1b7e9d2a6c41"
down_revision: str | None = "00f31c245a1a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("satis", sa.Column("alici_firma", sa.String(length=255), nullable=True))
    op.add_column("satis", sa.Column("belge_no", sa.String(length=120), nullable=True))


def downgrade() -> None:
    op.drop_column("satis", "belge_no")
    op.drop_column("satis", "alici_firma")
