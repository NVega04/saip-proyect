from fastapi import APIRouter, Depends, Header, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.core.dependencies import get_current_user
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
)
@limiter.limit("5/minute")
def login(
    request: Request,
    credentials: LoginRequest,
    service: AuthService = Depends(get_auth_service),
):
    return service.login(credentials)


@router.post(
    "/logout", status_code=status.HTTP_200_OK, summary="Cerrar sesión"
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
)
@limiter.limit("3/minute")
def forgot_password(
    request: Request,
    body: ForgotPasswordRequest,
    service: AuthService = Depends(get_auth_service),
):
    return service.forgot_password(body)


@router.post(
    "/reset-password",
    status_code=status.HTTP_200_OK,
    summary="Restablecer contraseña con token",
)
def reset_password(
    body: ResetPasswordRequest,
    service: AuthService = Depends(get_auth_service),
):
    return service.reset_password(body)


@router.post(
    "/change-password",
    status_code=status.HTTP_200_OK,
    summary="Cambiar contraseña estando autenticado",
)
def change_password(
    body: ChangePasswordRequest,
    service: AuthService = Depends(get_auth_service),
    current_user: User = Depends(get_current_user),
):
    return service.change_password(body, current_user)
