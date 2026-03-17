"""sessions add session_id and token

Revision ID: c1c21037a648
Revises: 3d4131aa3b0c
Create Date: 2026-03-15 23:30:22.722084

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = 'c1c21037a648'
down_revision: Union[str, Sequence[str], None] = '3d4131aa3b0c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Agregamos la columna primero (porque no existe)
    op.add_column('sessions', sa.Column('token', sqlmodel.sql.sqltypes.AutoString(), nullable=False))
    
    # 2. Reordenar las columnas (esto moverá la columna recién creada a su posición)
    op.execute("ALTER TABLE sessions MODIFY COLUMN token VARCHAR(36) NOT NULL AFTER id")
    op.execute("ALTER TABLE sessions MODIFY COLUMN id INT NOT NULL AUTO_INCREMENT FIRST")


def downgrade() -> None:
    # Eliminamos la columna que agregamos en el upgrade
    op.drop_column('sessions', 'token')