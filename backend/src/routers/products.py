from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime, timezone

from src.database import get_session
from src.models.models import Product, ProductStatus, User, Unit
from src.schemas.schemas import ProductCreate, ProductUpdate, ProductResponse
from src.dependencies import get_current_user

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/", response_model=list[ProductResponse], status_code=status.HTTP_200_OK)
def get_products(
    session: Session = Depends(get_session),
):
    products = session.exec(select(Product).where(Product.deleted_at == None)).all()
    return products


@router.get(
    "/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK
)
def get_product(
    product_id: int,
    session: Session = Depends(get_session),
):
    product = session.get(Product, product_id)
    if not product or product.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado",
        )
    return product


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    unit = session.get(Unit, product_data.unit_id)
    if not unit or unit.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unidad no encontrada",
        )

    existing = session.exec(
        select(Product).where(
            Product.name == product_data.name,
            Product.deleted_at == None,
        )
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un producto con ese nombre",
        )

    new_product = Product(
        name=product_data.name,
        description=product_data.description,
        unit_id=product_data.unit_id,
        available_quantity=product_data.available_quantity,
        min_stock=product_data.min_stock,
        max_stock=product_data.max_stock,
        is_locked=product_data.is_locked,
        status="active",
        created_by=current_user.id,
    )

    session.add(new_product)
    session.commit()
    session.refresh(new_product)

    return new_product


@router.patch(
    "/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK
)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    product = session.get(Product, product_id)
    if not product or product.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado",
        )

    if product.is_locked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El producto esta bloqueado y no puede ser modificado",
        )

    if product_data.name is not None and product_data.name != product.name:
        existing = session.exec(
            select(Product).where(
                Product.name == product_data.name,
                Product.id != product_id,
                Product.deleted_at == None,
            )
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un producto con ese nombre",
            )

    if product_data.unit_id is not None:
        unit = session.get(Unit, product_data.unit_id)
        if not unit or unit.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unidad no encontrada",
            )

    update_fields = product_data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(product, field, value)

    product.updated_at = datetime.now(timezone.utc)
    product.updated_by = current_user.id

    session.add(product)
    session.commit()
    session.refresh(product)

    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    product = session.get(Product, product_id)
    if not product or product.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado",
        )

    if product.is_locked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El producto esta bloqueado y no puede ser eliminado",
        )

    product.deleted_at = datetime.now(timezone.utc)
    product.deleted_by = current_user.id

    session.add(product)
    session.commit()

    return None


@router.patch(
    "/{product_id}/lock", response_model=ProductResponse, status_code=status.HTTP_200_OK
)
def toggle_product_lock(
    product_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    product = session.get(Product, product_id)
    if not product or product.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado",
        )

    product.is_locked = not product.is_locked
    product.updated_at = datetime.now(timezone.utc)
    product.updated_by = current_user.id

    session.add(product)
    session.commit()
    session.refresh(product)

    return product
