"""add started_at and cancelled_at to production_orders

Revision ID: c8d41f92ab73
Revises: 62d1217ec939
Create Date: 2026-08-22 10:15:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c8d41f92ab73"
down_revision: str | Sequence[str] | None = "62d1217ec939"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "production_orders",
        sa.Column("started_at", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "production_orders",
        sa.Column("cancelled_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("production_orders", "cancelled_at")
    op.drop_column("production_orders", "started_at")
