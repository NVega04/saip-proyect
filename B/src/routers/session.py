from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlmodel import Session, select
from datetime import datetime, timezone

from src.database import get_session
from src.models.models import User, SessionApp
from src.schemas.schemas import LoginRequest, LoginResponse
from src.security import verify_password, create_session_token, get_session_expiry
from src.dependencies import get_current_user

router = APIRouter(prefix="/session", tags=["Session"])


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK, summary="Iniciar sesión")
def login(credentials: LoginRequest, db: Session = Depends(get_session)):
    # 1. Buscar usuario por email
    user = db.exec(
        select(User).where(User.email == credentials.email)
    ).first()

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

    # 4. Invalidar sesiones anteriores activas
    old_sessions = db.exec(
        select(SessionApp).where(
            SessionApp.user_id == user.id,
            SessionApp.is_active == True,
        )
    ).all()
    for s in old_sessions:
        s.is_active = False
        db.add(s)

    # 5. Crear nueva sesión
    new_session = SessionApp(
        user_id=user.id,
        expires_at=get_session_expiry(),
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    db.refresh(user)

    return LoginResponse(
        session_token=new_session.id,
        expires_at=new_session.expires_at,
        user=user,
    )
@router.post("/logout",status_code=status.HTTP_200_OK, summary="Cerrar sesión")
def logout(db: Session = Depends(get_session), current_user: User = Depends(get_current_user), session_token: str = Header(...),
):
    #Buscar la sesión activa
    user_session = db.get(
        SessionApp, session_token)
    if not user_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sesión no encontrada"
        )
    
    # Invalidar la sesión
    user_session.is_active = False
    db.add(user_session)
    db.commit()

    return{"message": "Sesión cerrada correctamante"}