from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlmodel import Session

from src.core.database import get_session
from src.core.exceptions import ServerError

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
        raise ServerError("Base de datos no disponible", status_code=503)
    return {"status": "ok", "db": "ok"}
