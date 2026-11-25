"""Regresiones de la paginación acordada en Fase 6.

Fase 3 propuso ``skip``/``limit``, pero se conservó el contrato de Fase 6
(``page``/``limit`` con envelope ``items/total/page/limit``) para no romper
el frontend ni el OpenAPI aprobado.
"""

import pytest
from pydantic import ValidationError

from src.core.pagination import Page, PaginationParams, like_pattern


@pytest.mark.unit
def test_pagination_defaults():
    pagination = PaginationParams()
    assert pagination.model_dump() == {"page": 1, "limit": 20}
    assert pagination.offset == 0


@pytest.mark.unit
def test_pagination_offset_and_bounds():
    pagination = PaginationParams(page=3, limit=100)
    assert pagination.offset == 200


@pytest.mark.parametrize(
    "params",
    [{"page": 0}, {"limit": 0}, {"limit": 101}],
)
@pytest.mark.unit
def test_pagination_rejects_out_of_range(params):
    with pytest.raises(ValidationError):
        PaginationParams(**params)


@pytest.mark.unit
def test_page_envelope_has_the_approved_shape():
    page = Page[int](items=[1, 2], total=9, page=1, limit=2)
    assert page.model_dump() == {"items": [1, 2], "total": 9, "page": 1, "limit": 2}


@pytest.mark.unit
def test_like_pattern_escapes_wildcards():
    assert like_pattern("100%_pan") == r"%100\%\_pan%"
