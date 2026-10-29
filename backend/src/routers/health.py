from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlmodel import Session

from src.database import get_session

router = APIRouter(tags=["Health"])


@router.get("/health", include_in_schema=False)
def health(session: Session = Depends(get_session)):
    """Healthcheck simple: responde 200 si la API y la base de datos están OK.

    No lleva autenticación ni rate limit para que un monitor externo pueda
    consultarlo sin consumir cupo de slowapi.
    """
    try:
        session.execute(text("SELECT 1"))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Base de datos no disponible",
        )
    return {"status": "ok", "db": "ok"}
