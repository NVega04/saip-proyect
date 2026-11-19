"""Agregar las 6 foreign keys de auditoría ausentes en las migraciones.

Los modelos SQLModel declaran ``updated_by`` y ``deleted_by`` como FK a
``users.id`` en ``commercial_products``, ``product_categories`` y ``sales``,
pero las migraciones históricas nunca crearon esas restricciones. Esto hace
que ``alembic check`` detecte cambios y que una BD creada solo con migraciones
no tenga la misma integridad referencial que una creada desde la metadata.

Se verificó antes de escribir la migración que no existen filas huérfanas en
ninguna de las 6 columnas, por lo que agregar las restricciones no requiere
limpieza de datos. No se modifica ninguna migración ya aplicada.
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "756185c644ac"
down_revision: Union[str, Sequence[str], None] = "cd4e9f97101f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

FOREIGN_KEYS = (
    ("fk_commercial_product_updated_by", "commercial_products", "updated_by"),
    ("fk_commercial_product_deleted_by", "commercial_products", "deleted_by"),
    ("fk_product_category_updated_by", "product_categories", "updated_by"),
    ("fk_product_category_deleted_by", "product_categories", "deleted_by"),
    ("fk_sale_updated_by", "sales", "updated_by"),
    ("fk_sale_deleted_by", "sales", "deleted_by"),
)


def upgrade() -> None:
    for name, table, column in FOREIGN_KEYS:
        op.create_foreign_key(
            name,
            table,
            "users",
            [column],
            ["id"],
            use_alter=True,
        )


def downgrade() -> None:
    for name, table, _column in reversed(FOREIGN_KEYS):
        op.drop_constraint(name, table, type_="foreignkey")
