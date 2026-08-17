from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime
from zoneinfo import ZoneInfo

from src.database import get_session
from src.models.models import CommercialProduct, ProductCategory, Unit, Provider, User
from src.schemas.schemas import (
    CommercialProductCreate,
    CommercialProductUpdate,
    CommercialProductResponse,
    DeleteResponseCommercialProduct,
)
from src.dependencies import get_current_user

router = APIRouter(prefix="/commercial-products", tags=["CommercialProducts"])

BOGOTA_TZ = ZoneInfo("America/Bogota")


@router.get("/", response_model=list[CommercialProductResponse], status_code=status.HTTP_200_OK)
def get_all(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    return session.exec(select(CommercialProduct).where(CommercialProduct.deleted_at == None)).all()


@router.get("/{product_id}", response_model=CommercialProductResponse, status_code=status.HTTP_200_OK)
def get_one(product_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    product = session.get(CommercialProduct, product_id)
    if not product or product.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado.")
    return product


@router.post("/", response_model=CommercialProductResponse, status_code=status.HTTP_201_CREATED)
def create(data: CommercialProductCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    category = session.get(ProductCategory, data.category_id)
    if not category or category.status == "inactive":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"La categoría con id '{data.category_id}' no existe.")

    unit = session.get(Unit, data.unit_id)
    if not unit or unit.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"La unidad con id '{data.unit_id}' no existe.")

    if data.provider_id is not None:
        provider = session.get(Provider, data.provider_id)
        if not provider or provider.deleted_at is not None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"El proveedor con id '{data.provider_id}' no existe.")

    existing = session.exec(
        select(CommercialProduct).where(
            CommercialProduct.name == data.name,
            CommercialProduct.deleted_at == None,
        )
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Ya existe un producto con el nombre '{data.name}'.")

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
    session.add(new_product)
    session.commit()
    session.refresh(new_product)
    return new_product


@router.patch("/{product_id}", response_model=CommercialProductResponse, status_code=status.HTTP_200_OK)
def update(product_id: int, data: CommercialProductUpdate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    product = session.get(CommercialProduct, product_id)
    if not product or product.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado.")

    if data.name and data.name != product.name:
        existing = session.exec(
            select(CommercialProduct).where(
                CommercialProduct.name == data.name,
                CommercialProduct.id != product_id,
                CommercialProduct.deleted_at == None,
            )
        ).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Ya existe un producto con el nombre '{data.name}'.")

    if data.category_id is not None:
        category = session.get(ProductCategory, data.category_id)
        if not category or category.status == "inactive":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"La categoría con id '{data.category_id}' no existe.")

    if data.unit_id is not None:
        unit = session.get(Unit, data.unit_id)
        if not unit or unit.deleted_at is not None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"La unidad con id '{data.unit_id}' no existe.")

    if data.provider_id is not None:
        provider = session.get(Provider, data.provider_id)
        if not provider or provider.deleted_at is not None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"El proveedor con id '{data.provider_id}' no existe.")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(product, field, value)

    product.updated_at = datetime.now(BOGOTA_TZ)
    product.updated_by = current_user.id
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@router.delete("/{product_id}", response_model=DeleteResponseCommercialProduct, status_code=status.HTTP_200_OK)
def delete(product_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    product = session.get(CommercialProduct, product_id)
    if not product or product.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado.")

    now = datetime.now(BOGOTA_TZ)
    product.deleted_at = now
    product.deleted_by = current_user.id
    product.status = "inactive"
    session.add(product)
    session.commit()

    return DeleteResponseCommercialProduct(
        message=f"Producto '{product.name}' eliminado correctamente.",
        deleted_at=now,
        deleted_by=current_user.id,
    )