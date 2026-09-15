"""merge multiple heads

Revision ID: b0a44612d388
Revises: 351115c260de, a1b2c3d4e5f6
Create Date: 2026-03-24 20:11:12.819354

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "b0a44612d388"
down_revision: str | Sequence[str] | None = ("351115c260de", "a1b2c3d4e5f6")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""


def downgrade() -> None:
    """Downgrade schema."""
