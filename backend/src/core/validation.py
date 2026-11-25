"""Validación de límites de entrada en la capa de servicios (Fase 3).

Los esquemas Pydantic públicos se mantienen sin restricciones para no alterar
el OpenAPI aprobado en Fase 6. Este módulo aplica los límites que Fase 3
había definido con ``Field(...)``, después de la validación de tipos de
FastAPI y antes de cualquier acceso a la base de datos.
"""

from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel

from src.core.exceptions import UnprocessableError

Rule = Mapping[str, Any]


def _text(min_length: int | None = None, max_length: int | None = None) -> Rule:
    rule: dict[str, Any] = {}
    if min_length is not None:
        rule["min_length"] = min_length
    if max_length is not None:
        rule["max_length"] = max_length
    return rule


def _number(*, gt: float | None = None, ge: float | None = None) -> Rule:
    rule: dict[str, Any] = {}
    if gt is not None:
        rule["gt"] = gt
    if ge is not None:
        rule["ge"] = ge
    return rule


def _list(*, min_items: int | None = None, item: Rule | None = None) -> Rule:
    rule: dict[str, Any] = {}
    if min_items is not None:
        rule["min_items"] = min_items
    if item is not None:
        rule["item"] = item
    return rule


INGREDIENT_FIELDS: dict[str, Rule] = {
    "supply_id": _number(gt=0),
    "quantity": _number(gt=0),
    "unit_id": _number(gt=0),
    "notes": _text(max_length=255),
}

SALE_ITEM_FIELDS: dict[str, Rule] = {
    "item_id": _number(gt=0),
    "quantity": _number(gt=0),
}

RULES: dict[str, dict[str, Rule]] = {
    "ProductCreate": {
        "name": _text(min_length=1, max_length=150),
        "description": _text(max_length=500),
        "unit_id": _number(gt=0),
        "available_quantity": _number(ge=0),
        "min_stock": _number(ge=0),
        "max_stock": _number(ge=0),
    },
    "ProductUpdate": {
        "name": _text(min_length=1, max_length=150),
        "description": _text(max_length=500),
        "unit_id": _number(gt=0),
        "available_quantity": _number(ge=0),
        "min_stock": _number(ge=0),
        "max_stock": _number(ge=0),
    },
    "CommercialProductCreate": {
        "name": _text(min_length=1, max_length=150),
        "description": _text(max_length=500),
        "category_id": _number(gt=0),
        "unit_id": _number(gt=0),
        "provider_id": _number(gt=0),
        "purchase_price": _number(ge=0),
        "sale_price": _number(ge=0),
        "available_quantity": _number(ge=0),
        "min_stock": _number(ge=0),
        "max_stock": _number(ge=0),
    },
    "CommercialProductUpdate": {
        "name": _text(min_length=1, max_length=150),
        "description": _text(max_length=500),
        "category_id": _number(gt=0),
        "unit_id": _number(gt=0),
        "provider_id": _number(gt=0),
        "purchase_price": _number(ge=0),
        "sale_price": _number(ge=0),
        "available_quantity": _number(ge=0),
        "min_stock": _number(ge=0),
        "max_stock": _number(ge=0),
    },
    "ProductCategoryCreate": {
        "name": _text(min_length=1, max_length=100),
        "description": _text(max_length=255),
    },
    "ProductCategoryUpdate": {
        "name": _text(min_length=1, max_length=100),
        "description": _text(max_length=255),
    },
    "SupplyCategoryCreate": {
        "name": _text(min_length=1, max_length=150),
        "description": _text(max_length=500),
    },
    "SupplyCategoryUpdate": {
        "name": _text(min_length=1, max_length=150),
        "description": _text(max_length=500),
    },
    "SupplyCreate": {
        "name": _text(min_length=1, max_length=100),
        "description": _text(max_length=255),
        "category_id": _number(gt=0),
        "unit_id": _number(gt=0),
        "available_quantity": _number(ge=0),
        "min_stock": _number(ge=0),
        "max_stock": _number(ge=0),
        "supplier_id": _number(gt=0),
    },
    "SupplyUpdate": {
        "name": _text(min_length=1, max_length=100),
        "description": _text(max_length=255),
        "category_id": _number(gt=0),
        "unit_id": _number(gt=0),
        "available_quantity": _number(ge=0),
        "min_stock": _number(ge=0),
        "max_stock": _number(ge=0),
        "supplier_id": _number(gt=0),
    },
    "UnitCreate": {
        "name": _text(min_length=1, max_length=100),
        "abbreviation": _text(min_length=1, max_length=20),
        "description": _text(max_length=255),
        "quantity": _number(ge=0),
    },
    "UnitUpdate": {
        "name": _text(min_length=1, max_length=100),
        "abbreviation": _text(min_length=1, max_length=20),
        "description": _text(max_length=255),
        "quantity": _number(ge=0),
    },
    "ProviderCreate": {
        "company": _text(min_length=1, max_length=150),
        "nit": _text(min_length=1, max_length=20),
        "email": _text(max_length=150),
    },
    "ProviderUpdate": {
        "company": _text(min_length=1, max_length=150),
        "nit": _text(min_length=1, max_length=20),
        "email": _text(max_length=150),
    },
    "ProviderContactCreate": {
        "name": _text(min_length=1, max_length=150),
        "email": _text(max_length=150),
        "phone": _text(max_length=20),
        "notes": _text(max_length=500),
    },
    "ProviderContactUpdate": {
        "name": _text(min_length=1, max_length=150),
        "email": _text(max_length=150),
        "phone": _text(max_length=20),
        "notes": _text(max_length=500),
    },
    "RecipeIngredientCreate": INGREDIENT_FIELDS,
    "RecipeCreate": {
        "name": _text(min_length=1, max_length=150),
        "description": _text(max_length=500),
        "product_id": _number(gt=0),
        "yield_quantity": _number(gt=0),
        "yield_unit_id": _number(gt=0),
        "ingredients": _list(min_items=1, item={"fields": INGREDIENT_FIELDS}),
    },
    "RecipeUpdate": {
        "name": _text(min_length=1, max_length=150),
        "description": _text(max_length=500),
        "product_id": _number(gt=0),
        "yield_quantity": _number(gt=0),
        "yield_unit_id": _number(gt=0),
        "ingredients": _list(min_items=1, item={"fields": INGREDIENT_FIELDS}),
    },
    "ProductionOrderCreate": {
        "recipe_id": _number(gt=0),
        "quantity_multiplier": _number(gt=0),
        "notes": _text(max_length=500),
    },
    "RoleCreate": {
        "name": _text(min_length=1, max_length=100),
        "description": _text(max_length=500),
    },
    "RoleUpdate": {
        "name": _text(min_length=1, max_length=100),
        "description": _text(max_length=500),
    },
    "RoleModuleAssign": {
        "module_ids": _list(min_items=1),
    },
    "SaleItemCreate": SALE_ITEM_FIELDS,
    "SaleCreate": {
        "items": _list(min_items=1, item={"fields": SALE_ITEM_FIELDS}),
        "notes": _text(max_length=500),
    },
    "UserCreate": {
        "first_name": _text(min_length=1, max_length=100),
        "last_name": _text(min_length=1, max_length=100),
        "email": _text(max_length=150),
        "phone": _text(max_length=20),
        "role_id": _number(gt=0),
    },
    "UserUpdate": {
        "first_name": _text(min_length=1, max_length=100),
        "last_name": _text(min_length=1, max_length=100),
        "email": _text(max_length=150),
        "phone": _text(max_length=20),
        "role_id": _number(gt=0),
    },
}


