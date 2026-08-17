from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime
from zoneinfo import ZoneInfo

from src.database import get_session
from src.models.models import Recipe, RecipeIngredient, Unit, Supply, User
from src.schemas.schemas import (
    RecipeCreate,
    RecipeUpdate,
    RecipeResponse,
    RecipeIngredientCreate,
    DeleteResponseRecipe,
)
from src.dependencies import get_current_user

router = APIRouter(prefix="/recipes", tags=["Recipes"])

BOGOTA_TZ = ZoneInfo("America/Bogota")


def _load_ingredients(recipe_id: int, session: Session) -> list[RecipeIngredient]:
    return session.exec(
        select(RecipeIngredient).where(RecipeIngredient.recipe_id == recipe_id)
    ).all()


@router.get("/", response_model=list[RecipeResponse], status_code=status.HTTP_200_OK)
def get_all(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    return session.exec(select(Recipe).where(Recipe.deleted_at == None)).all()


@router.get("/{recipe_id}", response_model=RecipeResponse, status_code=status.HTTP_200_OK)
def get_one(recipe_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    recipe = session.get(Recipe, recipe_id)
    if not recipe or recipe.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receta no encontrada.")
    return recipe


@router.post("/", response_model=RecipeResponse, status_code=status.HTTP_201_CREATED)
def create(data: RecipeCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    existing = session.exec(
        select(Recipe).where(Recipe.name == data.name, Recipe.deleted_at == None)
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Ya existe una receta con el nombre '{data.name}'.")

    unit = session.get(Unit, data.yield_unit_id)
    if not unit or unit.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"La unidad con id '{data.yield_unit_id}' no existe.")

    if data.product_id is not None:
        from src.models.models import Product
        product = session.get(Product, data.product_id)
        if not product or product.deleted_at is not None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"El producto con id '{data.product_id}' no existe.")

    for ing in data.ingredients:
        supply = session.get(Supply, ing.supply_id)
        if not supply or supply.deleted_at is not None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"El insumo con id '{ing.supply_id}' no existe.")
        ing_unit = session.get(Unit, ing.unit_id)
        if not ing_unit or ing_unit.deleted_at is not None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"La unidad con id '{ing.unit_id}' no existe.")

    recipe = Recipe(
        name=data.name,
        description=data.description,
        product_id=data.product_id,
        yield_quantity=data.yield_quantity,
        yield_unit_id=data.yield_unit_id,
        created_by=current_user.id,
    )
    session.add(recipe)
    session.flush()

    for ing in data.ingredients:
        ri = RecipeIngredient(
            recipe_id=recipe.id,
            supply_id=ing.supply_id,
            quantity=ing.quantity,
            unit_id=ing.unit_id,
            notes=ing.notes,
        )
        session.add(ri)

    session.commit()
    session.refresh(recipe)
    return recipe


@router.patch("/{recipe_id}", response_model=RecipeResponse, status_code=status.HTTP_200_OK)
def update(recipe_id: int, data: RecipeUpdate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    recipe = session.get(Recipe, recipe_id)
    if not recipe or recipe.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receta no encontrada.")

    if data.name is not None and data.name != recipe.name:
        existing = session.exec(
            select(Recipe).where(Recipe.name == data.name, Recipe.id != recipe_id, Recipe.deleted_at == None)
        ).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Ya existe una receta con el nombre '{data.name}'.")

    if data.yield_unit_id is not None:
        unit = session.get(Unit, data.yield_unit_id)
        if not unit or unit.deleted_at is not None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"La unidad con id '{data.yield_unit_id}' no existe.")

    if data.product_id is not None:
        from src.models.models import Product
        product = session.get(Product, data.product_id)
        if not product or product.deleted_at is not None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"El producto con id '{data.product_id}' no existe.")

    update_fields = data.model_dump(exclude_unset=True, exclude={"ingredients"})
    for field, value in update_fields.items():
        setattr(recipe, field, value)

    recipe.updated_at = datetime.now(BOGOTA_TZ)
    recipe.updated_by = current_user.id

    if data.ingredients is not None:
        old_ingredients = _load_ingredients(recipe.id, session)
        for old in old_ingredients:
            session.delete(old)

        for ing in data.ingredients:
            supply = session.get(Supply, ing.supply_id)
            if not supply or supply.deleted_at is not None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"El insumo con id '{ing.supply_id}' no existe.")
            ing_unit = session.get(Unit, ing.unit_id)
            if not ing_unit or ing_unit.deleted_at is not None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"La unidad con id '{ing.unit_id}' no existe.")

            ri = RecipeIngredient(
                recipe_id=recipe.id,
                supply_id=ing.supply_id,
                quantity=ing.quantity,
                unit_id=ing.unit_id,
                notes=ing.notes,
            )
            session.add(ri)

    session.add(recipe)
    session.commit()
    session.refresh(recipe)
    return recipe


@router.delete("/{recipe_id}", response_model=DeleteResponseRecipe, status_code=status.HTTP_200_OK)
def delete(recipe_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    recipe = session.get(Recipe, recipe_id)
    if not recipe or recipe.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receta no encontrada.")

    now = datetime.now(BOGOTA_TZ)
    recipe.deleted_at = now
    recipe.deleted_by = current_user.id
    recipe.status = RecipeStatus.INACTIVE
    session.add(recipe)
    session.commit()

    return DeleteResponseRecipe(
        message=f"Receta '{recipe.name}' eliminada correctamente.",
        deleted_at=now,
        deleted_by=current_user.id,
    )
