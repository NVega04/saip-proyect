from datetime import datetime, timezone

from sqlmodel import Session, select

from src.core.exceptions import (
    ConflictError,
    GoneError,
    NotFoundError,
    PermissionDeniedError,
)
from src.modules.roles.models import Module, Role, RoleModule, RoleStatus
from src.modules.roles.schemas import RoleCreate, RoleModuleAssign, RoleUpdate
from src.modules.users.models import User


class RolesService:
    def __init__(self, session: Session):
        self.session = session

    def create_role(self, data: RoleCreate) -> Role:
        existing = self.session.exec(
            select(Role).where(Role.name == data.name)
        ).first()
        if existing:
            raise ConflictError(f"El rol '{data.name}' ya existe.")

        role = Role(
            name=data.name,
            description=data.description,
            status=RoleStatus.ACTIVE,
        )
        self.session.add(role)
        self.session.commit()
        self.session.refresh(role)
        return role

    def update_role(self, role_id: int, data: RoleUpdate, current_user: User) -> Role:
        role = self.session.get(Role, role_id)
        if role is None:
            raise NotFoundError("Rol no encontrado")

        if role.status == RoleStatus.INACTIVE:
            raise GoneError("No se puede modificar un rol desactivado")

        if role.name.lower() in {"admin"}:
            raise PermissionDeniedError(
                f"No se puede modificar el rol de sistema '{role.name}'"
            )

        if data.name is not None and data.name.lower() != role.name.lower():
            existing = self.session.exec(
                select(Role).where(Role.name == data.name)
            ).first()
            if existing:
                raise ConflictError(f"Ya exixte un rol con el nombre '{data.name}'")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(role, field, value)

        role.updated_at = datetime.now(timezone.utc)
        role.updated_by = current_user.id

        self.session.add(role)
        self.session.commit()
        self.session.refresh(role)
        return role

    def deactivate_role(self, role_id: int, current_user: User) -> None:
        role = self.session.get(Role, role_id)
        if role is None:
            raise NotFoundError("Rol no encontrado")

        if role.status == RoleStatus.INACTIVE:
            raise GoneError("El rol ya esta desactivado")

        if role.name.lower() in {"admin"}:
            raise PermissionDeniedError(
                f"No se puede desactivar el rol de sistema '{role.name}'"
            )

        role.status = RoleStatus.INACTIVE
        role.deleted_at = datetime.now(timezone.utc)
        role.deleted_by = current_user.id

        self.session.add(role)
        self.session.commit()

    def list_roles(self) -> list[Role]:
        return self.session.exec(select(Role)).all()


class RoleModulesService:
    def __init__(self, session: Session):
        self.session = session

    def list_modules(self) -> list[Module]:
        return self.session.exec(select(Module)).all()

    def list_role_modules(self, role_id: int) -> list[RoleModule]:
        role = self.session.get(Role, role_id)
        if not role:
            raise NotFoundError(f"El rol con id '{role_id}' no existe.")

        role_modules = self.session.exec(
            select(RoleModule).where(RoleModule.role_id == role_id)
        ).all()

        for rm in role_modules:
            _ = rm.module

        return role_modules

    def assign_modules(
        self, role_id: int, data: RoleModuleAssign
    ) -> list[RoleModule]:
        role = self.session.get(Role, role_id)
        if not role:
            raise NotFoundError(f"El rol con id '{role_id}' no existe.")

        old_modules = self.session.exec(
            select(RoleModule).where(RoleModule.role_id == role_id)
        ).all()
        for module in old_modules:
            self.session.delete(module)
        self.session.flush()

        new_modules = []
        for module_id in data.module_ids:
            module = self.session.get(Module, module_id)
            if not module:
                raise NotFoundError(f"El módulo con id '{module_id}' no existe.")
            role_module = RoleModule(role_id=role_id, module_id=module_id)
            self.session.add(role_module)
            new_modules.append(role_module)

        self.session.commit()
        for module in new_modules:
            self.session.refresh(module)

        return new_modules
