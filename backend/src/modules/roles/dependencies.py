from fastapi import Depends
from sqlmodel import Session

from src.core.database import get_session
from src.modules.roles.service import RoleModulesService, RolesService


def get_roles_service(session: Session = Depends(get_session)) -> RolesService:
    return RolesService(session)


def get_role_modules_service(
    session: Session = Depends(get_session),
) -> RoleModulesService:
    return RoleModulesService(session)
