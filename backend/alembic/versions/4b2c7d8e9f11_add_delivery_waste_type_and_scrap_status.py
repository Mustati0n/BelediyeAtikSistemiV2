"""add delivery waste type and scrap status

Revision ID: 4b2c7d8e9f11
Revises: 3a8d5d2f9c10
Create Date: 2026-06-14 18:30:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "4b2c7d8e9f11"
down_revision: str | None = "3a8d5d2f9c10"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TYPE arac_durumu_enum ADD VALUE IF NOT EXISTS 'HURDA'")
    teslim_atik_tipi = sa.Enum(
        "PLASTIK",
        "CAM",
        "METAL",
        "KAGIT",
        "ORGANIK",
        "DIGER",
        name="teslim_atik_tipi_enum",
    )
    teslim_atik_tipi.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "tesisteslim",
        sa.Column("atik_tipi", teslim_atik_tipi, nullable=True),
    )


def downgrade() -> None:
    op.drop_column("tesisteslim", "atik_tipi")
    sa.Enum(name="teslim_atik_tipi_enum").drop(op.get_bind(), checkfirst=True)
