from datetime import datetime, timezone
from typing import Literal

from sqlmodel import Session, select

from src.bulk.parser import (
    RowError,
    name_key,
    optional_text,
    parse_spreadsheet,
    required,
    run_bulk,
    safe_float,
)
from src.core.exceptions import ConflictError, NotFoundError, PermissionDeniedError
from src.core.schemas import BulkImportResult
from src.modules.products.models import Product
from src.modules.products.schemas import ProductCreate, ProductUpdate
from src.modules.units.models import Unit
from src.modules.users.models import User

BULK_PRODUCT_HEADERS = [
    "nombre",
    "descripcion",
    "unidad",
    "stock_disponible",
    "stock_min",
    "stock_max",
]
BULK_PRODUCT_EXAMPLES = [
    ["Pan frances", "Pan artesanal de 250g", "unidad", 120, 20, 300],
]


class ProductsService:
    def __init__(self, session: Session):
        self.session = session

    def list(self) -> list[Product]:
        return self.session.exec(
            select(Product).where(Product.deleted_at == None)
        ).all()

    def get(self, product_id: int) -> Product:
        product = self.session.get(Product, product_id)
        if not product or product.deleted_at is not None:
            raise NotFoundError("Producto no encontrado")
        return product

    def create(self, data: ProductCreate, current_user: User) -> Product:
        unit = self.session.get(Unit, data.unit_id)
        if not unit or unit.deleted_at is not None:
            raise NotFoundError("Unidad no encontrada")

        existing = self.session.exec(
            select(Product).where(
                Product.name == data.name,
                Product.deleted_at == None,
            )
        ).first()
        if existing:
            raise ConflictError("Ya existe un producto con ese nombre")

        new_product = Product(
            name=data.name,
            description=data.description,
            unit_id=data.unit_id,
            available_quantity=data.available_quantity,
            min_stock=data.min_stock,
            max_stock=data.max_stock,
            is_locked=data.is_locked,
            status="active",
            created_by=current_user.id,
        )

        self.session.add(new_product)
        self.session.commit()
        self.session.refresh(new_product)
        return new_product

    def update(
        self, product_id: int, data: ProductUpdate, current_user: User
    ) -> Product:
        product = self.get(product_id)

        if product.is_locked:
            raise PermissionDeniedError(
                "El producto esta bloqueado y no puede ser modificado"
            )

        if data.name is not None and data.name != product.name:
            existing = self.session.exec(
                select(Product).where(
                    Product.name == data.name,
                    Product.id != product_id,
                    Product.deleted_at == None,
                )
            ).first()
            if existing:
                raise ConflictError("Ya existe un producto con ese nombre")

        if data.unit_id is not None:
            unit = self.session.get(Unit, data.unit_id)
            if not unit or unit.deleted_at is not None:
                raise NotFoundError("Unidad no encontrada")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(product, field, value)

        product.updated_at = datetime.now(timezone.utc)
        product.updated_by = current_user.id

        self.session.add(product)
        self.session.commit()
        self.session.refresh(product)
        return product

    def delete(self, product_id: int, current_user: User) -> None:
        product = self.get(product_id)

        if product.is_locked:
            raise PermissionDeniedError(
                "El producto esta bloqueado y no puede ser eliminado"
            )

        product.deleted_at = datetime.now(timezone.utc)
        product.deleted_by = current_user.id

        self.session.add(product)
        self.session.commit()

    def toggle_lock(self, product_id: int, current_user: User) -> Product:
        product = self.get(product_id)

        product.is_locked = not product.is_locked
        product.updated_at = datetime.now(timezone.utc)
        product.updated_by = current_user.id

        self.session.add(product)
        self.session.commit()
        self.session.refresh(product)
        return product

    def bulk_import(
        self, mode: Literal["create", "upsert"], file, current_user: User
    ) -> BulkImportResult:
        rows = parse_spreadsheet(file)
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
            unidad_name = required(row, "unidad", "unidad")

            unit = units.get(unidad_name) or units_abbr.get(unidad_name)
            if unit is None:
                raise RowError(f"No existe la unidad '{row.get('unidad')}'.")

            existing = self.session.exec(
                select(Product).where(
                    Product.name == nombre, Product.deleted_at == None
                )
            ).first()

            min_stock = safe_float(row.get("stock_min"), "stock_min")
            max_stock = safe_float(row.get("stock_max"), "stock_max")

            if mode == "upsert" and existing:
                if existing.is_locked:
                    raise RowError(
                        f"El producto '{row.get('nombre')}' esta bloqueado y no puede ser modificado."
                    )
                if descripcion is not None:
                    existing.description = descripcion
                existing.min_stock = min_stock
                existing.max_stock = max_stock
                existing.updated_at = datetime.now(timezone.utc)
                existing.updated_by = current_user.id
                self.session.add(existing)
                return True

            if existing:
                raise RowError(
                    f"Ya existe un producto con el nombre '{row.get('nombre')}'."
                )

            new_product = Product(
                name=nombre,
                description=descripcion,
                unit_id=unit.id,
                available_quantity=safe_float(
                    row.get("stock_disponible"), "stock_disponible"
                ),
                min_stock=min_stock,
                max_stock=max_stock,
                is_locked=False,
                status="active",
                created_by=current_user.id,
            )
            self.session.add(new_product)
            return False

        return run_bulk(self.session, rows, process_row)
