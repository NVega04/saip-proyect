"""amplia enums movement_type e item_type de inventory_movements

Revision ID: 9bfa5c1e2d30
Revises: 9d8802c850be
Create Date: 2026-08-30

Agrega MovementType.ENTRY y MovementType.MANUAL al enum movement_type, y
ItemType.SUPPLY al enum item_type, para soportar cargas masivas de stock.
"""
from alembic import op

revision = "9bfa5c1e2d30"
down_revision = "9d8802c850be"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE inventory_movements MODIFY movement_type "
        "ENUM('SALE','SALE_ANNULMENT','ENTRY','MANUAL') NOT NULL"
    )
    op.execute(
        "ALTER TABLE inventory_movements MODIFY item_type "
        "ENUM('PRODUCT','COMMERCIAL','SUPPLY') NOT NULL"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE inventory_movements MODIFY movement_type "
        "ENUM('SALE','SALE_ANNULMENT') NOT NULL"
    )
    op.execute(
        "ALTER TABLE inventory_movements MODIFY item_type "
        "ENUM('PRODUCT','COMMERCIAL') NOT NULL"
    )