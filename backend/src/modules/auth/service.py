import secrets
import uuid
from datetime import datetime, timedelta

from sqlmodel import Session, select

from src.core.config import settings
from src.core.email import send_reset_email
from src.core.exceptions import (
    BusinessRuleError,
    ConflictError,
    LockedError,
    NotFoundError,
    PermissionDeniedError,
    UnauthorizedError,
)
from src.core.security import (
    create_jwt,
    decode_jwt,
    get_session_expiry,
    hash_password,
    verify_password,
)
from src.core.time import BOGOTA_TZ
from src.modules.auth.schemas import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    LoginResponse,
    ResetPasswordRequest,
)
from src.modules.users.models import PasswordReset, SessionApp, User

MAX_LOGIN_ATTEMPTS = 3
LOCK_DURATION_MINUTES = 3
PASSWORD_RESET_EXPIRE_MINUTES = 30


class AuthService:
    def __init__(self, session: Session):
        self.session = session

    def login(self, credentials: LoginRequest) -> LoginResponse:
        user = self.session.exec(
            select(User).where(User.email == credentials.email)
        ).first()

        now = datetime.now(BOGOTA_TZ)

        if user is not None:
            if user.locked_until is not None:
                locked_until = user.locked_until
                if locked_until.tzinfo is None:
                    locked_until = locked_until.replace(tzinfo=BOGOTA_TZ)
                if now < locked_until:
                    remaining = (
                        int((locked_until - now).total_seconds() // 60) + 1
                    )
                    raise LockedError(
                        "Cuenta bloqueada temporalmente por intentos fallidos. "
                        f"Inténtalo de nuevo en aproximadamente {remaining} min."
                    )
                user.failed_login_attempts = 0
                user.locked_until = None
                self.session.add(user)

        if not user:
            raise UnauthorizedError("Credenciales inválidas.")

        if user.status.value != "active":
            raise PermissionDeniedError(
                "El usuario está inactivo. Contacte al administrador."
            )

        if not verify_password(credentials.password, user.password_hash):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= MAX_LOGIN_ATTEMPTS:
                user.failed_login_attempts = 0
                user.locked_until = datetime.now(BOGOTA_TZ) + timedelta(
                    minutes=LOCK_DURATION_MINUTES
                )
            self.session.add(user)
            self.session.commit()
            attempts_left = max(
                MAX_LOGIN_ATTEMPTS - user.failed_login_attempts, 0
            )
            detail = "Credenciales inválidas."
            if user.locked_until is not None:
                detail = (
                    "Credenciales inválidas. La cuenta fue bloqueada temporalmente "
                    "por 3 minutos por exceder el número de intentos permitidos."
                )
            elif attempts_left > 0:
                detail = (
                    f"Credenciales inválidas. Te quedan {attempts_left} intento(s)."
                )
            raise UnauthorizedError(detail)

        if user.failed_login_attempts != 0 or user.locked_until is not None:
            user.failed_login_attempts = 0
            user.locked_until = None
            self.session.add(user)

        if not user.accepted_terms:
            if not credentials.accepted_terms:
                raise PermissionDeniedError(
                    "Debe aceptar los términos y condiciones para continuar."
                )
            user.accepted_terms = True
            user.accepted_terms_at = datetime.now(BOGOTA_TZ)
            self.session.add(user)

        old_sessions = self.session.exec(
            select(SessionApp).where(
                SessionApp.user_id == user.id,
                SessionApp.is_active == True,
            )
        ).all()
        for s in old_sessions:
            s.is_active = False
            self.session.add(s)

        new_session = SessionApp(
            token=str(uuid.uuid4()),
            user_id=user.id,
            expires_at=get_session_expiry(),
        )

        self.session.add(new_session)
        self.session.commit()
        self.session.refresh(new_session)
        self.session.refresh(user)

        jwt_token = create_jwt(
            new_session.token, user.id, new_session.expires_at
        )

        return LoginResponse(
            session_token=jwt_token,
            expires_at=new_session.expires_at,
            user=user,
            terms_required=False,
        )

    def logout(self, raw_token: str) -> dict:
        payload = decode_jwt(raw_token)
        if payload is None:
            raise UnauthorizedError("Token inválido")
        internal_token = payload["session_token"]

        user_session = self.session.exec(
            select(SessionApp).where(
                SessionApp.token == internal_token,
                SessionApp.is_active == True,
            )
        ).first()

        if not user_session:
            raise NotFoundError("Sesión no encontrada")

        user_session.is_active = False
        self.session.add(user_session)
        self.session.commit()

        return {"message": "Sesión cerrada correctamante"}

    def logout_all(self, current_user: User) -> dict:
        active_sessions = self.session.exec(
            select(SessionApp).where(
                SessionApp.user_id == current_user.id,
                SessionApp.is_active == True,
            )
        ).all()

        for s in active_sessions:
            s.is_active = False
            self.session.add(s)

        self.session.commit()

        return {"message": "Sesión cerrada en todos los dispositivos."}

    def forgot_password(self, body: ForgotPasswordRequest) -> dict:
        user = self.session.exec(
            select(User).where(
                User.email == body.email, User.deleted_at == None
            )
        ).first()

        if not user or user.status.value != "active":
            return {
                "message": "Si el correo está registrado, recibirás instrucciones."
            }

        old_tokens = self.session.exec(
            select(PasswordReset).where(
                PasswordReset.user_id == user.id,
                PasswordReset.used == False,
            )
        ).all()
        for t in old_tokens:
            t.used = True
            self.session.add(t)

        raw_token = secrets.token_urlsafe(32)
        reset_entry = PasswordReset(
            user_id=user.id,
            token=raw_token,
            expires_at=datetime.now(BOGOTA_TZ)
            + timedelta(minutes=PASSWORD_RESET_EXPIRE_MINUTES),
        )
        self.session.add(reset_entry)
        self.session.commit()

        reset_link = f"{settings.frontend_url}/reset-password?token={raw_token}"
        try:
            send_reset_email(user.email, reset_link)
        except Exception as e:
            print(f"[EMAIL ERROR] No se pudo enviar a {user.email}: {e}")

        return {
            "message": "Si el correo está registrado, recibirás instrucciones."
        }

    def reset_password(self, body: ResetPasswordRequest) -> dict:
        reset_entry = self.session.exec(
            select(PasswordReset).where(PasswordReset.token == body.token)
        ).first()

        if not reset_entry:
            raise BusinessRuleError("Token inválido.")

        if reset_entry.used:
            raise BusinessRuleError("El token ya fue utilizado.")

        if datetime.now(BOGOTA_TZ) > reset_entry.expires_at.replace(
            tzinfo=BOGOTA_TZ
        ):
            raise BusinessRuleError("El token ha expirado.")

        user = reset_entry.user
        user.password_hash = hash_password(body.new_password)
        user.updated_at = datetime.now(BOGOTA_TZ)
        self.session.add(user)

        reset_entry.used = True
        self.session.add(reset_entry)

        active_sessions = self.session.exec(
            select(SessionApp).where(
                SessionApp.user_id == user.id,
                SessionApp.is_active == True,
            )
        ).all()
        for s in active_sessions:
            s.is_active = False
            self.session.add(s)

        self.session.commit()

        return {"message": "Contraseña actualizada correctamente."}

    def change_password(
        self, body: ChangePasswordRequest, current_user: User
    ) -> dict:
        if not verify_password(
            body.current_password, current_user.password_hash
        ):
            raise BusinessRuleError("La contraseña actual es incorrecta.")

        current_user.password_hash = hash_password(body.new_password)
        current_user.updated_at = datetime.now(BOGOTA_TZ)
        self.session.add(current_user)
        self.session.commit()

        return {"message": "Contraseña actualizada correctamente."}
