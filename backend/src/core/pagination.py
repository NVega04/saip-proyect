"""Paginación reutilizable de listados (Fase 6, mínimo de la Fase 3.2).

Contrato acordado (igual que ``SaleListPage`` e ``InventoryPage``
existentes): query params ``page`` (>= 1) y ``limit`` (1..100), respuesta

    {"items": [...], "total": N, "page": P, "limit": L}

``PaginationParams`` se inyecta con ``Depends()`` y sus campos aparecen
documentados en OpenAPI. Los servicios usan ``offset`` para la consulta;
el total se obtiene con un ``COUNT`` aparte.
"""

from typing import Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Parámetros de paginación de un listado."""

    page: int = Query(
        default=1, ge=1, description="Página solicitada (numerada desde 1)."
    )
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Filas por página (entre 1 y 100).",
    )

    @property
    def offset(self) -> int:
        """Desplazamiento SQL para la página actual."""
        return (self.page - 1) * self.limit


def like_pattern(term: str) -> str:
    """Convierte un texto de búsqueda en un patrón ``LIKE`` seguro.

    Escapa los comodines ``%``, ``_`` y ``\\`` para que el usuario pueda
    buscarlos literalmente.
    """
    escaped = (
        term.strip()
        .replace("\\", "\\\\")
        .replace("%", "\\%")
        .replace("_", "\\_")
    )
    return f"%{escaped}%"


class Page(BaseModel, Generic[T]):
    """Envelope de listado paginado."""

    items: list[T]
    total: int
    page: int
    limit: int
