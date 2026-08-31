"""merge_bulk_import_and_login_lockout

Revision ID: cd4e9f97101f
Revises: 59fbc25c12c6, 9bfa5c1e2d30
Create Date: 2026-08-31 02:01:52.220107

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cd4e9f97101f'
down_revision: Union[str, Sequence[str], None] = ('59fbc25c12c6', '9bfa5c1e2d30')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
