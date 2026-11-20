from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from src.core.dependencies import require_admin
from src.modules.audit.dependencies import get_audit_read_service
from src.modules.audit.schemas import AuditLogPage
from src.modules.audit.service import AuditReadService
from src.modules.users.models import User

router = APIRouter(prefix="/audit", tags=["Audit"])


@router.get(
    "/",
    response_model=AuditLogPage,
    status_code=status.HTTP_200_OK,
    summary="Consultar el registro de auditoría (solo administradores)",
)
def list_audit_log(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=1, le=200),
    action: Optional[str] = Query(default=None, max_length=100),
    user_id: Optional[int] = Query(default=None),
    service: AuditReadService = Depends(get_audit_read_service),
    current_user: User = Depends(require_admin),
):
    """Consulta la auditoría con paginación y filtros opcionales.

    Solo administradores (403 para el resto). Los registros se ordenan por
    fecha descendente; los valores sensibles (contraseñas, tokens, secretos)
    se eliminan antes de almacenarse. ``password``/``token`` nunca aparecen.
    """
    return service.list(page, limit, action, user_id)
