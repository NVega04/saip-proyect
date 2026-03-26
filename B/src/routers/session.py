from fastapi import APIRouter, Depends, HTTPException, status, Header, Request
from sqlmodel import Session, select
from src.database import get_session
from src.models.models import User, SessionApp, PasswordReset
from src.schemas.schemas import (
    LoginRequest,
    LoginResponse,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from src.security import verify_password, get_session_expiry, hash_password
from src.dependencies import get_current_user
from slowapi import Limiter
from slowapi.util import get_remote_address
import uuid
import os
from datetime import datetime, timedelta
import secrets
from src.email import send_reset_email
from src.schemas.schemas import ChangePasswordRequest
from zoneinfo import ZoneInfo

BOGOTA_TZ = ZoneInfo("America/Bogota")

router = APIRouter(prefix="/session", tags=["Session"])

limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Iniciar sesión",
)
@limiter.limit("5/minute")  # ← máximo 5 intentos por minuto por IP
def login(
    request: Request, credentials: LoginRequest, db: Session = Depends(get_session)
):
    # 1. Buscar usuario por email
    user = db.exec(select(User).where(User.email == credentials.email)).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas.",
        )

    # 2. Verificar que el usuario esté activo
    if user.status.value != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario está inactivo. Contacte al administrador.",
        )

    # 3. Verificar password
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas.",
        )

    # 4. Verificar aceptación de términos
    if not user.accepted_terms:
        if not credentials.accepted_terms:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Debe aceptar los términos y condiciones para continuar.",
            )
        user.accepted_terms = True
        user.accepted_terms_at = datetime.now(BOGOTA_TZ)
        db.add(user)

    # 5. Invalidar sesiones anteriores activas
    old_sessions = db.exec(
        select(SessionApp).where(
            SessionApp.user_id == user.id,
            SessionApp.is_active == True,
        )
    ).all()
    for s in old_sessions:
        s.is_active = False
        db.add(s)

    # 6. Crear nueva sesión
    new_session = SessionApp(
        token=str(uuid.uuid4()),
        user_id=user.id,
        expires_at=get_session_expiry(),
    )

    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    db.refresh(user)

    return LoginResponse(
        session_token=new_session.token,
        expires_at=new_session.expires_at,
        user=user,
        terms_required=False,
    )


@router.post("/logout", status_code=status.HTTP_200_OK, summary="Cerrar sesión")
def logout(
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    session_token: str = Header(..., alias="session_token"),
):
    # Buscar la sesión activa
    user_session = db.exec(
        select(SessionApp).where(
            SessionApp.token == session_token,
            SessionApp.is_active == True,
        )
    ).first()

    if not user_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sesión no encontrada"
        )

    # Invalidar la sesión
    user_session.is_active = False
    db.add(user_session)
    db.commit()

    return {"message": "Sesión cerrada correctamante"}


@router.post(
    "/logout-all",
    status_code=status.HTTP_200_OK,
    summary="Cerrar sesión en todos los dispositivos",
)
def logout_all(
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    active_sessions = db.exec(
        select(SessionApp).where(
            SessionApp.user_id == current_user.id,
            SessionApp.is_active == True,
        )
    ).all()

    for s in active_sessions:
        s.is_active = False
        db.add(s)

    db.commit()

    return {"message": "Sesión cerrada en todos los dispositivos."}


PASSWORD_RESET_EXPIRE_MINUTES = 30


@router.post(
    "/forgot-password",
    status_code=status.HTTP_200_OK,
    summary="Solicitar recuperación de contraseña",
)
@limiter.limit("3/minute")
def forgot_password(
    request: Request,
    body: ForgotPasswordRequest,
    db: Session = Depends(get_session),
):
    user = db.exec(
        select(User).where(User.email == body.email, User.deleted_at == None)
    ).first()

    if not user or user.status.value != "active":
        return {"message": "Si el correo está registrado, recibirás instrucciones."}

    old_tokens = db.exec(
        select(PasswordReset).where(
            PasswordReset.user_id == user.id,
            PasswordReset.used == False,
        )
    ).all()
    for t in old_tokens:
        t.used = True
        db.add(t)

    raw_token = secrets.token_urlsafe(32)
    reset_entry = PasswordReset(
        user_id=user.id,
        token=raw_token,
        expires_at=datetime.now(BOGOTA_TZ)
        + timedelta(minutes=PASSWORD_RESET_EXPIRE_MINUTES),
    )
    db.add(reset_entry)
    db.commit()

    reset_link = f"{os.getenv('FRONTEND_URL')}/reset-password?token={raw_token}"
    try:
        send_reset_email(user.email, reset_link)
    except Exception as e:
        print(f"[EMAIL ERROR] No se pudo enviar a {user.email}: {e}")

    return {"message": "Si el correo está registrado, recibirás instrucciones."}


@router.post(
    "/reset-password",
    status_code=status.HTTP_200_OK,
    summary="Restablecer contraseña con token",
)
def reset_password(
    body: ResetPasswordRequest,
    db: Session = Depends(get_session),
):
    reset_entry = db.exec(
        select(PasswordReset).where(PasswordReset.token == body.token)
    ).first()

    if not reset_entry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido.",
        )

    if reset_entry.used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El token ya fue utilizado.",
        )

    if datetime.now(BOGOTA_TZ) > reset_entry.expires_at.replace(tzinfo=BOGOTA_TZ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El token ha expirado.",
        )

    # Actualizar contraseña
    user = reset_entry.user
    user.password_hash = hash_password(body.new_password)
    user.updated_at = datetime.now(BOGOTA_TZ)
    db.add(user)

    # Marcar token como usado
    reset_entry.used = True
    db.add(reset_entry)

    # Invalidar todas las sesiones activas por seguridad
    active_sessions = db.exec(
        select(SessionApp).where(
            SessionApp.user_id == user.id,
            SessionApp.is_active == True,
        )
    ).all()
    for s in active_sessions:
        s.is_active = False
        db.add(s)

    db.commit()

    return {"message": "Contraseña actualizada correctamente."}


@router.post(
    "/change-password",
    status_code=status.HTTP_200_OK,
    summary="Cambiar contraseña estando autenticado",
)
def change_password(
    body: ChangePasswordRequest,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if not verify_password(body.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña actual es incorrecta.",
        )

    current_user.password_hash = hash_password(body.new_password)
    current_user.updated_at = datetime.now(BOGOTA_TZ)
    db.add(current_user)
    db.commit()

    return {"message": "Contraseña actualizada correctamente."}
