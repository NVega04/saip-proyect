"""Crear la tabla ``audit_log`` para trazabilidad de acciones críticas.

La tabla es append-only a nivel de aplicación: no existen endpoints para
editar o borrar registros. ``old_value`` y ``new_value`` se almacenan como
JSON y el servicio de auditoría elimina contraseñas, hashes y tokens antes
de escribirlos. No se modifican migraciones ya aplicadas.

Revision ID: 898807c7b86f
Revises: 756185c644ac
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "898807c7b86f"
down_revision: Union[str, Sequence[str], None] = "756185c644ac"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "audit_log",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("resource_type", sa.String(length=100), nullable=False),
        sa.Column("resource_id", sa.Integer(), nullable=True),
        sa.Column("old_value", sa.JSON(), nullable=True),
        sa.Column("new_value", sa.JSON(), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_audit_log_action"), "audit_log", ["action"], unique=False
    )
    op.create_index(
        op.f("ix_audit_log_resource_id"),
        "audit_log",
        ["resource_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_audit_log_timestamp"), "audit_log", ["timestamp"], unique=False
    )
    op.create_index(
        op.f("ix_audit_log_user_id"), "audit_log", ["user_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_audit_log_user_id"), table_name="audit_log")
    op.drop_index(op.f("ix_audit_log_timestamp"), table_name="audit_log")
    op.drop_index(op.f("ix_audit_log_resource_id"), table_name="audit_log")
    op.drop_index(op.f("ix_audit_log_action"), table_name="audit_log")
    op.drop_table("audit_log")
