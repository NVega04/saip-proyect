from fastapi import APIRouter, Depends, Header, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.core.dependencies import get_current_user
from src.core.openapi import (
    AUTH_FLOW_ERRORS,
    BAD_REQUEST,
    RATE_LIMITED,
    UNAUTHORIZED,
)
from src.modules.auth.dependencies import get_auth_service
from src.modules.auth.schemas import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    LoginResponse,
    ResetPasswordRequest,
)
from src.modules.auth.service import AuthService
from src.modules.users.models import User

router = APIRouter(prefix="/session", tags=["Session"])

limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Iniciar sesión",
    responses={
        401: {"description": "Credenciales inválidas"},
        **AUTH_FLOW_ERRORS,
    },
)
@limiter.limit("5/minute")
def login(
    request: Request,
    credentials: LoginRequest,
    service: AuthService = Depends(get_auth_service),
):
    """Valida credenciales y abre una sesión.

    Reglas de negocio: la cuenta debe aceptar los términos (403), se bloquea
    temporalmente tras varios intentos fallidos (423) y el endpoint admite
    5 peticiones por minuto por IP (429). La contraseña nunca se registra.
    """
    return service.login(credentials)


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Cerrar sesión",
    responses={401: UNAUTHORIZED},
)
def logout(
    service: AuthService = Depends(get_auth_service),
    current_user: User = Depends(get_current_user),
    session_token: str = Header(..., alias="session_token"),
):
    return service.logout(session_token)


@router.post(
    "/logout-all",
    status_code=status.HTTP_200_OK,
    summary="Cerrar sesión en todos los dispositivos",
    responses={401: UNAUTHORIZED},
)
def logout_all(
    service: AuthService = Depends(get_auth_service),
    current_user: User = Depends(get_current_user),
):
    return service.logout_all(current_user)


@router.post(
    "/forgot-password",
    status_code=status.HTTP_200_OK,
    summary="Solicitar recuperación de contraseña",
    responses={429: RATE_LIMITED},
)
@limiter.limit("3/minute")
def forgot_password(
    request: Request,
    body: ForgotPasswordRequest,
    service: AuthService = Depends(get_auth_service),
):
    """Envía un token de recuperación por correo.

    Máximo 3 peticiones por minuto por IP (429). Por seguridad, la respuesta
    es la misma aunque el correo no exista o la cuenta esté inactiva, y los
    tokens anteriores sin usar se invalidan al generar uno nuevo.
    """
    return service.forgot_password(body)


@router.post(
    "/reset-password",
    status_code=status.HTTP_200_OK,
    summary="Restablecer contraseña con token",
    responses={400: BAD_REQUEST},
)
def reset_password(
    body: ResetPasswordRequest,
    service: AuthService = Depends(get_auth_service),
):
    """Cambia la contraseña con un token de recuperación.

    El token debe existir, no haber sido usado y no estar expirado; la nueva
    contraseña debe cumplir la política de contraseñas (400).
    """
    return service.reset_password(body)


@router.post(
    "/change-password",
    status_code=status.HTTP_200_OK,
    summary="Cambiar contraseña estando autenticado",
    responses={400: BAD_REQUEST, 401: UNAUTHORIZED},
)
def change_password(
    body: ChangePasswordRequest,
    service: AuthService = Depends(get_auth_service),
    current_user: User = Depends(get_current_user),
):
    """Cambia la contraseña del usuario autenticado.

    Requiere la contraseña actual correcta y una nueva que cumpla la política
    (mínimo 12 caracteres, mayúscula, minúscula, dígito y símbolo). La acción
    se registra en la auditoría sin guardar ninguna contraseña.
    """
    return service.change_password(body, current_user)
