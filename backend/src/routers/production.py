from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, col, select
from datetime import datetime
from zoneinfo import ZoneInfo

from src.database import get_session
from src.models.models import (
    ProductionOrder,
    ProductionOrderSnapshot,
    ProductionOrderStatus,
    Product,
    Recipe,
    RecipeIngredient,
    RecipeStatus,
    Supply,
    User,
)
from src.schemas.schemas import (
    ProductionOrderCreate,
    ProductionOrderCancelRequest,
    ProductionOrderResponse,
    ProductionOrderStatusChangeResponse,
    ProductionCompleteResponse,
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


@router.post("/{order_id}/complete", response_model=ProductionCompleteResponse, status_code=status.HTTP_200_OK)
def complete(order_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    order = _get_order_or_404(order_id, session)

    # RN-067: solo se ejecuta con orden previamente confirmada (in_progress).
    if order.status != ProductionOrderStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Solo se pueden completar órdenes en estado 'in_progress' (estado actual: '{order.status.value}').",
        )

    # RN-068: la receta debe existir, no estar eliminada y estar activa.
    recipe = session.get(Recipe, order.recipe_id)
    if not recipe or recipe.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"La receta con id '{order.recipe_id}' no existe.")
    if recipe.status != RecipeStatus.ACTIVE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"La receta '{recipe.name}' no está activa.")

    if order.quantity_multiplier <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El multiplicador de cantidad de la orden debe ser mayor a 0.",
        )

    ingredients = session.exec(
        select(RecipeIngredient).where(RecipeIngredient.recipe_id == recipe.id)
    ).all()
    if not ingredients:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La receta '{recipe.name}' no tiene ingredientes definidos.",
        )

    # La unidad del ingrediente debe coincidir con la unidad del insumo:
    # sin tabla de conversión, descontar con unidades distintas corrompería el stock.
    unit_mismatches = []
    for ing in ingredients:
        ing_supply = session.get(Supply, ing.supply_id)
        if not ing_supply or ing_supply.deleted_at is not None:
            unit_mismatches.append(f"{ing_supply.name if ing_supply else f'Insumo #{ing.supply_id}'} (insumo inexistente o eliminado)")
        elif ing.unit_id != ing_supply.unit_id:
            unit_mismatches.append(f"{ing_supply.name} (receta en unidad id {ing.unit_id}, inventario en unidad id {ing_supply.unit_id})")
    if unit_mismatches:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unidades inconsistentes entre la receta y el inventario: " + "; ".join(unit_mismatches) + ". Corrige las unidades antes de completar la producción.",
        )

    # Bloqueo pesimista de filas (SELECT ... FOR UPDATE) sobre los insumos
    # involucrados, en orden determinista por id para evitar deadlocks. Esto
    # serializa confirmaciones concurrentes que comparten insumos y cierra la
    # ventana entre la validación de stock y el descuento (RN-069/RN-070).
    supply_ids = sorted({ing.supply_id for ing in ingredients})
    locked_supplies = session.exec(
        select(Supply).where(col(Supply.id).in_(supply_ids)).with_for_update().order_by(col(Supply.id))
    ).all()
    supply_by_id = {s.id: s for s in locked_supplies}

    # Validación completa de stock ANTES de mutar nada: si falta cualquier
    # insumo se aborta toda la operación sin descuentos parciales.
    insufficient = []
    required_by_supply: dict[int, float] = {}
    for ing in ingredients:
        supply = supply_by_id[ing.supply_id]
        required = ing.quantity * order.quantity_multiplier
        required_by_supply[supply.id] = required_by_supply.get(supply.id, 0) + required
    for supply_id in supply_ids:
        supply = supply_by_id[supply_id]
        required = required_by_supply[supply_id]
        if required > supply.available_quantity:
            insufficient.append(f"{supply.name} (requiere {required} {supply.unit.abbreviation if supply.unit else ''}, disponible {supply.available_quantity} {supply.unit.abbreviation if supply.unit else ''})".strip())
    if insufficient:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stock insuficiente para completar la producción. Faltantes: " + "; ".join(insufficient) + ".",
        )

    # Descuento + snapshot por cada insumo (RN-071).
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
        session.add(supply)

    # Incremento del producto terminado asociado a la receta (si existe).
    product_name: Optional[str] = None
    product_quantity_added: Optional[float] = None
    product: Optional[Product] = None
    if recipe.product_id is not None:
        product = session.get(Product, recipe.product_id)
        if product and product.deleted_at is None:
            product.available_quantity += order.total_yield
            product.updated_at = now
            product.updated_by = current_user.id
            product_name = product.name
            product_quantity_added = order.total_yield
            session.add(product)

    # Estado final de la orden + auditoría (CA-012.4).
    order.status = ProductionOrderStatus.COMPLETED
    order.completed_at = now
    order.updated_at = now
    order.updated_by = current_user.id
    session.add(order)

    for snapshot in snapshots:
        session.add(snapshot)

    # Un único commit: si algo falla antes de aquí, no se descuenta nada.
    session.commit()

    return ProductionCompleteResponse(
        message=f"Orden de producción #{order.id} completada correctamente. Se descontaron {len(snapshots)} insumo(s).",
        id=order.id,
        status=order.status,
        total_yield=order.total_yield,
        completed_at=now,
        product_id=product.id if product else None,
        product_name=product_name,
        product_quantity_added=product_quantity_added,
        snapshots=snapshots,
        completed_by=current_user.id,
    )
