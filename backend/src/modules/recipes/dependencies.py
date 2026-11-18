from fastapi import Depends
from sqlmodel import Session

from src.core.database import get_session
from src.modules.recipes.service import RecipesService


def get_recipes_service(session: Session = Depends(get_session)) -> RecipesService:
    return RecipesService(session)
