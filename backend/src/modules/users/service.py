import logging
from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Session, select

from src.core.email import send_deactivation_email, send_welcome_email
from src.core.exceptions import (
    BusinessRuleError,
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
    UnauthorizedError,
)
from src.core.password import validate_password
from src.core.security import (
    generate_temp_password,
    hash_password,
    verify_password,
)
from src.modules.audit.service import AuditService
from src.modules.roles.models import Role
from src.modules.users.models import SessionApp, User, UserStatus
from src.modules.users.schemas import (
    DeleteResponseUser,
    UserCreate,
    UserUpdate,
)

logger = logging.getLogger(__name__)


def _user_snapshot(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone": user.phone,
        "role_id": user.role_id,
        "is_admin": user.is_admin,
        "status": user.status.value if user.status else None,
    }


class UsersService:
    def __init__(self, session: Session, ip_address: Optional[str] = None):
        self.session = session
        self.audit = AuditService(session, ip_address=ip_address)

    def create(self, data: UserCreate, current_user: User) -> User:
        role = self.session.get(Role, data.role_id)
        if not role:
            raise NotFoundError(f"El rol con id '{data.role_id}' no existe.")

        existing_user = self.session.exec(
            select(User).where(User.email == data.email)
        ).first()
        if existing_user:
            raise ConflictError(f"El email '{data.email}' ya está registrado.")

        temp_password = generate_temp_password()
        validate_password(temp_password)
        hashed = hash_password(temp_password)
        logger.info("Se generó la contraseña temporal para la cuenta '%s'.", data.email)

        new_user = User(
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            phone=data.phone,
            role_id=data.role_id,
            is_admin=data.is_admin,
            password_hash=hashed,
        )

        self.session.add(new_user)
        self.session.commit()
        self.session.refresh(new_user)
        self.audit.log_action(
            "user.created",
            "user",
            resource_id=new_user.id,
            new_value=_user_snapshot(new_user),
            user_id=current_user.id,
            commit=True,
        )

        try:
            send_welcome_email(new_user.email, new_user.first_name, temp_password)
        except Exception:
            logger.warning(
                "No se pudo enviar la bienvenida a %s.", new_user.email
            )

        return new_user

    def delete_own_account(
        self, confirm_password: str, current_user: User
    ) -> DeleteResponseUser:
        if current_user.is_admin:
            raise PermissionDeniedError(
                "Los administradores no pueden eliminar su propia cuenta."
            )

        if current_user.status == UserStatus.INACTIVE:
            raise ConflictError("La cuenta ya fue eliminada.")

        if not verify_password(confirm_password, current_user.password_hash):
            raise UnauthorizedError(
                "Contraseña incorrecta. No se puede eliminar la cuenta."
            )

        old_snapshot = _user_snapshot(current_user)
        now = datetime.now(timezone.utc)
        current_user.deleted_at = now
        current_user.deleted_by = current_user.id
        current_user.status = UserStatus.INACTIVE

        active_sessions = self.session.exec(
            select(SessionApp).where(
                SessionApp.user_id == current_user.id,
                SessionApp.is_active == True,
            )
        ).all()
        for s in active_sessions:
            s.is_active = False
            self.session.add(s)

        self.session.add(current_user)
        self.audit.log_action(
            "user.self_deleted",
            "user",
            resource_id=current_user.id,
            old_value=old_snapshot,
            new_value={"status": UserStatus.INACTIVE.value},
            user_id=current_user.id,
        )
        self.session.commit()

        return DeleteResponseUser(
            message=f"Cuenta '{current_user.email}' eliminada correctamente.",
            deleted_at=now,
            deleted_by=current_user.id,
        )

    def delete_user(self, user_id: int, current_user: User) -> DeleteResponseUser:
        user = self.session.get(User, user_id)
        if not user:
            raise NotFoundError(f"El usuario con id '{user_id}' no existe.")

        if user.status == UserStatus.INACTIVE:
            raise ConflictError(
                f"El usuario con id '{user_id}' ya fue eliminado."
            )

        if user.is_admin:
            raise PermissionDeniedError(
                "No se puede eliminar a un administrador."
            )

        if user_id == current_user.id:
            raise BusinessRuleError("No puedes eliminarte a ti mismo.")

        old_snapshot = _user_snapshot(user)
        now = datetime.now(timezone.utc)
        user.deleted_at = now
        user.deleted_by = current_user.id
        user.status = UserStatus.INACTIVE

        active_sessions = self.session.exec(
            select(SessionApp).where(
                SessionApp.user_id == user_id,
                SessionApp.is_active == True,
            )
        ).all()
        for s in active_sessions:
            s.is_active = False
            self.session.add(s)

        self.session.add(user)
        self.audit.log_action(
            "user.deleted",
            "user",
            resource_id=user.id,
            old_value=old_snapshot,
            new_value={"status": UserStatus.INACTIVE.value},
            user_id=current_user.id,
        )
        self.session.commit()

        try:
            send_deactivation_email(user.email, user.first_name)
        except Exception as e:
            logger.warning(
                f"[EMAIL ERROR] No se pudo notificar desactivación a {user.email}: {e}"
            )

        return DeleteResponseUser(
            message=f"Usuario '{user.email}' eliminado correctamente.",
            deleted_at=now,
            deleted_by=current_user.id,
        )

    def update(
        self, user_id: int, data: UserUpdate, current_user: User
    ) -> User:
        user = self.session.get(User, user_id)
        if not user:
            raise NotFoundError(f"El usuario con id '{user_id}' no existe.")

        if user.status == UserStatus.INACTIVE:
            raise ConflictError(
                f"El usuario con id '{user_id}' está inactivo."
            )

        if data.email and data.email != user.email:
            existing = self.session.exec(
                select(User).where(User.email == data.email)
            ).first()
            if existing:
                raise ConflictError(
                    f"El email '{data.email}' ya está registrado."
                )

        if data.role_id:
            role = self.session.get(Role, data.role_id)
            if not role:
                raise NotFoundError(
                    f"El rol con id '{data.role_id}' no existe."
                )

        was_active = user.status == UserStatus.ACTIVE
        old_snapshot = _user_snapshot(user)

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)

        user.updated_at = datetime.now(timezone.utc)
        user.updated_by = current_user.id

        self.session.add(user)
        self.audit.log_action(
            "user.updated",
            "user",
            resource_id=user.id,
            old_value=old_snapshot,
            new_value=_user_snapshot(user),
            user_id=current_user.id,
        )
        self.session.commit()
        self.session.refresh(user)

        if was_active and user.status == UserStatus.INACTIVE:
            try:
                send_deactivation_email(user.email, user.first_name)
            except Exception as e:
                logger.warning(
                    f"[EMAIL ERROR] No se pudo notificar desactivación a {user.email}: {e}"
                )

        return user

    def list(self) -> list[User]:
        return self.session.exec(select(User)).all()
