"""add maintenance detail fields

Revision ID: 2c9a1b44d7f0
Revises: 1b7e9d2a6c41
Create Date: 2026-06-13 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "2c9a1b44d7f0"
down_revision: str | None = "1b7e9d2a6c41"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("bakimkaydi", sa.Column("bakim_turu", sa.String(length=80), nullable=True))
    op.add_column("bakimkaydi", sa.Column("oncelik", sa.String(length=40), nullable=True))
    op.add_column("bakimkaydi", sa.Column("parca_maliyeti_tl", sa.Numeric(12, 2), nullable=True))
    op.add_column("bakimkaydi", sa.Column("iscilik_maliyeti_tl", sa.Numeric(12, 2), nullable=True))
    op.add_column("bakimkaydi", sa.Column("tedarikci", sa.String(length=160), nullable=True))
    op.add_column("bakimkaydi", sa.Column("kilometre", sa.Integer(), nullable=True))
    op.add_column("bakimkaydi", sa.Column("planlanan_tarih", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("bakimkaydi", "planlanan_tarih")
    op.drop_column("bakimkaydi", "kilometre")
    op.drop_column("bakimkaydi", "tedarikci")
    op.drop_column("bakimkaydi", "iscilik_maliyeti_tl")
    op.drop_column("bakimkaydi", "parca_maliyeti_tl")
    op.drop_column("bakimkaydi", "oncelik")
    op.drop_column("bakimkaydi", "bakim_turu")
