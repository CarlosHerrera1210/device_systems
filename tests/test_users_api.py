import pytest
from fastapi.testclient import TestClient

from app.data.users_db import users_db
from app.main import app


client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_users_db():
    users_db.clear()
    users_db.extend(
        [
            {
                "id": 1,
                "name": "Carlos Herrera",
                "email": "carlos@example.com",
                "role": "admin",
                "is_active": True,
            },
            {
                "id": 2,
                "name": "Laura Gomez",
                "email": "laura@example.com",
                "role": "support",
                "is_active": True,
            },
            {
                "id": 3,
                "name": "Andres Perez",
                "email": "andres@example.com",
                "role": "user",
                "is_active": False,
            },
        ]
    )
    yield
    users_db.clear()


def test_health_endpoint_returns_custom_headers():
    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["X-App-Name"] == "device_systems"
    assert response.headers["X-API-Version"] == "2.0.0"


def test_openapi_schema_is_available():
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert response.json()["info"]["title"] == "device_systems API"
    assert "/users" in response.json()["paths"]


def test_redoc_page_uses_available_stable_bundle():
    response = client.get("/redoc")

    assert response.status_code == 200
    assert "redoc@2.5.0/bundles/redoc.standalone.js" in response.text


def test_list_users_returns_headers_and_users():
    response = client.get("/users")

    assert response.status_code == 200
    assert response.headers["X-App-Name"] == "device_systems"
    assert response.headers["X-API-Version"] == "2.0.0"
    assert response.json()["total"] >= 3


def test_get_user_by_id():
    response = client.get("/users/1")

    assert response.status_code == 200
    assert response.json()["email"] == "carlos@example.com"


def test_filter_users_by_role():
    response = client.get("/users?role=admin")

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["users"][0]["role"] == "admin"


def test_filter_users_by_active_status():
    response = client.get("/users?is_active=false")

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["users"][0]["is_active"] is False


def test_create_user():
    payload = {
        "name": "Maria Lopez",
        "email": "maria.lopez@example.com",
        "role": "user",
        "is_active": True,
    }

    response = client.post("/users", json=payload)

    assert response.status_code == 201
    assert response.json()["id"] == 4
    assert response.json()["email"] == "maria.lopez@example.com"


def test_duplicate_email_returns_bad_request():
    payload = {
        "name": "Carlos Herrera",
        "email": "carlos@example.com",
        "role": "admin",
        "is_active": True,
    }

    response = client.post("/users", json=payload)

    assert response.status_code == 400


def test_invalid_name_returns_validation_error():
    payload = {
        "name": "Al",
        "email": "alberto@example.com",
        "role": "support",
        "is_active": True,
    }

    response = client.post("/users", json=payload)

    assert response.status_code == 422


def test_invalid_email_returns_validation_error():
    payload = {
        "name": "Alberto Torres",
        "email": "correo-no-valido",
        "role": "user",
        "is_active": True,
    }

    response = client.post("/users", json=payload)

    assert response.status_code == 422


def test_invalid_role_returns_validation_error():
    payload = {
        "name": "Pedro Ruiz",
        "email": "pedro@example.com",
        "role": "manager",
        "is_active": True,
    }

    response = client.post("/users", json=payload)

    assert response.status_code == 422


def test_unknown_user_returns_not_found():
    response = client.get("/users/999")

    assert response.status_code == 404


def test_update_user_full():
    payload = {
        "name": "Carlos Actualizado",
        "email": "carlos.actualizado@example.com",
        "role": "support",
        "is_active": False,
    }

    response = client.put("/users/1", json=payload)

    assert response.status_code == 200
    assert response.json()["name"] == "Carlos Actualizado"
    assert response.json()["role"] == "support"


def test_update_user_partial():
    payload = {"role": "support"}

    response = client.patch("/users/1", json=payload)

    assert response.status_code == 200
    assert response.json()["role"] == "support"


def test_patch_empty_returns_bad_request():
    response = client.patch("/users/1", json={})

    assert response.status_code == 400


def test_delete_user():
    response = client.delete("/users/1")

    assert response.status_code == 204


def test_delete_unknown_user_returns_not_found():
    response = client.delete("/users/999")

    assert response.status_code == 404

