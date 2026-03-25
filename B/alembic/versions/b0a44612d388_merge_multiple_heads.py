"""merge multiple heads

Revision ID: b0a44612d388
Revises: 351115c260de, a1b2c3d4e5f6
Create Date: 2026-03-24 20:11:12.819354

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = 'b0a44612d388'
down_revision: Union[str, Sequence[str], None] = ('351115c260de', 'a1b2c3d4e5f6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
