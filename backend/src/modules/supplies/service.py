from datetime import datetime, timezone

from sqlmodel import Session, select

from src.bulk.parser import (
    RowError,
    name_key,
    optional_text,
    parse_datetime,
    parse_spreadsheet,
    required,
    run_bulk,
    safe_float,
)
from src.core.exceptions import ConflictError, NotFoundError
from src.core.schemas import BulkImportResult
from src.modules.supplies.models import Supply, SupplyCategory
from src.modules.supplies.schemas import (
    DeleteResponseSupply,
    SupplyCreate,
    SupplyUpdate,
)
from src.modules.units.models import Unit
from src.modules.users.models import User

BULK_SUPPLY_HEADERS = [
    "nombre",
    "descripcion",
    "categoria",
    "unidad",
    "stock_disponible",
    "stock_min",
    "stock_max",
    "fecha_vencimiento",
]
BULK_SUPPLY_EXAMPLES = [
    [
        "Harina de trigo",
        "Harina panadera tipo 550",
        "Insumos basicos",
        "kg",
        25,
        10,
        100,
        "2026-12-31",
    ],
]


class SuppliesService:
    def __init__(self, session: Session):
        self.session = session

    def create(self, data: SupplyCreate, current_user: User) -> Supply:
        category = self.session.get(SupplyCategory, data.category_id)
        if not category or category.status == "inactive":
            raise NotFoundError(
                f"La categoría con id '{data.category_id}' no existe."
            )

        unit = self.session.get(Unit, data.unit_id)
        if not unit or unit.deleted_at is not None:
            raise NotFoundError(f"La unidad con id '{data.unit_id}' no existe.")

        existing = self.session.exec(
            select(Supply).where(
                Supply.name == data.name,
                Supply.deleted_at == None,
            )
        ).first()
        if existing:
            raise ConflictError(
                f"Ya existe un insumo con el nombre '{data.name}'."
            )

        new_supply = Supply(
            name=data.name,
            description=data.description,
            category_id=data.category_id,
            unit_id=data.unit_id,
            available_quantity=data.available_quantity,
            min_stock=data.min_stock,
            max_stock=data.max_stock,
            supplier_id=data.supplier_id,
            expiration_date=data.expiration_date,
            created_by=current_user.id,
        )

        self.session.add(new_supply)
        self.session.commit()
        self.session.refresh(new_supply)
        return new_supply

    def list(self, skip: int = 0, limit: int = 20) -> list[Supply]:
        return self.session.exec(
            select(Supply).where(Supply.deleted_at == None).offset(skip).limit(limit)
        ).all()

    def get(self, supply_id: int) -> Supply:
        supply = self.session.get(Supply, supply_id)
        if not supply or supply.deleted_at is not None:
            raise NotFoundError(f"El insumo con id '{supply_id}' no existe.")
        return supply

    def update(self, supply_id: int, data: SupplyUpdate, current_user: User) -> Supply:
        supply = self.get(supply_id)

        if data.name and data.name != supply.name:
            existing = self.session.exec(
                select(Supply).where(
                    Supply.name == data.name,
                    Supply.id != supply_id,
                    Supply.deleted_at == None,
                )
            ).first()
            if existing:
                raise ConflictError(
                    f"Ya existe un insumo con el nombre '{data.name}'."
                )

        if data.category_id is not None:
            category = self.session.get(SupplyCategory, data.category_id)
            if not category or category.status == "inactive":
                raise NotFoundError(
                    f"La categoría con id '{data.category_id}' no existe."
                )

        if data.unit_id is not None:
            unit = self.session.get(Unit, data.unit_id)
            if not unit or unit.deleted_at is not None:
                raise NotFoundError(f"La unidad con id '{data.unit_id}' no existe.")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(supply, field, value)

        supply.updated_at = datetime.now(timezone.utc)
        supply.updated_by = current_user.id

        self.session.add(supply)
        self.session.commit()
        self.session.refresh(supply)
        return supply

    def delete(self, supply_id: int, current_user: User) -> DeleteResponseSupply:
        supply = self.session.get(Supply, supply_id)
        if not supply:
            raise NotFoundError(f"El insumo con id '{supply_id}' no existe.")

        if supply.deleted_at is not None:
            raise ConflictError(
                f"El insumo con id '{supply_id}' ya fue eliminado."
            )

        now = datetime.now(timezone.utc)
        supply.deleted_at = now
        supply.deleted_by = current_user.id
        supply.status = "inactive"

        self.session.add(supply)
        self.session.commit()

        return DeleteResponseSupply(
            message=f"Insumo '{supply.name}' eliminado correctamente.",
            deleted_at=now,
            deleted_by=current_user.id,
        )

    def bulk_import(self, file, current_user: User) -> BulkImportResult:
        rows = parse_spreadsheet(file)
        categories = {
            name_key(c.name): c
            for c in self.session.exec(select(SupplyCategory)).all()
            if c.status == "active"
        }
        units = {
            name_key(u.name): u
            for u in self.session.exec(select(Unit)).all()
            if u.deleted_at is None
        }
        units_abbr = {name_key(u.abbreviation): u for u in units.values()}

        def process_row(row):
            nombre = required(row, "nombre", "nombre")
            if len(nombre) > 150:
                raise RowError("El nombre supera los 150 caracteres.")
            descripcion = optional_text(row, "descripcion")
            categoria_name = required(row, "categoria", "categoria")
            unidad_name = required(row, "unidad", "unidad")

            category = categories.get(categoria_name)
            if category is None:
                raise RowError(f"No existe la categoría '{row.get('categoria')}'.")

            unit = units.get(unidad_name) or units_abbr.get(unidad_name)
            if unit is None:
                raise RowError(f"No existe la unidad '{row.get('unidad')}'.")

            existing = self.session.exec(
                select(Supply).where(
                    Supply.name == nombre, Supply.deleted_at == None
                )
            ).first()
            if existing:
                raise RowError(
                    f"Ya existe un insumo con el nombre '{row.get('nombre')}'."
                )

            new_supply = Supply(
                name=nombre,
                description=descripcion,
                category_id=category.id,
                unit_id=unit.id,
                available_quantity=safe_float(
                    row.get("stock_disponible"), "stock_disponible"
                ),
                min_stock=safe_float(row.get("stock_min"), "stock_min"),
                max_stock=safe_float(row.get("stock_max"), "stock_max"),
                supplier_id=None,
                expiration_date=parse_datetime(
                    row.get("fecha_vencimiento"), "fecha_vencimiento"
                ),
                created_by=current_user.id,
            )
            self.session.add(new_supply)
            return False

        return run_bulk(self.session, rows, process_row)
