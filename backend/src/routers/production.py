from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select
from datetime import datetime
from zoneinfo import ZoneInfo

from src.database import get_session
from src.models.models import (
    ProductionOrder,
    ProductionOrderStatus,
    Recipe,
    RecipeStatus,
    User,
)
from src.schemas.schemas import (
    ProductionOrderCreate,
    ProductionOrderCancelRequest,
    ProductionOrderResponse,
    ProductionOrderStatusChangeResponse,
)
from src.dependencies import get_current_user

router = APIRouter(prefix="/production/orders", tags=["Production"])

BOGOTA_TZ = ZoneInfo("America/Bogota")


def _get_order_or_404(order_id: int, session: Session) -> ProductionOrder:
    order = session.get(ProductionOrder, order_id)
    if not order or order.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orden de producción no encontrada.",
        )
    return order


@router.post("/", response_model=ProductionOrderResponse, status_code=status.HTTP_201_CREATED)
def create(data: ProductionOrderCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    recipe = session.get(Recipe, data.recipe_id)
    if not recipe or recipe.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"La receta con id '{data.recipe_id}' no existe.")
    if recipe.status != RecipeStatus.ACTIVE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"La receta '{recipe.name}' no está activa.")

    order = ProductionOrder(
        recipe_id=data.recipe_id,
        quantity_multiplier=data.quantity_multiplier,
        total_yield=recipe.yield_quantity * data.quantity_multiplier,
        scheduled_at=data.scheduled_at,
        notes=data.notes,
        status=ProductionOrderStatus.PENDING,
        created_by=current_user.id,
    )
    session.add(order)
    session.commit()
    session.refresh(order)
    return order


@router.get("/", response_model=list[ProductionOrderResponse], status_code=status.HTTP_200_OK)
def get_all(
    status_filter: Optional[ProductionOrderStatus] = Query(default=None, alias="status"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    query = select(ProductionOrder).where(ProductionOrder.deleted_at == None)
    if status_filter is not None:
        query = query.where(ProductionOrder.status == status_filter)
    return session.exec(query).all()


@router.get("/{order_id}", response_model=ProductionOrderResponse, status_code=status.HTTP_200_OK)
def get_one(order_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    return _get_order_or_404(order_id, session)


@router.patch("/{order_id}/start", response_model=ProductionOrderStatusChangeResponse, status_code=status.HTTP_200_OK)
def start(order_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    order = _get_order_or_404(order_id, session)
    if order.status != ProductionOrderStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Solo se pueden iniciar órdenes en estado 'pending' (estado actual: '{order.status.value}').",
        )

    now = datetime.now(BOGOTA_TZ)
    order.status = ProductionOrderStatus.IN_PROGRESS
    order.started_at = now
    order.updated_at = now
    order.updated_by = current_user.id
    session.add(order)
    session.commit()

    return ProductionOrderStatusChangeResponse(
        message=f"Orden de producción #{order.id} iniciada correctamente.",
        id=order.id,
        status=order.status,
        changed_at=now,
        changed_by=current_user.id,
    )


@router.patch("/{order_id}/cancel", response_model=ProductionOrderStatusChangeResponse, status_code=status.HTTP_200_OK)
def cancel(
    order_id: int,
    data: ProductionOrderCancelRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    order = _get_order_or_404(order_id, session)
    if order.status not in (ProductionOrderStatus.PENDING, ProductionOrderStatus.IN_PROGRESS):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Solo se pueden cancelar órdenes en estado 'pending' o 'in_progress' (estado actual: '{order.status.value}').",
        )

    now = datetime.now(BOGOTA_TZ)
    if data.reason:
        suffix = f"Motivo de cancelación: {data.reason}"
        order.notes = f"{order.notes} | {suffix}"[:500] if order.notes else suffix[:500]
    order.status = ProductionOrderStatus.CANCELLED
    order.cancelled_at = now
    order.updated_at = now
    order.updated_by = current_user.id
    session.add(order)
    session.commit()

    return ProductionOrderStatusChangeResponse(
        message=f"Orden de producción #{order.id} cancelada correctamente.",
        id=order.id,
        status=order.status,
        changed_at=now,
        changed_by=current_user.id,
    )
