from typing import Optional, Dict, Tuple
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select, func
from datetime import datetime, date
from zoneinfo import ZoneInfo

from src.database import get_session
from src.models.models import (
    Sale,
    SaleItem,
    InventoryMovement,
    SaleStatus,
    ItemType,
    MovementType,
    Product,
    CommercialProduct,
    User,
)
from src.schemas.schemas import (
    SaleCreate,
    SaleResponse,
    SaleListResponse,
    SaleListPage,
    SaleCreateResponse,
    SaleAnnulResponse,
    StockWarning,
)
from src.dependencies import get_current_user

router = APIRouter(prefix="/sales", tags=["Sales"])

BOGOTA_TZ = ZoneInfo("America/Bogota")


def _get_item(item_type: ItemType, item_id: int, session: Session):
    if item_type == ItemType.PRODUCT:
        item = session.get(Product, item_id)
    elif item_type == ItemType.COMMERCIAL:
        item = session.get(CommercialProduct, item_id)
    else:
        item = None
    if not item or item.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado",
        )
    return item


def _get_sale_or_404(sale_id: int, session: Session) -> Sale:
    sale = session.get(Sale, sale_id)
    if not sale or sale.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venta no encontrada",
        )
    return sale


@router.post(
    "/", response_model=SaleCreateResponse, status_code=status.HTTP_201_CREATED
)
def create_sale(
    data: SaleCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    aggregated: Dict[Tuple[str, int], float] = {}
    for item in data.items:
        key = (item.item_type.value, item.item_id)
        aggregated[key] = aggregated.get(key, 0.0) + item.quantity

    validated: list[Tuple[ItemType, int, float, str]] = []
    for (type_value, item_id), quantity in aggregated.items():
        item_type = ItemType(type_value)
        product = _get_item(item_type, item_id, session)
        if quantity > product.available_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Stock insuficiente para '{product.name}': "
                    f"disponible {product.available_quantity}, solicitado {quantity}."
                ),
            )
        validated.append((item_type, item_id, quantity, product.name))

    try:
        sale = Sale(
            user_id=current_user.id,
            status=SaleStatus.COMPLETED,
            notes=data.notes,
            created_by=current_user.id,
        )
        session.add(sale)
        session.flush()

        warnings: list[StockWarning] = []
        for item_type, item_id, quantity, item_name in validated:
            product = _get_item(item_type, item_id, session)
            stock_before = product.available_quantity
            product.available_quantity = stock_before - quantity
            session.add(product)

            sale_item = SaleItem(
                sale_id=sale.id,
                item_type=item_type,
                item_id=item_id,
                item_name=item_name,
                quantity=quantity,
            )
            session.add(sale_item)

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
            session.add(movement)

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

        session.commit()
    except Exception:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al registrar la venta. Intente nuevamente.",
        )

    session.refresh(sale)
    return SaleCreateResponse(sale=sale, warnings=warnings)


@router.get("/", response_model=SaleListPage, status_code=status.HTTP_200_OK)
def get_sales(
    date_from: Optional[date] = Query(default=None),
    date_to: Optional[date] = Query(default=None),
    status_filter: Optional[SaleStatus] = Query(default=None, alias="status"),
    item_type: Optional[ItemType] = Query(default=None),
    item_id: Optional[int] = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=1, le=200),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    base = select(Sale).where(Sale.deleted_at == None)
    if date_from is not None:
        base = base.where(Sale.sale_date >= datetime.combine(date_from, datetime.min.time(), tzinfo=BOGOTA_TZ))
    if date_to is not None:
        base = base.where(Sale.sale_date <= datetime.combine(date_to, datetime.max.time(), tzinfo=BOGOTA_TZ))
    if status_filter is not None:
        base = base.where(Sale.status == status_filter)
    if item_type is not None or item_id is not None:
        item_query = select(SaleItem.sale_id)
        if item_type is not None:
            item_query = item_query.where(SaleItem.item_type == item_type)
        if item_id is not None:
            item_query = item_query.where(SaleItem.item_id == item_id)
        base = base.where(Sale.id.in_(item_query))

    total = len(session.exec(base).all())
    base = base.order_by(Sale.sale_date.desc()).offset((page - 1) * limit).limit(limit)
    sales = session.exec(base).all()

    counts = {}
    if sales:
        rows = session.exec(
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


@router.get(
    "/{sale_id}", response_model=SaleResponse, status_code=status.HTTP_200_OK
)
def get_sale(
    sale_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    sale = _get_sale_or_404(sale_id, session)
    _ = sale.items
    return sale


@router.patch(
    "/{sale_id}/annul", response_model=SaleAnnulResponse, status_code=status.HTTP_200_OK
)
def annul_sale(
    sale_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    sale = _get_sale_or_404(sale_id, session)
    if sale.status != SaleStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La venta ya fue anulada.",
        )

    items = sale.items
    try:
        for sale_item in items:
            product = _get_item(sale_item.item_type, sale_item.item_id, session)
            stock_before = product.available_quantity
            product.available_quantity = stock_before + sale_item.quantity
            session.add(product)

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
            session.add(movement)

        sale.status = SaleStatus.ANNULLED
        sale.updated_at = datetime.now(BOGOTA_TZ)
        sale.updated_by = current_user.id
        session.add(sale)
        session.commit()
    except Exception:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al anular la venta. Intente nuevamente.",
        )

    return SaleAnnulResponse(
        message="Venta anulada y stock restaurado.",
        id=sale.id,
        status=sale.status,
        changed_at=sale.updated_at,
        changed_by=current_user.id,
    )