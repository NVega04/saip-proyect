from datetime import datetime
from io import BytesIO
from typing import Optional

from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from sqlmodel import Session, col, select

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
from src.core.exceptions import BusinessRuleError, ConflictError, NotFoundError
from src.core.schemas import BulkImportResult
from src.core.time import BOGOTA_TZ
from src.modules.production.models import (
    ProductionOrder,
    ProductionOrderSnapshot,
    ProductionOrderStatus,
)
from src.modules.production.schemas import (
    ProductionCompleteResponse,
    ProductionOrderCancelRequest,
    ProductionOrderCreate,
    ProductionOrderStatusChangeResponse,
    ProductionSnapshotResponse,
)
from src.modules.products.models import Product
from src.modules.recipes.models import Recipe, RecipeIngredient, RecipeStatus
from src.modules.supplies.models import Supply
from src.modules.supplies.schemas import SupplyBasic
from src.modules.units.schemas import UnitBasic
from src.modules.users.models import User
from src.utils.excel import (
    add_title_row,
    apply_data_row,
    apply_header_row,
    auto_width,
    fmt_dt,
)

BULK_ORDER_HEADERS = ["receta", "multiplicador", "programada_para", "notas"]
BULK_ORDER_EXAMPLES = [["Pan frances", 4, "2026-08-31", "Turno manana"]]


