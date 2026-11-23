"""Parámetros de paginación reutilizables para los listados de SAIP.

Se mantiene el tipo de respuesta ``list[...]``: solo se acota el número de
filas devueltas. El cliente solicita ``skip`` (filas a omitir) y ``limit``
(tamaño de página, máximo 100).
"""

from typing import Annotated

from fastapi import Depends, Query
from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    skip: int = Field(default=0, ge=0, description="Número de filas a omitir")
    limit: int = Field(
        default=20, ge=1, le=100, description="Número máximo de filas devueltas"
    )


def get_pagination_params(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PaginationParams:
    return PaginationParams(skip=skip, limit=limit)


Pagination = Annotated[PaginationParams, Depends(get_pagination_params)]
