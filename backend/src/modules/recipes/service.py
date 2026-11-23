from datetime import datetime

from sqlmodel import Session, select

from src.core.exceptions import (
    BusinessRuleError,
    ConflictError,
    NotFoundError,
)
from src.core.time import BOGOTA_TZ
from src.modules.products.models import Product
from src.modules.recipes.models import Recipe, RecipeIngredient, RecipeStatus
from src.modules.recipes.schemas import (
    DeleteResponseRecipe,
    RecipeCreate,
    RecipeUpdate,
)
from src.modules.supplies.models import Supply
from src.modules.units.models import Unit
from src.modules.users.models import User


class RecipesService:
    def __init__(self, session: Session):
        self.session = session

    def _load_ingredients(self, recipe_id: int) -> list[RecipeIngredient]:
        return self.session.exec(
            select(RecipeIngredient).where(RecipeIngredient.recipe_id == recipe_id)
        ).all()

    def list(self, skip: int = 0, limit: int = 20) -> list[Recipe]:
        return self.session.exec(
            select(Recipe).where(Recipe.deleted_at == None).offset(skip).limit(limit)
        ).all()

    def get(self, recipe_id: int) -> Recipe:
        recipe = self.session.get(Recipe, recipe_id)
        if not recipe or recipe.deleted_at is not None:
            raise NotFoundError("Receta no encontrada.")
        return recipe

    def create(self, data: RecipeCreate, current_user: User) -> Recipe:
        existing = self.session.exec(
            select(Recipe).where(
                Recipe.name == data.name, Recipe.deleted_at == None
            )
        ).first()
        if existing:
            raise ConflictError(
                f"Ya existe una receta con el nombre '{data.name}'."
            )

        unit = self.session.get(Unit, data.yield_unit_id)
        if not unit or unit.deleted_at is not None:
            raise NotFoundError(
                f"La unidad con id '{data.yield_unit_id}' no existe."
            )

        product = self.session.get(Product, data.product_id)
        if not product or product.deleted_at is not None:
            raise NotFoundError(
                f"El producto con id '{data.product_id}' no existe."
            )

        for ing in data.ingredients:
            supply = self.session.get(Supply, ing.supply_id)
            if not supply or supply.deleted_at is not None:
                raise NotFoundError(
                    f"El insumo con id '{ing.supply_id}' no existe."
                )
            ing_unit = self.session.get(Unit, ing.unit_id)
            if not ing_unit or ing_unit.deleted_at is not None:
                raise NotFoundError(
                    f"La unidad con id '{ing.unit_id}' no existe."
                )

        recipe = Recipe(
            name=data.name,
            description=data.description,
            product_id=data.product_id,
            yield_quantity=data.yield_quantity,
            yield_unit_id=data.yield_unit_id,
            created_by=current_user.id,
        )
        self.session.add(recipe)
        self.session.flush()

        for ing in data.ingredients:
            ri = RecipeIngredient(
                recipe_id=recipe.id,
                supply_id=ing.supply_id,
                quantity=ing.quantity,
                unit_id=ing.unit_id,
                notes=ing.notes,
            )
            self.session.add(ri)

        self.session.commit()
        self.session.refresh(recipe)
        return recipe

    def update(
        self, recipe_id: int, data: RecipeUpdate, current_user: User
    ) -> Recipe:
        recipe = self.get(recipe_id)

        if data.name is not None and data.name != recipe.name:
            existing = self.session.exec(
                select(Recipe).where(
                    Recipe.name == data.name,
                    Recipe.id != recipe_id,
                    Recipe.deleted_at == None,
                )
            ).first()
            if existing:
                raise ConflictError(
                    f"Ya existe una receta con el nombre '{data.name}'."
                )

        if data.yield_unit_id is not None:
            unit = self.session.get(Unit, data.yield_unit_id)
            if not unit or unit.deleted_at is not None:
                raise NotFoundError(
                    f"La unidad con id '{data.yield_unit_id}' no existe."
                )

        if data.product_id is not None:
            product = self.session.get(Product, data.product_id)
            if not product or product.deleted_at is not None:
                raise NotFoundError(
                    f"El producto con id '{data.product_id}' no existe."
                )
        elif "product_id" in data.model_dump(exclude_unset=True):
            raise BusinessRuleError(
                "El producto terminado es obligatorio: no se puede desvincular el producto de la receta."
            )

        update_fields = data.model_dump(exclude_unset=True, exclude={"ingredients"})
        for field, value in update_fields.items():
            setattr(recipe, field, value)

        recipe.updated_at = datetime.now(BOGOTA_TZ)
        recipe.updated_by = current_user.id

        if data.ingredients is not None:
            old_ingredients = self._load_ingredients(recipe.id)
            for old in old_ingredients:
                self.session.delete(old)

            for ing in data.ingredients:
                supply = self.session.get(Supply, ing.supply_id)
                if not supply or supply.deleted_at is not None:
                    raise NotFoundError(
                        f"El insumo con id '{ing.supply_id}' no existe."
                    )
                ing_unit = self.session.get(Unit, ing.unit_id)
                if not ing_unit or ing_unit.deleted_at is not None:
                    raise NotFoundError(
                        f"La unidad con id '{ing.unit_id}' no existe."
                    )

                ri = RecipeIngredient(
                    recipe_id=recipe.id,
                    supply_id=ing.supply_id,
                    quantity=ing.quantity,
                    unit_id=ing.unit_id,
                    notes=ing.notes,
                )
                self.session.add(ri)

        self.session.add(recipe)
        self.session.commit()
        self.session.refresh(recipe)
        return recipe

    def delete(self, recipe_id: int, current_user: User) -> DeleteResponseRecipe:
        recipe = self.get(recipe_id)

        now = datetime.now(BOGOTA_TZ)
        recipe.deleted_at = now
        recipe.deleted_by = current_user.id
        recipe.status = RecipeStatus.INACTIVE
        self.session.add(recipe)
        self.session.commit()

        return DeleteResponseRecipe(
            message=f"Receta '{recipe.name}' eliminada correctamente.",
            deleted_at=now,
            deleted_by=current_user.id,
        )
