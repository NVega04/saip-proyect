import logging
from datetime import datetime, timezone

from sqlmodel import Session, select

from src.core.email import send_deactivation_email, send_welcome_email
from src.core.exceptions import (
    BusinessRuleError,
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
    UnauthorizedError,
)
from src.core.security import (
    generate_temp_password,
    hash_password,
    verify_password,
)
from src.modules.roles.models import Role
from src.modules.users.models import SessionApp, User, UserStatus
from src.modules.users.schemas import (
    DeleteResponseUser,
    UserCreate,
    UserUpdate,
)

logger = logging.getLogger(__name__)


class UsersService:
    def __init__(self, session: Session):
        self.session = session

    def create(self, data: UserCreate) -> User:
        role = self.session.get(Role, data.role_id)
        if not role:
            raise NotFoundError(f"El rol con id '{data.role_id}' no existe.")

        existing_user = self.session.exec(
            select(User).where(User.email == data.email)
        ).first()
        if existing_user:
            raise ConflictError(f"El email '{data.email}' ya está registrado.")

        temp_password = generate_temp_password()
        hashed = hash_password(temp_password)
        logger.warning(
            f"[SAIP] Password temporal generada para '{data.email}': {temp_password}"
        )

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

        try:
            send_welcome_email(new_user.email, new_user.first_name, temp_password)
        except Exception as e:
            logger.warning(
                f"[EMAIL ERROR] No se pudo enviar bienvenida a {new_user.email}: {e}"
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

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)

        user.updated_at = datetime.now(timezone.utc)
        user.updated_by = current_user.id

        self.session.add(user)
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
