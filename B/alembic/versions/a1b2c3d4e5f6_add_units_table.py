"""add units table

Revision ID: a1b2c3d4e5f6
Revises: fe1534ddc01c
Create Date: 2026-03-23 10:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
import sqlmodel


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "fe1534ddc01c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "units",
        sa.Column("id", mysql.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("token", mysql.VARCHAR(length=255), nullable=False),
        sa.Column("name", mysql.VARCHAR(length=100), nullable=False),
        sa.Column("abbreviation", mysql.VARCHAR(length=20), nullable=False),
        sa.Column("description", mysql.VARCHAR(length=255), nullable=True),
        sa.Column("quantity", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("created_by", mysql.INTEGER(), autoincrement=False, nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("updated_by", mysql.INTEGER(), autoincrement=False, nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_by", mysql.INTEGER(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(
            ["created_by"], ["users.id"], name=op.f("units_ibfk_1")
        ),
        sa.ForeignKeyConstraint(
            ["updated_by"], ["users.id"], name=op.f("units_ibfk_2")
        ),
        sa.ForeignKeyConstraint(
            ["deleted_by"], ["users.id"], name=op.f("units_ibfk_3")
        ),
        sa.PrimaryKeyConstraint("id"),
        mysql_collate="utf8mb4_0900_ai_ci",
        mysql_default_charset="utf8mb4",
        mysql_engine="InnoDB",
    )
    op.create_index(op.f("ix_units_token"), "units", ["token"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_units_token"), table_name="units")
    op.drop_table("units")
