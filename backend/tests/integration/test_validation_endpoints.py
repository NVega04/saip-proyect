import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.validation


@pytest.mark.parametrize(
    ("path", "params"),
    [
        ("/sales/", {"page": 0}),
        ("/sales/", {"limit": 201}),
        ("/inventory/summary", {"limit": 101}),
        ("/audit/", {"limit": 0}),
        ("/stats/dashboard", {"days": 400}),
        ("/reports/products", {"format": "pdf"}),
    ],
)
def test_invalid_query_parameters_are_rejected(
    client: TestClient, admin_headers: dict[str, str], path: str, params: dict
):
    response = client.get(path, headers=admin_headers, params=params)

    assert response.status_code == 422


def test_pagination_is_reflected_in_response(
    client: TestClient, admin_headers: dict[str, str]
):
    response = client.get(
        "/sales/", headers=admin_headers, params={"page": 2, "limit": 1}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 2
    assert data["limit"] == 1
    assert len(data["items"]) <= 1
