from datetime import date, datetime
from io import BytesIO
from typing import Dict, Optional, Tuple

from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from sqlmodel import Session, func, select

from src.core.exceptions import BusinessRuleError, NotFoundError, ServerError
from src.core.time import BOGOTA_TZ
from src.modules.inventory.models import InventoryMovement, MovementType
from src.modules.products.models import Product
from src.modules.commercial_products.models import CommercialProduct
from src.modules.sales.models import ItemType, Sale, SaleItem, SaleStatus
from src.modules.sales.schemas import (
    SaleAnnulResponse,
    SaleCreate,
    SaleCreateResponse,
    SaleListPage,
    SaleListResponse,
    SaleResponse,
    StockWarning,
)
from src.modules.users.models import User
from src.utils.excel import (
    add_title_row,
    apply_data_row,
    apply_header_row,
    auto_width,
    fmt_dt,
)


def _sales_base_query(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    status_filter: Optional[SaleStatus] = None,
    item_type: Optional[ItemType] = None,
    item_id: Optional[int] = None,
):
    base = select(Sale).where(Sale.deleted_at == None)
    if date_from is not None:
        base = base.where(
            Sale.sale_date
            >= datetime.combine(date_from, datetime.min.time(), tzinfo=BOGOTA_TZ)
        )
    if date_to is not None:
        base = base.where(
            Sale.sale_date
            <= datetime.combine(date_to, datetime.max.time(), tzinfo=BOGOTA_TZ)
        )
    if status_filter is not None:
        base = base.where(Sale.status == status_filter)
    if item_type is not None or item_id is not None:
        item_query = select(SaleItem.sale_id)
        if item_type is not None:
            item_query = item_query.where(SaleItem.item_type == item_type)
        if item_id is not None:
            item_query = item_query.where(SaleItem.item_id == item_id)
        base = base.where(Sale.id.in_(item_query))
    return base


