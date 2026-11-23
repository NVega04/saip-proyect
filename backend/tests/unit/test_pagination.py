"""Regresiones de la dependencia de paginación de la Fase 3."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.core.pagination import Pagination, PaginationParams

app = FastAPI()


@app.get("/items")
def list_items(pagination: Pagination):
    return {"skip": pagination.skip, "limit": pagination.limit}


client = TestClient(app)


@pytest.mark.unit
def test_pagination_defaults():
    assert PaginationParams().model_dump() == {"skip": 0, "limit": 20}
    assert client.get("/items").json() == {"skip": 0, "limit": 20}


@pytest.mark.unit
def test_pagination_accepts_valid_range():
    response = client.get("/items", params={"skip": 5, "limit": 100})
    assert response.status_code == 200
    assert response.json() == {"skip": 5, "limit": 100}


@pytest.mark.parametrize(
    "params",
    [{"skip": -1}, {"limit": 0}, {"limit": 101}],
)
@pytest.mark.unit
def test_pagination_rejects_out_of_range(params):
    assert client.get("/items", params=params).status_code == 422