class ProductionService:
    def __init__(self, session: Session):
        self.session = session

    def _get_order_or_404(self, order_id: int) -> ProductionOrder:
        order = self.session.get(ProductionOrder, order_id)
        if not order or order.deleted_at is not None:
            raise NotFoundError("Orden de producción no encontrada.")
        return order

    def create(self, data: ProductionOrderCreate, current_user: User) -> ProductionOrder:
        recipe = self.session.get(Recipe, data.recipe_id)
        if not recipe or recipe.deleted_at is not None:
            raise NotFoundError(
                f"La receta con id '{data.recipe_id}' no existe."
            )
        if recipe.status != RecipeStatus.ACTIVE:
            raise BusinessRuleError(f"La receta '{recipe.name}' no está activa.")

        order = ProductionOrder(
            recipe_id=data.recipe_id,
            quantity_multiplier=data.quantity_multiplier,
            total_yield=recipe.yield_quantity * data.quantity_multiplier,
            scheduled_at=data.scheduled_at,
            notes=data.notes,
            status=ProductionOrderStatus.PENDING,
            created_by=current_user.id,
        )
        self.session.add(order)
        self.session.commit()
        self.session.refresh(order)
        return order

    def list(
        self, status_filter: Optional[ProductionOrderStatus]
    ) -> list[ProductionOrder]:
        query = select(ProductionOrder).where(ProductionOrder.deleted_at == None)
        if status_filter is not None:
            query = query.where(ProductionOrder.status == status_filter)
        return self.session.exec(query).all()

    def export_orders(
        self, status_filter: Optional[ProductionOrderStatus]
    ) -> StreamingResponse:
        query = (
            select(ProductionOrder)
            .where(ProductionOrder.deleted_at == None)
            .order_by(ProductionOrder.created_at.desc())
        )
        if status_filter is not None:
            query = query.where(ProductionOrder.status == status_filter)
        orders = self.session.exec(query).all()

        headers = [
            "ID",
            "Receta",
            "Multiplicador",
            "Rendimiento Total",
            "Estado",
            "Programada",
            "Iniciada",
            "Completada",
            "Notas",
            "Creada",
        ]

        wb = Workbook()
        ws = wb.active
        ws.title = "Ordenes Produccion"
        ws.freeze_panes = "A3"

        apply_header_row(ws, headers)

        for i, order in enumerate(orders, start=2):
            recipe = order.recipe.name if order.recipe else "—"
            apply_data_row(
                ws,
                i,
                [
                    order.id,
                    recipe,
                    order.quantity_multiplier,
                    order.total_yield,
                    order.status.value,
                    fmt_dt(order.scheduled_at),
                    fmt_dt(order.started_at),
                    fmt_dt(order.completed_at),
                    order.notes or "—",
                    fmt_dt(order.created_at),
                ],
            )

        col_count = len(headers)
        add_title_row(
            ws,
            f"Reporte de Órdenes de Producción — {datetime.now(BOGOTA_TZ).strftime('%Y-%m-%d %H:%M')}",
            col_count,
        )
        auto_width(ws, headers)

        stream = BytesIO()
        wb.save(stream)
        stream.seek(0)

        filename = f"ordenes_produccion_{datetime.now(BOGOTA_TZ).strftime('%Y%m%d_%H%M%S')}.xlsx"
        return StreamingResponse(
            stream,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    def get(self, order_id: int) -> ProductionOrder:
        return self._get_order_or_404(order_id)

    def start(
        self, order_id: int, current_user: User
    ) -> ProductionOrderStatusChangeResponse:
        order = self._get_order_or_404(order_id)
        if order.status != ProductionOrderStatus.PENDING:
            raise ConflictError(
                f"Solo se pueden iniciar órdenes en estado 'pending' (estado actual: '{order.status.value}')."
            )

        now = datetime.now(BOGOTA_TZ)
        order.status = ProductionOrderStatus.IN_PROGRESS
        order.started_at = now
        order.updated_at = now
        order.updated_by = current_user.id
        self.session.add(order)
        self.session.commit()

        return ProductionOrderStatusChangeResponse(
            message=f"Orden de producción #{order.id} iniciada correctamente.",
            id=order.id,
            status=order.status,
            changed_at=now,
            changed_by=current_user.id,
        )

    def cancel(
        self,
        order_id: int,
        data: ProductionOrderCancelRequest,
        current_user: User,
    ) -> ProductionOrderStatusChangeResponse:
        order = self._get_order_or_404(order_id)
        if order.status not in (
            ProductionOrderStatus.PENDING,
            ProductionOrderStatus.IN_PROGRESS,
        ):
            raise ConflictError(
                f"Solo se pueden cancelar órdenes en estado 'pending' o 'in_progress' (estado actual: '{order.status.value}')."
            )

        now = datetime.now(BOGOTA_TZ)
        if data.reason:
            suffix = f"Motivo de cancelación: {data.reason}"
            order.notes = (
                f"{order.notes} | {suffix}"[:500] if order.notes else suffix[:500]
            )
        order.status = ProductionOrderStatus.CANCELLED
        order.cancelled_at = now
        order.updated_at = now
        order.updated_by = current_user.id
        self.session.add(order)
        self.session.commit()

        return ProductionOrderStatusChangeResponse(
            message=f"Orden de producción #{order.id} cancelada correctamente.",
            id=order.id,
            status=order.status,
            changed_at=now,
            changed_by=current_user.id,
        )

    def complete(
        self, order_id: int, current_user: User
    ) -> ProductionCompleteResponse:
        order = self._get_order_or_404(order_id)

        if order.status != ProductionOrderStatus.IN_PROGRESS:
            raise ConflictError(
                f"Solo se pueden completar órdenes en estado 'in_progress' (estado actual: '{order.status.value}')."
            )

        recipe = self.session.get(Recipe, order.recipe_id)
        if not recipe or recipe.deleted_at is not None:
            raise NotFoundError(
                f"La receta con id '{order.recipe_id}' no existe."
            )
        if recipe.status != RecipeStatus.ACTIVE:
            raise BusinessRuleError(f"La receta '{recipe.name}' no está activa.")

        if order.quantity_multiplier <= 0:
            raise BusinessRuleError(
                "El multiplicador de cantidad de la orden debe ser mayor a 0."
            )

        ingredients = self.session.exec(
            select(RecipeIngredient).where(RecipeIngredient.recipe_id == recipe.id)
        ).all()
        if not ingredients:
            raise BusinessRuleError(
                f"La receta '{recipe.name}' no tiene ingredientes definidos."
            )

        unit_mismatches = []
        for ing in ingredients:
            ing_supply = self.session.get(Supply, ing.supply_id)
            if not ing_supply or ing_supply.deleted_at is not None:
                unit_mismatches.append(
                    f"{ing_supply.name if ing_supply else f'Insumo #{ing.supply_id}'} (insumo inexistente o eliminado)"
                )
            elif ing.unit_id != ing_supply.unit_id:
                unit_mismatches.append(
                    f"{ing_supply.name} (receta en unidad id {ing.unit_id}, inventario en unidad id {ing_supply.unit_id})"
                )
        if unit_mismatches:
            raise BusinessRuleError(
                "Unidades inconsistentes entre la receta y el inventario: "
                + "; ".join(unit_mismatches)
                + ". Corrige las unidades antes de completar la producción."
            )

        supply_ids = sorted({ing.supply_id for ing in ingredients})
        locked_supplies = self.session.exec(
            select(Supply)
            .where(col(Supply.id).in_(supply_ids))
            .with_for_update()
            .order_by(col(Supply.id))
        ).all()
        supply_by_id = {s.id: s for s in locked_supplies}

        supply_info_by_id: dict[int, tuple[SupplyBasic, UnitBasic]] = {}
        for s in locked_supplies:
            assert s.unit is not None
            supply_info_by_id[s.id] = (
                SupplyBasic(
                    id=s.id, token=s.token, name=s.name, status=s.status
                ),
                UnitBasic(
                    id=s.unit.id,
                    name=s.unit.name,
                    abbreviation=s.unit.abbreviation,
                ),
            )

        insufficient = []
        required_by_supply: dict[int, float] = {}
        for ing in ingredients:
            supply = supply_by_id[ing.supply_id]
            required = ing.quantity * order.quantity_multiplier
            required_by_supply[supply.id] = (
                required_by_supply.get(supply.id, 0) + required
            )
        for supply_id in supply_ids:
            supply = supply_by_id[supply_id]
            required = required_by_supply[supply_id]
            if required > supply.available_quantity:
                insufficient.append(
                    f"{supply.name} (requiere {required} {supply.unit.abbreviation if supply.unit else ''}, disponible {supply.available_quantity} {supply.unit.abbreviation if supply.unit else ''})".strip()
                )
        if insufficient:
            raise BusinessRuleError(
                "Stock insuficiente para completar la producción. Faltantes: "
                + "; ".join(insufficient)
                + "."
            )

        snapshots: list[ProductionOrderSnapshot] = []
        now = datetime.now(BOGOTA_TZ)
        for ing in ingredients:
            supply = supply_by_id[ing.supply_id]
            required = required_by_supply[supply.id]
            stock_before = supply.available_quantity
            supply.available_quantity -= required
            snapshots.append(
                ProductionOrderSnapshot(
                    production_order_id=order.id,
                    supply_id=supply.id,
                    quantity_used=required,
                    unit_id=ing.unit_id,
                    stock_before=stock_before,
                    stock_after=supply.available_quantity,
                )
            )
            self.session.add(supply)

        product_name: Optional[str] = None
        product_quantity_added: Optional[float] = None
        product: Optional[Product] = None
        if recipe.product_id is not None:
            candidate = self.session.get(Product, recipe.product_id)
            if candidate and candidate.deleted_at is None:
                product = candidate
                product.available_quantity += order.total_yield
                product.updated_at = now
                product.updated_by = current_user.id
                product_name = product.name
                product_quantity_added = order.total_yield
                self.session.add(product)

        order.status = ProductionOrderStatus.COMPLETED
        order.completed_at = now
        order.updated_at = now
        order.updated_by = current_user.id
        self.session.add(order)

        for snapshot in snapshots:
            self.session.add(snapshot)

        self.session.commit()

        completed_snapshots = [
            ProductionSnapshotResponse(
                id=sn.id,
                supply_id=sn.supply_id,
                supply=supply_info_by_id[sn.supply_id][0],
                quantity_used=sn.quantity_used,
                unit_id=sn.unit_id,
                unit=supply_info_by_id[sn.supply_id][1],
                stock_before=sn.stock_before,
                stock_after=sn.stock_after,
            )
            for sn in snapshots
        ]

        return ProductionCompleteResponse(
            message=f"Orden de producción #{order.id} completada correctamente. Se descontaron {len(completed_snapshots)} insumo(s).",
            id=order.id,
            status=order.status,
            total_yield=order.total_yield,
            completed_at=now,
            product_id=product.id if product else None,
            product_name=product_name,
            product_quantity_added=product_quantity_added,
            snapshots=completed_snapshots,
            completed_by=current_user.id,
        )

    def bulk_import(self, file, current_user: User) -> BulkImportResult:
        rows = parse_spreadsheet(file)
        recipes = {
            name_key(r.name): r
            for r in self.session.exec(select(Recipe)).all()
            if r.status == RecipeStatus.ACTIVE and r.deleted_at is None
        }

        def process_row(row):
            recipe_name = required(row, "receta", "receta")
            recipe = recipes.get(recipe_name)
            if recipe is None:
                raise RowError(
                    f"No existe la receta activa '{row.get('receta')}'."
                )

            multiplicador = safe_float(
                row.get("multiplicador"), "multiplicador"
            )
            if multiplicador <= 0:
                raise RowError("El multiplicador debe ser mayor a 0.")

            self.session.add(
                ProductionOrder(
                    recipe_id=recipe.id,
                    quantity_multiplier=multiplicador,
                    total_yield=recipe.yield_quantity * multiplicador,
                    scheduled_at=parse_datetime(
                        row.get("programada_para"), "programada_para"
                    ),
                    notes=optional_text(row, "notas"),
                    status=ProductionOrderStatus.PENDING,
                    created_by=current_user.id,
                )
            )
            return False

        return run_bulk(self.session, rows, process_row)