class SalesService:
    def __init__(self, session: Session):
        self.session = session

    def _get_item(self, item_type: ItemType, item_id: int):
        if item_type == ItemType.PRODUCT:
            item = self.session.get(Product, item_id)
        elif item_type == ItemType.COMMERCIAL:
            item = self.session.get(CommercialProduct, item_id)
        else:
            item = None
        if not item or item.deleted_at is not None:
            raise NotFoundError("Producto no encontrado")
        return item

    def _get_sale_or_404(self, sale_id: int) -> Sale:
        sale = self.session.get(Sale, sale_id)
        if not sale or sale.deleted_at is not None:
            raise NotFoundError("Venta no encontrada")
        return sale

    def create(self, data: SaleCreate, current_user: User) -> SaleCreateResponse:
        aggregated: Dict[Tuple[str, int], float] = {}
        for item in data.items:
            key = (item.item_type.value, item.item_id)
            aggregated[key] = aggregated.get(key, 0.0) + item.quantity

        validated: list[Tuple[ItemType, int, float, str]] = []
        for (type_value, item_id), quantity in aggregated.items():
            item_type = ItemType(type_value)
            product = self._get_item(item_type, item_id)
            if quantity > product.available_quantity:
                raise BusinessRuleError(
                    f"Stock insuficiente para '{product.name}': "
                    f"disponible {product.available_quantity}, solicitado {quantity}."
                )
            validated.append((item_type, item_id, quantity, product.name))

        try:
            sale = Sale(
                user_id=current_user.id,
                status=SaleStatus.COMPLETED,
                notes=data.notes,
                created_by=current_user.id,
            )
            self.session.add(sale)
            self.session.flush()

            warnings: list[StockWarning] = []
            for item_type, item_id, quantity, item_name in validated:
                product = self._get_item(item_type, item_id)
                stock_before = product.available_quantity
                product.available_quantity = stock_before - quantity
                self.session.add(product)

                sale_item = SaleItem(
                    sale_id=sale.id,
                    item_type=item_type,
                    item_id=item_id,
                    item_name=item_name,
                    quantity=quantity,
                )
                self.session.add(sale_item)

                movement = InventoryMovement(
                    item_type=item_type,
                    item_id=item_id,
                    movement_type=MovementType.SALE,
                    quantity=quantity,
                    stock_before=stock_before,
                    stock_after=product.available_quantity,
                    reference_type="sale",
                    reference_id=sale.id,
                    user_id=current_user.id,
                )
                self.session.add(movement)

                if product.available_quantity < product.min_stock:
                    warnings.append(
                        StockWarning(
                            item_type=item_type,
                            item_id=item_id,
                            item_name=item_name,
                            available_quantity=product.available_quantity,
                            min_stock=product.min_stock,
                        )
                    )

            self.session.commit()
        except Exception:
            self.session.rollback()
            raise ServerError("Error al registrar la venta. Intente nuevamente.")

        self.session.refresh(sale)
        return SaleCreateResponse(sale=sale, warnings=warnings)

    def list(
        self,
        date_from: Optional[date],
        date_to: Optional[date],
        status_filter: Optional[SaleStatus],
        item_type: Optional[ItemType],
        item_id: Optional[int],
        page: int,
        limit: int,
    ) -> SaleListPage:
        base = _sales_base_query(
            date_from=date_from,
            date_to=date_to,
            status_filter=status_filter,
            item_type=item_type,
            item_id=item_id,
        )

        total = len(self.session.exec(base).all())
        base = (
            base.order_by(Sale.sale_date.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        sales = self.session.exec(base).all()

        counts = {}
        if sales:
            rows = self.session.exec(
                select(
                    SaleItem.sale_id,
                    func.count(SaleItem.id),
                    func.coalesce(func.sum(SaleItem.quantity), 0.0),
                )
                .where(SaleItem.sale_id.in_([s.id for s in sales]))
                .group_by(SaleItem.sale_id)
            ).all()
            counts = {r[0]: (r[1], r[2]) for r in rows}

        items = []
        for sale in sales:
            item_count, total_quantity = counts.get(sale.id, (0, 0.0))
            items.append(
                SaleListResponse(
                    id=sale.id,
                    token=sale.token,
                    user_id=sale.user_id,
                    user=sale.user,
                    sale_date=sale.sale_date,
                    status=sale.status,
                    notes=sale.notes,
                    item_count=item_count,
                    total_quantity=total_quantity,
                    created_at=sale.created_at,
                )
            )

        return SaleListPage(items=items, total=total, page=page, limit=limit)

    def export(
        self,
        date_from: Optional[date],
        date_to: Optional[date],
        status_filter: Optional[SaleStatus],
    ) -> StreamingResponse:
        base = _sales_base_query(
            date_from=date_from, date_to=date_to, status_filter=status_filter
        ).order_by(Sale.sale_date.desc())
        sales = self.session.exec(base).all()

        headers = [
            "ID",
            "Fecha",
            "Vendedor",
            "Estado",
            "Notas",
            "Nro. Items",
            "Cantidad Total",
        ]

        wb = Workbook()
        ws = wb.active
        ws.title = "Ventas"
        ws.freeze_panes = "A3"

        apply_header_row(ws, headers)

        for i, sale in enumerate(sales, start=2):
            item_count = 0
            total_qty = 0.0
            if sale.items:
                for it in sale.items:
                    item_count += 1
                    total_qty += it.quantity
            seller = (
                f"{sale.user.first_name} {sale.user.last_name}".strip()
                if sale.user
                else "—"
            )
            apply_data_row(
                ws,
                i,
                [
                    sale.id,
                    fmt_dt(sale.sale_date),
                    seller,
                    sale.status.value,
                    sale.notes or "—",
                    item_count,
                    total_qty,
                ],
            )

        col_count = len(headers)
        add_title_row(
            ws,
            f"Reporte de Ventas — {datetime.now(BOGOTA_TZ).strftime('%Y-%m-%d %H:%M')}",
            col_count,
        )
        auto_width(ws, headers)

        stream = BytesIO()
        wb.save(stream)
        stream.seek(0)

        filename = f"ventas_{datetime.now(BOGOTA_TZ).strftime('%Y%m%d_%H%M%S')}.xlsx"
        return StreamingResponse(
            stream,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    def get(self, sale_id: int) -> SaleResponse:
        sale = self._get_sale_or_404(sale_id)
        _ = sale.items
        return sale

    def annul(self, sale_id: int, current_user: User) -> SaleAnnulResponse:
        sale = self._get_sale_or_404(sale_id)
        if sale.status != SaleStatus.COMPLETED:
            raise BusinessRuleError("La venta ya fue anulada.")

        items = sale.items
        try:
            for sale_item in items:
                product = self._get_item(sale_item.item_type, sale_item.item_id)
                stock_before = product.available_quantity
                product.available_quantity = stock_before + sale_item.quantity
                self.session.add(product)

                movement = InventoryMovement(
                    item_type=sale_item.item_type,
                    item_id=sale_item.item_id,
                    movement_type=MovementType.SALE_ANNULMENT,
                    quantity=sale_item.quantity,
                    stock_before=stock_before,
                    stock_after=product.available_quantity,
                    reference_type="sale",
                    reference_id=sale.id,
                    user_id=current_user.id,
                )
                self.session.add(movement)

            sale.status = SaleStatus.ANNULLED
            sale.updated_at = datetime.now(BOGOTA_TZ)
            sale.updated_by = current_user.id
            self.session.add(sale)
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise ServerError("Error al anular la venta. Intente nuevamente.")

        return SaleAnnulResponse(
            message="Venta anulada y stock restaurado.",
            id=sale.id,
            status=sale.status,
            changed_at=sale.updated_at,
            changed_by=current_user.id,
        )