def _fail(field: str, message: str) -> None:
    raise UnprocessableError(f"{field}: {message}")


def _validate_value(field: str, value: Any, rule: Rule) -> None:
    if value is None:
        return

    if isinstance(value, str):
        min_length = rule.get("min_length")
        if min_length is not None and len(value.strip()) < min_length:
            _fail(field, f"debe tener al menos {min_length} carácter(es)")
        max_length = rule.get("max_length")
        if max_length is not None and len(value) > max_length:
            _fail(field, f"no puede superar los {max_length} carácter(es)")
        return

    if isinstance(value, bool):
        return

    if isinstance(value, (int, float)):
        gt = rule.get("gt")
        if gt is not None and value <= gt:
            _fail(field, f"debe ser mayor que {gt}")
        ge = rule.get("ge")
        if ge is not None and value < ge:
            _fail(field, f"debe ser mayor o igual que {ge}")
        return

    if isinstance(value, (list, tuple)):
        min_items = rule.get("min_items")
        if min_items is not None and len(value) < min_items:
            _fail(field, f"debe tener al menos {min_items} elemento(s)")
        item_rule = rule.get("item")
        if item_rule is not None:
            for index, item in enumerate(value):
                _validate_value(f"{field}[{index}]", item, item_rule)
        return

    if isinstance(value, Mapping) and "fields" in rule:
        for name, nested in rule["fields"].items():
            if name in value:
                _validate_value(f"{field}.{name}", value[name], nested)


def validate_input(data: BaseModel, schema: str) -> None:
    """Aplica los límites de ``schema`` a los datos ya parseados por Pydantic."""
    rules = RULES.get(schema)
    if rules is None:
        raise ValueError(f"No hay reglas de validación para {schema!r}")
    values = data.model_dump()
    for field, rule in rules.items():
        if field in values:
            _validate_value(field, values[field], rule)
