"""Cifrar NIT y teléfonos, con índice ciego para el NIT.

Los valores existentes se cifran en la propia migración y se conserva la
unicidad mediante un HMAC del NIT normalizado (``nit_hash``). La columna
cifrada deja de ser única porque el mismo texto plano produce ciphertexts
distintos. La migración es reversible: el downgrade descifra los valores.

Requiere ``ENCRYPTION_KEY``: perder la clave imposibilita recuperar los datos.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.core.crypto import blind_index, fernet

# revision identifiers, used by Alembic.
revision: str = "6ef9e1aec914"
down_revision: Union[str, Sequence[str], None] = "898807c7b86f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

PHONE_COLUMNS = (
    ("users", "phone"),
    ("provider_contacts", "phone"),
)


def _encrypt_table(table: str, column: str) -> None:
    connection = op.get_bind()
    rows = connection.execute(
        sa.text(f"SELECT id, {column} FROM {table} WHERE {column} IS NOT NULL")
    ).fetchall()
    for row_id, value in rows:
        if not value:
            continue
        connection.execute(
            sa.text(f"UPDATE {table} SET {column} = :value WHERE id = :id"),
            {"value": fernet.encrypt(str(value).encode()).decode(), "id": row_id},
        )


def _decrypt_table(table: str, column: str) -> None:
    connection = op.get_bind()
    rows = connection.execute(
        sa.text(f"SELECT id, {column} FROM {table} WHERE {column} IS NOT NULL")
    ).fetchall()
    for row_id, value in rows:
        if not value:
            continue
        connection.execute(
            sa.text(f"UPDATE {table} SET {column} = :value WHERE id = :id"),
            {"value": fernet.decrypt(str(value).encode()).decode(), "id": row_id},
        )


def upgrade() -> None:
    op.add_column("providers", sa.Column("nit_hash", sa.String(64), nullable=True))
    op.drop_index("ix_providers_nit", table_name="providers")
    op.alter_column(
        "providers",
        "nit",
        existing_type=sa.String(20),
        type_=sa.String(255),
        existing_nullable=False,
    )
    for table, column in PHONE_COLUMNS:
        op.alter_column(
            table,
            column,
            existing_type=sa.String(20),
            type_=sa.String(255),
            existing_nullable=True,
        )

    # Los datos se cifran después de ampliar las columnas para no truncarlos.
    _encrypt_table("providers", "nit")
    for table, column in PHONE_COLUMNS:
        _encrypt_table(table, column)

    connection = op.get_bind()
    for row_id, nit in connection.execute(
        sa.text("SELECT id, nit FROM providers")
    ).fetchall():
        connection.execute(
            sa.text("UPDATE providers SET nit_hash = :value WHERE id = :id"),
            {"value": blind_index(fernet.decrypt(nit.encode()).decode()), "id": row_id},
        )

    op.create_index(
        "ix_providers_nit_hash", "providers", ["nit_hash"], unique=True
    )
    op.alter_column(
        "providers",
        "nit_hash",
        existing_type=sa.String(64),
        nullable=False,
    )


def downgrade() -> None:
    _decrypt_table("providers", "nit")
    for table, column in PHONE_COLUMNS:
        _decrypt_table(table, column)

    op.alter_column(
        "providers",
        "nit_hash",
        existing_type=sa.String(64),
        nullable=True,
    )
    op.drop_index("ix_providers_nit_hash", table_name="providers")
    op.drop_column("providers", "nit_hash")

    op.alter_column(
        "providers",
        "nit",
        existing_type=sa.String(255),
        type_=sa.String(20),
        existing_nullable=False,
    )
    op.create_index("ix_providers_nit", "providers", ["nit"], unique=True)
    for table, column in PHONE_COLUMNS:
        op.alter_column(
            table,
            column,
            existing_type=sa.String(255),
            type_=sa.String(20),
            existing_nullable=True,
        )
