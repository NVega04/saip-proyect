from datetime import datetime
from typing import Literal

from sqlalchemy import func
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
from src.core.exceptions import ConflictError, NotFoundError
from src.core.pagination import Page, PaginationParams, like_pattern
from src.core.schemas import BulkImportResult
from src.core.time import BOGOTA_TZ
from src.modules.commercial_products.models import CommercialProduct, ProductCategory
from src.modules.commercial_products.schemas import (
    CommercialProductCreate,
    CommercialProductUpdate,
    DeleteResponseCommercialProduct,
)
from src.modules.providers.models import Provider
from src.modules.units.models import Unit
from src.modules.users.models import User

BULK_COMMERCIAL_HEADERS = [
    "nombre",
    "descripcion",
    "categoria",
    "unidad",
    "proveedor",
    "precio_compra",
    "precio_venta",
    "stock_disponible",
    "stock_min",
    "stock_max",
]
BULK_COMMERCIAL_EXAMPLES = [
    [
        "Palitos de ajonjoli",
        "Empaque x12",
        "Snacks",
        "paquete",
        "Distribuidora ABC",
        4200,
        6500,
        90,
        20,
        200,
    ],
]


class CommercialProductsService:
    def __init__(self, session: Session):
        self.session = session

    def list(
        self, pagination: PaginationParams, search: str | None = None
    ) -> Page[CommercialProduct]:
        filters = [CommercialProduct.deleted_at == None]  # noqa: E712
        if search and search.strip():
            pattern = like_pattern(search)
            filters.append(
                CommercialProduct.name.like(pattern)
                | CommercialProduct.description.like(pattern)
            )
        total = self.session.exec(
            select(func.count())
            .select_from(CommercialProduct)
            .where(*filters)
        ).one()
        rows = self.session.exec(
            select(CommercialProduct)
            .where(*filters)
            .order_by(CommercialProduct.id)
            .offset(pagination.offset)
            .limit(pagination.limit)
        ).all()
        return Page[CommercialProduct](
            items=rows,
            total=total,
            page=pagination.page,
            limit=pagination.limit,
        )

    def get(self, product_id: int) -> CommercialProduct:
        product = self.session.get(CommercialProduct, product_id)
        if not product or product.deleted_at is not None:
            raise NotFoundError("Producto no encontrado.")
        return product

    def create(
        self, data: CommercialProductCreate, current_user: User
    ) -> CommercialProduct:
        category = self.session.get(ProductCategory, data.category_id)
        if not category or category.status == "inactive":
            raise NotFoundError(
                f"La categoría con id '{data.category_id}' no existe."
            )

        unit = self.session.get(Unit, data.unit_id)
        if not unit or unit.deleted_at is not None:
            raise NotFoundError(f"La unidad con id '{data.unit_id}' no existe.")

        if data.provider_id is not None:
            provider = self.session.get(Provider, data.provider_id)
            if not provider or provider.deleted_at is not None:
                raise NotFoundError(
                    f"El proveedor con id '{data.provider_id}' no existe."
                )

        existing = self.session.exec(
            select(CommercialProduct).where(
                CommercialProduct.name == data.name,
                CommercialProduct.deleted_at == None,
            )
        ).first()
        if existing:
            raise ConflictError(
                f"Ya existe un producto con el nombre '{data.name}'."
            )

        new_product = CommercialProduct(
            name=data.name,
            description=data.description,
            category_id=data.category_id,
            unit_id=data.unit_id,
            provider_id=data.provider_id,
            purchase_price=data.purchase_price,
            sale_price=data.sale_price,
            available_quantity=data.available_quantity,
            min_stock=data.min_stock,
            max_stock=data.max_stock,
            created_by=current_user.id,
        )
        self.session.add(new_product)
        self.session.commit()
        self.session.refresh(new_product)
        return new_product

    def update(
        self, product_id: int, data: CommercialProductUpdate, current_user: User
    ) -> CommercialProduct:
        product = self.get(product_id)

        if data.name and data.name != product.name:
            existing = self.session.exec(
                select(CommercialProduct).where(
                    CommercialProduct.name == data.name,
                    CommercialProduct.id != product_id,
                    CommercialProduct.deleted_at == None,
                )
            ).first()
            if existing:
                raise ConflictError(
                    f"Ya existe un producto con el nombre '{data.name}'."
                )

        if data.category_id is not None:
            category = self.session.get(ProductCategory, data.category_id)
            if not category or category.status == "inactive":
                raise NotFoundError(
                    f"La categoría con id '{data.category_id}' no existe."
                )

        if data.unit_id is not None:
            unit = self.session.get(Unit, data.unit_id)
            if not unit or unit.deleted_at is not None:
                raise NotFoundError(f"La unidad con id '{data.unit_id}' no existe.")

        if data.provider_id is not None:
            provider = self.session.get(Provider, data.provider_id)
            if not provider or provider.deleted_at is not None:
                raise NotFoundError(
                    f"El proveedor con id '{data.provider_id}' no existe."
                )

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(product, field, value)

        product.updated_at = datetime.now(BOGOTA_TZ)
        product.updated_by = current_user.id
        self.session.add(product)
        self.session.commit()
        self.session.refresh(product)
        return product

    def delete(
        self, product_id: int, current_user: User
    ) -> DeleteResponseCommercialProduct:
        product = self.get(product_id)

        now = datetime.now(BOGOTA_TZ)
        product.deleted_at = now
        product.deleted_by = current_user.id
        product.status = "inactive"
        self.session.add(product)
        self.session.commit()

        return DeleteResponseCommercialProduct(
            message=f"Producto '{product.name}' eliminado correctamente.",
            deleted_at=now,
            deleted_by=current_user.id,
        )

    def bulk_import(
        self,
        mode: Literal["create", "upsert"],
        file,
        current_user: User,
    ) -> BulkImportResult:
        rows = parse_spreadsheet(file)
        categories = {
            name_key(c.name): c
            for c in self.session.exec(select(ProductCategory)).all()
            if c.status == "active" and c.deleted_at is None
        }
        units = {
            name_key(u.name): u
            for u in self.session.exec(select(Unit)).all()
            if u.deleted_at is None
        }
        units_abbr = {name_key(u.abbreviation): u for u in units.values()}
        providers = {
            name_key(p.company): p
            for p in self.session.exec(select(Provider)).all()
            if p.deleted_at is None and p.status == "active"
        }

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

            proveedor_value = row.get("proveedor")
            provider = None
            if proveedor_value is not None and str(proveedor_value).strip() != "":
                provider = providers.get(name_key(proveedor_value))
                if provider is None:
                    raise RowError(f"No existe el proveedor '{proveedor_value}'.")

            precio_compra = safe_float(row.get("precio_compra"), "precio_compra")
            precio_venta = safe_float(row.get("precio_venta"), "precio_venta")
            min_stock = safe_float(row.get("stock_min"), "stock_min")
            max_stock = safe_float(row.get("stock_max"), "stock_max")

            existing = self.session.exec(
                select(CommercialProduct).where(
                    CommercialProduct.name == nombre,
                    CommercialProduct.deleted_at == None,
                )
            ).first()

            if mode == "upsert" and existing:
                if descripcion is not None:
                    existing.description = descripcion
                existing.provider_id = provider.id if provider else None
                existing.purchase_price = precio_compra
                existing.sale_price = precio_venta
                existing.min_stock = min_stock
                existing.max_stock = max_stock
                existing.updated_at = datetime.now(BOGOTA_TZ)
                existing.updated_by = current_user.id
                self.session.add(existing)
                return True

            if existing:
                raise RowError(
                    f"Ya existe un producto con el nombre '{row.get('nombre')}'."
                )

            new_product = CommercialProduct(
                name=nombre,
                description=descripcion,
                category_id=category.id,
                unit_id=unit.id,
                provider_id=provider.id if provider else None,
                purchase_price=precio_compra,
                sale_price=precio_venta,
                available_quantity=safe_float(
                    row.get("stock_disponible"), "stock_disponible"
                ),
                min_stock=min_stock,
                max_stock=max_stock,
                created_by=current_user.id,
            )
            self.session.add(new_product)
            return False

        return run_bulk(self.session, rows, process_row)
